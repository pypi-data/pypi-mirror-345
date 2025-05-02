'''
This module contains utility / shared classes that may be used by multiple other modules in isoSegDenoise.
This includes classes that handle directory setup, logging, and table entry. 

Some of the code in this file is derived 

singleton package: https://github.com/jmaroeder/python-singletons/blob/master/src/singletons/singleton.py  (Copyright (c) 2019, James Roeder, MIT License)

Directory structures (but not code) derived from:
steinbock package: https://github.com/BodenmillerGroup/steinbock (Copyright (c) 2021 University of Zurich, MIT license)

MIT license (from steinbock, for steinbock derived portions):

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

import os
import logging
from typing import Union
import re
import threading
from multiprocessing import Process
import tkinter as tk

import tifffile as tf
import customtkinter as ctk
import pandas as pd
import numpy as np
import napari

__all__ = []

homedir = __file__.replace("\\","/")
homedir = homedir[:(homedir.rfind("/"))]

def filename_checker(filename: str, 
                     regex: str = "[a-zA-Z0-9-_]",
                     ) -> bool:
    '''
    '''
    for i in re.split(regex, filename):    #### splitting by all the lowercase/uppercase letters, numbers, underscore, and dash only 
                                                    # leaves other characters in the list
        if len(i) != 0:                             ### this means a special character was in the filename
            warning_window("An unsupported special character was in your filename! "
                           "Please only use letters, numbers, underscores, or dashes in your filename and plot again.")
            return True   ## if an error occurs trigger an abort of the parent process
    return False  ### else continue

def folder_checker(foldername: str, 
                   GUI_object = None,
                   regex: str = "[a-zA-Z0-9-_]",
                   ) -> bool:
    '''
    '''
    foldername = foldername.strip()
    if foldername == "":
        tk.messagebox.showwarning("Warning!", message = "You must specifiy a folder name!")
        if GUI_object is not None:
            GUI_object.focus()
        return True   ## if an error occurs trigger abort the parent process
    for i in re.split(regex, foldername):    
        if len(i) != 0: 
            tk.messagebox.showwarning("Warning!", 
                message = "An unsupported special character was in your foldername! "
                "Please only use letters, numbers, underscores, or dashes and try again.")
            if GUI_object is not None:
                GUI_object.focus()
            return True   ## if an error occurs trigger an abort of the parent process
    return False  ### else continue

def overwrite_approval(full_path: str, file_or_folder: str = "file", custom_message: str = None, GUI_object = None) -> bool:
    '''
    This function checks if a folder / file exists so that a user-warning & choice that be created before overwriting it.

    Args:
        full_path (string or Path): the file path of the folder / file you are about to write a new folder / file to. Will check if this 
            folder / file already exists, and if it does will prompt the user whether to proceed with overwriting or cancel.

        file_or_folder (string): either "file" or "folder". Customizes the tk.messagebox message.

        custom_message (string or None): if not None, will be used to customize the question asked of the user by the message box

        GUI_object (ctk.CTkToplevel, or None): tk message boxes defocus the current window (at least for customtkinter Toplevel windows) --
            supply the window in this argument to automatically re-focus on that window after the tk messagebox prompt. 

    Specify the GUI_object, if this is called inside a CTkToplevel window and you want that window to be focused after the tkinter
    message box pop-up. 
    '''
    full_path = str(full_path)
    if os.path.exists(full_path):
        file_or_folder = str(file_or_folder)
        has_files = True
        if file_or_folder == "folder":
            has_files = (len(os.listdir(full_path)) > 0)
        overwrite_message = str(custom_message)
        if custom_message is None:
            if file_or_folder == "file":
                overwrite_message = "Are you sure you want to overwrite the existing file?"
            if file_or_folder == "folder":
                overwrite_message = "Are you sure you want to potentially overwrite files in this folder?"
        if has_files:
            response = tk.messagebox.askyesno(title = "Overwrite Warning!", message = f"The {file_or_folder} path: \n\n {full_path} \n\n already exists! {overwrite_message}")
            if GUI_object is not None:
                GUI_object.focus()
            if response:
                return True
            else:
                return False
        else:
            return True
    else:
        return True       ### if the path does not exist, does not contain files (and is a folder), or if the user says "yes", proceed with the step

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
## The following code (between the ~~~~~~~~~~~) was modified from the singleton package: 
#        https://github.com/jmaroeder/python-singletons/blob/master/src/singletons/singleton.py   

# Singleton license (MIT):
# ------------
# Copyright (c) 2019, James Roeder

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# -----------

# Edited 3-28-25 to change noqa lines for ruff
from collections import defaultdict       # noqa: E402
from typing import Any, ClassVar, MutableMapping, Type, TypeVar # noqa: E402
T = TypeVar("T")  

class CtkSingletonWindow(type):
    '''
    ############### 
    This class edited from the singleton package: https://github.com/jmaroeder/python-singletons/blob/master/src/singletons/singleton.py   
                                                                    (originally the singleton.Singleton class)
    Edits needed because of the desire to focus a singleton window when it was "opened" again (accomplished with a ctk call in the singleton class)
    Singleton package copyright / license: Copyright (c) 2019, James Roeder, MIT License
    ############### 
    
    Thread-safe singleton metaclass.

    Ensures that one instance is created.

    Note that if the process is forked before any instances have been accessed, then all processes
    will actually each have their own instances. You may be able to avoid this by instantiating the
    instance before forking.

    Usage::

        >>> class Foo(metaclass=Singleton):
        ...     pass
        >>> a = Foo()
        >>> b = Foo()
        >>> assert a is b

    '''
    __instances: ClassVar[MutableMapping[Type, Any]] = {}
    __locks: ClassVar[MutableMapping[Type, threading.Lock]] = defaultdict(threading.Lock)

    def __call__(cls: Type[T], *args: Any, **kwargs: Any) -> T:  # noqa: D102
        if cls not in CtkSingletonWindow.__instances:
            with CtkSingletonWindow.__locks[cls]:
                if cls not in CtkSingletonWindow.__instances:  # pragma: no branch
                    # double checked locking pattern
                    CtkSingletonWindow.__instances[cls] = super().__call__(*args, **kwargs) 
                    CtkSingletonWindow.__instances[cls].geometry("+10+10")
                    return CtkSingletonWindow.__instances[cls]  
        else:
            try: 
                if CtkSingletonWindow.__instances[cls].state() == "withdrawn":
                    CtkSingletonWindow.__instances[cls].destroy()
                    CtkSingletonWindow.__instances[cls] = super().__call__(*args, **kwargs) 
                    CtkSingletonWindow.__instances[cls].geometry("+0+0")
                    return CtkSingletonWindow.__instances[cls] 

                else:
                    CtkSingletonWindow.__instances[cls].focus()   ## This focuses the window
                    ## This will throw an error if the window has been closed ("tkinter.TclError: bad window path name"), 
                    #                       so if an error occurs in focusing --> just open a new window:
            
            except Exception:
                CtkSingletonWindow.__instances[cls] = super().__call__(*args, **kwargs) 
                CtkSingletonWindow.__instances[cls].geometry("+0+0")
                return CtkSingletonWindow.__instances[cls] 

class LogSemiSingleton(type):
    ''' 
    ##############
    This class edited from the singleton package: https://github.com/jmaroeder/python-singletons/blob/master/src/singletons/singleton.py   (
                                            originally the singleton.Singleton class)
    Edits needed because of the desire to have the option to undo & produce another "singleton" (when [re]loading a new experiment). 
    Hence, it is only a "semi"-singleton. This will make the project log initialized at the entry point carry over to all future project 
    logs (until a new directory is provided to the project log).
    Singleton package copyright / license: Copyright (c) 2019, James Roeder, MIT License
    ##############
    
    Thread-safe singleton metaclass.

    Ensures that one instance is created.

    Note that if the process is forked before any instances have been accessed, then all processes
    will actually each have their own instances. You may be able to avoid this by instantiating the
    instance before forking.

    Usage::

        >>> class Foo(metaclass=Singleton):
        ...     pass
        >>> a = Foo()
        >>> b = Foo()
        >>> assert a is b

    '''
    __instances: ClassVar[MutableMapping[Type, Any]] = {}
    __locks: ClassVar[MutableMapping[Type, threading.Lock]] = defaultdict(threading.Lock)

    def __call__(cls: Type[T], proj_dir = None) -> T:  # noqa: D102
        #### Note: throws an error if proj_dir = None (default) when the Project logger is first called (does not throw an error after 
        # the first call with a directory)
        if (cls not in LogSemiSingleton.__instances) and (proj_dir is not None):
            with LogSemiSingleton.__locks[cls]:
                if cls not in LogSemiSingleton.__instances:  # pragma: no branch
                    # double checked locking pattern
                    LogSemiSingleton.__instances[cls] = super().__call__(proj_dir) 
                    return LogSemiSingleton.__instances[cls]
        elif (LogSemiSingleton.__instances[cls].proj_dir == proj_dir) or (proj_dir is None):    
                    ### same directory or None is passed into the Project_log class -- just return the existing LogSemiSingleton
            return LogSemiSingleton.__instances[cls]
        elif proj_dir is not None:                                                           
                    ### different directory -- initialize a new project logger with the new directory, unless proj_dir is None
            LogSemiSingleton.__instances[cls] = super().__call__(proj_dir)
            return LogSemiSingleton.__instances[cls] 
        else:
            raise ValueError("no instance of Project Logger exists, and no directory was provided!")    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Project_logger(metaclass = LogSemiSingleton):
    '''
    Because of its metaclass, this class will:
        --> Initialize a logger in the directory provided by the entrypoint that writes inside that directory
        --> If a Project logger already exists in the session, calling this function will not create a new logger unless the directory provided 
            is different
    '''
    def __init__(self, proj_dir = None):
        self.proj_dir = proj_dir
        if proj_dir is not None:
            try:
                for i in self.log.handlers:
                    self.log.removeHandler(i)
            except Exception:
                pass
            self.log = logging.getLogger("Project_Log")
            if not os.path.exists(f"{proj_dir}/Logs"):
                os.mkdir(f"{proj_dir}/Logs")
            log_a_log_handler = logging.FileHandler(f"{proj_dir}/Logs/Project.log")
            log_a_format = logging.Formatter("%(name)s: %(asctime)s: %(message)s")    
            log_a_log_handler.setFormatter(log_a_format)
            self.log.setLevel(logging.INFO)
            self.log.addHandler(log_a_log_handler)

    def return_log(self) -> logging.Logger:
        return self.log

def warning_window(warning_to_show: str, 
                   title: str = "Warning!", 
                   logger: Union[None, logging.Logger]  = None,
                   ) -> None:
    '''
    This just displays a warning window in the GUI, with text corresonding to the string passed into the function (the "warning_to_show").

    The logger variable determines what log it is written to. Default is the current Project_log, but if that throws an error, it will still 
    try to log in the main log, to preserve the message and prevent an interruption of the program
    '''
    sub_window = ctk.CTkToplevel()
    sub_window.title(title)
    sub_label = ctk.CTkLabel(master = sub_window, text = warning_to_show)
    sub_label.grid(padx = 25, pady = 25)
    sub_window.after(200, lambda: sub_window.focus())
    if logger is None:
        try:
            logger = Project_logger().return_log()
            logger.info(f"Warning window generated: {warning_to_show}")  
        except Exception:
            pass
        
## The following class sets up & saves the directory structure of a steinbock-style experiment
## Originally written to setup the structure used by the steinbock package: https://github.com/BodenmillerGroup/steinbock (MIT license), and the
## directory used by the CATALYST package (R): https://github.com/HelenaLC/CATALYST  (GPL>=2)
## but this has been substantially changed and extended since then
## Still, some of the directory naming conventions or overall structure [with or without renaming] from the underlying packages have been carried 
# through
class DirSetup:
    def __init__(self, directory: str) -> None:
        self.main = directory

        self.raw_dir = directory + '/raw'
        self.img_dir = directory + '/images'
        self.masks_dir = directory + '/masks'
        self.logs = directory + '/Logs'

    def makedirs(self):
        if not os.path.exists(self.raw_dir):
            os.mkdir(self.raw_dir)
        if not os.path.exists(self.img_dir):
            os.mkdir(self.img_dir)
        if not os.path.exists(self.masks_dir):
            os.mkdir(self.masks_dir)
        if not os.path.exists(self.logs):
            os.mkdir(self.logs)

def run_napari(image: np.ndarray[Union[int, float]], 
            masks: Union[None, np.ndarray[int]] = None, 
            channel_axis: Union[None, int] = None,
            ) -> None:
    '''This function launches napari with the provided image & mask. The mask is shown as a layer over the image.'''
    if channel_axis is not None:
        viewer, layer = napari.imshow(image, channel_axis = channel_axis)
    else:
        viewer, layer = napari.imshow(image)    
    if masks is not None:
        viewer.add_labels(masks, name = "layer")
    napari.run()

class DirectoryDisplay(ctk.CTkFrame):
    """
    This widget class is for displaying the directory structure of the project.
    """
    def __init__(self, master, deleter: bool = False) -> None:
        super().__init__(master)
        self.master = master

        self.Placeholder = ctk.CTkLabel(master = self, text = "Directory Display")
        self.Placeholder.grid()
        self.deleter = deleter
        self.experiment = None
        self.currentdir = None

    def setup_with_dir(self, 
                       directory: str, 
                       experiment = None, 
                       delete_remove: bool = False,
                       ) -> None:
        '''
        This method allows the separation of the placement of the widget from the setup of the widget with a directory inside
        '''
        self.Placeholder.destroy()
        self.experiment = experiment
        self.configure(width = 450)
        self.directories = DirSetup(directory)
        self.currentdir = directory
        self.option_menu = ctk.CTkButton(master = self, 
                                        text = self.currentdir)
        self.option_menu.grid(column = 0, row = 0, padx = 1, pady = 3)
        self.option_menu.configure(state = 'disabled', text_color_disabled = self.option_menu.cget("text_color"))
        self.button_list = []
        self.list_dir()
        if delete_remove is False:
            self.delete_button = ctk.CTkButton(master = self, text = "Enter Delete Mode", command  = self.switch_deleter)
            self.delete_button.grid(column = 0, row = 2, padx = 1, pady = 3)

    def switch_deleter(self) -> None:
        '''
        Switch in and out of a mode where clicking on a FILE will delete it --> folder deletion is not allowed (will still just change directories)
        '''
        if self.deleter is False:
            self.deleter = True
            self.setup_with_dir(self.directories.main, self.experiment)   #### setup the widget again, but with the new deleter attribute updated
            self.delete_button = ctk.CTkButton(master = self, text = "Exit Delete Mode", command  = self.switch_deleter)
            self.delete_button.grid(column = 0, row = 2)
        elif self.deleter is True:
            self.deleter = False
            self.setup_with_dir(self.directories.main, self.experiment)   #### setup the widget again, but with the new deleter attribute updated
            self.delete_button = ctk.CTkButton(master = self, text = "Enter Delete Mode", command  = self.switch_deleter)
            self.delete_button.grid(column = 0, row = 2)

    class varButton(ctk.CTkButton):
        '''
        a button that can return its own value to the parent object and change directories, etc.
        '''
        def __init__(self, 
                     master, 
                     textvariable, 
                     height: int, 
                     width: int, 
                     fg_color: str, 
                     hover_color: str, 
                     folder_file: str, 
                     parent):
            '''
            '''
            super().__init__(master = master, 
                             textvariable = textvariable, 
                             height = height, 
                             width = width, 
                             fg_color = fg_color, 
                             hover_color = hover_color)
            self.textvar = textvariable
            self.type = folder_file
            self.parent = parent

        def configure_cmd(self) -> None:
            if self.type == "folder":
                self.configure(command = lambda: self.folder_click(self.parent, self.cget("textvariable").get()))     
            elif self.type == "file":
                self.configure(command = lambda: self.file_click(self.parent, self.cget("textvariable").get()))  
            elif self.type == "main":
                self.configure(command = lambda: self.folder_click(self.parent, "main"))  

        def file_click(self, 
                       parent, 
                       value: str,
                       ) -> None:
            '''
            '''
            parent.out = value
            filepath = parent.currentdir + "/" + parent.out
            identifier = parent.out[(parent.out.rfind(".")):]
            file_name = parent.out[:(parent.out.rfind("."))]
            if self.parent.deleter is True:
                os.remove(filepath)
                self.destroy()
                try:
                    Project_logger().return_log().info(f"{filepath} deleted!")
                except Exception:
                    pass

            elif identifier == ".csv":
                dataframe_head = pd.read_csv(filepath).head(25)
                TableLaunch(None, 1, 1, parent.currentdir, dataframe_head, f"First 25 entries of {file_name}{identifier}", parent.experiment)
            elif identifier == ".tiff":
                image = tf.imread(filepath)
                if image.dtype != 'int':
                    p = Process(target = run_napari, args = (image, None))
                    p.start()
                elif image.dtype == 'int':
                    p = Process(target = run_napari, args = (np.zeros(image.shape), image))
                    p.start()         
            elif identifier == ".txt":
                text_window(self, filepath)

        def folder_click(self, parent, value: str) -> None:
            parent.change_dir(value)

    def list_dir(self) -> None:
        '''
        '''
        container = ctk.CTkScrollableFrame(master = self)
        for i in self.button_list:
            i.destroy()
        self.button_list = []
        a = 1
        if self.currentdir != self.directories.main:
            button = self.varButton(master = container, textvariable = ctk.StringVar(value = "Go up one folder"), 
                                    height = 20, width = 350, fg_color = "blue", hover_color= "blue", folder_file = "main", parent = self)
            button.configure_cmd()
            button.grid(column = 0, row = 1, pady = 5, sticky = "ew")
            self.button_list.append(button)
            a = 2
        for i,ii in enumerate(os.scandir(self.currentdir)):
            if ii.is_dir() is True:
                button = self.varButton(master = container, 
                                        textvariable = ctk.StringVar(value = ii.name), 
                                        height = 20, 
                                        width = 350, 
                                        fg_color = "transparent", 
                                        hover_color= "blue", 
                                        folder_file = "folder", 
                                        parent = self)
                button.configure_cmd()
                button.grid(column = 0, row = i+a, pady = 5, sticky = "ew")
                self.button_list.append(button)
            else:
                button = self.varButton(master = container, 
                                        textvariable = ctk.StringVar(value = ii.name), 
                                        height = 20, 
                                        width = 350, 
                                        fg_color = "transparent", 
                                        hover_color= "blue", 
                                        folder_file = "file", 
                                        parent = self)
                button.configure_cmd()
                button.grid(column = 0, row = i+a, pady = 5, sticky = "ew")
                self.button_list.append(button)

        container.grid(column=0,row=1, padx = 3, pady = 1)
        container.configure(width = 350)
        
    def change_dir(self, 
                   new_dir: str, 
                   option_menu: bool = False,
                   ) -> None:
        '''
        '''
        if new_dir == "main":
            to_dir = self.currentdir[:self.currentdir.rfind("/")]
        elif option_menu is True:
            to_dir = self.directories.main + f"/{new_dir}"
        else:
            to_dir = self.currentdir + f"/{new_dir}"
        
        self.currentdir = to_dir
        self.option_menu.configure(text = new_dir)
        self.list_dir()

## This class launches TableWidget instances in a new window, and automatically updates / saves the .csv file when closed.
class TableLaunch(ctk.CTkToplevel, metaclass = CtkSingletonWindow):
    '''
    '''
    def __init__(self, 
                 master, 
                 width: int, 
                 height: int, 
                 directory: str, 
                 dataframe: pd.DataFrame, 
                 table_type: str, 
                 experiment, 
                 favor_table: bool = False):
        '''
        '''
        super().__init__(master)
        self.title('Table Examination')
        self.directory = directory
        try:
            self.logger = Project_logger().return_log()
        except Exception:
            self.logger = None
        if table_type != "other":
            label1 = ctk.CTkLabel(self, text = f"Values of the {table_type} file")
        else:
            clip = directory.rfind('/')
            if clip == -1:
                clip = 0
            label1 = ctk.CTkLabel(self, text = f"Values of the {directory[clip:]} file")
        label1.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = "ew")
        label1.configure(anchor = 'w')
        self.tablewidget = TableWidget(self)
        self.tablewidget.setup_data_table(directory, dataframe, table_type[:-4], favor_table = favor_table)
        self.tablewidget.setup_width_height(width, height, scale_width_height = True)

        self.tablewidget.grid(column = 0, row = 1, padx = 5, pady = 5)
        self.column = 1
        self.tablewidget.populate_table()
        self.table_list = [self.tablewidget]
        if (table_type != "other"):
            self.accept_button = ctk.CTkButton(master = self, 
                                               text = "Accept Choices and Return", 
                                               command = lambda: self.accept_and_return(experiment))
            self.accept_button.grid(column = 0, row = 2, pady = 15)
        
        self.after(200, lambda: self.focus())

    def add_table(self, 
                  width: int, 
                  height: int, 
                  directory: str, 
                  dataframe: pd.DataFrame, 
                  table_type: str, 
                  favor_table: bool = False,
                  ) -> None:
        '''
        '''
        if table_type != "other":
            label1 = ctk.CTkLabel(self, text = f"Values of the {table_type} file")
        else:
            clip = directory.rfind('/')
            if clip == -1:
                clip = 0
            label1 = ctk.CTkLabel(self, text = f"Values of the {directory[clip:]} file")
        label1.grid(column = self.column, row = 0, padx = 5, pady = 5, sticky = "ew")
        label1.configure(anchor = 'w')
        self.tablewidget = TableWidget(self)
        self.tablewidget.setup_data_table(directory, dataframe, table_type, favor_table = favor_table)
        self.tablewidget.setup_width_height(width, height, scale_width_height = True)

        self.tablewidget.grid(column = self.column, row = 1, padx = 5, pady = 5)
        self.tablewidget.populate_table()
        self.table_list.append(self.tablewidget)
        self.column += 1

    def accept_and_return(self, experiment) -> None:
        '''
        '''
        for i in self.table_list:
            i.recover_input()
            if experiment is not None:
                experiment.panel = i.table_dataframe
            self.panel_write(i.table_dataframe)
        self.destroy()

    def panel_write(self, table: pd.DataFrame, alt_directory: Union[None, str] = None) -> None:
        '''
        '''
        if alt_directory is not None:
            directory = alt_directory
        else:
            directory = self.directory
        try:
            table.to_csv(directory + '/panel.csv', index = False)
            if self.logger is not None:
                with open(directory + '/panel.csv') as file:
                    self.logger.info(f"Wrote panel file, with values: \n {file.read()}")
        except Exception:
            warning_window("""Could not write panel file! \n 
                           Do you have the .csv open right now in excel or another program?""")

## This is a core class for representing, interacting, and editing .csv / panel / metadata files
class TableWidget(ctk.CTkScrollableFrame):
    '''
    This class is for the table widget -- specifically for the widget representing the 
    panel / metadata files.

    Initialize this class with six values (now split between multiple methods):
        1. master (__int__) -- the CTk window you want to embed the table in
        2. width (setup_width_height) -- the width of the table widget, scaled by the number of columns / rows in the dataframe
        3. height (setup_width_height) -- the height of the table widget, scaled by the number of columns / rows in the dataframe 
        4. directory (setup_data_table) -- the directory where the file is to be written (directory_class.main + "/" + table_type + ".csv")
        5. dataframe (setup_data_table) -- the pandas dataframe containing the values of the table
        6. table_type (setup_data_table) -- whether the table is the "panel", "Analysis_panel", or "metadata" file -- this class will treat 
                                            each of those slightly differently
    '''
    def __init__(self, master):
        '''
        '''
        super().__init__(master)
        self.widgetframe = pd.DataFrame()

    def setup_data_table(self, 
                         directory: str, 
                         dataframe: pd.DataFrame, 
                         table_type: str = "panel", 
                         favor_table: bool = False,
                         ) -> None:
        '''decouple data loading from setup (to allow widgets to be displayed before directory is loaded in by user) '''
        self.type = table_type
        self.Analysis_internal_dir = directory
        if favor_table is False:
            try:
                self.directory = "".join([directory, "/", table_type, ".csv"])
                self.table_dataframe = pd.read_csv(directory + f'/{table_type}.csv')
                for i in self.table_dataframe.columns:
                    self.table_dataframe[i] = self.table_dataframe[i].astype("str")
            except FileNotFoundError:
                # self.directory = "".join([directory, "/", table_type, ".csv"])
                self.table_dataframe = dataframe
                if dataframe is None:
                    warning_window(f"No dataframe provided, and no existing {table_type} file is in the directory!")
                else:
                    for i in self.table_dataframe.columns:
                        self.table_dataframe[i] = self.table_dataframe[i].astype("str")

        elif favor_table is True:
            if dataframe is None:
                try:
                    self.directory = "".join([directory, "/", table_type, ".csv"])
                    self.table_dataframe = pd.read_csv(directory + f'/{table_type}.csv')
                    for i in self.table_dataframe.columns:
                        self.table_dataframe[i] = self.table_dataframe[i].astype("str")
                except FileNotFoundError:
                    warning_window(f"No dataframe provided, and no existing {table_type} file is in the directory!")

            else:
                self.table_dataframe = dataframe
                for i in self.table_dataframe.columns:
                    self.table_dataframe[i] = self.table_dataframe[i].astype("str")
    
    def setup_width_height(self, 
                           width: int, 
                           height: int, 
                           scale_width_height: bool = False,
                           ) -> None:
        ''' Decouple the widget placement from its size determination
        Also decoupled from loading the data so as to allow two different orders of construction:
               1.) place widget and manually set width / height (scale_width_height = False) without the table data pre-loaded into the widget
               2.) place the widget, load the data, then setup the width / height automatically, scaled by the number of columns&rows 
                    (scale_width_height = True). Scaling will not work without the data loaded, the number of columns/rows is not known
        '''
        self.configure(width = width, height = height)
        if scale_width_height is True:     
                # In this case, a value for height / width should be ~1, and the overall size of the table will determined 
                # by the number of columns / rows multiplied by constants defined below & the height/width passed into the constructor:
            if height*(len(self.table_dataframe.index)*35) > 700:  
                    ## cap out the height so the situation of a too long scrollable frame with a non-functional scroll bar does not occur (as much)
                self.configure(width = width*(len(self.table_dataframe.columns)*175), height = 700)
            else:
                self.configure(width = width*(len(self.table_dataframe.columns)*175), height = height*(len(self.table_dataframe.index)*35))

    def label_column(self, 
                     col_num: int, 
                     offset: int = 0, 
                     add_row_optionns: bool = False,
                     ) -> None:
        '''
        Creates a column of plain labels inside the scrollable table, of the col_num specified (zero-indexed). 
        Offset shifts the column location to the right within the scrollable frame (offset of 1 needed for tables that display the index as well).
        '''
        class varLabel(ctk.CTkLabel):
            def __init__(self, master, text, real_text):
                super().__init__(master, text = text)
                self.real_text = real_text

        column_list = []
        col1_title = ctk.CTkLabel(master = self, text = self.table_dataframe.columns[col_num])
        col1_title.grid(column = col_num + offset, row = 0, padx = 5, pady = 3)

        for i,ii in enumerate(self.table_dataframe.iloc[:,col_num]):
            col1_label = varLabel(master = self, text = ii[:20], real_text = ii)   # only display up to 20 characters to prevent overflow
            col1_label.grid(column = col_num + offset, row = i + 1, padx = 5, pady = 3)
            col1_label.configure(width = 25)
            column_list.append(col1_label)
        self.widgetframe[str(col_num)] = column_list
        if add_row_optionns is True:
            self.add_row_button = ctk.CTkButton(self, text = 'Add a Row to this file', command = lambda: self.add_row((col_num + offset)))
            self.add_row_button.grid(column = col_num + offset, row = i + 2, padx = 5, pady = 3)

    def drop_down_column(self, 
                         col_num: int, 
                         values: list = [],
                           offset: int = 0, 
                           state: str = 'normal',
                           ) -> None:
        '''
        Creates a column of drop menus inside the scrollable table, of the col_num specified (zero-indexed). 
        Values = a list of the values to be in the drop menu of the comboboxes
        Offset shifts the column location to the right within the scrollable frame (offset of 1 needed for tables that display the index as well).
        '''
        column_list = []
        col1_title = ctk.CTkLabel(master = self, text = self.table_dataframe.columns[col_num])
        col1_title.grid(column = col_num + offset, row = 0, padx = 5, pady = 3)
        for i,ii in enumerate(self.table_dataframe.iloc[:,col_num]):
            variable = ctk.StringVar(value = str(ii))
            ## only want the segmentation colum to treated special:
            if (self.type == "panel") and (col_num == 3):
                if str(ii) == "1.0":
                    variable = ctk.StringVar(value = "Nuclei")
                elif str(ii) == "2.0":
                    variable = ctk.StringVar(value = "Cytoplasmic / Membrane")
            col_dropdown = ctk.CTkOptionMenu(master = self, variable = variable, values = values)
            col_dropdown.grid(column = col_num + offset, row = i + 1, padx = 5, pady = 3)
            col_dropdown.configure(state = state)
            column_list.append(col_dropdown)
        self.widgetframe[str(col_num)] = column_list

        self.select_all = ctk.CTkOptionMenu(master = self, 
                                            variable = ctk.StringVar(value = "Set All in Column"), 
                                            values = values, 
                                            command = lambda selection: self.selector(selection = selection, 
                                                                                      column = self.widgetframe[str(col_num)]))
        self.select_all.grid(column = col_num + offset, row = i + 2, padx = 5, pady = 3)

    def selector(self, selection: str, column: list) -> None:
        '''
        '''
        for i in column:
            i.set(selection)

    def entry_column(self, 
                     col_num: int, 
                     offset: int = 0,
                     ) -> None:
        '''
        Creates a column of plain labels inside the scrollable table, of the col_num specified (zero-indexed). 
        Values = a list of the vlaues to be in the drop menu of the comboboxes
        Offset shifts the column location to the right within the scrollable frame (offset of 1 needed for tables that display the index as well).
        '''
        column_list = []
        col1_title = ctk.CTkLabel(master = self, text = self.table_dataframe.columns[col_num])
        col1_title.grid(column = col_num + offset, row = 0, padx = 3, pady = 3)
        for i,ii in enumerate(self.table_dataframe.iloc[:,col_num]):
            variable = ctk.StringVar(value = str(ii))
            col_dropdown = ctk.CTkEntry(master = self, textvariable = variable)
            col_dropdown.grid(column = col_num + offset, row = i + 1, padx = 3, pady = 3)
            column_list.append(col_dropdown)
        self.widgetframe[str(col_num)] = column_list

    class delete_varButton(ctk.CTkButton):
            ''''''
            def __init__ (self, master, text, argument):
                super().__init__(master = master, text = text)
                self.master = master
                self.configure(command = lambda: self.master.delete_row(argument))

    def delete_column(self, 
                      col_num: int, 
                      offset: int = 0, 
                      state: str = "disabled",
                      ) -> None:
        '''
        a rows of buttons, that -- if activated -- clicking on will delete the selected row from the file. 
        '''
        self.delete_state = state
        column_list = []
        col1_title = ctk.CTkButton(master = self, text = "Toggle Delete", command = lambda: self.toggle_delete_column(self.delete_state))
        col1_title.grid(column = col_num + offset, row = 0, padx = 3, pady = 3)
        for i,ii in enumerate(self.table_dataframe.index):
            col_dropdown = self.delete_varButton(master = self, text = "delete row", argument = i )
            col_dropdown.configure(state = state)
            col_dropdown.grid(column = col_num + offset, row = i + 1)
            column_list.append(col_dropdown)
        self.widgetframe[str(col_num)] = column_list

    def toggle_delete_column(self, state: str) -> None:
        '''
        '''
        col_num = self.widgetframe.columns[-1]
        if state == 'normal':
            for ii,i in enumerate(self.widgetframe.loc[:,col_num]):
                i.configure(state = 'disabled')
            self.delete_state = 'disabled'
        else:
            for i in self.widgetframe.loc[:,col_num]:
                i.configure(state = 'normal')
            self.delete_state = 'normal'
            
    def delete_row(self, row_number: int) -> None:
        '''
        '''
        for i in self.widgetframe.loc[row_number,:]:
            try:
                i.destroy()
            except Exception:
                pass
        self.widgetframe = self.widgetframe[self.widgetframe.index != row_number]

    def populate_table(self) -> None:
        '''
        '''
        # for auto-keep method (delete keep column and repopulate)
        try:
            for j in self.widgetframe.iloc[:,2]:
                del j
        except Exception:
            pass
        # for panel file only, I include the python 0-indexed channel numbers (useful for napari identification)
        if self.type == "panel":
            self.table_dataframe['keep'] = self.table_dataframe['keep'].astype('int')
            index_list = []
            for i,ii in enumerate(self.table_dataframe.index):
                index_label = ctk.CTkLabel(master = self, text = ii)
                index_label.grid(column = 0, row = i + 1)
                index_list.append(index_label)
            self.widgetframe['index'] = index_list
            self.label_column(0, offset = 1)
            self.entry_column(1, offset = 1)
            self.drop_down_column(2, values = ["0","1"], offset = 1, state = "disabled")
            self.drop_down_column(3,values = ["", "Nuclei", "Cytoplasmic / Membrane"], offset = 1)
            #self.delete_column(4, offset  = 1)
            self.offset = 1
        
        ## other wise, just show the values in the dataframe:
        else:
            for i,ii in enumerate(self.table_dataframe.index):
                index_label = ctk.CTkLabel(master = self, text = ii)
                index_label.grid(column = 0, row = i + 1)
            for i,ii in enumerate(self.table_dataframe.columns):
                self.label_column(i, offset = 1)
                self.offset = 1

        self.widgetframe = self.widgetframe.dropna(axis = 1)

    def add_row(self, column_of_button: int) -> None:
        '''
        '''
        row_list = []
        if len(self.widgetframe) == 0:
            row_number = 0
        else:
            row_number = self.widgetframe.index[-1]
        
        for i,ii in enumerate(self.widgetframe.columns):
            if i != (len(self.widgetframe.columns) - 1): 
                empty_entry = ctk.CTkEntry(self, textvariable = ctk.StringVar(value = ""))
                empty_entry.grid(column = i, row = row_number + 2, padx = 5, pady = 3)
                row_list.append(empty_entry)
            else:
                deleter = self.delete_varButton(master = self, text = "delete row", argument = row_number + 1)
                deleter.configure(state = self.delete_state)
                deleter.grid(column = i, row = row_number + 2, padx = 5, pady = 3)
                row_list.append(deleter)

        row_df = pd.DataFrame(row_list).T
        row_df.columns = self.widgetframe.columns
        row_df.index = [row_number + 1]
        self.widgetframe = pd.concat([self.widgetframe, row_df], axis = 0, ignore_index = False)
        self.add_row_button.grid(column = column_of_button, row = row_number + 3, padx = 5, pady = 3)

    def recover_input(self) -> None:
        '''
        This method recovers the user entered data from the GUI into the self.table_dataframe dataframe, and writes 
        the recovered data to a .csv file.
        '''          
        new_table_dataframe = pd.DataFrame()
        try:
            self.widgetframe = self.widgetframe.drop('index', axis = 1)
        except KeyError:
            pass
        for i,ii in zip(self.widgetframe.columns, self.table_dataframe.iloc[:,:(len(self.widgetframe.columns))]):
            column_of_interest = self.widgetframe[i]
            retrieval_list = []
            for i in column_of_interest:
                try:
                    out = i.get()
                except Exception:
                    out = i.real_text
                out = out.strip()
                if out == "Nuclei":
                    out = 1
                elif out == "Cytoplasmic / Membrane":
                    out = 2
                retrieval_list.append(out)
            new_table_dataframe[ii] = retrieval_list
            if (self.type == "panel") and (ii == 3):
                print(new_table_dataframe[ii] )
                new_table_dataframe[ii] = new_table_dataframe[ii].replace({"Nuclei":1,"Cytoplasmic / Membrane":2})
        self.table_dataframe = new_table_dataframe

class text_window(ctk.CTkToplevel):
    '''
    '''
    def __init__(self, master,  filepath: str):
        super().__init__(master)
        self.master = master
        self.title("Text Window")

        text_frame = ctk.CTkTextbox(master = self) 
        text_frame.configure(width = 800, height = 500, wrap = 'none')
        text_frame.grid()

        with open(filepath, encoding = "utf-8") as file:
            text_to_display = file.read()
            text_to_display = text_to_display.replace("||","|")

        text_frame.insert(0.0, text_to_display)
        text_frame.configure(state = "disabled")

        self.after(200, lambda: self.focus())
