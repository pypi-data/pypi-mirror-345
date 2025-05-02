'''
This module handles the widgets on the second page/tab of the GUI that deal with segmentation and denoising once the IMC project 
directory has been entered.

'''

import os
from typing import Union
import tkinter as tk

import customtkinter as ctk

from .sharedClasses import CtkSingletonWindow, DirectoryDisplay, TableWidget, Project_logger, warning_window, folder_checker, overwrite_approval
from .processing_class import mask_expand

__all__ = []

class ImageProcessingWidgets(ctk.CTkFrame):
    '''
    
    '''
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        label1 = ctk.CTkLabel(master = self, text = "Steinbock-style Panel File:")
        label1.grid(column = 0, row = 0)

        self.TableWidget = TableWidget(self) 
        self.TableWidget.setup_width_height(600, 700) 
        self.TableWidget.grid(column = 0, row = 1, rowspan = 4)

        label2 = ctk.CTkLabel(master = self, text = "Directory navigator")
        label2.grid(column = 1, row = 2)

        self.dir_disp = DirectoryDisplay(self) 
        self.dir_disp.grid(column = 1, row = 3)

        label3 = ctk.CTkLabel(master = self, text = "Processing Functions")
        label3.grid(column = 1, row = 0)
        
        self.buttonframe = self.ButtonFrame(self)
        self.buttonframe.grid(column = 1, row = 1)

    def add_Experiment(self, Experiment_object, from_mcds: bool = True):
        self.Experiment_object = Experiment_object
        self.Experiment_object.TableWidget = self.TableWidget
        self.from_mcds = from_mcds

    def initialize_buttons(self, directory: str) -> None:
        ## decoupler for widget setup and data setup
        self.directory = directory
        self.ImageAnalysisPortionLogger = Project_logger(directory).return_log()
        self.dir_disp.setup_with_dir(directory, self.Experiment_object)
        self.TableWidget.setup_data_table(directory, self.Experiment_object.panel, "panel")
        self.TableWidget.populate_table()
        self.call_write_panel()
        self.Experiment_object._panel_setup()
        self.buttonframe.initialize_buttons()
        
    class ButtonFrame(ctk.CTkFrame):
        '''
        Contains the buttons for launching the sub-windows which in turn execute the denoising/segmentation methods of the program.
        '''
        def __init__(self, master):
            super().__init__(master)
            self.master = master

            spacer1 = ctk.CTkLabel(self, text = "Denoising:")
            spacer1.grid(column = 1, row = 2)

            self.simple_denoise = ctk.CTkButton(self, text = "Simple Denoising")
            self.simple_denoise.grid(column = 1, row = 3)
            self.simple_denoise.configure(state = "disabled")

            self.cellposer = ctk.CTkButton(self, text = "Cellpose Denoiser")
            self.cellposer.grid(column = 1, row = 4, padx= 5, pady = 5)
            self.cellposer.configure(state = "disabled")

            label2 = ctk.CTkLabel(self, text = "Segmentation Options")
            label2.grid(row = 5, column = 1, padx = 5, pady = 5)

            self.DeepCell = ctk.CTkButton(self, text = "Run DeepCell")
            self.DeepCell.grid(column = 1, row = 6, padx= 5, pady = 5)
            self.DeepCell.configure(state = "disabled")

            self.cellpose_seg = ctk.CTkButton(self, text = "Run Cellpose")
            self.cellpose_seg.grid(column = 1, row = 7, padx= 5, pady = 5)
            self.cellpose_seg.configure(state = "disabled")

            self.expander = ctk.CTkButton(self, text = "Expand Masks")
            self.expander.grid(column = 1, row = 9, padx= 5, pady = 5)

        def initialize_buttons(self) -> None:
            ###This function allow the set up of the commands to coordinated
            try:
                image_folders = [i for i in os.listdir(self.master.Experiment_object.directory_object.img_dir) if i.find(".") == -1]
                if len(image_folders) > 0:   
                                    ### denoise / segmentation not activated if there are no images available
                    self.DeepCell.configure(command = self.master.call_deepcell_mesmer_segmentor, state = "normal")
                    self.cellpose_seg.configure(state = "normal", command = self.master.call_cellpose_seg)
                    self.cellposer.configure(command = self.master.call_cellposer, state = "normal")
                    self.simple_denoise.configure(command = self.master.call_simple_denoise, state = "normal")
                    self.expander.configure(command = self.master.call_mask_expand, state = "normal")

            except Exception:
                tk.messagebox.showwarning("Warning!", message = "Error: Could not initialize commands!")

    def call_deepcell_mesmer_segmentor(self) -> None:
        '''
        Runs the deepcell segmentation. Also writes the panel to the disk before segmentation to properly catch any edits in the panel file
        '''
        ## the panel write / setup block is too ensure the panel settings are saved while running, and also to avoid a bizarre bug where
        ## deep cell was using np.nan's as a third group for the channels (I have no idea why...). Reading from a file solves that problem somehow
        self.call_write_panel()
        self.Experiment_object._panel_setup()

        DeepCell_window(self)

    def run_deepcell(self, 
                     image_choice: str, 
                     re_do: bool, 
                     image_folder: Union[None, str] = None, 
                     output_folder: Union[None, str] = None,
                     ) -> None:  
        '''
        ''' 
        warning_window('''Don't worry if this step takes a while to complete or the window appears to freeze!\n
                    This behavior during Deepcell / Mesmer segmentation is normal.''')
        
        self.after(200, lambda: self.Experiment_object.deepcell_segment(image_choice = image_choice,
                                                                             re_do = re_do, 
                                                                             image_folder = image_folder, 
                                                                             output_folder = output_folder))
        self.buttonframe.initialize_buttons()

    def call_mask_expand(self) -> None:
        Expander_window(self)

    def call_mask_expand_part_2(self, 
                                  distance: int, 
                                  image_source: str, 
                                  output_directory: Union[None, str] = None,
                                  ) -> None:
        ## First, copy the unexpanded data to a subdirectory --> allows restoration of original segmentation:
        mask_expand(distance, image_source, output_directory = output_directory) 

    def call_cellposer(self) -> None:
        CellPoseDenoiseWindow(self) 

    def call_simple_denoise(self) -> None:
        SimpleDenoiseWindow(self)

    def call_cellpose_seg(self) -> None:
        '''
        Launches Cellpose segmentation window. Also writes the panel to the disk before segmentation to properly catch any edits in the panel file
        '''
        self.call_write_panel()
        self.Experiment_object._panel_setup()
        CellPoseSegmentationWindow(self)  

    def call_write_panel(self) -> None:
        # writes panel file after recovering data from TableWidget
        self.Experiment_object.TableWidget.recover_input()
        self.Experiment_object.panel = self.Experiment_object.TableWidget.table_dataframe
        self.Experiment_object.panel_write()      

class up_down_class(ctk.CTkFrame):
    '''
    This class defines a pair of widgets which will increment the value of a master.value optionmenu widget +/- 1
    This is for use with integer based optionmenus where the range of possible values is too great to anticipate easily,
    while still avoiding using an entry field.
    '''
    def __init__(self, master, column = 1, row = 0):
        super().__init__(master)
        self.master = master
        self.column = column
        self.row = row

        upvalue = ctk.CTkButton(master = self, text = "^", command = lambda: self.upvalue(master))
        upvalue.configure(width = 15, height = 10)
        upvalue.grid(column = 0, row = 0)

        downvalue = ctk.CTkButton(master = self, text = "˅", command = lambda: self.downvalue(master))
        downvalue.configure(width = 15, height = 10)
        downvalue.grid(column = 0, row = 1)

    def upvalue(self, master) -> None:
        current_val = int(master.value.get())
        current_val += 1
        master.values_list.append(str(current_val))
        master.values_list = list(set(master.values_list))
        master.values_list.sort()
        master.value.configure(values = master.values_list)
        master.value.set(current_val)

    def downvalue(self, master) -> None:
        current_val = int(master.value.get())
        current_val = current_val - 1
        if current_val < 0:
            current_val = 0
        master.values_list.append(str(current_val))
        master.values_list = list(set(master.values_list))
        master.values_list.sort()
        master.value.configure(values = master.values_list)
        master.value.set(current_val)

class Expander_window(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    This coordinates & executes the pixel expansion options
    '''
    def __init__(self, master): 
        #### Set up the buttons / options / entry fields in the window      
        super().__init__(master)
        self.master = master
        self.title('Mask Pixel Expansion')
        label1 = ctk.CTkLabel(master = self, text = "Choose The number of pixels to expand your masks by:")
        label1.grid(column = 0, row = 0, padx = 10, pady = 10)
        self.values_list = ["5"]
        self.values_list = list(set(self.values_list))
        self.value = ctk.CTkOptionMenu(master = self, values = self.values_list, variable = ctk.StringVar(value = "5"))
        self.value.grid(column = 1, row = 0, padx = 10, pady = 10)

        up_down = up_down_class(self)
        up_down.grid(column = 2, row = 0)
            
        label_8 = ctk.CTkLabel(self, text = "Select folder of masks to be expanded:")
        label_8.grid(column = 0, row = 1)

        def refresh3(enter = ""):
            self.image_folders = [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.masks_dir)) if i.find(".") == -1]
            self.image_folder.configure(values = self.image_folders)

        self.image_folder = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = ""))
        self.image_folder.grid(column = 1, row = 1, padx = 5, pady = 5)
        self.image_folder.bind("<Enter>", refresh3)

        label_9 = ctk.CTkLabel(self, text = "Name folder where the expanded masks will be save to:")   
                ## will want to strictly block overwriting the originals (these can only be overwritten from re-running deepcell / cellpose, etc.)
        label_9.grid(column = 0, row = 2)

        self.output_folder = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "Expanded_masks"))
        self.output_folder.grid(column = 1, row = 2, padx = 5, pady = 5)

        accept_button = ctk.CTkButton(master = self, text = "Accept & proceed", command = lambda: self.read_values())
        accept_button.grid(column = 0, row = 3, padx = 10, pady = 10)

        self.after(200, lambda: self.focus())
        
    def read_values(self) -> None:
        image_folder_choice = self.image_folder.get()
        if image_folder_choice == "":
            tk.messagebox.showwarning("Error!", 
                    message = "No Mask folder to expand was selected!")
            self.focus()
            return
        if folder_checker(self.output_folder.get(), self):
            return
        ### Read in the values and return it to the experiment
        output_directory = self.master.Experiment_object.directory_object.masks_dir + "/" + self.output_folder.get().strip()
        if not overwrite_approval(output_directory, file_or_folder = "folder", GUI_object = self):
            return
        self.master.call_mask_expand_part_2(int(self.value.get()), 
                            image_source = self.master.Experiment_object.directory_object.masks_dir + "/" + image_folder_choice, 
                            output_directory = output_directory)
        self.master.ImageAnalysisPortionLogger.info(f"Expanding masks by {self.value.get()} pixels")
        self.master.dir_disp.list_dir()
        self.destroy()

class SimpleDenoiseWindow(ctk.CTkToplevel, metaclass = CtkSingletonWindow):    
                        ### bulk of code initially copied from cellpose denoising window and re-tooled to execute a simpler denoising algorithm
    '''
    This coordinates and executes my SimpleDenoising method (see that sub-class of Experiment for details).    
    '''
    def __init__(self, master):
        super().__init__(master)
        self.title("Simple Denoising Options:")
        self.master = master

        self.denoiser = self.master.Experiment_object

        label = ctk.CTkLabel(self, text = "Simple Denoising options:")
        label.grid(column = 0,row = 0, padx = 5, pady = 5)

        label_4 = ctk.CTkLabel(self, text = "Select channels to denoise:")
        label_4.grid(column = 0, row = 2)

        self.channels = self.channel_lister(self)
        self.channels.grid(column = 0, row = 3)

        label_8 = ctk.CTkLabel(self, text = "Select an image folder to denoise:")
        label_8.grid(column = 0, row = 5)

        def refresh5b(enter = ""):
            self.image_folders = [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir)) if i.find(".") == -1]
            self.image_folder.configure(values = self.image_folders)

        self.image_folder = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "img"))
        self.image_folder.grid(column = 1, row = 5, padx = 5, pady = 5)
        self.image_folder.bind("<Enter>", refresh5b)

        label8b = ctk.CTkLabel(self, text = "Select an individual image to denoise \n (or leave blank to denoise all):")
        label8b.grid(column = 0, row = 6)

        def refresh5c(enter = ""):
            self.images = [""] + [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir + "/" + self.image_folder.get())) if i.lower().find(".tif") != -1]
            self.single_image.configure(values = self.images)

        self.single_image = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = ""))
        self.single_image.grid(column = 1, row = 6, padx = 5, pady = 5)
        self.single_image.bind("<Enter>", refresh5c)

        label_9 = ctk.CTkLabel(self, 
                               text = "Name the output folder: \n (note that naming ouput == input folder will \n cause overwriting behaviour!)")
        label_9.grid(column = 0, row = 7)

        self.output_folder = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "Denoised_images_1"))
        self.output_folder.grid(column = 1, row = 7, padx = 5, pady = 5)

        button_run_clustering = ctk.CTkButton(self,
                                            text = "Run Denoising",
                                            command = self.run_denoise)
        button_run_clustering.grid(column = 1, row = 8, padx = 5, pady = 5)

        self.after(200, self.focus())

    class channel_lister (ctk.CTkScrollableFrame):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.configure(width = 300)

            df = self.master.master.Experiment_object.panel[self.master.master.Experiment_object.panel["keep"] == 1]["name"].reset_index()

            channel_name = list(df["name"])
            channel_number = list(df.index)
            counter = 0
            self.checkbox_list = []
            for i,ii in zip(channel_name, channel_number):
                length = len(i)
                middle = length // 2
                if length > 20:
                    label = ctk.CTkLabel(master = self, text = i[:middle] + "\n" + i[middle:], width = 150)
                    label.grid(column = 0, row = counter, pady = 5, padx = 5)
                else:
                    label = ctk.CTkLabel(master = self, text = i, width = 150)
                    label.grid(column = 0, row = counter, pady = 5, padx = 5)
                label2 = ctk.CTkLabel(master = self, text = ii)
                label2.grid(column = 1, row = counter, pady = 5, padx = 5)
            
                checkbox = ctk.CTkCheckBox(master = self, text = "", onvalue = ii, offvalue = False)
                checkbox.grid(column = 2, row = counter, pady = 5, padx = 5)
                self.checkbox_list.append(checkbox)
                counter += 1

        def retrieve(self) -> None:
            checkbox_output = [i.get() for i in self.checkbox_list if i.get() is not False]
            return checkbox_output

    def run_denoise(self) -> None:
        '''
        '''
        if folder_checker(self.output_folder.get(), self):
            return
        
        channel_list = self.channels.retrieve()
        if len(channel_list) == 0:
            tk.messagebox.showwarning("Error!", 
                    message = "No Channel to denoise was selected!")
            self.focus()
            return
        
        single_image = self.single_image.get()
        image_folder = self.master.Experiment_object.directory_object.img_dir + "/" + self.image_folder.get()
        if self.output_folder.get() == "img":
            tk.messagebox.showwarning("Error!", 
                    message = "Overwriting the original image folder (img) with denoised files is not allowed")
            self.focus()
            return
        output_folder = self.master.Experiment_object.directory_object.img_dir + "/" + self.output_folder.get().strip()
        if not overwrite_approval(output_folder, 
                                  file_or_folder = "folder", 
                                  GUI_object = self):
            return
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        
        if len(single_image) > 0:
            self.master.ImageAnalysisPortionLogger.info(f"""Simple Denoising channel {channel_list} for one image {single_image}: 
                                                                image folder = {image_folder}, 
                                                                output folder = {output_folder}""")
            self.denoiser.simple_denoise(image_folder = image_folder, 
                                        channel_list = channel_list, 
                                        image = single_image,
                                        output_folder = output_folder, 
                                        sigma_range = None, 
                                        pre_cal = False)

        else:
            self.master.ImageAnalysisPortionLogger.info(f"""Simple Denoising channel {channel_list}: 
                                                                image folder = {image_folder}, 
                                                                output folder = {output_folder}""")
            self.denoiser.simple_denoise(image_folder = image_folder, 
                                        channel_list = channel_list, 
                                        output_folder = output_folder, 
                                        sigma_range = None, 
                                        pre_cal = False)
            warning_window("Simple Denoising complete!")
            self.destroy()


class CellPoseDenoiseWindow(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    This coordinates and executes a Cellpose Denoising model.    
    '''
    def __init__(self, master):
        super().__init__(master)
        self.title("Cellpose Denoising Options:")
        self.master = master
        self.denoiser = self.master.Experiment_object
        
        ###### A bank of buttons:
        label = ctk.CTkLabel(self, text = "Cellpose Denoising options:")
        label.grid(column = 0,row = 0, padx = 5, pady = 5)

        label_1 = ctk.CTkLabel(self, text = "Choose a Cellpose Denoise/Deblur/Upsample Model:")
        label_1.grid(column = 0, row = 1)

        denoise_model_list = ['denoise_cyto3', 'deblur_cyto3', 'upsample_cyto3', 'denoise_nuclei', 'deblur_nuclei', 'upsample_nuclei']   
                                                        ## may want to remove the upsampling ability (?)
        self.model_type = ctk.CTkOptionMenu(self, values = denoise_model_list, variable = ctk.StringVar(value = "denoise_cyto3"))
        self.model_type.grid(column = 1, row = 1, padx = 5, pady = 5)

        label_2 = ctk.CTkLabel(self, text = "Select an average object Diameter (pixels). \n Select 0 to try auto-estimation of this parameter:")
        label_2.grid(column = 0, row = 2)

        self.avg_diamter = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "30.0"))
        self.avg_diamter.grid(column = 1, row = 2, padx = 5, pady =5)
        
        label_4 = ctk.CTkLabel(self, text = "Select channels to denoise:")
        label_4.grid(column = 0, row = 3)

        self.channels = self.channel_lister(self)
        self.channels.grid(column = 0, row = 4)

        label_8 = ctk.CTkLabel(self, text = "Select an image folder that will be denoised:")
        label_8.grid(column = 0, row = 5)

        def refresh5(enter = ""):
            self.image_folders = [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir)) if i.find(".") == -1]
            self.image_folder.configure(values = self.image_folders)

        self.image_folder = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "img"))
        self.image_folder.grid(column = 1, row = 5, padx = 5, pady = 5)
        self.image_folder.bind("<Enter>", refresh5)

        label8b = ctk.CTkLabel(self, text = "Select an individual image to denoise \n (or leave blank to denoise all):")
        label8b.grid(column = 0, row = 6)

        def refresh5c(enter = ""):
            self.images = [""] + [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir + "/" + self.image_folder.get())) if i.lower().find(".tif") != -1]
            self.single_image.configure(values = self.images)

        self.single_image = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = ""))
        self.single_image.grid(column = 1, row = 6, padx = 5, pady = 5)
        self.single_image.bind("<Enter>", refresh5c)

        label_9 = ctk.CTkLabel(self, 
                               text = "Name the output folder: \n (note that naming ouput == input folder will \n cause overwriting behaviour!)")
        label_9.grid(column = 0, row = 7)

        self.output_folder = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "Denoised_images_1"))
        self.output_folder.grid(column = 1, row = 7, padx = 5, pady = 5)

        self.gpu = ctk.CTkCheckBox(master = self, text = "Use GPU", onvalue = True, offvalue = False)
        self.gpu.grid(column = 0, row = 9, padx = 5, pady = 5)

        button_run_clustering = ctk.CTkButton(self,
                                            text = "Run Denoising", 
                                            command = lambda: self.run_denoise(self.denoiser,
                                                                               self.model_type.get(), 
                                                                               self.avg_diamter.get(),
                                                                               self.channels.retrieve(),
                                                                               self.image_folder.get(),
                                                                               self.output_folder.get().strip(),
                                                                               gpu = self.gpu.get()))
        button_run_clustering.grid(column = 1, row = 8, padx = 5, pady = 5)
        self.after(200, lambda: self.focus())

    def run_denoise(self, 
                    cellposer, 
                    model_type: str, 
                    diam_mean: float, 
                    channel_list: list[int], 
                    image_folder: str, 
                    output_folder: str, 
                    gpu: bool = False,
                    ) -> None:
        '''
        '''
        if len(channel_list) == 0:
            tk.messagebox.showwarning("Warning!", 
                    message = "No Channel to denoise was selected!")
            self.focus()
            return
        img = self.single_image.get()
        if folder_checker(output_folder, self):
            return
        image_folder = self.master.Experiment_object.directory_object.img_dir + "/" + image_folder
        if output_folder == "img":
            tk.messagebox.showwarning("Warning!", 
                    message = "Overwriting the original image folder (img) with denoised files is not allowed")
            self.focus()
            return
        output_folder = self.master.Experiment_object.directory_object.img_dir + "/" + output_folder
        try:
            diam_mean = float(diam_mean)
        except ValueError:
            tk.messagebox.showwarning("Average object diameter must be a number, but a number was not provided!")
            self.focus()
            return 
        if not overwrite_approval(output_folder, 
                                  file_or_folder = "folder", 
                                  GUI_object = self):
            return           
        self.master.ImageAnalysisPortionLogger.info(f"Running Cellpose Denoising with gpu = {gpu}, \n" 
                                                    f"model_type = {model_type}, \n"
                                                    f"diam_mean = {diam_mean}, \n"
                                                    f"and channel_list = {''.join([str(i) for i in channel_list])}"
                                                    f"image_folder = {image_folder}"
                                                    f"output_folder = {output_folder}"
                                                    f"img = {img}")
        cellposer.cellpose_denoise(channel_list, 
                                   image_folder, 
                                   output_folder, 
                                   img = img, 
                                   gpu = gpu, 
                                   model_type = model_type, 
                                   diam_mean = diam_mean)
        self.master.dir_disp.list_dir()
        if img == "":
            warning_window("Cellpose Denoising is Complete!")
            self.withdraw()

    class channel_lister (ctk.CTkScrollableFrame):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.configure(width = 300)
            df = self.master.master.Experiment_object.panel[self.master.master.Experiment_object.panel["keep"] == 1]["name"].reset_index()

            channel_name = list(df["name"])
            channel_number = list(df.index)
            counter = 0
            self.checkbox_list = []
            for i,ii in zip(channel_name, channel_number):
                length = len(i)
                middle = length // 2
                if length > 20:
                    label = ctk.CTkLabel(master = self, text = i[:middle] + "\n" + i[middle:], width = 150)
                    label.grid(column = 0, row = counter, pady = 5, padx = 5)
                else:
                    label = ctk.CTkLabel(master = self, text = i, width = 150)
                    label.grid(column = 0, row = counter, pady = 5, padx = 5)
                label2 = ctk.CTkLabel(master = self, text = ii)
                label2.grid(column = 1, row = counter, pady = 5, padx = 5)
            
                checkbox = ctk.CTkCheckBox(master = self, text = "", onvalue = ii, offvalue = False)
                checkbox.grid(column = 2, row = counter, pady = 5, padx = 5)
                self.checkbox_list.append(checkbox)
                counter += 1

        def retrieve(self) -> list[int]:
            checkbox_output = [i.get() for i in self.checkbox_list if i.get() is not False]
            return checkbox_output

class CellPoseSegmentationWindow(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    This coordinates and executes Cellpose segmentation
    '''
    def __init__(self, master):
        super().__init__(master)
        self.title("Cellpose Segmentation Options:")
        self.master = master
        self.segmentor = self.master.Experiment_object
        
        ###### A bank of buttons:
        label = ctk.CTkLabel(self, text = "Cellpose Segmentation options:")
        label.grid(column = 0,row = 0, padx = 5, pady = 5)

        label_1 = ctk.CTkLabel(self, text = "Choose a Cellpose Segmentation Model:")
        label_1.grid(column = 0, row = 1)

        segmentation_model_list = ["cyto3", 
                                   "nuclei", 
                                   "cyto2_cp3", 
                                   "tissuenet_cp3", 
                                   "livecell_cp3", 
                                   "yeast_PhC_cp3",
                                   "yeast_BF_cp3", 
                                   "bact_phase_cp3", 
                                   "bact_fluor_cp3", 
                                   "deepbacs_cp3", 
                                   "cyto2", 
                                   "cyto",
                                   "transformer_cp3", 
                                   "neurips_cellpose_default", 
                                   "neurips_cellpose_transformer",
                                   "neurips_grayscale_cyto2"]        
                        ###### This is the full list copied from cellpose --> some can likely be dropped (they are for bacteria, etc.... --> 
                        # although IMC could be done on those as well, theoretically)
        
        self.model_type = ctk.CTkOptionMenu(self, values = segmentation_model_list, variable = ctk.StringVar(value = "cyto3"))
        self.model_type.grid(column = 1, row = 1, padx = 5, pady = 5)

        label_2 = ctk.CTkLabel(self, text = "Select object Diameter (higher number = smaller objects):")
        label_2.grid(column = 0, row = 2)

        self.avg_diamter = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "30.0"))
        self.avg_diamter.grid(column = 1, row = 2, padx = 5, pady = 5)

        label_3 = ctk.CTkLabel(self, text = "Object error threshold (higher numbers reduce number of objects):")
        label_3.grid(column = 0, row = 3)

        self.error_thresh = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "0.4"))
        self.error_thresh.grid(column = 1, row = 3, padx = 5, pady = 5)

        label_4 = ctk.CTkLabel(self, text = "Masks probability threshold (higher numbers shrink mask size):")
        label_4.grid(column = 0, row = 4)

        self.prob_thresh = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "0.0"))
        self.prob_thresh.grid(column = 1, row = 4, padx = 5, pady = 5)

        label_5 = ctk.CTkLabel(self, text = "Minimum Size of objects (in number of pixels):")
        label_5.grid(column = 0, row = 5)

        self.min_diameter = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = "15"))
        self.min_diameter.grid(column = 1, row = 5, padx = 5, pady = 5)

        label_8 = ctk.CTkLabel(self, text = "Select an image folder from which to source images for masking:")
        label_8.grid(column = 0, row = 6)

        def refresh6(enter = ""):
            self.image_folders = [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir)) if i.find(".") == -1]
            self.image_folder.configure(values = self.image_folders)
        self.image_folder = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "img"))
        self.image_folder.grid(column = 1, row = 6, padx = 5, pady = 5)
        self.image_folder.bind("<Enter>", refresh6)

        label_6 = ctk.CTkLabel(self, text = "Select an image to segment, or segment ALL:")
        label_6.grid(column = 0, row = 7)

        def refresh7(enter = ""):
            self.image_options = ["ALL"] + [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir +"/" + self.image_folder.get())) if i.lower().find(".tif") != -1]
            self.image_to_segment.configure(values = self.image_options)

        self.image_to_segment = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "ALL"))
        self.image_to_segment.grid(column = 1, row = 7, padx = 5, pady = 5)
        self.image_to_segment.bind("<Enter>", refresh7)

        label_7 = ctk.CTkLabel(self, 
                               text = "(When running ALL) Leave checked to redo any prior masks \n"
                                      "Unchecked to only segment previously unsegmented files:")
        label_7.grid(column = 0, row = 9)   

        self.re_do = ctk.CTkCheckBox(master = self, text = "", onvalue = True, offvalue = False)
        self.re_do.grid(column = 1, row = 9, padx = 5, pady = 5)
        self.re_do.select()

        self.gpu = ctk.CTkCheckBox(master = self, text = "Run with GPU", onvalue = True, offvalue = False)
        self.gpu.grid(column = 0, row = 11, padx = 5, pady = 5)

        button_run_clustering = ctk.CTkButton(self,
                                            text = "Run Segmentation", 
                                            command = lambda: self.run_segmentation(self.segmentor,
                                                                               self.model_type.get(), 
                                                                               self.avg_diamter.get(),
                                                                               self.error_thresh.get(),
                                                                               self.prob_thresh.get(),
                                                                               self.min_diameter.get(),
                                                                               self.image_to_segment.get(),
                                                                               self.re_do.get(),
                                                                               image_folder = self.image_folder.get(),
                                                                               gpu = self.gpu.get()))
        button_run_clustering.grid(column = 1, row = 10, padx = 5, pady = 5)

        self.after(200, lambda: self.focus())

    def run_segmentation(self,  
                         cellposer, 
                         model_type: str, 
                         diam_mean: float, 
                         flow_threshold: float, 
                         cellprob_threshold: float, 
                         min_size: int, 
                         image: str, 
                         re_do: bool, 
                         image_folder: Union[None, str] = None, 
                         output_folder: Union[None, str] = None,  
                         gpu: bool = False,
                         ) -> None:
        '''
        '''
        image_folder = self.master.Experiment_object.directory_object.img_dir + "/" + image_folder   
                            ## full folder path, not only the name of the folder inside the img dir
        if output_folder is None:
            output_folder = self.master.Experiment_object.directory_object.masks_dir + "/cellpose_masks"   
                                
        try:
            diam_mean = float(diam_mean)
            flow_threshold = float(flow_threshold)
            cellprob_threshold = float(cellprob_threshold)
            min_size = int(min_size)
        except ValueError:
            tk.messagebox.showwarning("Warning!", 
                    message = "Average object diameter, minimum diameter, error threshold, and & probability threshold must all be numbers,"
                    " but a number was not provided for one of these parameters!")
            self.focus()
            return
        if not overwrite_approval(output_folder, file_or_folder = "folder", GUI_object = self):
            return
        self.master.ImageAnalysisPortionLogger.info(f"Segmenting with cellpose using gpu = {gpu}, \n"
                                                    f"model_type = {model_type}, \n"
                                                    f"diam_mean = {diam_mean}, \n"
                                                    f"flow_threshold = {flow_threshold}, \n"
                                                    f"cellprob_threshold = {cellprob_threshold}, \n"
                                                    f"min_size = {min_size}, \n"
                                                    f"image = {image}, \n"
                                                    f"image_folder = {image_folder}")
        #import time
        #start = time.time()
        if image == "ALL":
            cellposer.cellpose_segment(image_folder, 
                              output_folder, 
                              flow_threshold = flow_threshold, 
                              cellprob_threshold = cellprob_threshold, 
                              min_size = min_size, 
                              re_do = re_do,
                              gpu = gpu, 
                                model_type = model_type, 
                                diam_mean = diam_mean)
        else:
            cellposer.cellpose_segment(image_folder, 
                              output_folder, 
                              img = image, 
                              flow_threshold = flow_threshold, 
                              cellprob_threshold = cellprob_threshold, 
                              min_size = min_size, 
                              re_do = re_do,
                              gpu = gpu, 
                            model_type = model_type, 
                            diam_mean = diam_mean)
        #print(time.time() - start)      

        self.master.buttonframe.initialize_buttons()
        self.master.dir_disp.list_dir()
        if image == "ALL":
            self.withdraw()

class DeepCell_window(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    This coordinates and executes Deepcell segmentation 
    '''
    def __init__(self, master):
        super().__init__(master)
        self.title("DeepCell Segmentation Options:")
        self.master = master
        
        ###### A bank of buttons:
        label = ctk.CTkLabel(self, text = "DeepCell Segmentation options:")
        label.grid(column = 0,row = 0, padx = 5, pady = 5)
        
        label_2 = ctk.CTkLabel(self, text = "Select an image folder from which to source images for masking:")
        label_2.grid(column = 0, row = 1)


        def refresh8(enter = ""):
            self.image_folders = [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir)) if i.find(".") == -1]
            self.image_folder.configure(values = self.image_folders)

        self.image_folder = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "img"))
        self.image_folder.grid(column = 1, row = 1, padx = 5, pady = 5)
        self.image_folder.bind("<Enter>", refresh8)

        label_6 = ctk.CTkLabel(self, text = "Select an image to segment, or segment ALL:")
        label_6.grid(column = 0, row = 2)

        def refresh9(enter = ""):
            self.image_options = ["ALL"] + [i for i in sorted(os.listdir(self.master.Experiment_object.directory_object.img_dir + "/" + self.image_folder.get())) if i.lower().find(".tif") != -1]
            self.image_to_segment.configure(values = self.image_options)

        self.image_to_segment = ctk.CTkOptionMenu(self, values = [""], variable = ctk.StringVar(value = "ALL"))
        self.image_to_segment.grid(column = 1, row = 2, padx = 5, pady = 5)
        self.image_to_segment.bind("<Enter>", refresh9)

        label_7 = ctk.CTkLabel(self, 
                text = "(When running ALL) Check to redo any prior masks \n Leave unchecked to only segment previously unsegmented files:")
        label_7.grid(column = 0, row = 4)   

        self.re_do = ctk.CTkCheckBox(master = self, text = "", onvalue = True, offvalue = False)
        self.re_do.grid(column = 1, row = 4, padx = 5, pady = 5)

        button_run_segmentation = ctk.CTkButton(self,
                                    text = "Run Segmentation", 
                                    command = lambda: self.run_segmentation(self.image_to_segment.get(), 
                                                image_folder = (self.master.Experiment_object.directory_object.img_dir + "/" + self.image_folder.get())
                                                ))
        button_run_segmentation.grid(column = 1, row = 5, padx = 5, pady = 5)

        self.after(200, lambda: self.focus())

    def run_segmentation(self, 
                         image: str, 
                         image_folder: Union[None, str] = None, 
                         output_folder: Union[None, str] = None,
                         ) -> None:
        '''
        '''
        #import time
        #start = time.time()
        if output_folder is None: 
            output_folder = self.master.Experiment_object.directory_object.masks_dir + "/deepcell_masks"
        if not overwrite_approval(output_folder, file_or_folder = "folder", GUI_object = self):
            return
        if image != "ALL":
            image = image[:image.rfind(".")]
        self.master.ImageAnalysisPortionLogger.info(f"Segmenting with DeepCell using image = {image}")
        self.master.run_deepcell(image, re_do = self.re_do.get(), image_folder = image_folder, output_folder = output_folder)
        self.master.dir_disp.list_dir()

        if image == "ALL":
            warning_window("Deepcell Segmentation is complete!")
            self.withdraw()

        #print(time.time() - start)






