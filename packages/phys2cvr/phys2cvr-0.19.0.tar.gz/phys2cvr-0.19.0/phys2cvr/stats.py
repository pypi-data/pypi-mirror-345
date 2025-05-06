#!/usr/bin/env python3
"""
Statistical module for phys2cvr.

Attributes
----------
LGR :
    Logger
"""

import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as sct

from phys2cvr.io import FIGSIZE, SET_DPI, export_regressor
from phys2cvr.signal import resample_signal

R2MODEL = ["full", "partial", "intercept", "adj_full", "adj_partial", "adj_intercept"]

LGR = logging.getLogger(__name__)
LGR.setLevel(logging.INFO)


def x_corr(func, co2, lastrep, firstrep=0, offset=0, abs_xcorr=False):
    """
    Cross correlation between `func` and `co2`.

    Parameters
    ----------
    func : np.ndarray
        Timeseries, must be SHORTER (or of equal length) than `co2`
    co2 : np.ndarray
        Second timeseries, can be LONGER than `func`
    lastrep : int
        Last index to take into account in `func`
    firstrep : int, optional
        First index totake into account in `func`
    offset : int, optional
        Optional amount of offset desired for `func`
    abs_xcorr : bool, optional
        If True, x_corr will find the maximum absolute correlation,
        i.e. max(|corr(func, co2)|)

    Returns
    -------
    float :
        Highest correlation
    int :
        Index of higher correlation
    xcorr : np.ndarray
        Full Xcorr

    Raises
    ------
    ValueError
        If `offset` is too high for the functional file
    """
    if len(func) + offset > len(co2):
        if offset != 0:
            raise ValueError(
                f"The specified offset of {offset} is too high to "
                f"compare func of length {len(func)} with co2 of "
                f"length {len(co2)}"
            )
        else:
            LGR.warning(
                f"The timeseries has length of {len(func)}, but the co2 "
                f"has length of {len(co2)}. Matching co2 to func."
            )
        if firstrep + len(co2) > len(func):
            firstrep = len(func) - len(co2)
        elif firstrep < 0:
            firstrep = 0
        if lastrep + len(co2) > len(func):
            lastrep = len(func) - len(co2)
        elif lastrep < firstrep:
            lastrep = firstrep + 1

        xcorr = np.empty(lastrep - firstrep, dtype="float32")
        for i in range(firstrep, lastrep):
            xcorr[i] = np.corrcoef(co2, func[0 + i : len(co2) + i].T)[1, 0]
    else:
        if firstrep + offset + len(func) > len(co2):
            firstrep = len(co2) - offset - len(func)
        elif firstrep + offset < 0:
            firstrep = -offset
        if lastrep + offset + len(func) > len(co2):
            lastrep = len(co2) - offset - len(func)
        elif lastrep < firstrep:
            lastrep = firstrep + 1

        xcorr = np.empty(lastrep - firstrep, dtype="float32")
        for i in range(firstrep, lastrep):
            xcorr[i] = np.corrcoef(
                func, co2[0 + i + offset : len(func) + i + offset].T
            )[1, 0]

    if abs_xcorr:
        xcorr = np.abs(xcorr)

    return xcorr.max(), (xcorr.argmax() + firstrep + offset), xcorr


def get_regr(
    func_avg,
    petco2hrf,
    tr,
    freq,
    outname,
    lag_max=None,
    trial_len=None,
    n_trials=None,
    ext=".1D",
    lagged_regression=True,
    legacy=False,
    abs_xcorr=False,
    skip_xcorr=False,
):
    """
    Create regressor(s) of interest for nifti GLM.

    Parameters
    ----------
    func_avg : np.ndarray
        Functional timeseries (1D)
    petco2hrf : np.ndarray
        Regressor of interest
    tr : str, int, or float
        TR of timeseries
    freq : str, int, or float
        Sample frequency of petco2hrf
    outname : list or path
        Path to output directory for regressors.
    lag_max : int or float, optional
        Limits (both positive and negative) of the temporal area to explore,
        expressed in seconds.
        Default: 9 (i.e. ±9 seconds)
    trial_len : str or int, optional
        Length of each single trial for tasks that have more than one
        (E.g. BreathHold, CO2 challenges, ...)
        Used to improve cross correlation estimation.
        Default: None
    n_trials : str or int, optional
        Number of trials in the task.
        Default: None
    ext : str, optional
        Extension to be used for the exported regressors.
    lagged_regression : bool, optional
        Estimate regressors for each possible lag of `petco2hrf`.
        If True, the maximum number of regressors will be `(freq*lag_max*2)+1`
    legacy : bool, optional
        If True, exclude the upper lag limit from the regression estimation.
        If True, the maximum number of regressors will be `(freq*lag_max*2)`
    abs_xcorr : bool, optional
        If True, the cross correlation will consider the maximum absolute
        correlation, i.e. if a negative correlation is higher than the highest
        positive, the negative correlation will be chosen instead.
    skip_xcorr : bool, optional
        If True, skip the cross correlation step.

    Returns
    -------
    petco2hrf_demean : np.ndarray
        The central, demeaned petco2hrf regressor.
    petco2hrf_shifts : np.ndarray
        The other shifted versions of the regressor.
    """
    # Setting up some variables
    first_tp, last_tp = 0, -1

    if trial_len and n_trials:
        # If both are specified, disregard two extreme _trial from matching.
        LGR.info(f"Specified {n_trials} trials lasting {trial_len} seconds")
        if n_trials > 2:
            LGR.info("Ignoring first trial to improve first bulk shift estimation")
            first_tp = int(trial_len * freq)
        else:
            LGR.info("Using all trials for bulk shift estimation")
        if n_trials > 3:
            LGR.info("Ignoring last trial to improve first bulk shift estimation")
            last_tp = first_tp * (n_trials - 1)

    elif trial_len and not n_trials:
        LGR.warning(
            "The length of trial was specified, but the number of "
            "trials was not. Using all trials for bulk shift estimation"
        )
    elif not trial_len and n_trials:
        LGR.warning(
            "The number of trials was specified, but the length of "
            "trial was not. Using all trials for bulk shift estimation"
        )
    else:
        LGR.info("Using all trials for bulk shift estimation.")

    # Upsample functional signal
    func_upsampled = resample_signal(func_avg, 1 / tr, freq)
    len_upd = func_upsampled.shape[0]

    # Preparing breathhold and CO2 trace for Xcorr
    func_cut = func_upsampled[first_tp:last_tp]
    petco2hrf_cut = petco2hrf[first_tp:]

    nrep = abs(petco2hrf_cut.shape[0] - func_cut.shape[0])

    # Preparing time axis for plots
    time_axis = np.arange(0, nrep / freq, 1 / freq)

    if nrep < time_axis.shape[0]:
        time_axis = time_axis[:nrep]
    elif nrep > time_axis.shape[0]:
        time_axis = np.pad(
            time_axis, (0, int(nrep - time_axis.shape[0])), "linear_ramp"
        )

    if not skip_xcorr:
        _, optshift, xcorr = x_corr(func_cut, petco2hrf, nrep, abs_xcorr=abs_xcorr)
        LGR.info(f"Cross correlation estimated bulk shift at {optshift / freq} seconds")
        # Export estimated optimal shift in seconds
        with open(f"{outname}_optshift.1D", "w") as f:
            print(f"{(optshift / freq):.4f}", file=f)
        # Export xcorr figure
        plt.figure(figsize=FIGSIZE, dpi=SET_DPI)
        plt.plot(time_axis, xcorr)
        plt.title("optshift")
        plt.savefig(f"{outname}_optshift.png", dpi=SET_DPI)
        plt.close()
    else:
        optshift = 0

    # Check which timeseries was shifted
    if func_cut.shape[0] <= petco2hrf.shape[0]:
        petco2hrf_shift = petco2hrf[optshift : optshift + len_upd]
    elif func_cut.shape[0] > petco2hrf.shape[0]:
        petco2hrf_shift = np.pad(
            petco2hrf,
            (int(optshift), int(func_cut.shape[0] - petco2hrf.shape[0] - optshift)),
            "mean",
        )
        optshift = 0

    # Exporting figures of shift
    plt.figure(figsize=FIGSIZE, dpi=SET_DPI)
    plt.plot(sct.zscore(petco2hrf_shift), "-", sct.zscore(func_upsampled), "-")
    plt.title("GM and shift")
    plt.savefig(f"{outname}_petco2hrf.png", dpi=SET_DPI)
    plt.close()

    petco2hrf_demean = export_regressor(
        petco2hrf_shift, freq, tr, outname, "petco2hrf", ext
    )

    # Initialise the shifts first.
    petco2hrf_shifts = None
    if lagged_regression and lag_max:
        outprefix = os.path.join(
            os.path.split(outname)[0], "regr", os.path.split(outname)[1]
        )
        os.makedirs(os.path.join(os.path.split(outname)[0], "regr"), exist_ok=True)

        # Set num of fine shifts: 9 seconds is a bit more than physiologically feasible
        negrep = int(lag_max * freq)
        if legacy:
            posrep = negrep
        else:
            posrep = negrep + 1
        petco2hrf_shifts = np.empty(
            [func_avg.shape[0], negrep + posrep], dtype="float32"
        )

        # Padding regressor for shift, and padding optshift too

        if (optshift - negrep) < 0:
            lpad = negrep - optshift
        else:
            lpad = 0

        if (optshift + posrep + len_upd) > petco2hrf.shape[0]:
            rpad = (optshift + posrep + len_upd) - petco2hrf.shape[0]
        else:
            rpad = 0

        if func_cut.shape[0] <= petco2hrf.shape[0]:
            petco2hrf_padded = np.pad(petco2hrf, (int(lpad), int(rpad)), "mean")
        elif func_cut.shape[0] > petco2hrf.shape[0]:
            petco2hrf_padded = np.pad(petco2hrf_shift, (int(lpad), int(rpad)), "mean")

        for n, i in enumerate(range(-negrep, posrep)):
            petco2hrf_lagged = petco2hrf_padded[
                optshift + lpad - i : optshift + lpad - i + len_upd
            ]
            petco2hrf_shifts[:, n] = export_regressor(
                petco2hrf_lagged, freq, tr, outprefix, f"{n:04g}", ext
            )

    elif lagged_regression and lag_max is None:
        LGR.warning(
            "The generation of lagged regressors was requested, "
            "but the maximum lag was not specified. Skipping "
            "lagged regressor generation."
        )
    else:
        LGR.info("Skipping lag regressors generation.")

    return petco2hrf_demean, petco2hrf_shifts


def get_legendre(degree, length):
    """
    Producesthe Legendre polynomials of order `degree`.

    Parameters
    ----------
    degree : int
        Highest order desired.
    length : int
        Number of samples of the polynomials.

    Returns
    -------
    legendre : np.ndarray
        A `degree`*`length` array with all the polynomials up to order `degree`
    """

    def _bonnet(d, x):
        if d == 0:
            return np.ones_like(x)
        elif d == 1:
            return x
        else:
            return (
                (2 * d - 1) * x * _bonnet(d - 1, x) - (d - 1) * _bonnet(d - 2, x)
            ) / d

    x = np.linspace(-1, 1, length)
    legendre = np.empty([length, degree + 1], dtype="float32")
    for n in range(degree + 1):
        legendre[:, n] = _bonnet(n, x)
    return legendre


def ols(Ymat, Xmat, r2model="full", residuals=False, demean=False):
    """
    Implement Ordinary Least Square linear regression.

    Both Ymat and Xmat must encode the time axis in axis 0.
    This is the barebone OLS implementation. For the full regression step,
    see `stats.regression`.

    Parameters
    ----------
    Ymat : np.ndarray
        Dependent variable, 1D or 2D.
        The time axis must be in columns, i.e. time axis must be axis 0.
    Xmat : np.ndarray
        Independent variables, 1D or 2D. The regressor of interest MUST be the last one.
        Regressors must be in columns, i.e. time axis must be axis 0.
    r2model : {'full', 'partial', 'intercept', 'adj_full', 'adj_partial', 'adj_intercept'}, optional
        R^2 to report.
        Possible models are:
            - 'full' (default)
                Use every regressor in the model, i.e. compare versus baseline 0
            - 'partial'
                Consider only the first vector of Xmat in the model, i.e. compare
                versus baseline composed by all vectors of Xmat beside the first.
            - 'intercept'
                Use every regressor in the model, but the intercept, i.e. compare
                versus baseline intercept (Legendre polynomial order 0, a.k.a.
                average signal)
            - 'adj_*'
                Adjusted R^2 version of simple counterpart
        Under normal conditions, while the R^2 value will be different between options,
        a lagged regression based on any R^2 model will give the same results.
        This WILL NOT be the case if orthogonalisations between the first vector of Xmat
        and the others are introduced: a lagged regression based on `partial` might hold
        different results from .
        Default: 'full'
    residuals : bool, optional
        If True, output only residuals of the model - this is mainly for orthogonalisation
        If False, output betas, tstats, R^2 (default).
    demean : bool, optional
        If True, demean Xmat before running OLS.
        Default is False.

    Returns
    -------
    betas : np.ndarray
        Beta values
    t_stats : np.ndarray
        T-stats values
    r_square : np.ndarray
        R^2 values

    Raises
    ------
    NotImplementedError
        If Ymat has more than 2 dimensions
        If Xmat has more than 2 dimensions
        At the moment, if "poly" R^2 is declared, as it's not implemented yet.
    ValueError
        If a non-valid R^2 value is declared
    """
    if Ymat.ndim > 2:
        raise NotImplementedError(
            "OLS on data with more than 2 dimensions is not implemented yet."
        )
    elif Ymat.ndim < 2:
        Ymat = Ymat[..., np.newaxis]
    if Xmat.ndim > 2:
        raise NotImplementedError(
            "OLS with regressors with more than 2 dimensions is not implemented yet."
        )
    elif Xmat.ndim < 2:
        Xmat = Xmat[..., np.newaxis]

    if demean:
        LGR.info("Demean regressors")
        Xmat = Xmat - Xmat.mean(axis=0)

    try:
        betas, RSS, _, _ = np.linalg.lstsq(Xmat, Ymat, rcond=None)
        if not RSS.any():
            RSS = np.zeros(betas.shape[1])

    except np.linalg.LinAlgError:
        raise ValueError(
            "The given matrices might not be oriented correctly. Try to transpose the "
            "regressor matrix."
        )

    if residuals:
        return Ymat - (Xmat @ betas)
    else:
        # compute t-values of betas (estimates)
        # first compute number of degrees of freedom
        df = Xmat.shape[0] - Xmat.shape[1]

        # compute sigma:
        # RSS = sum{[mdata - (X * betas)]^2}
        # sigma = RSS / Degrees_of_Freedom
        # RSS = np.sum(np.power(Ymat.T - np.dot(Xmat, betas), 2), axis=0)
        sigma = RSS / df
        sigma = sigma[..., np.newaxis]

        # Copmute std of betas:
        # C = (mat^T * mat)_ii^(-1)
        # std(betas) = sqrt(sigma * C)
        C = np.diag(np.linalg.pinv(np.dot(Xmat.T, Xmat)))
        C = C[..., np.newaxis]
        std_betas = np.sqrt(np.outer(C, sigma))
        tstats = betas / std_betas
        tstats[np.isneginf(tstats)] = -9999
        tstats[np.isposinf(tstats)] = 9999

        # Compute R^2 coefficient of multiple determination!
        r2model_support = False
        for model in R2MODEL:
            if r2model == model:
                r2model_support = True
        if not r2model_support:
            raise ValueError(
                f"{r2model} R^2 not supported. Supported R^2 models are {R2MODEL}"
            )

        r2msg = ""
        # R^2 = 1 - RSS/TSS, (TSS = total sum of square)
        if "full" in r2model:
            # Baseline model is 0 - this is what we're using ATM
            TSS = np.sum(np.power(Ymat, 2), axis=0)
        elif "intercept" in r2model:
            # Baseline model is intercept: TSS is variance*samples
            TSS = Ymat.var(axis=0) * Ymat.shape[0]
        elif "poly" in r2model:
            # Baseline model is legendre polynomials - or others: TSS is RSS of partial matrix
            # Could improve efficiency by moving this fitting step outside the regression loop
            # polynomials = Xmat[:, 0:4]
            # TSS = np.linalg.lstsq(polynomials, Ymat.T, rcond=None)[1]
            raise NotImplementedError("'poly' R^2 not implemented yet")
            r2msg = "polynomial"
        elif "partial" in r2model:
            pass

        if "partial" in r2model:
            # We could also compute PARTIAL R square of regr instead (or on top)
            # See for computation: https://sscc.nimh.nih.gov/sscc/gangc/tr.html
            tstats_square = np.power(tstats, 2)
            r_square = (tstats_square / (tstats_square + df))[-1, :]
        else:
            r_square = np.ones(Ymat.shape[1], dtype="float32") - (RSS / TSS)

        if r2msg == "":
            r2msg = r2model
        if "adj_" in r2model:
            # We could compute ADJUSTED R^2 instead
            r_square = 1 - ((1 - r_square) * (Xmat.shape[0] - 1) / (df - 1))
            r2msg = f"adjusted {r2msg}"

        LGR.info(f"Adopting {r2msg} baseline to compute R^2.")

        return betas, tstats, r_square


def regression(
    data,
    regr,
    denoise_mat=None,
    ortho_mat=None,
    extra_mat=None,
    mask=None,
    r2model="full",
    debug=False,
    x1D="mat.1D",
):
    """
    Estimate regression parameters.

    Parameters
    ----------
    data : np.ndarray
        Dependent variable of the model (i.e. Y), as a 4D volume.
    regr : np.ndarray
        Regressor of interest
    denoise_mat : np.ndarray or None, optional
        Confounding effects (regressors)
    ortho_mat : np.ndarray or None, optional
        Confounding effects (regressors) that will be orthogonalised w.r.t. `regr`, `denoise_mat`, and
        `extra_mat`
    extra_mat : np.ndarray or None, optional
        Extra factors (regressors) that will be used to orthogonalise `ortho_mat`
    mask : np.ndarray or None, optional
        A 3D mask to reduce the number of voxels to run the regression for.
    r2model : {'full', 'partial', 'intercept', 'adj_full', 'adj_partial', 'adj_intercept'}, optional
        R^2 to report.
        Possible models are:
            - 'full' (default)
                Use every regressor in the model, i.e. compare versus baseline 0
            - 'partial'
                Consider only `regr` in the model, i.e. compare versus baseline
                composed by all other regressors (`denoise_mat`)
            - 'intercept'
                Use every regressor in the model, but the intercept, i.e. compare
                versus baseline intercept (Legendre polynomial order 0, a.k.a.
                average signal)
            - 'adj_*'
                Adjusted R^2 version of normal counterpart
        Under normal conditions, while the R^2 value will be different between options,
        a lagged regression based on any R^2 model will give the same results.
        This WILL NOT be the case if orthogonalisations between `regr` and `denoise_mat`
        are introduced: a lagged regression based on `partial` might hold different
        results.
        Default: 'full'

    Returns
    -------
    bout : np.ndarray
        Beta map
    tout : np.ndarray
        T-stats map
    rout : np.ndarray
        R^2 map

    Raises
    ------
    ValueError
        If `denoise_mat` and `regr` do not have at least one common dimension.
    """
    # Obtain data in 2d
    if mask is None:
        mask = np.ones(data.shape[:-1])

    mask = mask.astype("bool")

    Ymat = data[mask]
    # Check that regr has "two" dimensions
    if regr.ndim < 2:
        regr = regr[..., np.newaxis]

    if denoise_mat is not None:
        if regr.shape[0] != denoise_mat.shape[0]:
            denoise_mat = denoise_mat.T
            if regr.shape[0] != denoise_mat.shape[0]:
                raise ValueError(
                    "The provided confounding matrix does not match "
                    "the dimensionality of the PetCO2hrf regressor!"
                )
        # Stack mat
        # Note: Xmat is not currently demeaned within this function, so inputs
        # should already be demeaned
        Xmat = np.hstack([denoise_mat, regr])
        if ortho_mat is not None:
            if ortho_mat.shape[0] != denoise_mat.shape[0]:
                ortho_mat = ortho_mat.T
                if ortho_mat.shape[0] != denoise_mat.shape[0]:
                    raise ValueError(
                        "The provided orthogonalised matrix does not match "
                        "the dimensionality of the PetCO2hrf regressor!"
                    )

            nuisance_mat = Xmat.copy()
            if extra_mat is not None:
                if extra_mat.shape[0] != denoise_mat.shape[0]:
                    extra_mat = extra_mat.T
                    if extra_mat.shape[0] != denoise_mat.shape[0]:
                        raise ValueError(
                            "The provided extra matrix does not match "
                            "the dimensionality of the PetCO2hrf regressor!"
                        )
                nuisance_mat = np.hstack([nuisance_mat, extra_mat])

            ortho_mat = ols(ortho_mat, nuisance_mat, residuals=True)
            Xmat = np.hstack([ortho_mat, Xmat])
    else:
        Xmat = regr

    if debug:
        os.makedirs(os.path.dirname(x1D), exist_ok=True)
        np.savetxt(x1D, Xmat, fmt="%.6f")

    betas, tstats, r_square = ols(
        Ymat.T, Xmat, r2model="full", residuals=False, demean=False
    )
    if debug:
        # debug should eport betas, tstats, r_square
        pass

    # Assign betas, Rsquare and tstats to new volume
    bout = mask * 1.0
    tout = mask * 1.0
    rout = mask * 1.0
    bout[mask] = betas[-1, :]
    tout[mask] = tstats[-1, :]
    rout[mask] = r_square
    return bout, tout, rout


"""
Copyright 2021, Stefano Moia.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
