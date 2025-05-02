'''
This module handles the widgets on the first page of PalmettoBUG that deal with entering an IMC directory.
'''

import os
from typing import Union
import tkinter as tk
from tkinter import messagebox        
             ## why this is unecessary for palmettobug, but needed here is a mystery
            ## helpful discussion for resolving this:
            #    https://stackoverflow.com/questions/29774938/tkinter-messagebox-showinfo-doesnt-always-work  (TigerHawkT3 & jonrsharpe answers)
            ## or this discussion: 
            #   https://stackoverflow.com/questions/56268474/why-do-i-need-to-import-tkinter-messagebox-but-dont-need-to-import-tkinter-tk

import customtkinter as ctk
import pandas as pd

from .sharedClasses import Project_logger, CtkSingletonWindow, DirectoryDisplay
from .processing_class import toggle_in_gui, imc_entrypoint
from .processing_GUI import ImageProcessingWidgets 

__all__ = []

homedir = __file__.replace("\\","/")
homedir = homedir[:(homedir.rfind("/"))]
Theme_link = homedir + '/Assets/theme.txt'

chosen_dir_file = homedir + "/Assets/dir_choice.txt"
with open(chosen_dir_file) as file:
    chosen_dir = file.read()
if chosen_dir == 'None"' :
    chosen_dir = homedir[:(homedir.find("/")) + 1]

class App(ctk.CTk):
    '''
    This is the main window for the GUI. It also contains the Tabholder class, which coordinates the tabs of the program
    '''
    def __init__(self, directory: Union[None, str] = None, resolutions: Union[None, tuple[float, float]] = None) -> None:
        super().__init__()
        self.light_dark = "dark"
        toggle_in_gui()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")   
        ### The 1200 by 1920 ratio is from the computer I was using to develop this program:
        dev_comp_height = 1200
        dev_comp_width = 1920
        with open(Theme_link) as theme:
            self.theme = theme.read()
        if len(self.theme) == 0:
            self.theme = "blue"   ## this is the default theme for ctk
        elif (self.theme == "green") or (self.theme == "blue"):
            ctk.set_default_color_theme(self.theme)       ## green and blue are themes bundled with customtkinter (don't require a link)
        else:
            theme_dir = homedir +  "/Assets/ctkThemeBuilderThemes/"
            ctk.set_default_color_theme(theme_dir + self.theme + ".json")

        instance_height = self.winfo_screenheight()
        instance_width = self.winfo_screenwidth()
        ratio_height = instance_height / dev_comp_height
        ratio_width = instance_width / dev_comp_width
        self.ratio = min(ratio_height,ratio_width)
        self.scaling = 1.1
        ctk.set_widget_scaling(self.ratio * 1.1)
        ctk.set_window_scaling(self.ratio * 1.1)

        self.geometry("1200x875+0+0")
        self.resizable(True,True)
        self.title("Segmentation and Denoising: Deepcell and Cellpose")

        self.Tabs = self.Tabholder(self, directory = True)
        self.entrypoint = EntryPoint(self.Tabs)
        self.entrypoint.grid(row = 0, column = 0, padx = 10, pady = 10)

        if directory is not None:
            file_list = [i for i in os.listdir(directory + "/raw") if ((i.lower().find(".mcd") != -1) or (i.lower().find(".tif") != -1))]
            if file_list[0][-1] == "f":    ## aka, tiff or tif files...
                self.entrypoint.img_entry_func(directory = directory, resolutions = resolutions, from_mcds = False)
            else:
                self.entrypoint.img_entry_func(directory = directory, resolutions = resolutions, from_mcds = True)

    def re__init__(self) -> None:
        '''Used in changing the appearance of the GUI, as sometimes widgets must be re-made to update'''
        self.Tabs.destroy()
        self.Tabs = self.Tabholder(self)

        self.entrypoint.destroy()
        self.entrypoint = EntryPoint(self.Tabs)
        self.entrypoint.grid(row = 0, column = 0, padx = 10, pady = 10)

    class Tabholder(ctk.CTkTabview):
        '''This class holds the tabs of the GUI'''
        def __init__(self, master, directory = False):
            super().__init__(master)
            self.start = self.add('Start')
            self.start.directory = None

            self.mcdprocessing = self.add('Segmentation & Denoising')

            self.configure(width = 1050, height = 700)
            self.grid(row = 0, column = 0)

            self.image_proc_widg = None
            if not directory:
                self.image_proc_widg = ImageProcessingWidgets(self.mcdprocessing)
                self.image_proc_widg.grid()
                self.set('Start')

class EntryPoint(ctk.CTkFrame):
    '''
    This is the initial frame that helps the user provide the directory for data ingestion.

    It can always be returned to by the user to re-start the data ingestion / processing. 
    '''
    def __init__(self, Tabholder: App.Tabholder):
        super().__init__(Tabholder.start)
        self.master = Tabholder   ##### so: self.master.master  == the main App
        self.directory = None
        self.image_proc_widg = self.master.image_proc_widg
        self.configure(height = 400, width = 1050)

        ## widget set for the MCD entry point
        label = ctk.CTkLabel(master = self, 
                             text = "Directory structure requirements:" 
                                    "\n\n 1). The folder should contain a panel.csv file, in the format of PalmettoBUG"
                                    "\n\n 2). The folder should contain an /images subfolder, which in turns should have"
                                     "\n at least 1 sub-folder with all images of the dataset in it in the form of"
                                     "\n .tiff files (usually /images/img, from PalmettoBUG).")

        label.grid(column = 0, row = 0, padx = 10, pady = 10, rowspan = 4)
        label.configure(anchor = "w")

        button_MCD = ctk.CTkButton(master = self, 
                                   text = "Choose directory and begin", 
                                   command = lambda: self.img_entry_func("", from_mcds = True))
        button_MCD.grid(column = 1, row = 1, padx = 10, pady = 10)

        ## The widget for the entry of the resolution of the images (can ignore for CyTOF / solution mode analyses)
        self.X_Y_entry = self.X_Y_res_frame(self)
        self.X_Y_entry.grid(column = 1, row = 4, padx = 10, pady = 10)

        #label_dir_disp = ctk.CTkLabel(master = self, text = "Alternatively, select the folder \n using the directory display below:")
        #label_dir_disp.grid(column = 0, row = 5, padx = 10, pady = 10)

        self.dir_disp = DirectoryDisplay(self)
        self.dir_disp.grid(column = 0, row = 6, padx = 3, pady = 3, rowspan = 4)
        try:
            self.dir_disp.setup_with_dir(chosen_dir) 
        except FileNotFoundError:
            root_dir = homedir[:(homedir.find("/")) + 1]
            self.dir_disp.setup_with_dir(root_dir)

        self.dir_helper = directory_display_helper_frame(self, self.dir_disp)
        #self.dir_helper.grid(column = 0, row = 10, padx = 3, pady = 10, rowspan = 3)

        buttonConfig = ctk.CTkButton(master = self, text = "Launch GUI configuration window", command = self.call_configGUI)
        buttonConfig.grid(column = 3, row = 1, padx = 10, pady = 10)
        buttonConfig.configure(anchor = "e")

        def show_License():
            License_window(self)
        button_baby = ctk.CTkButton(master = self, text = "See LICENSE Details", command = show_License)
        button_baby.grid(column = 3, row = 2, padx = 10, pady = 10) 
  
        self.after(200, lambda: self.focus())

    def call_configGUI(self) -> None:
        configGUI_window(self.master.master)

    class X_Y_res_frame(ctk.CTkFrame):
        '''
        The widget frame containing the entries for the X & Y resolutions of the images
        '''
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            label = ctk.CTkLabel(master = self, text = "Enter X and Y resolution (in micrometers): \n X       Y")
            label.grid(column = 0, row = 0, columnspan = 2, padx = 10, pady = 10)
            
            self.entry_X = ctk.CTkEntry(master = self, textvariable = ctk.StringVar(value = "1.0"))
            self.entry_X.grid(column = 0, row = 1, padx = 10, pady = 10)

            self.entry_Y = ctk.CTkEntry(master = self, textvariable = ctk.StringVar(value = "1.0"))
            self.entry_Y.grid(column = 1, row = 1, padx = 10, pady = 10)

    def img_entry_func(self, directory: str = None, resolutions = None, from_mcds = True) -> None:
        '''
        This function directs the directory (and resolutions) into an experiment -- with MCD initial read-in -- 
        and sets up the Image processing Widgets 
        '''
        if resolutions is None:
            try:
                resX = float(self.X_Y_entry.entry_X.get())
                resY = float(self.X_Y_entry.entry_Y.get())
            except ValueError:
                messagebox.showwarning("Warning!", message = "Resolution X / Y must be numbers!")
                return
        else:
            resX = resolutions[0]
            resY = resolutions[1]
        
              
        ### don't want the current directory to be searched (when entry field is blank)....
        if directory is None:
            directory = "not a directory"   
                    ## if the directory remains None, odd behaviours can result because of default arguments in downstream functions ---> 
                    #           like the current directory being searched
        if len(directory) == 0:
            directory = tk.filedialog.askdirectory()   
        directory = directory.replace("\\","/")
        try:
            try:
                pd.read_csv(directory + "/panel.csv")
            except FileNotFoundError:
                messagebox.showwarning("Warning!", message = "There is no panel.csv!")
                return
            image_folder_list = [i for i in os.listdir(directory + "/images") if i.find(".") == -1]
            if len(image_folder_list) == 0:
                messagebox.showwarning("Warning!", message = "There are no images subfolders -- there will be no data to work with in this directory!")
                return
        except FileNotFoundError:
            messagebox.showwarning("Warning!", message = "This is not a valid directory!")
            return

        ## setup experiment & directory:
        Experiment = imc_entrypoint(directory = directory, resolutions = [resX, resY], from_mcds = from_mcds)
        ## set up project logger once setup is "successful":
        project_log = Project_logger(directory).return_log()
        project_log.info(f"Start log in directory {directory}/Logs after loading from MCD files")

        ## this removes any old widgets of a previously entered  MCD directory:
        if self.image_proc_widg is not None:
            self.image_proc_widg.destroy()
            self.image_proc_widg = ImageProcessingWidgets(self.master.mcdprocessing)
            self.image_proc_widg.grid(column = 0, row = 0)
        else:
            self.image_proc_widg = ImageProcessingWidgets(self.master.mcdprocessing)
            self.image_proc_widg.grid(column = 0, row = 0)

        self.image_proc_widg.add_Experiment(Experiment, from_mcds = from_mcds)

        # Initialize the image processing widgets:                 
        self.image_proc_widg.initialize_buttons(directory) 
        self.master.set('Segmentation & Denoising')

class directory_display_helper_frame(ctk.CTkFrame):
    '''
    This provides an alternate way of selecting a directory (perhaps deprecate & remove?)
    '''
    def __init__(self, master, dir_disp):
        super().__init__(master)
        self.master = master

        self.dir_disp = dir_disp

        label = ctk.CTkLabel(master = self, text = "Working Directory:")
        label.grid(column = 0, row = 0, pady = 3)

        self.directory = ctk.StringVar(value = self.dir_disp.currentdir)

        self.directory_entry = ctk.CTkEntry(master = self, textvariable = self.directory, width = 360)
        self.directory_entry.grid(column = 0, columnspan = 2, row = 1, pady = 3)

        self.dir_disp.bind("<Enter>", lambda enter:  self.get_current_directory()) 
                 ## helpful video that helped get started with events:
                 #           https://www.youtube.com/watch?v=8mZ9lZlsDHY&list=PLpMixYKO4EXeaGnqT_YWx7_mA77bz2VqM&index=9

        button2 = ctk.CTkButton(master = self, text = "Save working directory as default", command = self.set_as_home_directory)
        button2.grid(column = 1, row = 3, pady = 3)

        label2 = ctk.CTkLabel(master = self, text = "Launch from Directory Display Options:")
        label2.grid(column = 0, row = 4, columnspan = 2, pady = 3)

        self.frame = ctk.CTkFrame(master = self)
        self.frame.grid(column = 0, row = 5, columnspan = 2, pady = 3)

        self.launch_selection = ctk.StringVar(value = "mcd")
        radio1 = ctk.CTkRadioButton(master = self.frame, text = "from MCD files", variable = self.launch_selection, value = "mcd")
        radio1.grid(row = 0, column = 0, padx = 1, pady = 1)

        radio2 = ctk.CTkRadioButton(master = self.frame, text = "from .tiff files", variable = self.launch_selection, value = "tiff")
        radio2.grid(row = 0, column = 1, padx = 1, pady = 1)

        radio3 = ctk.CTkRadioButton(master = self.frame, text = "from .fcs files", variable = self.launch_selection, value = "fcs")
        radio3.grid(row = 0, column = 2, padx = 1, pady = 1)

        button3 = ctk.CTkButton(master = self, text = "Launch Analysis from working directory", command = self.entry_from_dir_disp)
        button3.grid(column = 1, row = 6, pady = 3) 

    def entry_from_dir_disp(self) -> None:
        directory = self.directory_entry.get().strip()
        launch_selection = self.launch_selection.get()
        if launch_selection == "mcd":
            self.master.img_entry_func(directory = directory, from_mcds = True)
        elif launch_selection == "tiff":
            self.master.img_entry_func(directory = directory, from_mcds = False)
        elif launch_selection == "fcs":
            self.master.FCS_choice(directory = directory)

    def get_current_directory(self) -> None:
        directory = self.dir_disp.currentdir
        self.directory.set(directory)

    def set_as_home_directory(self) -> None:
        directory = self.directory.get()
        if directory != "None":
            try:
                os.listdir(directory)
            except FileNotFoundError:
                messagebox.showwarning("Warning!", message = "This is not a valid directory to save!")
                return
        with open(chosen_dir_file, mode = 'w') as file:
            file.write(directory)
        self.dir_disp.setup_with_dir(directory)

class License_window(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    Displays License of project & acknowledges critical dependencies / packages that were built on by the project
    '''
    def __init__(self, master):
        super().__init__(master)
        license_dir = homedir + "/Assets/LICENSE_files/LICENSE-BSD-primary.txt"
        with open(license_dir) as file:
            license = file.read()

        label = ctk.CTkLabel(master = self, text = """Copyright Medical University of South Carolina 2024-2025   (BSD-3 license)
                             
                    While this project is licensed as BSD-3,
                    Much of this project is also heavily based on / derived from a number of existing open-source packages:
                        \t Steinbock (https://github.com/BodenmillerGroup/steinbock, MIT license): much of MCD and Image processing, project directory structure, steinbock_for_deepcell_alone.py file
                        \t singletons (https://github.com/jmaroeder/python-singletons, MIT): Utils/shared_classes, for windows and loggers
                        \t scikit-image (https://github.com/scikit-image/scikit-image, BSD-3): simple denoising uses techniques discussed in skimage documentation
                        \t ctk_theme_builder (https://github.com/avalon60/ctk_theme_builder, MIT): many of the pre-made GUI themes
                        \t apeer-ometiff-library (https://github.com/apeer-micro/apeer-ometiff-library, MIT and BSD3): in the vendors sub-folder of the package. Handles reading/writing .ome.tiff files
                        \t 
                        \t deepcell-tf and deepcel-toolbox (https://github.com/vanvalenlab/deepcell-tf and https://github.com/vanvalenlab/deepcell-toolbox, modified Apache2.0, non-commercial / academic-only): 
                        \t                       vendors/_deepcell.py & _vendorss/mesmer.onnx, DeepCell / Mesmer segmentation modle and code
                    The listed packages are noted because of their use beyond merely importation / use of API / use of documentation files for the many library dependencies of this project,
                    and because of their extensive use in different parts of the program. See individual .py files for details & any other packages that parts of the program may have derived from.
            
                    For full copyright notices (authors, dates) find the LICENSE files in isosegdenoise/Assets/LICENSE_files, or look at individual python files

                    Also, note that the deepcell / Mesmer models are licensed for "non-commercial" use only, and the main cellpose models were trained on "non-commercial" 
                    datasets. These do not affect the licensing of isosegdenoise code itself, they affect how you can legally use the models isosegdenoise connects to.  
            """, 
            anchor = 'w', justify = 'left')
        
        label.grid(pady = 10, padx = 10, column = 0, row = 0, columnspan = 2)

        display = ctk.CTkTextbox(master = self, activate_scrollbars = True, wrap = 'none', width = 700, height = 450)
        display.grid(column = 0, row = 1)

        display.insert("0.0", license)
        display.configure(state = "disabled")

        self.after(200, lambda: self.focus())

class configGUI_window(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    Alter the GUI appearance within this window
    '''
    def __init__(self, App_instance: App):
        super().__init__()
        from pathlib import Path
        self.master = App_instance
        self.lt_drk = App_instance.light_dark

        label = ctk.CTkLabel(master = self, text = "Make changes to the GUI appearance:")
        label.grid(padx = 5, pady = 5)

        label1 = ctk.CTkLabel(master = self, text = "Select a Ratio to change the sizes of the widgets & window:")
        label1.grid(padx = 5, pady = 5)

        self.slider = ctk.CTkComboBox(master = self, 
                                      values = ["0.85","0.9","0.95","1.0","1.05","1.1","1.15","1.2","1.25","1.3"], 
                                      command = self.slider_moved)
        self.slider.grid(padx = 5, pady = 5)
        self.slider.set(App_instance.scaling)

        self.theme_dir = homedir +  "/Assets/ctkThemeBuilderThemes"
        to_display = [str(i).replace(".json","").replace("\\","/") for i in Path(self.theme_dir).rglob("[!.]*.json")]
        to_display = ["green","blue"] + [i[(i.rfind("/") + 1):] for i in to_display] 

        label2 = ctk.CTkLabel(master = self, text = "Change the color theme (note this may reset unsaved progress in an analysis):")
        label2.grid(padx = 5, pady = 5)

        self.combobox = ctk.CTkComboBox(master = self, values = to_display, command = self.change_theme)
        self.combobox.grid(padx = 5, pady = 5)
        self.combobox.set(App_instance.theme)

        self.light_dark = ctk.CTkButton(master = self, text = "Toggle theme light / dark", command = self.toggle_light_dark)
        self.light_dark.grid(padx = 5, pady = 5)

        self.after(200, lambda: self.focus())

    def re__init__(self) -> None:
        Appinstance = self.master
        self.destroy()
        configGUI_window(Appinstance)
    
    def toggle_light_dark(self) -> None:
        if self.master.light_dark == "dark":
            ctk.set_appearance_mode("light")
            self.master.light_dark = "light"
        elif self.master.light_dark == "light":
            ctk.set_appearance_mode("dark")
            self.master.light_dark = "dark"
        self.after(200, lambda: self.focus())

    def slider_moved(self, scaling: float) -> None:
        scaling = float(scaling)
        ctk.set_widget_scaling(self.master.ratio * scaling)
        ctk.set_window_scaling(self.master.ratio * scaling)
        self.master.scaling = scaling

    def change_theme(self, new_theme: str) -> None:
        if new_theme in ["green", "blue"]:
            ctk.set_default_color_theme(new_theme) 
        else:
            ctk.set_default_color_theme(self.theme_dir + f"/{new_theme}.json") 
        with open(Theme_link, mode = 'w') as theme:
            theme.write(new_theme)
        self.master.theme = new_theme
        self.master.re__init__()
        self.re__init__()
