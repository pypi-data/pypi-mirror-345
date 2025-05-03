from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
from scipy.signal import find_peaks

from prospecpy.second_deriv import flip_order


def baseline_spline(anchor_points, degree=3, smooth=0):
    """
    Function to fit a spline curve to anchor points data to estimate baseline.

    Parameters:
    - anchor_points: DataFrame
        DataFrame containing anchor points with 'wavenumber' and 'absorbance' columns.
    - degree: int, optional (default=3)
        Degree of the spline interpolation.
    - smooth: float, optional (default=0)
        Smoothing parameter for spline fitting.

    Returns:
    - baseline_curve: DataFrame
        DataFrame containing the fitted baseline curve with 'wavenumber' and 'absorbance' columns.
    """
    spline_fit = UnivariateSpline(
        anchor_points["wavenumber"], anchor_points["absorbance"], k=degree, s=smooth
    )
    x_range = np.linspace(
        int(min(anchor_points["wavenumber"])), int(max(anchor_points["wavenumber"])), 1000
    )
    # x_range = anchor_points['wavenumber']
    baseline_fit = spline_fit(x_range)
    baseline_curve = pd.DataFrame({"wavenumber": x_range, "absorbance": baseline_fit})
    return baseline_curve


def raw_spline(raw_wavenumber, raw_absorbance, degree=3, smooth=0):
    """
    Function to fit a spline curve to raw points data to avoid discreet peaks misrepresenting the subtracted baseline result

    Parameters:
    - raw_wavenumber: array
       List of wavenumber values from raw data.
    - raw_absorbance: array
       List of absorbance values from raw data.
    - degree: int, optional (default=3)
        Degree of the spline interpolation.
    - smooth: float, optional (default=0)
        Smoothing parameter for spline fitting.

    Returns:
    - baseline_curve: DataFrame
        DataFrame containing the fitted baseline curve with 'wavenumber' and 'absorbance' columns.
    """
    raw_spline_fit = UnivariateSpline(
        flip_order(raw_wavenumber), flip_order(raw_absorbance), k=degree, s=smooth
    )
    raw_x_range = np.linspace(int(min(raw_wavenumber)), int(max(raw_wavenumber)), 1000)
    raw_fit = raw_spline_fit(raw_x_range)
    return [raw_x_range, raw_fit]


def baseline_correction(baseline_points, raw_wavenumber, raw_absorbance):
    """
    Perform baseline correction on raw absorbance data using baseline points.

    Args:
    - baseline_points (DataFrame): DataFrame containing baseline wavenumber and absorbance values.
    - raw_wavenumber (array): List of wavenumber values from raw data.
    - raw_absorbance (array): List of absorbance values from raw data.

    Returns:
    - baseline_corrected_abs (list): List of baseline-corrected absorbance values.
    """
    baseline_corrected_abs = []
    for idx, wv_num in enumerate(raw_wavenumber):  # iterate through each data point in raw data
        # subtract the wv_num from the baseline[wavenumber] and take absolute of the diff and sort it and get the
        # idx of the point from the baseline that is closest to the raw datapoint
        diff_array = abs(baseline_points["wavenumber"] - wv_num)
        # this is the index of the closest wavenumber in the baseline curve to that of the datapoint
        closest_wv_num = diff_array.idxmin()
        # Now subtract the baseline absornace from the raw data absorbance
        raw_minus_baseline = raw_absorbance[idx] - baseline_points.loc[closest_wv_num, "absorbance"]

        if raw_minus_baseline < 0:
            # if the difference is negative, then baseline point is higher than raw absorbance which is not possible. Hence appending 0 at those points
            baseline_corrected_abs.append(0)
        else:
            baseline_corrected_abs.append(raw_minus_baseline)

    return baseline_corrected_abs


def get_baseline_peak_index(baseline_corrected_abs, rawdata_wavenumber, raw_data_peak_wv):
    # get all the peaks index in the baselinecorrected data with no thresholds
    peak_index_baseline = find_peaks(baseline_corrected_abs)
    # print('peak index baseline', peak_index_baseline)
    # get the corresponding wavenumbers present at the peak_index
    baseline_peak_wv = [[rawdata_wavenumber[i], i] for i in peak_index_baseline[0]]
    # print('baseline_peak_wv', baseline_peak_wv)
    # Now obtain the corresponding peak wavenumbers using raw_data_peak_wv as reference. This was found using the
    # raw spectra data

    # adjust the range till the function result aligns with the raw_data_peak_wv
    range_val = 1  # changed becuase we are using spline results

    peak_wv_baseline = []
    peak_idx_baseline = []
    # use the raw data peak wv as the standard of when to stop
    while len(peak_wv_baseline) < len(raw_data_peak_wv):
        # print(f'baseline peak wv{peak_wv_baseline}, raw peak wv {raw_data_peak_wv}')
        range_val = range_val + 0.5  # progressive range val to find all the desired peaks
        # print('range updated', range)
        if range_val > 1000:
            break
        for raw_wv in raw_data_peak_wv:
            for wv in baseline_peak_wv:
                if abs(wv[0] - raw_wv) <= range_val and wv[0] not in peak_wv_baseline:
                    peak_wv_baseline.append(wv[0])
                    peak_idx_baseline.append(wv[1])

    # cleaning the peak_wv_baseline list, such that the peaks with negligible abs are deleted
    # print(len(baseline_corrected_abs), baseline_corrected_abs[491])
    i = 0
    while i < len(peak_wv_baseline):
        # print('i',i, 'len of var', len(peak_idx_baseline))
        idx = peak_idx_baseline[i]
        if baseline_corrected_abs[idx] < max(baseline_corrected_abs) * 0.01:
            peak_idx_baseline.remove(peak_idx_baseline[i])
            peak_wv_baseline.remove(peak_wv_baseline[i])
            i = 0
            continue
        i += 1

    peak_baseline_abs = []
    for index in peak_idx_baseline:
        peak_baseline_abs.append(baseline_corrected_abs[index])

    return peak_idx_baseline, peak_wv_baseline, peak_baseline_abs


def plot_baseline_corrected_data(
    x_wavenb, baseline_abs, peak_wv, peak_abs, sample_name, batch_id, showplots
):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_wavenb, baseline_abs, label="Baseline Subtracted Data")
    ax.plot(peak_wv, peak_abs, "ro", label="peaks")
    for s, d in zip(peak_wv, peak_abs, strict=False):
        plt.annotate(round(s, 2), xy=(s, d), rotation=90)
    if batch_id is not None:
        ax.set_title(f"{sample_name} from batch_d {batch_id}")
    else:
        ax.set_title(f"{sample_name}")
    ax.set_xlabel("wavenumber ($cm^{-1}$)")
    ax.set_ylabel("absorbance")
    ax.legend()
    if showplots:
        plt.show()
    else:
        plt.close(fig)
    return fig


def baseline_correction_prospecpy_objects(
    list_of_propspecpy_object, showplot=False, save=True, verbose=True
):
    """
    Batched adaptation of second_deriv function.
    """

    for prospecpy_obj in list_of_propspecpy_object:
        prospecpy_obj.subtract_baseline(save, showplot, verbose)
