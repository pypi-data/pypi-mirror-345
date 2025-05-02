''' 
This code is directly copied from Steinbock (https://github.com/BodenmillerGroup/steinbock), with a few edits to "unhook" them from the rest of the package
The code here is from the following files of Steinbock:

steinbock.segmentation.deepcell    
steinbock.io
The edits listed below are in part because this originally was part of the PALMETTOBUG steinbock_unhooked.py file 
Since this file retains the io module / read image code, I do expect that all modification noted here do apply:

Edits:  

--> removed mmap reading code (my program will not ever use that format, I think)

--> Removed the io.dtype calls in some of the np.array set ups --> replaced with simple dtype calls (astype / dtype --> 'int')

--> removed special Steinbock______Exceptions, and left them as plain Exceptions

--> In concatenating the files listed above, and removed redundant and unused code / imports

--> in the code taken from the io module (just the first two functions --> removed dtype & special exceptions)

--> (2-6-25): also disconnected the MCD reading / panel functions, since this not handled by iSD, and removed assert statements

--> __all__ = []  for auto-api control

--> 3-28-25: commented-out / removed more unused imports (ruff linter), then added noqa line to pause any future linting (for now)

Reasons: disconnect the files listed above from all other modules of steinbock.

Steinbock License:

MIT License

Copyright (c) 2021 University of Zurich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# ruff: noqa

__all__ = []

import logging
from os import PathLike
import numpy as np
#import pandas as pd

import tifffile as tf

from pathlib import Path
from enum import Enum
from functools import partial
#from zipfile import ZipFile
#from tempfile import TemporaryDirectory

#from readimc import MCDFile

from typing import (
    TYPE_CHECKING,
    Generator,
    Optional,
    Sequence,
    Tuple,
    Union,
    Mapping,
    Protocol,
    Any
)

__all__ = []

logger = logging.getLogger(__name__)

'''
def list_mcd_files(mcd_dir: Union[str, PathLike], unzip: bool = False) -> List[Path]:
    mcd_files = sorted(Path(mcd_dir).rglob("[!.]*.mcd"))
    if unzip:
        for zip_file in sorted(Path(mcd_dir).rglob("[!.]*.zip")):
            with ZipFile(zip_file) as fzip:
                for zip_info in sorted(fzip.infolist(), key=lambda x: x.filename):
                    if not zip_info.is_dir() and zip_info.filename.endswith(".mcd"):
                        mcd_files.append(zip_file / zip_info.filename)
    return mcd_files


def create_panel_from_mcd_files(
    mcd_files: Sequence[Union[str, PathLike]], unzip: bool = False
) -> pd.DataFrame:
    panels = []
    for mcd_file in mcd_files:
        zip_file_mcd_member = _get_zip_file_member(mcd_file)
        if zip_file_mcd_member is None:
            panels += create_panels_from_mcd_file(mcd_file)
        elif unzip:
            zip_file, mcd_member = zip_file_mcd_member
            with ZipFile(zip_file) as fzip:
                with TemporaryDirectory() as temp_dir:
                    extracted_mcd_file = fzip.extract(mcd_member, path=temp_dir)
                    panels += create_panels_from_mcd_file(extracted_mcd_file)
    panel = pd.concat(panels, ignore_index=True, copy=False)
    panel.drop_duplicates(inplace=True, ignore_index=True)
    return _clean_panel(panel)

def create_panels_from_mcd_file(mcd_file: Union[str, PathLike]) -> List[pd.DataFrame]:
    panels = []
    with MCDFile(mcd_file) as f:
        for slide in f.slides:
            for acquisition in slide.acquisitions:
                panel = pd.DataFrame(
                    data={
                        "channel": pd.Series(
                            data=acquisition.channel_names,
                            dtype=pd.StringDtype(),
                        ),
                        "name": pd.Series(
                            data=acquisition.channel_labels,
                            dtype=pd.StringDtype(),
                        ),
                    },
                )
                panels.append(panel)
    return panels

def _clean_panel(panel: pd.DataFrame) -> pd.DataFrame:
    panel.sort_values(
        "channel",
        key=lambda s: pd.to_numeric(s.str.replace("[^0-9]", "", regex=True)),
        inplace=True,
    )
    name_dupl_mask = panel["name"].duplicated(keep=False)
    name_suffixes = panel.groupby("name").cumcount().map(lambda i: f" {i + 1}")
    panel.loc[name_dupl_mask, "name"] += name_suffixes[name_dupl_mask]
    if "keep" not in panel:
        panel["keep"] = pd.Series([True] * len(panel.index), dtype=pd.BooleanDtype())
    if "ilastik" not in panel:
        panel["ilastik"] = pd.Series(dtype=pd.UInt8Dtype())
        panel.loc[panel["keep"], "ilastik"] = range(1, panel["keep"].sum() + 1)
    if "deepcell" not in panel:
        panel["deepcell"] = pd.Series(dtype=pd.UInt8Dtype())
    if "cellpose" not in panel:
        panel["cellpose"] = pd.Series(dtype=pd.UInt8Dtype())
    next_column_index = 0
    for column in ("channel", "name", "keep", "ilastik", "deepcell", "cellpose"):
        if column in panel:
            column_data = panel[column]
            panel.drop(columns=[column], inplace=True)
            panel.insert(next_column_index, column, column_data)
            next_column_index += 1
    return panel


def _get_zip_file_member(path: Union[str, PathLike]) -> Optional[Tuple[Path, str]]:
    for parent_path in Path(path).parents:
        if parent_path.suffix == ".zip" and parent_path.is_file():
            member_path = Path(path).relative_to(parent_path)
            return parent_path, str(member_path)
    return None
'''

class AggregationFunction(Protocol):
    def __call__(self, img: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        ...

def read_image(
    img_file: Union[str, PathLike],
    native_dtype: bool = False,
) -> np.ndarray:
    img = tf.imread(img_file, squeeze=False)
    img = _fix_image_shape(img_file, img)
    return img

def _fix_image_shape(img_file: Union[str, PathLike], img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        img = img[np.newaxis, :, :]
    elif img.ndim == 4:
        if img.shape[-1] == 1:
            img = img[:, :, :, 0]
        elif img.shape[0] == 1:
            img = img[0, :, :, :]
        else:
            raise Exception(
                f"{img_file}: unsupported four-dimensional shape {img.shape}"
            )
    elif img.ndim == 5:
        size_t, size_z, size_c, size_y, size_x = img.shape
        if size_t != 1 or size_z != 1:
            raise Exception(
                f"{img_file}: unsupported TZCYX shape {img.shape}"
            )
        img = img[0, 0, :, :, :]
    elif img.ndim == 6:
        size_t, size_z, size_c, size_y, size_x, size_s = img.shape
        if size_t != 1 or size_z != 1 or size_s != 1:
            raise Exception(
                f"{img_file}: unsupported TZCYXS shape {img.shape}"
            )
        img = img[0, 0, :, :, :, 0]
    elif img.ndim != 3:
        raise Exception(
            f"{img_file}: unsupported number of dimensions ({img.ndim})"
        )
    return img

if TYPE_CHECKING:
    from tensorflow.keras.models import Model  # type: ignore

def create_segmentation_stack(
    img: np.ndarray,
    channelwise_minmax: bool = False,
    channelwise_zscore: bool = False,
    channel_groups: Optional[np.ndarray] = None,
    aggr_func: AggregationFunction = np.mean,
) -> np.ndarray:
    if channelwise_minmax:
        channel_mins = np.nanmin(img, axis=(1, 2))
        channel_maxs = np.nanmax(img, axis=(1, 2))
        channel_ranges = channel_maxs - channel_mins
        img -= channel_mins[:, np.newaxis, np.newaxis]
        img[channel_ranges > 0] /= channel_ranges[
            channel_ranges > 0, np.newaxis, np.newaxis
        ]
    if channelwise_zscore:
        channel_means = np.nanmean(img, axis=(1, 2))
        channel_stds = np.nanstd(img, axis=(1, 2))
        img -= channel_means[:, np.newaxis, np.newaxis]
        img[channel_stds > 0] /= channel_stds[channel_stds > 0, np.newaxis, np.newaxis]
    if channel_groups is not None:
        img = np.stack(
            [
                aggr_func(img[channel_groups == channel_group], axis=0)
                for channel_group in np.unique(channel_groups)
                if not np.isnan(channel_group)
            ]
        )
    return img

# deepcell_available = find_spec("deepcell") is not None
def _mesmer_application(model=None, is_torch = None): ##>>## added is_torch
    #from deepcell.applications import Mesmer
    from ._deepcell import Mesmer # type: ignore

    app = Mesmer(model=model, is_torch = is_torch) ##>>## added is_torch

    def predict(
        img: np.ndarray,
        *,
        pixel_size_um: Optional[float] = None,
        segmentation_type: Optional[str] = None,
        preprocess_kwargs: Optional[Mapping[str, Any]] = None,
        postprocess_kwargs: Optional[Mapping[str, Any]] = None,
    ) -> np.ndarray:
        if not img.ndim == 3:
            raise Exception     ## removed assert
        if pixel_size_um is None:
            raise Exception("Unknown pixel size")
        if segmentation_type is None:
            raise Exception("Unknown segmentation type")
        mask = app.predict(
            np.expand_dims(np.moveaxis(img, 0, -1), 0),
            batch_size=1,
            image_mpp=pixel_size_um,
            compartment=segmentation_type,
            preprocess_kwargs=preprocess_kwargs or {},
            postprocess_kwargs_whole_cell=postprocess_kwargs or {},
            postprocess_kwargs_nuclear=postprocess_kwargs or {},
        )[0, :, :, 0]
        if not mask.shape == img.shape[1:]:
            raise Exception   ## removed assert
        return mask

    return app, predict

class Application(Enum):
    MESMER = partial(_mesmer_application)

def try_segment_objects(
    img_files: Sequence[Union[str, PathLike]],
    application: Application,
    model: Optional["Model"] = None,
    channelwise_minmax: bool = False,
    channelwise_zscore: bool = False,
    channel_groups: Optional[np.ndarray] = None,
    aggr_func: AggregationFunction = np.mean,
    is_torch = None,                                                   ##>>## added is_torch
    **predict_kwargs,
) -> Generator[Tuple[Path, np.ndarray], None, None]:
    app, predict = application.value(model=model, is_torch = is_torch)   ##>>## added is_torch
    for img_file in img_files:
        try:
            img = create_segmentation_stack(
                read_image(img_file),
                channelwise_minmax=channelwise_minmax,
                channelwise_zscore=channelwise_zscore,
                channel_groups=channel_groups,
                aggr_func=aggr_func,
            )
            if img.shape[0] != 2:
                raise Exception(
                    f"Invalid number of aggregated channels: "
                    f"expected 2, got {img.shape[0]}"
                )
            mask = predict(img, **predict_kwargs)
            yield Path(img_file), mask
            del img, mask
        except Exception as e:
            logger.exception(f"Error segmenting objects in {img_file}: {e}")
