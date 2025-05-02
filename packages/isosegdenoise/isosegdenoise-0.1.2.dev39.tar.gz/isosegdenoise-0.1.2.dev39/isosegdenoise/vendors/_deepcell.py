### DeppCell-tf-0.12.4 License:
# Copyright 2016-2023 The Van Valen Lab at the California Institute of
# Technology (Caltech), with support from the Paul Allen Family Foundation,
# Google, & National Institutes of Health (NIH) under Grant U24CA224309-01.
# All rights reserved.
#
# Licensed under a modified Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.github.com/vanvalenlab/deepcell-tf/LICENSE
#
# The Work provided may be used for non-commercial academic purposes only.
# For any other use of the Work, including commercial use, please contact:
# vanvalenlab@gmail.com
#
# Neither the name of Caltech nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


#### DeppCell-toolbox-0.12.0 license
# Copyright 2016-2022 The Van Valen Lab at the California Institute of
# Technology (Caltech), with support from the Paul Allen Family Foundation,
# Google, & National Institutes of Health (NIH) under Grant U24CA224309-01.
# All rights reserved.
#
# Licensed under a modified Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.github.com/vanvalenlab/deepcell-data-processing/LICENSE
#
# The Work provided may be used for non-commercial academic purposes only.
# For any other use of the Work, including commercial use, please contact:
# vanvalenlab@gmail.com
#
# Neither the name of Caltech nor the names of its contributors may be used
# to endorse or promote products derived from this software without specific
# prior written permission.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
'''
This is the modified necessary code for running steinbock from the deepcell toolbox / associated deepcell packages.

The full, original license text can be found in the LICENSE-other-non-commercial.txt file, in the GitHub repository or the packages /Assets/LICENSE_files folder

Modifications: 1). Code from the various deepcell packages has been combined into a single file, will all the edits contingent from that, including removing
                redundant imports, etc.

                2). A Onnx version of the original tensorflow model was created (see tests/convert_pytorch.py file). This file was edited to allow for this
                Onnx model to be used by PyTorch search for

                                    ##>>## 

                to find lines / blocks of code with edits added for the PyTorch integration.  

                3). add __all__ = []  to block auto-api from creating documentation for this
'''
# ruff: noqa

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np

##>>## edits to allow torch if no tensorflow is available:
try:
    import tensorflow as tf
    _is_torch = False

except ImportError:
    _is_torch = True

import torch
import onnx
import onnx2torch
    
##>>##

import logging
import warnings

import timeit

import cv2
from scipy.signal import windows
import scipy.ndimage as nd

from skimage import transform
from skimage.feature import peak_local_max
from skimage.measure import label, regionprops
from skimage.exposure import equalize_adapthist, rescale_intensity
from skimage.morphology import disk, ball, square, cube, dilation, remove_small_objects, h_maxima, remove_small_holes
from skimage.segmentation import relabel_sequential, watershed, find_boundaries

__all__ = []

def erode_edges(mask, erosion_width):
    """Erode edge of objects to prevent them from touching

    Args:
        mask (numpy.array): uniquely labeled instance mask
        erosion_width (int): integer value for pixel width to erode edges

    Returns:
        numpy.array: mask where each instance has had the edges eroded

    Raises:
        ValueError: mask.ndim is not 2 or 3
    """

    if mask.ndim not in {2, 3}:
        raise ValueError('erode_edges expects arrays of ndim 2 or 3.'
                         'Got ndim: {}'.format(mask.ndim))
    if erosion_width:
        new_mask = np.copy(mask)
        for _ in range(erosion_width):
            boundaries = find_boundaries(new_mask, mode='inner')
            new_mask[boundaries > 0] = 0
        return new_mask

    return mask

def fill_holes(label_img, size=10, connectivity=1):
    """Fills holes located completely within a given label with pixels of the same value

    Args:
        label_img (numpy.array): a 2D labeled image
        size (int): maximum size for a hole to be filled in
        connectivity (int): the connectivity used to define the hole

    Returns:
        numpy.array: a labeled image with no holes smaller than ``size``
            contained within any label.
    """
    output_image = np.copy(label_img)
    props = regionprops(np.squeeze(label_img.astype('int')), cache=False)
    for prop in props:
        if prop.euler_number < 1:

            patch = output_image[prop.slice]

            filled = remove_small_holes(
                ar=(patch == prop.label),
                area_threshold=size,
                connectivity=connectivity)

            output_image[prop.slice] = np.where(filled, prop.label, patch)
    return output_image

def deep_watershed(outputs,
                   radius=10,
                   maxima_threshold=0.1,
                   interior_threshold=0.01,
                   maxima_smooth=0,
                   interior_smooth=1,
                   maxima_index=0,
                   interior_index=-1,
                   label_erosion=0,
                   small_objects_threshold=0,
                   fill_holes_threshold=0,
                   pixel_expansion=None,
                   maxima_algorithm='h_maxima',
                   **kwargs):
    """Uses ``maximas`` and ``interiors`` to perform watershed segmentation.
    ``maximas`` are used as the watershed seeds for each object and
    ``interiors`` are used as the watershed mask.

    Args:
        outputs (list): List of [maximas, interiors] model outputs.
            Use `maxima_index` and `interior_index` if list is longer than 2,
            or if the outputs are in a different order.
        radius (int): Radius of disk used to search for maxima
        maxima_threshold (float): Threshold for the maxima prediction.
        interior_threshold (float): Threshold for the interior prediction.
        maxima_smooth (int): smoothing factor to apply to ``maximas``.
            Use ``0`` for no smoothing.
        interior_smooth (int): smoothing factor to apply to ``interiors``.
            Use ``0`` for no smoothing.
        maxima_index (int): The index of the maxima prediction in ``outputs``.
        interior_index (int): The index of the interior prediction in
            ``outputs``.
        label_erosion (int): Number of pixels to erode segmentation labels.
        small_objects_threshold (int): Removes objects smaller than this size.
        fill_holes_threshold (int): Maximum size for holes within segmented
            objects to be filled.
        pixel_expansion (int): Number of pixels to expand ``interiors``.
        maxima_algorithm (str): Algorithm used to locate peaks in ``maximas``.
            One of ``h_maxima`` (default) or ``peak_local_max``.
            ``peak_local_max`` is much faster but seems to underperform when
            given regious of ambiguous maxima.

    Returns:
        numpy.array: Integer label mask for instance segmentation.

    Raises:
        ValueError: ``outputs`` is not properly formatted.
    """
    try:
        maximas = outputs[maxima_index]
        interiors = outputs[interior_index]
    except (TypeError, KeyError, IndexError):
        raise ValueError('`outputs` should be a list of at least two '
                         'NumPy arryas of equal shape.')

    valid_algos = {'h_maxima', 'peak_local_max'}
    if maxima_algorithm not in valid_algos:
        raise ValueError('Invalid value for maxima_algorithm: {}. '
                         'Must be one of {}'.format(
                             maxima_algorithm, valid_algos))

    total_pixels = maximas.shape[1] * maximas.shape[2]
    if maxima_algorithm == 'h_maxima' and total_pixels > 5000**2:
        warnings.warn('h_maxima peak finding algorithm was selected, '
                      'but the provided image is larger than 5k x 5k pixels.'
                      'This will lead to slow prediction performance.')
    # Handle deprecated arguments
    min_distance = kwargs.pop('min_distance', None)
    if min_distance is not None:
        radius = min_distance
        warnings.warn('`min_distance` is now deprecated in favor of `radius`. '
                      'The value passed for `radius` will be used.',
                      DeprecationWarning)

    # distance_threshold vs interior_threshold
    distance_threshold = kwargs.pop('distance_threshold', None)
    if distance_threshold is not None:
        interior_threshold = distance_threshold
        warnings.warn('`distance_threshold` is now deprecated in favor of '
                      '`interior_threshold`. The value passed for '
                      '`distance_threshold` will be used.',
                      DeprecationWarning)

    # detection_threshold vs maxima_threshold
    detection_threshold = kwargs.pop('detection_threshold', None)
    if detection_threshold is not None:
        maxima_threshold = detection_threshold
        warnings.warn('`detection_threshold` is now deprecated in favor of '
                      '`maxima_threshold`. The value passed for '
                      '`detection_threshold` will be used.',
                      DeprecationWarning)

    if maximas.shape[:-1] != interiors.shape[:-1]:
        raise ValueError('All input arrays must have the same shape. '
                         'Got {} and {}'.format(
                             maximas.shape, interiors.shape))

    if maximas.ndim not in {4, 5}:
        raise ValueError('maxima and interior tensors must be rank 4 or 5. '
                         'Rank 4 is 2D data of shape (batch, x, y, c). '
                         'Rank 5 is 3D data of shape (batch, frames, x, y, c).')

    input_is_3d = maximas.ndim > 4

    # fill_holes is not supported in 3D
    if fill_holes_threshold and input_is_3d:
        warnings.warn('`fill_holes` is not supported for 3D data.')
        fill_holes_threshold = 0

    label_images = []
    for maxima, interior in zip(maximas, interiors):
        # squeeze out the channel dimension if passed
        maxima = nd.gaussian_filter(maxima[..., 0], maxima_smooth)
        interior = nd.gaussian_filter(interior[..., 0], interior_smooth)

        if pixel_expansion:
            fn = cube if input_is_3d else square
            interior = dilation(interior, footprint=fn(pixel_expansion * 2 + 1))

        # peak_local_max is much faster but has poorer performance
        # when dealing with more ambiguous local maxima
        if maxima_algorithm == 'peak_local_max':
            coords = peak_local_max(
                maxima,
                min_distance=radius,
                threshold_abs=maxima_threshold,
                exclude_border=kwargs.get('exclude_border', False))

            markers = np.zeros_like(maxima)
            slc = tuple(coords[:, i] for i in range(coords.shape[1]))
            markers[slc] = 1
        else:
            # Find peaks and merge equal regions
            fn = ball if input_is_3d else disk
            markers = h_maxima(image=maxima,
                               h=maxima_threshold,
                               footprint=fn(radius))

        markers = label(markers)
        label_image = watershed(-1 * interior, markers,
                                mask=interior > interior_threshold,
                                watershed_line=0)

        if label_erosion:
            label_image = erode_edges(label_image, label_erosion)

        # Remove small objects
        if small_objects_threshold:
            label_image = remove_small_objects(label_image,
                                               min_size=small_objects_threshold)

        # fill in holes that lie completely within a segmentation label
        if fill_holes_threshold > 0:
            label_image = fill_holes(label_image, size=fill_holes_threshold)

        # Relabel the label image
        label_image, _, _ = relabel_sequential(label_image)

        label_images.append(label_image)

    label_images = np.stack(label_images, axis=0)
    label_images = np.expand_dims(label_images, axis=-1)

    return label_images


def deep_watershed_mibi(model_output,
                        interior_model='pixelwise-interior',
                        maxima_model='inner-distance',
                        **kwargs):
    """DEPRECATED. Please use ``deep_watershed`` instead.

    Postprocessing function for multiplexed deep watershed models. Thresholds the inner
    distance prediction to find cell centroids, which are used to seed a marker
    based watershed of the pixelwise interior prediction.

    Args:
        model_output (dict): DeepWatershed model output. A dictionary containing key: value pairs
            with the transform name and the corresponding output. Currently supported keys:

            - inner_distance: Prediction for the inner distance transform.
            - outer_distance: Prediction for the outer distance transform.
            - fgbg: Foreground prediction for the foregound/background transform.
            - pixelwise_interior: Interior prediction for the interior/border/background transform.

        interior_model (str): Name of semantic head used to predict interior
            of each object.
        maxima_model (str): Name of semantic head used to predict maxima of
            each object.
        kwargs (dict): Keyword arguments for ``deep_watershed``.

    Returns:
        numpy.array: Uniquely labeled mask.

    Raises:
        ValueError: if ``interior_model`` or ``maxima_model`` is invalid.
        ValueError: if ``interior_model`` or ``maxima_model`` predictions
            do not have length 4
    """
    text = ('deep_watershed_mibi is deprecated and will be removed in a '
            'future version. Please use '
            '`deepcell_toolbox.deep_watershed.deep_watershed` instead.')
    warnings.warn(text, DeprecationWarning)

    interior_model = str(interior_model).lower()
    maxima_model = str(maxima_model).lower()

    valid_model_names = {'inner-distance', 'outer-distance',
                         'fgbg-fg', 'pixelwise-interior'}

    zipped = zip(['interior_model', 'maxima_model'],
                 [interior_model, maxima_model])

    for name, model in zipped:
        if model not in valid_model_names:
            raise ValueError('{} must be one of {}, got {}'.format(
                name, valid_model_names, model))

        arr = model_output[model]
        if len(arr.shape) != 4:
            raise ValueError('Model output must be of length 4. The {} {} '
                             'output provided is of shape {}.'.format(
                                 name, model, arr.shape))

    output = [model_output[maxima_model], model_output[interior_model]]

    label_images = deep_watershed(output, **kwargs)

    return label_images

def histogram_normalization(image, kernel_size=None):
    """Pre-process images using Contrast Limited Adaptive
    Histogram Equalization (CLAHE).

    If one of the inputs is a constant-value array, it will
    be normalized as an array of all zeros of the same shape.

    Args:
        image (numpy.array): numpy array of phase image data.
        kernel_size (integer): Size of kernel for CLAHE,
            defaults to 1/8 of image size.

    Returns:
        numpy.array: Pre-processed image data with dtype float32.
    """
    if not np.issubdtype(image.dtype, np.floating):
        logging.info('Converting image dtype to float')
    image = image.astype('float32')

    for batch in range(image.shape[0]):
        for channel in range(image.shape[-1]):
            X = image[batch, ..., channel]
            sample_value = X[(0,) * X.ndim]
            if (X == sample_value).all():
                # TODO: Deal with constant value arrays
                # https://github.com/scikit-image/scikit-image/issues/4596
                logging.warning('Found constant value array in batch %s and '
                                'channel %s. Normalizing as zeros.',
                                batch, channel)
                image[batch, ..., channel] = np.zeros_like(X)
                continue

            # X = rescale_intensity(X, out_range='float')
            X = rescale_intensity(X, out_range=(0.0, 1.0))
            X = equalize_adapthist(X, kernel_size=kernel_size)
            image[batch, ..., channel] = X
    return image

def percentile_threshold(image, percentile=99.9):
    """Threshold an image to reduce bright spots

    Args:
        image: numpy array of image data
        percentile: cutoff used to threshold image

    Returns:
        np.array: thresholded version of input image
    """

    processed_image = np.zeros_like(image)
    for img in range(image.shape[0]):
        for chan in range(image.shape[-1]):
            current_img = np.copy(image[img, ..., chan])
            non_zero_vals = current_img[np.nonzero(current_img)]

            # only threshold if channel isn't blank
            if len(non_zero_vals) > 0:
                img_max = np.percentile(non_zero_vals, percentile)

                # threshold values down to max
                threshold_mask = current_img > img_max
                current_img[threshold_mask] = img_max

                # update image
                processed_image[img, ..., chan] = current_img

    return processed_image


def resize(data, shape, data_format='channels_last', labeled_image=False):
    """Resize the data to the given shape.
    Uses openCV to resize the data if the data is a single channel, as it
    is very fast. However, openCV does not support multi-channel resizing,
    so if the data has multiple channels, use skimage.

    Args:
        data (np.array): data to be reshaped. Must have a channel dimension
        shape (tuple): shape of the output data in the form (x,y).
            Batch and channel dimensions are handled automatically and preserved.
        data_format (str): determines the order of the channel axis,
            one of 'channels_first' and 'channels_last'.
        labeled_image (bool): flag to determine how interpolation and floats are handled based
         on whether the data represents raw images or annotations

    Raises:
        ValueError: ndim of data not 3 or 4
        ValueError: Shape for resize can only have length of 2, e.g. (x,y)

    Returns:
        numpy.array: data reshaped to new shape.
    """
    if len(data.shape) not in {3, 4}:
        raise ValueError('Data must have 3 or 4 dimensions, e.g. '
                         '[batch, x, y], [x, y, channel] or '
                         '[batch, x, y, channel]. Input data only has {} '
                         'dimensions.'.format(len(data.shape)))

    if len(shape) != 2:
        raise ValueError('Shape for resize can only have length of 2, e.g. (x,y).'
                         'Input shape has {} dimensions.'.format(len(shape)))

    original_dtype = data.dtype

    # cv2 resize is faster but does not support multi-channel data
    # If the data is multi-channel, use skimage.transform.resize
    channel_axis = 0 if data_format == 'channels_first' else -1
    batch_axis = -1 if data_format == 'channels_first' else 0

    # Use skimage for multichannel data
    if data.shape[channel_axis] > 1:
        # Adjust output shape to account for channel axis
        if data_format == 'channels_first':
            shape = tuple([data.shape[channel_axis]] + list(shape))
        else:
            shape = tuple(list(shape) + [data.shape[channel_axis]])

        # linear interpolation (order 1) for image data, nearest neighbor (order 0) for labels
        # anti_aliasing introduces spurious labels, include only for image data
        order = 0 if labeled_image else 1
        anti_aliasing = not labeled_image

        _resize = lambda d: transform.resize(d, shape, mode='constant', preserve_range=True,
                                             order=order, anti_aliasing=anti_aliasing)
    # single channel image, resize with cv2
    else:
        shape = tuple(shape)[::-1]  # cv2 expects swapped axes.

        # linear interpolation for image data, nearest neighbor for labels
        # CV2 doesn't support ints for linear interpolation, set to float for image data
        if labeled_image:
            interpolation = cv2.INTER_NEAREST
        else:
            interpolation = cv2.INTER_LINEAR
            data = data.astype('float32')

        _resize = lambda d: np.expand_dims(cv2.resize(np.squeeze(d), shape,
                                                      interpolation=interpolation),
                                           axis=channel_axis)

    # Check for batch dimension to loop over
    if len(data.shape) == 4:
        batch = []
        for i in range(data.shape[batch_axis]):
            d = data[i] if batch_axis == 0 else data[..., i]
            batch.append(_resize(d))
        resized = np.stack(batch, axis=batch_axis)
    else:
        resized = _resize(data)

    return resized.astype(original_dtype)

def spline_window(window_size, overlap_left, overlap_right, power=2):
    """
    Squared spline (power=2) window function:
    https://www.wolframalpha.com/input/?i=y%3Dx**2,+y%3D-(x-2)**2+%2B2,+y%3D(x-4)**2,+from+y+%3D+0+to+2
    """

    def _spline_window(w_size):
        intersection = int(w_size / 4)
        wind_outer = (abs(2 * (windows.triang(w_size))) ** power) / 2
        wind_outer[intersection:-intersection] = 0

        wind_inner = 1 - (abs(2 * (windows.triang(w_size) - 1)) ** power) / 2
        wind_inner[:intersection] = 0
        wind_inner[-intersection:] = 0

        wind = wind_inner + wind_outer
        wind = wind / np.amax(wind)
        return wind

    # Create the window for the left overlap
    if overlap_left > 0:
        window_size_l = 2 * overlap_left
        l_spline = _spline_window(window_size_l)[0:overlap_left]

    # Create the window for the right overlap
    if overlap_right > 0:
        window_size_r = 2 * overlap_right
        r_spline = _spline_window(window_size_r)[overlap_right:]

    # Put the two together
    window = np.ones((window_size,))
    if overlap_left > 0:
        window[0:overlap_left] = l_spline
    if overlap_right > 0:
        window[-overlap_right:] = r_spline

    return window

def window_2D(window_size, overlap_x=(32, 32), overlap_y=(32, 32), power=2):
    """
    Make a 1D window function, then infer and return a 2D window function.
    Done with an augmentation, and self multiplication with its transpose.
    Could be generalized to more dimensions.
    """
    window_x = spline_window(window_size[0], overlap_x[0], overlap_x[1], power=power)
    window_y = spline_window(window_size[1], overlap_y[0], overlap_y[1], power=power)

    window_x = np.expand_dims(np.expand_dims(window_x, -1), -1)
    window_y = np.expand_dims(np.expand_dims(window_y, -1), -1)

    window = window_x * window_y.transpose(1, 0, 2)
    return window

def untile_image(tiles, tiles_info, power=2, **kwargs):
    """Untile a set of tiled images back to the original model shape.

     Args:
         tiles (numpy.array): The tiled images image to untile.
         tiles_info (dict): Details of how the image was tiled (from tile_image).
         power (int): The power of the window function

     Returns:
         numpy.array: The untiled image.
     """
    # Define mininally acceptable tile_size and stride_ratio for spline interpolation
    min_tile_size = 32
    min_stride_ratio = 0.5

    stride_ratio = tiles_info['stride_ratio']
    image_shape = tiles_info['image_shape']
    batches = tiles_info['batches']
    x_starts = tiles_info['x_starts']
    x_ends = tiles_info['x_ends']
    y_starts = tiles_info['y_starts']
    y_ends = tiles_info['y_ends']
    overlaps_x = tiles_info['overlaps_x']
    overlaps_y = tiles_info['overlaps_y']
    tile_size_x = tiles_info['tile_size_x']
    tile_size_y = tiles_info['tile_size_y']
    stride_ratio = tiles_info['stride_ratio']
    x_pad = tiles_info['pad_x']
    y_pad = tiles_info['pad_y']

    image_shape = [image_shape[0], image_shape[1], image_shape[2], tiles.shape[-1]]
    window_size = (tile_size_x, tile_size_y)
    image = np.zeros(image_shape, dtype=float)

    window_cache = {}
    for x, y in zip(overlaps_x, overlaps_y):
        if (x, y) not in window_cache:
            w = window_2D(window_size, overlap_x=x, overlap_y=y, power=power)
            window_cache[(x, y)] = w

    for tile, batch, x_start, x_end, y_start, y_end, overlap_x, overlap_y in zip(
            tiles, batches, x_starts, x_ends, y_starts, y_ends, overlaps_x, overlaps_y):

        # Conditions under which to use spline interpolation
        # A tile size or stride ratio that is too small gives inconsistent results,
        # so in these cases we skip interpolation and just return the raw tiles
        if (min_tile_size <= tile_size_x < image_shape[1] and
                min_tile_size <= tile_size_y < image_shape[2] and
                stride_ratio >= min_stride_ratio):
            window = window_cache[(overlap_x, overlap_y)]
            image[batch, x_start:x_end, y_start:y_end, :] += tile * window
        else:
            image[batch, x_start:x_end, y_start:y_end, :] = tile

    image = image.astype(tiles.dtype)

    x_start = x_pad[0]
    y_start = y_pad[0]
    x_end = image_shape[1] - x_pad[1]
    y_end = image_shape[2] - y_pad[1]

    image = image[:, x_start:x_end, y_start:y_end, :]

    return image

def tile_image(image, model_input_shape=(512, 512),
               stride_ratio=0.75, pad_mode='constant'):
    """
    Tile large image into many overlapping tiles of size "model_input_shape".

    Args:
        image (numpy.array): The image to tile, must be rank 4.
        model_input_shape (tuple): The input size of the model.
        stride_ratio (float): The stride expressed as a fraction of the tile size.
        pad_mode (str): Padding mode passed to ``np.pad``.

    Returns:
        tuple: (numpy.array, dict): A tuple consisting of an array of tiled
            images and a dictionary of tiling details (for use in un-tiling).

    Raises:
        ValueError: image is not rank 4.
    """
    if image.ndim != 4:
        raise ValueError('Expected image of rank 4, got {}'.format(image.ndim))

    image_size_x, image_size_y = image.shape[1:3]
    tile_size_x = model_input_shape[0]
    tile_size_y = model_input_shape[1]

    ceil = lambda x: int(np.ceil(x))
    round_to_even = lambda x: int(np.ceil(x / 2.0) * 2)

    stride_x = min(round_to_even(stride_ratio * tile_size_x), tile_size_x)
    stride_y = min(round_to_even(stride_ratio * tile_size_y), tile_size_y)

    rep_number_x = max(ceil((image_size_x - tile_size_x) / stride_x + 1), 1)
    rep_number_y = max(ceil((image_size_y - tile_size_y) / stride_y + 1), 1)
    new_batch_size = image.shape[0] * rep_number_x * rep_number_y

    tiles_shape = (new_batch_size, tile_size_x, tile_size_y, image.shape[3])
    tiles = np.zeros(tiles_shape, dtype=image.dtype)

    # Calculate overlap of last tile
    overlap_x = (tile_size_x + stride_x * (rep_number_x - 1)) - image_size_x
    overlap_y = (tile_size_y + stride_y * (rep_number_y - 1)) - image_size_y

    # Calculate padding needed to account for overlap and pad image accordingly
    pad_x = (int(np.ceil(overlap_x / 2)), int(np.floor(overlap_x / 2)))
    pad_y = (int(np.ceil(overlap_y / 2)), int(np.floor(overlap_y / 2)))
    pad_null = (0, 0)
    padding = (pad_null, pad_x, pad_y, pad_null)
    image = np.pad(image, padding, pad_mode)

    counter = 0
    batches = []
    x_starts = []
    x_ends = []
    y_starts = []
    y_ends = []
    overlaps_x = []
    overlaps_y = []

    for b in range(image.shape[0]):
        for i in range(rep_number_x):
            for j in range(rep_number_y):
                x_axis = 1
                y_axis = 2

                # Compute the start and end for each tile
                if i != rep_number_x - 1:  # not the last one
                    x_start, x_end = i * stride_x, i * stride_x + tile_size_x
                else:
                    x_start, x_end = image.shape[x_axis] - tile_size_x, image.shape[x_axis]

                if j != rep_number_y - 1:  # not the last one
                    y_start, y_end = j * stride_y, j * stride_y + tile_size_y
                else:
                    y_start, y_end = image.shape[y_axis] - tile_size_y, image.shape[y_axis]

                # Compute the overlaps for each tile
                if i == 0:
                    overlap_x = (0, tile_size_x - stride_x)
                elif i == rep_number_x - 2:
                    overlap_x = (tile_size_x - stride_x, tile_size_x - image.shape[x_axis] + x_end)
                elif i == rep_number_x - 1:
                    overlap_x = ((i - 1) * stride_x + tile_size_x - x_start, 0)
                else:
                    overlap_x = (tile_size_x - stride_x, tile_size_x - stride_x)

                if j == 0:
                    overlap_y = (0, tile_size_y - stride_y)
                elif j == rep_number_y - 2:
                    overlap_y = (tile_size_y - stride_y, tile_size_y - image.shape[y_axis] + y_end)
                elif j == rep_number_y - 1:
                    overlap_y = ((j - 1) * stride_y + tile_size_y - y_start, 0)
                else:
                    overlap_y = (tile_size_y - stride_y, tile_size_y - stride_y)

                tiles[counter] = image[b, x_start:x_end, y_start:y_end, :]
                batches.append(b)
                x_starts.append(x_start)
                x_ends.append(x_end)
                y_starts.append(y_start)
                y_ends.append(y_end)
                overlaps_x.append(overlap_x)
                overlaps_y.append(overlap_y)
                counter += 1

    tiles_info = {}
    tiles_info['batches'] = batches
    tiles_info['x_starts'] = x_starts
    tiles_info['x_ends'] = x_ends
    tiles_info['y_starts'] = y_starts
    tiles_info['y_ends'] = y_ends
    tiles_info['overlaps_x'] = overlaps_x
    tiles_info['overlaps_y'] = overlaps_y
    tiles_info['stride_x'] = stride_x
    tiles_info['stride_y'] = stride_y
    tiles_info['tile_size_x'] = tile_size_x
    tiles_info['tile_size_y'] = tile_size_y
    tiles_info['stride_ratio'] = stride_ratio
    tiles_info['image_shape'] = image.shape
    tiles_info['dtype'] = image.dtype
    tiles_info['pad_x'] = pad_x
    tiles_info['pad_y'] = pad_y

    return tiles, tiles_info

class Application(object):
    """Application object that takes a model with weights
    and manages predictions

    Args:
        model (tensorflow.keras.Model): ``tf.keras.Model``
            with loaded weights.
        model_image_shape (tuple): Shape of input expected by ``model``.
        dataset_metadata (str or dict): Metadata for the data that
            ``model`` was trained on.
        model_metadata (str or dict): Training metadata for ``model``.
        model_mpp (float): Microns per pixel resolution of the
            training data used for ``model``.
        preprocessing_fn (function): Pre-processing function to apply
            to data prior to prediction.
        postprocessing_fn (function): Post-processing function to apply
            to data after prediction.
            Must accept an input of a list of arrays and then
            return a single array.
        format_model_output_fn (function): Convert model output
            from a list of matrices to a dictionary with keys for
            each semantic head.

    Raises:
        ValueError: ``preprocessing_fn`` must be a callable function
        ValueError: ``postprocessing_fn`` must be a callable function
        ValueError: ``model_output_fn`` must be a callable function
    """

    def __init__(self,
                 model,
                 model_image_shape=(128, 128, 1),
                 model_mpp=0.65,
                 preprocessing_fn=None,
                 postprocessing_fn=None,
                 format_model_output_fn=None,
                 dataset_metadata=None,
                 model_metadata=None):

        self.model = model

        self.model_image_shape = model_image_shape
        # Require dimension 1 larger than model_input_shape due to addition of batch dimension
        self.required_rank = len(self.model_image_shape) + 1

        self.required_channels = self.model_image_shape[-1]

        self.model_mpp = model_mpp
        self.preprocessing_fn = preprocessing_fn
        self.postprocessing_fn = postprocessing_fn
        self.format_model_output_fn = format_model_output_fn
        self.dataset_metadata = dataset_metadata
        self.model_metadata = model_metadata

        self.logger = logging.getLogger(self.__class__.__name__)

        # Test that pre and post processing functions are callable
        if self.preprocessing_fn is not None and not callable(self.preprocessing_fn):
            raise ValueError('Preprocessing_fn must be a callable function.')
        if self.postprocessing_fn is not None and not callable(self.postprocessing_fn):
            raise ValueError('Postprocessing_fn must be a callable function.')
        if self.format_model_output_fn is not None and not callable(self.format_model_output_fn):
            raise ValueError('Format_model_output_fn must be a callable function.')

    def predict(self, x):
        raise NotImplementedError

    def _resize_input(self, image, image_mpp):
        """Checks if there is a difference between image and model resolution
        and resizes if they are different. Otherwise returns the unmodified
        image.

        Args:
            image (numpy.array): Input image to resize.
            image_mpp (float): Microns per pixel for the ``image``.

        Returns:
            numpy.array: Input image resized if necessary to match ``model_mpp``
        """
        # Don't scale the image if mpp is the same or not defined
        if image_mpp not in {None, self.model_mpp}:
            shape = image.shape
            scale_factor = image_mpp / self.model_mpp
            new_shape = (int(shape[1] * scale_factor),
                         int(shape[2] * scale_factor))
            image = resize(image, new_shape, data_format='channels_last')
            self.logger.debug('Resized input from %s to %s', shape, new_shape)

        return image

    def _preprocess(self, image, **kwargs):
        """Preprocess ``image`` if ``preprocessing_fn`` is defined.
        Otherwise return ``image`` unmodified.

        Args:
            image (numpy.array): 4D stack of images
            kwargs (dict): Keyword arguments for ``preprocessing_fn``.

        Returns:
            numpy.array: The pre-processed ``image``.
        """
        if self.preprocessing_fn is not None:
            t = timeit.default_timer()
            self.logger.debug('Pre-processing data with %s and kwargs: %s',
                              self.preprocessing_fn.__name__, kwargs)

            image = self.preprocessing_fn(image, **kwargs)

            self.logger.debug('Pre-processed data with %s in %s s',
                              self.preprocessing_fn.__name__,
                              timeit.default_timer() - t)

        return image

    def _tile_input(self, image, pad_mode='constant'):
        """Tile the input image to match shape expected by model
        using the ``deepcell_toolbox`` function.

        Only supports 4D images.

        Args:
            image (numpy.array): Input image to tile
            pad_mode (str): The padding mode, one of "constant" or "reflect".

        Raises:
            ValueError: Input images must have only 4 dimensions

        Returns:
            (numpy.array, dict): Tuple of tiled image and dict of tiling
            information.
        """
        if len(image.shape) != 4:
            raise ValueError('deepcell_toolbox.tile_image only supports 4d images.'
                             'Image submitted for predict has {} dimensions'.format(
                                 len(image.shape)))

        # Check difference between input and model image size
        x_diff = image.shape[1] - self.model_image_shape[0]
        y_diff = image.shape[2] - self.model_image_shape[1]

        # Check if the input is smaller than model image size
        if x_diff < 0 or y_diff < 0:
            # Calculate padding
            x_diff, y_diff = abs(x_diff), abs(y_diff)
            x_pad = (x_diff // 2, x_diff // 2 + 1) if x_diff % 2 else (x_diff // 2, x_diff // 2)
            y_pad = (y_diff // 2, y_diff // 2 + 1) if y_diff % 2 else (y_diff // 2, y_diff // 2)

            tiles = np.pad(image, [(0, 0), x_pad, y_pad, (0, 0)], 'reflect')
            tiles_info = {'padding': True,
                          'x_pad': x_pad,
                          'y_pad': y_pad}
        # Otherwise tile images larger than model size
        else:
            # Tile images, needs 4d
            tiles, tiles_info = tile_image(image, model_input_shape=self.model_image_shape,
                                           stride_ratio=0.75, pad_mode=pad_mode)

        return tiles, tiles_info

    def _postprocess(self, image, **kwargs):
        """Applies postprocessing function to image if one has been defined.
        Otherwise returns unmodified image.

        Args:
            image (numpy.array or list): Input to postprocessing function
                either an ``numpy.array`` or list of ``numpy.arrays``.

        Returns:
            numpy.array: labeled image
        """
        if self.postprocessing_fn is not None:
            t = timeit.default_timer()
            self.logger.debug('Post-processing results with %s and kwargs: %s',
                              self.postprocessing_fn.__name__, kwargs)

            image = self.postprocessing_fn(image, **kwargs)

            # Restore channel dimension if not already there
            if len(image.shape) == self.required_rank - 1:
                image = np.expand_dims(image, axis=-1)

            self.logger.debug('Post-processed results with %s in %s s',
                              self.postprocessing_fn.__name__,
                              timeit.default_timer() - t)

        elif isinstance(image, list) and len(image) == 1:
            image = image[0]

        return image

    def _untile_output(self, output_tiles, tiles_info):
        """Untiles either a single array or a list of arrays
        according to a dictionary of tiling specs

        Args:
            output_tiles (numpy.array or list): Array or list of arrays.
            tiles_info (dict): Tiling specs output by the tiling function.

        Returns:
            numpy.array or list: Array or list according to input with untiled images
        """
        # If padding was used, remove padding
        if tiles_info.get('padding', False):
            def _process(im, tiles_info):
                x_pad, y_pad = tiles_info['x_pad'], tiles_info['y_pad']
                out = im[:, x_pad[0]:-x_pad[1], y_pad[0]:-y_pad[1], :]
                return out
        # Otherwise untile
        else:
            def _process(im, tiles_info):
                out = untile_image(im, tiles_info, model_input_shape=self.model_image_shape)
                return out

        if isinstance(output_tiles, list):
            output_images = [_process(o, tiles_info) for o in output_tiles]
        else:
            output_images = _process(output_tiles, tiles_info)

        return output_images

    def _format_model_output(self, output_images):
        """Applies formatting function the output from the model if one was
        provided. Otherwise, returns the unmodified model output.

        Args:
            output_images: stack of untiled images to be reformatted

        Returns:
            dict or list: reformatted images stored as a dict, or input
            images stored as list if no formatting function is specified.
        """
        if self.format_model_output_fn is not None:
            formatted_images = self.format_model_output_fn(output_images)
            return formatted_images
        else:
            return output_images

    def _resize_output(self, image, original_shape):
        """Rescales input if the shape does not match the original shape
        excluding the batch and channel dimensions.

        Args:
            image (numpy.array): Image to be rescaled to original shape
            original_shape (tuple): Shape of the original input image

        Returns:
            numpy.array: Rescaled image
        """
        if not isinstance(image, list):
            image = [image]

        for i in range(len(image)):
            img = image[i]
            # Compare x,y based on rank of image
            if len(img.shape) == 4:
                same = img.shape[1:-1] == original_shape[1:-1]
            elif len(img.shape) == 3:
                same = img.shape[1:] == original_shape[1:-1]
            else:
                same = img.shape == original_shape[1:-1]

            # Resize if same is false
            if not same:
                # Resize function only takes the x,y dimensions for shape
                new_shape = original_shape[1:-1]
                img = resize(img, new_shape,
                             data_format='channels_last',
                             labeled_image=True)
            image[i] = img

        if len(image) == 1:
            image = image[0]

        return image

    def _batch_predict(self, tiles, batch_size):
        """Batch process tiles to generate model predictions.

        The built-in keras.predict function has support for batching, but
        loads the entire image stack into GPU memory, which is prohibitive
        for large images. This function uses similar code to the underlying
        model.predict function without soaking up GPU memory.

        Args:
            tiles (numpy.array): Tiled data which will be fed to model
            batch_size (int): Number of images to predict on per batch

        Returns:
            list: Model outputs
        """
        # list to hold final output
        output_tiles = []

        # loop through each batch
        for i in range(0, tiles.shape[0], batch_size):
            batch_inputs = tiles[i:i + batch_size, ...]


            ###################################################     ##>>## edits from here to the following ##>>##!
            if self.torch_or_tf == 'tf':
                batch_outputs = self.model.predict(batch_inputs, batch_size=batch_size)
            elif self.torch_or_tf == 'torch':
                # alt. for pytorch model:
                with torch.inference_mode():
                    batch_outputs = self.model(torch.from_numpy(batch_inputs))
                    #print(batch_outputs)
            ####################################################      ##>>##

            # model with only a single output gets temporarily converted to a list
            if not isinstance(batch_outputs, list):
                batch_outputs = [batch_outputs]

            # initialize output list with empty arrays to hold all batches
            if not output_tiles:
                for batch_out in batch_outputs:
                    shape = (tiles.shape[0],) + batch_out.shape[1:]
                    output_tiles.append(np.zeros(shape, dtype=tiles.dtype))

            # save each batch to corresponding index in output list
            for j, batch_out in enumerate(batch_outputs):
                output_tiles[j][i:i + batch_size, ...] = batch_out

        return output_tiles

    def _run_model(self,
                   image,
                   batch_size=4,
                   pad_mode='constant',
                   preprocess_kwargs={}):
        """Run the model to generate output probabilities on the data.

        Args:
            image (numpy.array): Image with shape ``[batch, x, y, channel]``
            batch_size (int): Number of images to predict on per batch.
            pad_mode (str): The padding mode, one of "constant" or "reflect".
            preprocess_kwargs (dict): Keyword arguments to pass to
                the preprocessing function.

        Returns:
            numpy.array: Model outputs
        """
        # Preprocess image if function is defined
        image = self._preprocess(image, **preprocess_kwargs)

        # Tile images, raises error if the image is not 4d
        tiles, tiles_info = self._tile_input(image, pad_mode=pad_mode)

        # Run images through model
        t = timeit.default_timer()
        output_tiles = self._batch_predict(tiles=tiles, batch_size=batch_size)
        self.logger.debug('Model inference finished in %s s',
                          timeit.default_timer() - t)

        # Untile images
        output_images = self._untile_output(output_tiles, tiles_info)

        # restructure outputs into a dict if function provided
        formatted_images = self._format_model_output(output_images)

        return formatted_images

    def _predict_segmentation(self,
                              image,
                              batch_size=4,
                              image_mpp=None,
                              pad_mode='constant',
                              preprocess_kwargs={},
                              postprocess_kwargs={}):
        """Generates a labeled image of the input running prediction with
        appropriate pre and post processing functions.

        Input images are required to have 4 dimensions
        ``[batch, x, y, channel]``. Additional empty dimensions can be added
        using ``np.expand_dims``.

        Args:
            image (numpy.array): Input image with shape
                ``[batch, x, y, channel]``.
            batch_size (int): Number of images to predict on per batch.
            image_mpp (float): Microns per pixel for ``image``.
            pad_mode (str): The padding mode, one of "constant" or "reflect".
            preprocess_kwargs (dict): Keyword arguments to pass to the
                pre-processing function.
            postprocess_kwargs (dict): Keyword arguments to pass to the
                post-processing function.

        Raises:
            ValueError: Input data must match required rank, calculated as one
                dimension more (batch dimension) than expected by the model.

            ValueError: Input data must match required number of channels.

        Returns:
            numpy.array: Labeled image
        """
        # Check input size of image
        if len(image.shape) != self.required_rank:
            raise ValueError('Input data must have {} dimensions. '
                             'Input data only has {} dimensions'.format(
                                 self.required_rank, len(image.shape)))

        if image.shape[-1] != self.required_channels:
            raise ValueError('Input data must have {} channels. '
                             'Input data only has {} channels'.format(
                                 self.required_channels, image.shape[-1]))

        # Resize image, returns unmodified if appropriate
        resized_image = self._resize_input(image, image_mpp)

        # Generate model outputs
        output_images = self._run_model(
            image=resized_image, batch_size=batch_size,
            pad_mode=pad_mode, preprocess_kwargs=preprocess_kwargs
        )

        # Postprocess predictions to create label image
        label_image = self._postprocess(output_images, **postprocess_kwargs)

        # Resize label_image back to original resolution if necessary
        label_image = self._resize_output(label_image, image.shape)

        return label_image


MODEL_PATH = ('https://deepcell-data.s3-us-west-1.amazonaws.com/'
              'saved-models/MultiplexSegmentation-9.tar.gz')
MODEL_HASH = 'a1dfbce2594f927b9112f23a0a1739e0'


# pre- and post-processing functions
def mesmer_preprocess(image, **kwargs):
    """Preprocess input data for Mesmer model.

    Args:
        image: array to be processed

    Returns:
        np.array: processed image array
    """

    if len(image.shape) != 4:
        raise ValueError("Image data must be 4D, got image of shape {}".format(image.shape))

    output = np.copy(image)
    threshold = kwargs.get('threshold', True)
    if threshold:
        percentile = kwargs.get('percentile', 99.9)
        output = percentile_threshold(image=output, percentile=percentile)

    normalize = kwargs.get('normalize', True)
    if normalize:
        kernel_size = kwargs.get('kernel_size', 128)
        output = histogram_normalization(image=output, kernel_size=kernel_size)

    return output


def format_output_mesmer(output_list):
    """Takes list of model outputs and formats into a dictionary for better readability

    Args:
        output_list (list): predictions from semantic heads

    Returns:
        dict: Dict of predictions for whole cell and nuclear.

    Raises:
        ValueError: if model output list is not len(4)
    """
    expected_length = 4
    if len(output_list) != expected_length:
        raise ValueError('output_list was length {}, expecting length {}'.format(
            len(output_list), expected_length))

    formatted_dict = {
        'whole-cell': [output_list[0], output_list[1][..., 1:2]],
        'nuclear': [output_list[2], output_list[3][..., 1:2]],
    }

    return formatted_dict


def mesmer_postprocess(model_output, compartment='whole-cell',
                       whole_cell_kwargs=None, nuclear_kwargs=None):
    """Postprocess Mesmer output to generate predictions for distinct cellular compartments

    Args:
        model_output (dict): Output from the Mesmer model. A dict with a key corresponding to
            each cellular compartment with a model prediction. Each key maps to a subsequent dict
            with the following keys entries
            - inner-distance: Prediction for the inner distance transform.
            - outer-distance: Prediction for the outer distance transform
            - fgbg-fg: prediction for the foreground/background transform
            - pixelwise-interior: Prediction for the interior/border/background transform.
        compartment: which cellular compartments to generate predictions for.
            must be one of 'whole_cell', 'nuclear', 'both'
        whole_cell_kwargs (dict): Optional list of post-processing kwargs for whole-cell prediction
        nuclear_kwargs (dict): Optional list of post-processing kwargs for nuclear prediction

    Returns:
        numpy.array: Uniquely labeled mask for each compartment

    Raises:
        ValueError: for invalid compartment flag
    """

    valid_compartments = ['whole-cell', 'nuclear', 'both']

    if whole_cell_kwargs is None:
        whole_cell_kwargs = {}

    if nuclear_kwargs is None:
        nuclear_kwargs = {}

    if compartment not in valid_compartments:
        raise ValueError('Invalid compartment supplied: {}. '
                         'Must be one of {}'.format(compartment, valid_compartments))

    if compartment == 'whole-cell':
        label_images = deep_watershed(model_output['whole-cell'],
                                      **whole_cell_kwargs)
    elif compartment == 'nuclear':
        label_images = deep_watershed(model_output['nuclear'],
                                      **nuclear_kwargs)
    elif compartment == 'both':
        label_images_cell = deep_watershed(model_output['whole-cell'],
                                           **whole_cell_kwargs)

        label_images_nucleus = deep_watershed(model_output['nuclear'],
                                              **nuclear_kwargs)

        label_images = np.concatenate([
            label_images_cell,
            label_images_nucleus
        ], axis=-1)

    else:
        raise ValueError('Invalid compartment supplied: {}. '
                         'Must be one of {}'.format(compartment, valid_compartments))

    return label_images


class Mesmer(Application):
    """Loads a :mod:`deepcell.model_zoo.panopticnet.PanopticNet` model for
    tissue segmentation with pretrained weights.

    The ``predict`` method handles prep and post processing steps
    to return a labeled image.

    Example:

    .. code-block:: python

        from skimage.io import imread
        from deepcell.applications import Mesmer

        # Load the images
        im1 = imread('TNBC_DNA.tiff')
        im2 = imread('TNBC_Membrane.tiff')

        # Combined together and expand to 4D
        im = np.stack((im1, im2), axis=-1)
        im = np.expand_dims(im,0)

        # Create the application
        app = Mesmer()

        # create the lab
        labeled_image = app.predict(image)

    Args:
        model (tf.keras.Model): The model to load. If ``None``,
            a pre-trained model will be downloaded.
    """

    #: Metadata for the dataset used to train the model
    dataset_metadata = {
        'name': '20200315_IF_Training_6.npz',
        'other': 'Pooled whole-cell data across tissue types'
    }

    #: Metadata for the model and training process
    model_metadata = {
        'batch_size': 1,
        'lr': 1e-5,
        'lr_decay': 0.99,
        'training_seed': 0,
        'n_epochs': 30,
        'training_steps_per_epoch': 1739 // 1,
        'validation_steps_per_epoch': 193 // 1
    }

    def __init__(self, model=None, is_torch = None):
        self.torch_or_tf = 'tf' #########################################                            ##>>## edits!
        if is_torch is None:
            is_torch = _is_torch
        if is_torch:
            file_dir = __file__.replace("\\","/")
            file_dir = file_dir[:(file_dir.rfind("/"))] 
            model_path = file_dir + "/mesmer.onnx"
            onnx_model = onnx.load(model_path)
            torch_model = onnx2torch.convert(onnx_model)
            torch_model.recompile()
            model = torch_model
            self.torch_or_tf  = 'torch'

        if model is None:
            archive_path = tf.keras.utils.get_file(
                'MultiplexSegmentation.tgz', MODEL_PATH,
                file_hash=MODEL_HASH,
                extract=True, cache_subdir='models'
            )
            model_path = os.path.splitext(archive_path)[0]
            model = tf.keras.models.load_model(model_path)

        super(Mesmer, self).__init__(
            model,
            model_image_shape = (256,256,2),     ##>>## edit: changed from >>> model.input_shape[1:]
            model_mpp=0.5,
            preprocessing_fn=mesmer_preprocess,
            postprocessing_fn=mesmer_postprocess,
            format_model_output_fn=format_output_mesmer,
            dataset_metadata=self.dataset_metadata,
            model_metadata=self.model_metadata)

    def predict(self,
                image,
                batch_size=4,
                image_mpp=None,
                preprocess_kwargs={},
                compartment='whole-cell',
                pad_mode='constant',
                postprocess_kwargs_whole_cell={},
                postprocess_kwargs_nuclear={}):
        """Generates a labeled image of the input running prediction with
        appropriate pre and post processing functions.

        Input images are required to have 4 dimensions
        ``[batch, x, y, channel]``.
        Additional empty dimensions can be added using ``np.expand_dims``.

        Args:
            image (numpy.array): Input image with shape
                ``[batch, x, y, channel]``.
            batch_size (int): Number of images to predict on per batch.
            image_mpp (float): Microns per pixel for ``image``.
            compartment (str): Specify type of segmentation to predict.
                Must be one of ``"whole-cell"``, ``"nuclear"``, ``"both"``.
            preprocess_kwargs (dict): Keyword arguments to pass to the
                pre-processing function.
            postprocess_kwargs (dict): Keyword arguments to pass to the
                post-processing function.

        Raises:
            ValueError: Input data must match required rank of the application,
                calculated as one dimension more (batch dimension) than expected
                by the model.

            ValueError: Input data must match required number of channels.

        Returns:
            numpy.array: Instance segmentation mask.
        """
        default_kwargs_cell = {
            'maxima_threshold': 0.075,
            'maxima_smooth': 0,
            'interior_threshold': 0.2,
            'interior_smooth': 2,
            'small_objects_threshold': 15,
            'fill_holes_threshold': 15,
            'radius': 2
        }

        default_kwargs_nuc = {
            'maxima_threshold': 0.1,
            'maxima_smooth': 0,
            'interior_threshold': 0.2,
            'interior_smooth': 2,
            'small_objects_threshold': 15,
            'fill_holes_threshold': 15,
            'radius': 2
        }

        # overwrite defaults with any user-provided values
        postprocess_kwargs_whole_cell = {**default_kwargs_cell,
                                         **postprocess_kwargs_whole_cell}

        postprocess_kwargs_nuclear = {**default_kwargs_nuc,
                                      **postprocess_kwargs_nuclear}

        # create dict to hold all of the post-processing kwargs
        postprocess_kwargs = {
            'whole_cell_kwargs': postprocess_kwargs_whole_cell,
            'nuclear_kwargs': postprocess_kwargs_nuclear,
            'compartment': compartment
        }

        return self._predict_segmentation(image,
                                          batch_size=batch_size,
                                          image_mpp=image_mpp,
                                          pad_mode=pad_mode,
                                          preprocess_kwargs=preprocess_kwargs,
                                          postprocess_kwargs=postprocess_kwargs)