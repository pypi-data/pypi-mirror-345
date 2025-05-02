''' 
This module contains the back-end / image processing classes and functions that handle image segmentation and denoising.
Particularly the ImageProcessing class and its subclasses handles most of these functions. This is also the only important module
for the non-GUI API of isoSegDenoise, and the only module that call to the _steinbock.py module. 

Portions of this file  are derivative / partially copy&paste with modification from the steinbock package:

Steinbock License
-----------------

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

-----------------

functions of relevance derived from steinbock marked with a comment like:
             # ****stein_derived (notes)

Additionally, the assumed directory structure and panel file are derived from those structures/files from steinbock

The simple denoise method here is a self-made algorithm, although it was made with the assistance of the skimage documentation.
(probably not genuinely / legally considered "derivative" of those doc files, but the skimage doc files are: 
        Copyright: 2009-2022 the scikit-image team )
LICENSE text (BSD-3):

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the University nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE HOLDERS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
import os
from typing import Union

import numpy as np
import pandas as pd
import tifffile as tf
import skimage

from .vendors._apeerometiff import read_ometiff, write_ometiff
from .vendors._steinbock import try_segment_objects, Application   # list_mcd_files, create_panel_from_mcd_files,
from .sharedClasses import DirSetup, Project_logger, warning_window
from cellpose import denoise, models 

__all__ = ["ImageProcessing",
           "imc_entrypoint",
           "mask_expand"]

_in_gui = False
def toggle_in_gui():
    global _in_gui
    _in_gui = not _in_gui

def imc_entrypoint(directory: Union[None, str] = None,
               resolutions: tuple[float, float] = [1.0, 1.0], 
               from_mcds: bool = True,
               ) -> "ImageProcessing":
    '''
    This function is the entrypoint for a project using MCDs or TIFFs. It initializes and return an ImageAnalysis object using the 
    arguments passed in by the user.

    Args:
        directory (Path or string): 
            This is the path to a folder containing a subfolder /raw with either .tiff or .mcd files inside it

        resolutions (iterable of length two: float, float): 
            This is the [X, Y] resolutions of the images in micrometers / pixel. The default is 1.0 microns / pixels for both dimensions, as has been usual for IMC. 

        from_mcds (boolean): 
            whether the /raw subfolder contains .mcd files (= True) or .tiff files (= False)
    '''
    resolutions = [float(resolutions[0]), float(resolutions[1])]
    directory = str(directory).replace("\\","/")
    Experiment_obj = ImageProcessing(directory, resolutions = resolutions)
    return Experiment_obj
    try:
        Experiment_obj = ImageProcessing(directory, resolutions = resolutions)
    except Exception as e:
        print(e)
        if from_mcds:
            if _in_gui:
                messagebox.showwarning("Warning!", message = "Are you sure there are .mcd files in the 'raw' folder of your directory? \n" 
                            "Error in generating directory structure and preliminary panel file")
                return
            else:
                print("Are you sure there are .mcd files in the 'raw' folder of your directory? \n" 
                    "Error in generating directory structure and preliminary panel file")
                return 
             
        elif not from_mcds:
            if _in_gui:
                messagebox.showwarning("Warning!", message = "Are you sure there are image files in the 'img' folder of your directory? \n" 
                        "Error in generating directory structure and preliminary panel file")
                return
            else:
                print("Are you sure there are image files in the 'img' folder of your directory? \n" 
                    "Error in generating directory structure and preliminary panel file")
                return    
            
    Experiment_obj.directory_object.makedirs()
    return Experiment_obj

def mask_expand(distance: int, 
                image_source: str, 
                output_directory: str,
                ) -> None:                                 # ****stein_derived (ish -- only in the sense that it conciously replicates a 
                                                             # particular steinbock utility  
                                                             # The actual implementation here is not very similar to steinbocks')
    '''
    Function that expands the size of cell masks:

    Args:
        distance (integer):  
            the number of pixels to expand the masks by

        image_source (string or Path): 
            the file path to a folder containing the cell masks (as tiff files) to expand

        output_directory (string or Path): 
            the file path to a folder where you want to write the expanded masks. Must already exist or be creatable by os.mkdir()

    Inputs / Outputs:
        Inputs: 
            reads every file in image_source folder (expecting .tiff format for all)
    
        Outputs: 
            writes a (.ome).tiff into the output_directory folder for each file read-in from image_source
            The filenames in the image_source folder as preserved in the output_directory, so if image_source == output_directory
            then the original masks will be overwritten. 
    ''' 
    from skimage.segmentation import expand_labels
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    list_of_images = [i for i in sorted(os.listdir(image_source)) if i.lower().find(".tif") != -1]
    for i in list_of_images:
        read_dir = "".join([image_source, "/", i])
        out_dir = "".join([output_directory, "/", i])
        read_in_mask = tf.imread(read_dir)
        expanded_mask = expand_labels(read_in_mask, distance)
        tf.imwrite(out_dir, expanded_mask, photometric = "minisblack")

class ImageProcessing:
    '''
    This class coordinates the segmentation / denoising functions

    Key Attributes:
        directory (str): 
            the path to a folder contianing a directory/raw/ subfolder where the MCD or TIFF files are

        directory_object (DirSetup): 
            this attribute is a sub-class from Utils/SharedClasses.py module. it coordinates directories of the typical PalmettoBUG project.
            sub-Attributes:

                - directory_object.main = self.directory

                - directory_object.raw_dir = {self.directory}/raw, the folder where the original mcds / tiffs are located. Not interacted with by isoSegDenoise

                - directory_object.img_dir = {self.directory}/images, the folder where sub-folders of images are located. The /img subfolder contains the .tiffs converted from raw_dir. 
                In the GUI, many steps looks inside img_dir for sub-folders of images to use, and denoisings automatically export there as well.

                - directory_object.masks_dir = {self.directory}/masks, the folder where sub-folders of cell masks are located. deepcell and cellpose segmentation automatically export to 
                the subfolders masks_dir/deepcell_masks and masks_dir/cellpose_masks, respectively. Mask expansion reads/writes from subfolders of masks_dir. 

                - directory_object.logs = {self.directory}/Logs, the folder where log files are written by the GUI. 

        resolutions (list[float, float]): 
            the X and Y resolutions of the images, in micrometers / pixel
        
        panel (pandas dataframe): 
            this is a pandas dataframe read-in & written to directory/panel.csv. This is a steinbock-style panel (with changes), with
            four columns = "name","antigen","keep","segmentation"
    '''
    def __init__(self, 
                 directory: Union[Path, str, None],
                 resolutions: tuple[float, float] = [1.0, 1.0]):
        '''
        X and Y are the resolution of the images (in micrometers)
        '''
        #self.from_mcds = from_mcds
        self.resolutions = resolutions  
        if directory is not None:
            directory = str(directory)
            self.directory = directory 
            self.directory_object = DirSetup(directory) 
            self._panel_setup()       

    def _panel_setup(self) -> None:
        '''
        Setups the Panel file. Unlike PalmettoBUG version of this function, this always assumes a panel file is available in the provided directory
        (it does not attempt to construct a preliminary verison of the panel if a panel is not available in the directory)
        '''
        self.panel = pd.read_csv("".join([self.directory_object.main, "/panel.csv"]))   ## isosegdenoise can just always assume a panel should exist
        return
        #if self.from_mcds:
            #try:
        #    self.panel = pd.read_csv("".join([self.directory_object.main, "/panel.csv"]))
        #    '''
        #    except FileNotFoundError:
        #        MCD_list = list_mcd_files(self.directory_object.main) 
        #        self.panel = create_panel_from_mcd_files(MCD_list)  
        #        self.panel = self.panel.drop(['ilastik','cellpose','deepcell'], axis = 1)     
        #                # unwanted columns from the underlying steinbock package implementation
        #        self.panel['segmentation'] = ""

                ## This auto-sets background channels to keep = 0 (based on duplicating entry in the channel / name columns)
        #        numbers_channel = self.panel['channel'].str.replace("[^0-9]","", regex = True)
        #        letters_channel = self.panel['channel'].str.replace("[0-9]","", regex = True)
        #        self.panel['channel_test'] = numbers_channel + letters_channel
        #        
        #        numbers_name = self.panel['name'].str.replace("[^0-9]","", regex = True)
        #        letters_name = self.panel['name'].str.replace("[0-9]","", regex = True)
        #        self.panel['name_test'] = numbers_name + letters_name
        #        
        #        keep = (self.panel['channel_test'] != self.panel['name_test'])
        #        self.panel['keep'] = keep
        #        self.panel['keep'] = self.panel['keep'].astype('int')
        #        self.panel = self.panel.drop(['channel_test','name_test'],axis=1)
        #    '''
        #else:
        #    try:
        #        read_dir = "".join([self.directory_object.main, "/panel.csv"])
        #        self.panel = pd.read_csv(read_dir)     ## read in panel file if it already exists 
        #    except FileNotFoundError:
        #        image_list = sorted(os.listdir(self.directory_object.main + "/raw"))
        #        reader_string = "".join([self.directory_object.main, "/raw/", image_list[0]])
        #        tiff_file1 = tf.imread(reader_string)
        #        channel_list = [i for i in range(tiff_file1.shape[0])]
        #        #### now make the initial pd.DataFrame to hold the table widget:
        #        Init_Table = pd.DataFrame()
        #        Init_Table['channel'] = channel_list
        #        Init_Table['name'] = channel_list
        #        Init_Table['keep'] = 1         # default to keeping all channels
        #        Init_Table['segmentation'] = "" 
        #        self.panel = Init_Table
        #        Init_Table.to_csv(self.directory_object.main + "/panel.csv", index = False)  

    ##### Panel / Metadata / Analysis panel writers:
    def panel_write(self) -> None:
        ''''''
        if _in_gui:
            try:
                self.panel.to_csv(self.directory_object.main + '/panel.csv', index = False)
                with open(self.directory_object.main + '/panel.csv') as file:
                    Project_logger(self.directory_object.main).return_log().info(f"Wrote panel file, with values: \n {file.read()}")
            except Exception:
                tk.messagebox.showwarning("Warning!", message = "Could not write panel file! \n"
                            "Do you have the .csv open right now in excel or another program?")
        else:
            self.panel.to_csv(self.directory_object.main + '/panel.csv', index = False)

    # This method writes from MCDs --> .ome.tiffs (see DeepCell_Mesmer_Segmentor function in GUI_functions file for base code)
    def deepcell_segment(self, 
                         image_folder: str, 
                         output_folder: Union[str, None] = None,                             # TODO: set a None default to /images/img
                         image_choice: str = "ALL", 
                         re_do: bool = False,
                         is_torch: Union[bool, None] = None,
                         ) -> None:                                      # ****stein_derived (implements / directly uses parts of 
                                                                            # steinbock.segmentation.deepcell.py file
                                                                            # lines directly derived marked with # ***)
        '''
        Runs deepcell / mesmer segmentation, and writes masks to output_folder

        Args:
            image_folder (string / Pathlike): 
                The directory to a folder of .tiff files to be denoised. If attempting to run all the images in this folder (img = "")
                then this folder MUST ONLY contain .tiff files and nothing else (including no subfolders). 

            output_folder (string / Pathlike): 
                The directory of the folder where the denoised images are to be written.

            image_choice (string): 
                If "All" --> attempts to segment every file in image_folder. Otherwise, the value in the list should be one of the image's filenames
                (discoverable by os.listdir(image_folder)). 

            re_do (boolean): 
                whether to skip or to redo images that already have mask files in output_folder. If == False, then images in image_folder that
                already have a matching file in output_folder will be skipped and not segmented again.  If True, will segment every imgae in image_folder,
                overwriting any previously done masks with matching filenames to the filenames in image_folder. 
                Use case: if new .mcd's / .tiff's have been added to the project, and you only need those to be segmented, redo = False will save time by 
                not redoing the segmentation of the project's original images.

            is_torch (boolean, or None):
                whether to use the original tensorflow backend for mesmer segmentation (False), use the new PyTorch / ONNX converted backend (True), or allow
                iSD to automatically decide which to try to use (None). If None, iSD will prefer tensorflow if it can be imported -- and failing import of tensorflow
                will instead use PyTorch. 
        
        Inputs / Outputs:
            Inputs: 
                reads .tiff file(s) from image_folder

            Outputs: 
                writes .tiff file(s) to output_folder
        '''
        if output_folder is None:
            output_folder = self.directory + "/masks/deepcell_masks"
        if not os.path.exists(output_folder):
            os.mkdir(output_folder) 

        if image_choice == "ALL":
            img_files = sorted(Path(image_folder).rglob("[!.]*.tiff"))    # ***
        else:
            img_files =  sorted(Path(image_folder).rglob(f"*{image_choice}.tiff"))  # *** 
        
        if (re_do is False) and (image_choice == "ALL"): 
            new_list = []
            for i in img_files:
                path = str(i).replace("\\", '/')
                right_side = path.rfind("/")
                if path[(right_side + 1):] in os.listdir(output_folder):
                    pass
                else:
                    new_list.append(i)
            img_files = new_list

        number_img = len(img_files)
        if number_img == 0:
            if _in_gui:
                tk.messagebox.showwarning("Warning!", message = "No images to segment! (is the redo prior masks option not checked?)")
                return
            else:
                print("No images to segment! Were you intending to redo segmentations, but re_do == False (default)?")
                return
        
        segmentor = try_segment_objects(img_files,        # *** (whole function call --> calling to stein_unhooked)
            Application.MESMER,   
            channelwise_minmax = False,
            channelwise_zscore = True,
            channel_groups = self.panel[self.panel['keep'] == 1]['segmentation'],
            aggr_func = np.mean,
            pixel_size_um = (self.resolutions[0] * self.resolutions[1]),
            segmentation_type = "whole-cell",
            is_torch = is_torch)
        
        for i in img_files:
            path, mask = next(segmentor)
            path = str(path).replace("\\", '/')
            right_index = str(path).rfind('/')
            left_index = str(path).rfind('.ome.tiff')
            file_name = str(path)[right_index+1:left_index]
            mask_numb = mask.astype("int").max().max()
            if mask_numb == 0:
                if _in_gui:
                    warning_window(f"{file_name} has no cell masks in it! No mask file will be written for this image." 
                                   "Re-run segmentation or delete this image from the analysis!")
                else:
                    print(f"{file_name} has no cell masks in it! No mask file will be written for this image." 
                          "Re-run segmentation or delete this image from the analysis!")
            #### mask.astype('float') in the function below makes it export like steinbock (gray scale in Napari). 
            # However, removing that would make it export as ints (color in Napari), which might also be good.
            else:
                tf.imwrite(Path(output_folder, "".join([file_name, '.ome.tiff'])), mask.astype('float'), photometric='minisblack')
                print(f"{file_name} has been Segmented, with {mask_numb} masks in it!")

    def cellpose_segment(self, 
                        image_folder: str, 
                        output_folder: str,  
                        img: str = "", 
                        re_do: bool = False,
                        gpu: bool = False, 
                        flow_threshold: float = 0.4, 
                        cellprob_threshold: float = 0.0, 
                        min_size: int = 15, 
                        model_type: Union[None, str] = None, 
                        diam_mean: float = 30.0,
                        ) -> None:
        '''
        This executes cellpose segmentation on one or all of the images (.tiff) in a supplied folder

        Args:
            image_folder (string / Pathlike): 
                The directory to a folder of .tiff files to be denoised. If attempting to run all the images in this folder (img = "")
                then this folder MUST ONLY contain .tiff files and nothing else (including no subfolders). 

            output_folder (string / Pathlike): 
                The directory of the fodler where the denoised images are to be written.

            img (string): 
                default is the empty string, which leads to denoising of all images in the supplied directory. Otherwise this string should be the
                filename of one of the images in the directory. Only that image will be denoised. The strings that can be used for this argument can obtained 
                by os.listdir(img_directory)

            re_do (boolean): 
                whether to skip or to redo images that already have mask files in output_folder. If == False, then images in image_folder that
                already have a matching file in output_folder will be skipped and not segmented again.  If True, will segment every imgae in image_folder,
                overwriting any previously done masks with matching filenames to the filenames in image_folder. 
                Use case: if new .mcd's / .tiff's have been added to the project, and you only need those to be segmented, redo = False will save time by 
                not redoing the segmentation of the project's original images.

            gpu (boolean): 
                whether to attempt to run the dneoising using an installed GPU (True) or to simply use the CPU (False)
                Cellpose uses PyTorch (unlike DeepCell which uses tensorflow, and automatically attempts to detect a GPU).

            flow_threshold (float): 
                hyperparameter of cellpose model. Cells with flow error rates above this threshold will be excluded.
                Higher values should increase the number of cell masks, and lower values decrease the number of cell masks. 

            cellprob_threshold (float): 
                Hyperparameter of cellpose model. Pixels above this threshold included in cell masks, 
                Higher value shrink cell masks and lower values expand cell mask sizes. 

            min_size (int): 
                hyperparameter of cellpose model, minimum size (in pixels) for cell regions 

            model_type (string): 
                which cellpose model to use to modify the images
                options : "cyto3", "nuclei",  "cyto2_cp3", "tissuenet_cp3",  "livecell_cp3",  "yeast_PhC_cp3", "yeast_BF_cp3", "bact_phase_cp3", 
                "bact_fluor_cp3", "deepbacs_cp3", "cyto2", "cyto", "transformer_cp3", "neurips_cellpose_default", "neurips_cellpose_transformer",
                "neurips_grayscale_cyto2"

            diam_mean (float): 
                the average size of the objects in the image (in microns) -- used by cellpose to up/downscale the image to match what cellpose was 
                trained on before proceeding with denoising.
        
        Inputs / Outputs:
            Inputs: 
                reads .tiff file(s) from image_folder

            Outputs: 
                writes .tiff file(s) to output_folder
        '''
        self._cellpose_executor = _CellposeExecutor(self.panel)
        self._cellpose_executor.segment(image_folder = image_folder, 
                                        output_folder = output_folder,  
                                        img = img, 
                                        flow_threshold = flow_threshold, 
                                        cellprob_threshold = cellprob_threshold, 
                                        min_size = min_size, 
                                        re_do = re_do,
                                        gpu = gpu, 
                                        model_type = model_type, 
                                        diam_mean = diam_mean)
        
    def cellpose_denoise(self, 
                channel_list: list[int], 
                image_folder: Union[str, Path], 
                output_folder: Union[str, Path], 
                img: str = "",
                gpu: bool = False, 
                model_type: Union[None, str] = None, 
                diam_mean: float = 30.0,
                ) -> None:
        '''
        Executes cellpose based denoising on one or all of the image (.tiff) files in a directory, operating on the selected channels

        Args:
            channel_list (list of integers): 
                The channels in the images to denoise. The channels are represented as integers, as in, once the images are
                converted to numpy arrays, then each channel can be accessed by simple numpy subsetting::

                    channel = image_array[channel_number,:,:] 

                This means that this method assumes the images in the supplied folder all have the same order of channels. 

            image_folder (string / Pathlike): 
                The directory to a folder of .tiff files to be denoised. If attempting to run all the images in this folder (img = "")
                then this folder MUST ONLY contain .tiff files and nothing else (including no subfolders). 

            output_folder (string / Pathlike): 
                The directory of the fodler where the denoised images are to be written.

            img (string): 
                default is the empty string, which leads to denoising of all images in the supplied directory. Otherwise this string should be the
                fileanme of one of the images in the directory. Only that image will be denoised. The strings that can be used for this argument can obtained 
                by os.listdir(image_folder)

            gpu (boolean): 
                whether to attempt to run the dneoising using an installed GPU (True) or to simply use the CPU (False)
                Cellpose uses PyTorch (unlike DeepCell which uses tensorflow, and automatically attempts to detect a GPU).

            model_type (string): 
                which cellpose model to use to modify the images
                options : 'denoise_cyto3', 'deblur_cyto3', 'upsample_cyto3', 'denoise_nuclei', 'deblur_nuclei', 'upsample_nuclei' 

            diam_mean (float): 
                the average size of the objects in the image (in microns) -- used by cellpose to up/downscale the image to match what cellpose was 
                trained on before proceeding with denoising.
        
        Inputs / Outputs:
            Inputs: 
                reads .tiff file(s) from image_folder

            Outputs: 
                writes .tiff file(s) to output_folder
        '''
        self._cellpose_denoise_executor = _CellposeDenoiseExecutor()
        self._cellpose_denoise_executor.denoise(channel_list = channel_list, 
                                                img_directory = image_folder, 
                                                ouput_directory = output_folder, 
                                                img = img,
                                                gpu = gpu, 
                                                model_type = model_type, 
                                                diam_mean = diam_mean)

    def simple_denoise(self,
                       image_folder: str, 
                       output_folder: str, 
                       channel_list: list[int], 
                       image: str = "",
                       sigma_range: Union[None, list[float]] = None, 
                       pre_cal: bool = False, 
                       cal_img: int = 0,
                       ) -> None:
        '''
        Executes "simple" denoising on one or all of the image (.tiff) files in a directory, operating on the selected channels

        Args:
            channel_list (list of integers): 
                The channels in the images to denoise. The channels are represented as integers, as in, once the images are
                converted to numpy arrays, then each channel can be accessed by simple numpy subsetting::

                    channel = image_array[channel_number,:,:] 

                This means that this method assumes the images in the supplied folder all have the same order of channels. 

            image_folder (string / Pathlike): 
                The directory to a folder of .tiff files to be denoised. If attempting to run all the images in this folder (img = "")
                then this folder MUST ONLY contain .tiff files and nothing else (including no subfolders). 

            output_folder (string / Pathlike): 
                The directory of the fodler where the denoised images are to be written.

            img (string): 
                default is the empty string, which leads to denoising of all images in the supplied directory. Otherwise this string should be the
                filename of one of the images in the directory. Only that image will be denoised. The strings that can be used for this argument can obtained 
                by os.listdir(image_folder)

            sigma_range (list of integers, or None): 
                the range of sigmas to perform coarse calibration of the j-invariant nl means algorithm on. Once coarse 
                calibration is performed on one image, fine calibration is performed on each image before denoising, looking at a smaller range of sigmas
                above & below the optimum sigma determined during coarse calibration.

            pre_cal (boolean): 
                whether coarse calibration of sigma has already been performed (True), or not (False, default).

            cal_img (integer): 
                which image in os.listdir(image_folder) will be used for coarse calibratio nof sigma. By default the first image in that list is used (cal_img = 0)
        
        Inputs / Outputs:
            Inputs: 
                reads .tiff file(s) from image_folder

            Outputs: 
                writes .tiff file(s) to output_folder
        '''
        self._simple_denoise_executor = _simpleDenoiseExecutor()
        self._simple_denoise_executor.denoise(folder_path = image_folder, 
                                              output_folder_path = output_folder, 
                                              channel_list = channel_list, 
                                              image = image,
                                              sigma_range = sigma_range, 
                                              pre_cal = pre_cal, 
                                              cal_img = cal_img,
                                              )



class _CellposeDenoiseExecutor:
    '''
    This class coordinates cellpose denoising
    '''
    def __init__(self):
        pass
        
    def denoise(self, 
                channel_list: list, 
                img_directory: Union[str, Path], 
                ouput_directory: Union[str, Path], 
                img: str = "",
                gpu: bool = False, 
                model_type: Union[None, str] = None, 
                diam_mean: float = 30.0,
                ) -> None:
        '''
        This runs cellpose denoising 
        '''
        self._gpu = gpu
        self._model_type = model_type
        self._diam_mean = diam_mean
        img_directory = str(img_directory)
        ouput_directory = str(ouput_directory)
        if not os.path.exists(ouput_directory):
            os.mkdir(ouput_directory)

        if len(img) > 0:   
            img_path = "".join([img_directory, "/", img])
            output_path = "".join([ouput_directory, "/", img])
            image, metadata = self._read_OME_tiff(img_path)
            if channel_list == ["all"]:
                channel_list = []
                for i in range(0,image.shape[0]):
                    channel_list.append(i)
            for channel in channel_list:
                image[channel] = np.transpose(self._denoise_one_channel(image[channel]), [2, 0, 1])
            self._write_OME_tiff(metadata, image, output_path)
            print(f'{img} denoising has been completed!')
        else:                      ### if a specific image name is not given, denoise the entire directory 
            image_list = [i for i in sorted(os.listdir(img_directory)) if i.lower().find(".tif") != -1]
            for i in image_list:
                img_path = "".join([img_directory, "/", i])
                out_path = "".join([ouput_directory, "/", i])
                image, metadata = self._read_OME_tiff(img_path)
                if channel_list == ["all"]:
                    channel_list = []
                    for i in range(0,image.shape[0]):
                        channel_list.append(i)
                for channel in channel_list:
                    image[channel] = np.transpose(self._denoise_one_channel(image[channel]), [2, 0, 1])   
                                                ## this should reorder the images properly each time
                self._write_OME_tiff(metadata, image, out_path)
                print(f'{i} denoising has been completed!')

    def _read_OME_tiff(self, image_path: str) -> tuple[np.ndarray[float], str]:
        ''''''
        img_array, xml_metadata = read_ometiff(image_path)
        img_array = np.squeeze(img_array)
        return img_array, xml_metadata

    def _write_OME_tiff(self, 
                        metadata: str, 
                        image: np.ndarray[float], 
                        write_path: str,
                        ) -> None:
        ''''''
        try:
            write_ometiff(write_path, image, metadata)
        except Exception:
            tf.imwrite(write_path, image)
            print(f"Could not write {write_path} as ome.tiff with metadata. Writing wihtout metadata")
                    
    def _denoise_one_channel(self, image: np.ndarray[float]) -> np.ndarray[float]:
        '''
        This takes an input channel and denoises it using cellpose
        '''
        initialized_model = denoise.DenoiseModel(gpu = self._gpu, model_type = self._model_type, diam_mean = self._diam_mean)  
        output = initialized_model.eval(image, channels = [0,0]) 
                ### don't need choices for channels, since I intend to only pass single-channel images into the denoiser
        return output
    
class _CellposeExecutor:
    '''
    This class coordinates cellpose segmentation

    methods: 
            segment: execute cellpose segmentation. Accepts more hyperparameters of cellpose models
    '''
    def __init__(self, panel: pd.DataFrame):
        self.panel = panel[panel['keep'] == 1].reset_index().drop("index", axis = 1)
        
    def segment(self, 
                image_folder: str, 
                output_folder: str,  
                img: str = "", 
                flow_threshold: float = 0.4, 
                cellprob_threshold: float = 0.0, 
                min_size: int = 15, 
                re_do: bool = False,
                gpu: bool = False, 
                model_type: Union[None, str] = None, 
                diam_mean: float = 30.0,
                ) -> None:
        '''
        This function is for actually running the segmentation
        '''
        self._gpu = gpu
        self._model_type = model_type
        self._diam_mean = diam_mean
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        initialized_model = models.CellposeModel(gpu = self._gpu, model_type = self._model_type,
                                                diam_mean = self._diam_mean) 
        if len(img) > 0:   ## have an option to only segment one image (as a test before doing all)
            img_array, metadata = self._read_OME_tiff("".join([image_folder, "/", img]))
            img_array = self._normalize_channels_and_merge(img_array)
            masks, flows, styles = initialized_model.eval(img_array, 
                                                            channels = [2,1], 
                                                            flow_threshold = flow_threshold, 
                                                            cellprob_threshold = cellprob_threshold, 
                                                            min_size = min_size)
            mask_numb = masks.astype("int").max().max()
            if mask_numb == 0:
                if _in_gui:
                    warning_window(f"{img} has no cell masks in it! No mask file will be written for this image." 
                                    "Re-run segmentation or delete this image from the analysis!")
                else:
                    print(f"{img} has no cell masks in it! No mask file will be written for this image."
                            "Re-run segmentation or delete this image from the analysis!")
            else:
                tf.imwrite("".join([output_folder, "/", img]), masks, photometric = "minisblack")
                print(f"{img} has been Segmented with {mask_numb} masks in the image!") 
                return "".join([output_folder, "/", img])
        else:
            if (sorted(os.listdir(image_folder)) == sorted(os.listdir(output_folder))) and (re_do is False):
                if _in_gui:
                    tk.messagebox.showwarning("Warning!", message = "All images already have masks in the output folder!" 
                                                "Check redo option to redo segmentation, if desired") 
                else:
                    print("All images already have masks in the output folder! Check redo option to redo segmentation, if desired")  
                return  
            list_of_images = [i for i in sorted(os.listdir(image_folder)) if i.lower().find(".tif") != -1]
            for image in list_of_images:
                if (image in os.listdir(output_folder)) and (re_do is False):    ## don't re-segment images, unless re_do is set to True
                    pass              
                else:
                    img_array, metadata = self._read_OME_tiff("".join([image_folder, "/", image]))
                    img_array = self._normalize_channels_and_merge(img_array)
                    # print(img_array.shape)
                    masks, flows, styles = initialized_model.eval(img_array, 
                                                                    channels = [2,1], 
                                                                    flow_threshold = flow_threshold, 
                                                                    cellprob_threshold = cellprob_threshold, 
                                                                    min_size = min_size)
                    mask_numb = masks.astype("int").max().max()
                    if mask_numb == 0:
                        if _in_gui:
                            warning_window(f"{image} has no cell masks in it! No mask file will be written for this image." 
                                            "Re-run segmentation or delete this image from the analysis!")
                        else:
                            print(f"{image} has no cell masks in it! No mask file will be written for this image."
                                    "Re-run segmentation or delete this image from the analysis!")
                    else:
                        tf.imwrite("".join([output_folder, "/", image]), masks, photometric = "minisblack")
                        print(f'{image} has been Segmented with {mask_numb} masks in the image!')    
                                ## if / until the progress bar is working, I will instead print the completion of each image to the console
            
    def _read_OME_tiff(self, image_path: str) -> tuple[np.ndarray[float], str]:
        ''''''
        img_array, xml_metadata = read_ometiff(image_path)
        img_array = np.squeeze(img_array)
        return img_array, xml_metadata
    
    def _normalize_channels_and_merge(self, 
                                      image = np.ndarray[float],
                                      ) -> np.ndarray[float]:  # ****stein_derived (the way the channels are shaped / z-score 
                                                                # normalizated before segmentation parallel's steinbock's deepcell segmentation)
        '''
        Will need a function to normalize and then merge disparate channels (if users selects more than one cytoplasmic / nuclear channels)

        The self.panel object below is the  panel file read in as a pd.DataFrame
        The image argument should be a 3D numpy array, representing a 2D image with multiple channels (aka a tf.imread(XXX.ome.tiff) of one of the images)

        Returns --> a 3D-array (where the first dimension has two layers such that: image_out[0] == nuclei channels, image_out[1] == cytoplasmic channels)
        '''
        panel = self.panel[self.panel['segmentation'].notna()]
        nuclei = panel[panel['segmentation'].astype('int') == 1].index
        cyto = panel[panel['segmentation'].astype('int') == 2].index
        nuclei_channels = [image[i] for i in nuclei]
        cyto_channels = [image[i] for i in cyto]
        placeholder = np.zeros([image.shape[1], image.shape[2]])
        ## z-score normalize  --> see steinbock basis: 
        #       https://github.com/BodenmillerGroup/steinbock/blob/main/steinbock/segmentation/deepcell.py (MIT license)
        nuclei_channels = [(i - np.nanmean(i))[np.nanstd(i) > 0] / np.nanstd(i)[np.nanstd(i) > 0] for i in nuclei_channels]
        cyto_channels = [(i - np.nanmean(i))[np.nanstd(i) > 0] / np.nanstd(i)[np.nanstd(i) > 0] for i in cyto_channels]

        ## aggregate channels together:
        nuclear_aggregate = (nuclei_channels[0] - nuclei_channels[0].min()) / (nuclei_channels[0] - nuclei_channels[0].min()).max()  
                                    ## initialize object, and add first channel -- normalized between a min of 0 and a max of 1
        for i,ii in enumerate(nuclei_channels):
            if i > 0:
                nuclear_aggregate = nuclear_aggregate + (ii - ii.min()) / (ii- ii.min()).max()
        
        cyto_aggregate = (cyto_channels[0] - cyto_channels[0].min()) / (cyto_channels[0] - cyto_channels[0].min()).max()
        for i,ii in enumerate(cyto_channels):
            if i > 0:
                cyto_aggregate = cyto_aggregate + (ii - ii.min()) / (ii- ii.min()).max()

        image_out = np.array([nuclear_aggregate[0], cyto_aggregate[0], placeholder])
        return image_out
        

class _simpleDenoiseExecutor:
    '''
    This coordinates my custom "simple denoising", a variant of optimized nl-means denoising. Optimizing using j-invariant optimization
    of an nl-mean algorithm, then averages the optimized j-invariant denoising with the output of a non j-invariant nl-means algorithm with
    the same parameters as the optimized algorithm. 

    methods:
        denoise: This method does denoising within a provided folder, either all the images in the folder, or just one of those images.
                Coarse calibrates on the first image of the folder if doing all the images.

    Attributes:
        sigma_range (list): this equals = list(range(0.5,4,0.5)) by default (theooreticall if range objects could accept non-integers), but 
                can be set as well. This is the range of sigmas to perform corse calibration on.
        sigma_cal (float): this represents the final calibrated sigma
    
    '''
    def __init__(self):
        self.sigma_range = [i/2 for i in range(1,8,1)]
        self.sigma_cal = 1.0

    def _calibrate_on_img(self, 
                        image_path: str, 
                        channel: int, 
                        sigma_range: Union[None,list[float]] = None,
                        ) -> np.ndarray[float]:
        '''
        '''
        if sigma_range is None:
            sigma_range = self.sigma_range
        else:
            if np.array([sigma_range]).min() < 0:
                print("Removing negative sigma values!")
                sigma_range = [i for i in sigma_range if i > 0]
            self.sigma_range = sigma_range

        image = tf.imread(image_path)
        to_denoise = image[channel]
        denoised, self.sigma_cal, h_of_best_fx  = self._denoise_calibration_j_semi_variant_nl_means(to_denoise, sigmas = sigma_range)
        return denoised

    def _denoise_one(self, 
                image_path: str, 
                channel: int, 
                output_path: str = "", 
                sigma_range: Union[None,list[float]] = None, 
                pre_cal: bool = False,
                ) -> tuple[np.ndarray[float], np.ndarray[float], float]:
        '''
        '''
        if sigma_range is None:
            sigma_range = self.sigma_range
        else:
            if np.array([sigma_range]).min() < 0:
                print("Removing negative sigma values!")
                sigma_range = [i for i in sigma_range if i > 0]
            self.sigma_range = sigma_range
            
        if pre_cal is False:
            self._calibrate_on_img(image_path = image_path, channel = channel, sigma_range = sigma_range)

            new_sigmas = [self.sigma_cal - 0.25, self.sigma_cal, self.sigma_cal + 0.25]
            new_sigmas = [i for i in new_sigmas if i > 0]
        else:
            new_sigmas = sigma_range

        image, metadata = self._read_OME_tiff(image_path)
        to_denoise = image[channel]
        denoised, sigma_of_best_fx, h_of_best_fx  = self._denoise_calibration_j_semi_variant_nl_means(to_denoise, sigmas = new_sigmas)

        image[channel] = denoised
        if len(output_path) > 0:
            self._write_OME_tiff(metadata, image, output_path)
        return image, denoised, sigma_of_best_fx

    def _denoise_folder_one_channel(self, 
                        folder_path: str, 
                        output_folder_path: str, 
                        channel: int,
                        sigma_range: list[float], 
                        pre_cal: bool = False, 
                        cal_img: int = 0,
                        ) -> None:
        '''
        '''
        if not os.path.exists(output_folder_path):
            os.mkdir(output_folder_path)
        if sigma_range is None:
            sigma_range = self.sigma_range
        else:
            if np.array([sigma_range]).min() < 0:
                print("Removing negative sigma values!")
                sigma_range = [i for i in sigma_range if i > 0]
            self.sigma_range = sigma_range
            
        image_list = ["".join([folder_path,"/",i]) for i in sorted(os.listdir(folder_path)) if i.lower().find(".tif") != -1]
        output_list = ["".join([output_folder_path,"/",i]) for i in sorted(os.listdir(folder_path)) if i.lower().find(".tif") != -1]
        if pre_cal is False:
            cal_path =  image_list[cal_img]
            self._calibrate_on_img(image_path = cal_path, channel = channel, sigma_range = sigma_range)
            new_sigmas = [self.sigma_cal - 0.5, self.sigma_cal - 0.25, self.sigma_cal, self.sigma_cal + 0.25, self.sigma_cal + 0.5]
            new_sigmas = [i for i in new_sigmas if i > 0]
        else:
            new_sigmas = sigma_range
            
        for i,ii in zip(image_list,output_list):
            image, metadata = self._read_OME_tiff(i)
            to_denoise = image[channel]
            denoised, sigma_of_best_fx, h_of_best_fx  = self._denoise_calibration_j_semi_variant_nl_means(to_denoise, sigmas = new_sigmas)
            image[channel] = denoised
            self._write_OME_tiff(metadata, image, ii)
            print(f'{ii} denoising of channel {str(channel)} has been completed!')

    def denoise(self, 
                folder_path: str, 
                output_folder_path: str, 
                channel_list: list[int], 
                image: str = "",
                sigma_range: Union[None, list[float]] = None, 
                pre_cal: bool = False, 
                cal_img: int = 0,
                ) -> None:
        '''
        This runs the "simple denoising" algorithm on one or all of the images in the supplied folder

        Args:
            folder_path (string): the path to folder where the images-to-denoise are. This folder should ONLY contain .tiff files

            output_folder_path (string): the path to the folder where the denoised images are to be written.

            channel_list (list[integers]): the list of channels to denoise, as integers which denote the layer in the numpy array representation
                    of the images. Assumes all images in the provided folder have the same channels in the same order. 

            image (string): Either "" (empty string) means that all the files in the input folder will be denoised. Else, supply a filename for a specific
                    file in the folder to denoise.

            sigma_range (list[float, or None]): A list of sigmas to calibrate over. default = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

            pre_cal (boolean): whether coarse calibration has already been performed (if True, will skip coarse calibration)

            cal_img (integer): which image to perform coarse calibration on, as an integer of os.listdir(folder_path)[cal_img]

        Inputs / Outputs:
            Inputs: reads in .tiff files from folder_path
            
            Outputs: exports enoised .tiff files to output_folder_path, with the same names as the files read-in as inputs.
        '''
        if image == "":
            for i,ii in enumerate(channel_list):
                if i == 0:
                    self._denoise_folder_one_channel(folder_path, 
                                                        output_folder_path, 
                                                        channel = ii, 
                                                        sigma_range = sigma_range, 
                                                        pre_cal = pre_cal, 
                                                        cal_img = cal_img)
                ## once the first channel is denoised and written, we will want to read from the output folder 
                #       (otherwise reading/writing each channel will overwrite prior denoisings)
                else:
                    self._denoise_folder_one_channel(output_folder_path, 
                                                        output_folder_path, 
                                                        channel = ii, 
                                                        sigma_range = sigma_range, 
                                                        pre_cal = pre_cal, 
                                                        cal_img = cal_img)
        else:
            image_path = folder_path + "/" + image
            output_img_path = output_folder_path + "/" + image
            for i,ii in enumerate(channel_list):
                if i == 0:
                    self._denoise_one(image_path = image_path, 
                                channel = ii, 
                                output_path = output_img_path, 
                                sigma_range = sigma_range, 
                                pre_cal = pre_cal)
                    
                ## once the first channel is denoised and written, we will want to read from the output folder 
                #           (otherwise reading/writing each channel will overwrite prior denoisings)
                else:
                    self._denoise_one(image_path = output_img_path, 
                                channel = ii, 
                                output_path = output_img_path, 
                                sigma_range = sigma_range, 
                                pre_cal = pre_cal)

    def _read_OME_tiff(self, image_path: str) -> tuple[np.ndarray[float], str]:
        ''' '''
        img_array, xml_metadata = read_ometiff(image_path)
        img_array = np.squeeze(img_array)
        return img_array, xml_metadata

    def _write_OME_tiff(self, metadata: str, image: np.ndarray[float], write_path: str) -> None:
            ''' '''
        #try:
            write_ometiff(write_path, image, metadata)
        #except Exception:                                                   ## Should it try to write without metadata?
            #   write_ometiff(write_path, image, ascii(metadata))
            #   print("Error in metadata -- non-ASCII characters present! Image written without metadata")

    def _denoise_calibration_j_semi_variant_nl_means(self, 
                                                    image: np.ndarray[float], 
                                                    sigmas: list[float] = [i/2 for i in range(1,8,1)],
                                                    ) -> tuple[np.ndarray[float], float, float]:
        '''
        '''
        dict = {"sigma":sigmas, "preserve_range":[True]}
        best_function = skimage.restoration.calibrate_denoiser(image, skimage.restoration.denoise_nl_means, dict, extra_output = True)
        sigma_of_best_fx = best_function[1][0][np.argmin(best_function[1][1])]['sigma']

        dict2 = {"sigma":[sigma_of_best_fx], "h":np.array([0.5, 0.65, 0.8, 0.95])*sigma_of_best_fx, "preserve_range":[True]}
        best_function = skimage.restoration.calibrate_denoiser(image, skimage.restoration.denoise_nl_means, dict2, extra_output = True)

        h_of_best_fx = best_function[1][0][np.argmin(best_function[1][1])]['h']

        
        denoised1 =  skimage.restoration.denoise_nl_means(image, sigma = sigma_of_best_fx, h = h_of_best_fx, preserve_range = True)
        denoised2 = best_function[0](image)
        denoised = ((denoised1 + denoised2) / 2)   
                        ## I choose to average the j-invariant denoiser (which tends to have a lot of checkboard pattern) 
                        # and the j-variant (?) denoiser, which tends to maintain the underlying structure more accurately
        return denoised, sigma_of_best_fx, h_of_best_fx
