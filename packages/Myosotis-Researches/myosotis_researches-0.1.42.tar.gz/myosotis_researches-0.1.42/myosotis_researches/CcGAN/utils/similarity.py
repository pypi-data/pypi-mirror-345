import cv2
import math
import numpy as np
from PIL import Image
from scipy.special import rel_entr
from skimage.metrics import structural_similarity as ssim


# MSE
def _MSE(image_1, image_2):
    array_1 = np.asarray(image_1) / 255
    array_2 = np.asarray(image_2) / 255
    n, m, _ = array_1.shape
    return np.sum((array_1 - array_2) ** 2) / (n * m * 3)


def MSE(images):
    MSE_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            MSE_sum += _MSE(images[i], images[j])
    return MSE_sum / (n * (n - 1) / 2)


# SSIM


def _SSIM(image_1, image_2):

    array_1 = np.asarray(image_1)
    array_2 = np.asarray(image_2)
    score, _ = ssim(array_1, array_2, channel_axis=-1, full=True)
    return score


def SSIM(images):
    SSIM_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            SSIM_sum += _SSIM(images[i], images[j])
    return SSIM_sum / (n * (n - 1) / 2)


# PSNR
def _PSNR(image_1, image_2):
    mse = _MSE(image_1, image_2)
    if mse == 0:
        return float("inf")
    else:
        return 20 * math.log10(1.0 / math.sqrt(mse))


def PSNR(images):
    PSNR_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            PSNR_sum += _PSNR(images[i], images[j])
    return PSNR_sum / (n * (n - 1) / 2)


# Cross-correlation


def _cross_correlation(image_1, image_2):
    array_1 = np.asarray(image_1).astype(np.float32) / 255
    array_2 = np.asarray(image_2).astype(np.float32) / 255
    correlations = []
    for c in range(3):
        channel1 = array_1[..., c]
        channel2 = array_2[..., c]
        channel1 -= channel1.mean()
        channel2 -= channel2.mean()
        numerator = np.sum(channel1 * channel2)
        denominator = np.sqrt(np.sum(channel1**2) * np.sum(channel2**2))
        corr = numerator / denominator if denominator != 0 else 0
        correlations.append(corr)
    return np.mean(correlations)


def cross_correlation(images):
    cross_correlation_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            cross_correlation_sum += _cross_correlation(images[i], images[j])
    return cross_correlation_sum / (n * (n - 1) / 2)


# Histogram intersection
def _rgb_histogram(image, bins=32):
    """
    image: numpy array of shape (H, W, 3), RGB format
    returns: concatenated and normalized histogram for R, G, B channels
    """
    image = np.asarray(image)
    hist_r, _ = np.histogram(image[:, :, 0], bins=bins, range=(0, 256))
    hist_g, _ = np.histogram(image[:, :, 1], bins=bins, range=(0, 256))
    hist_b, _ = np.histogram(image[:, :, 2], bins=bins, range=(0, 256))
    hist = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float64)
    hist /= np.sum(hist)  # Normalize to make it a probability distribution
    return hist


def _histogram_intersection(image_1, image_2):
    array_1 = np.asarray(image_1)
    array_2 = np.asarray(image_2)
    hist_1 = _rgb_histogram(array_1)
    hist_2 = _rgb_histogram(array_2)
    return np.sum(np.minimum(hist_1, hist_2))


def histogram_intersection(images):
    histogram_intersection_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            histogram_intersection_sum += _histogram_intersection(images[i], images[j])
    return histogram_intersection_sum / (n * (n - 1) / 2)


# KL divergence
def _kl_divergence(image_1, image_2, bins=256):
    kl_values = []

    for c in range(3):
        arr1 = np.array(image_1)[:, :, c].flatten()
        arr2 = np.array(image_2)[:, :, c].flatten()
        hist1, _ = np.histogram(arr1, bins=bins, range=(0, 256), density=True)
        hist2, _ = np.histogram(arr2, bins=bins, range=(0, 256), density=True)
        hist1 += 1e-10
        hist2 += 1e-10
        kl_1_2 = np.sum(rel_entr(hist1, hist2))
        kl_2_1 = np.sum(rel_entr(hist2, hist1))
        sym_kl = 0.5 * (kl_1_2 + kl_2_1)
        kl_values.append(sym_kl)
    return float(np.mean(kl_values))


def kl_divergence(images):
    kl_divergence_sum = 0
    n = len(images)
    for i in range(n):
        for j in range(i + 1, n):
            kl_divergence_sum += _kl_divergence(images[i], images[j])
    return kl_divergence_sum / (n * (n - 1) / 2)


# Similarity
_method_dict = {
    "MSE": MSE,
    "SSIM": SSIM,
    "PSNR": PSNR,
    "cross-correlation": cross_correlation,
    "histogram-intersection": histogram_intersection,
    "kl-divergence": kl_divergence,
}


def similarity(images, method):
    return _method_dict[method](images)


__all__ = ["similarity"]
