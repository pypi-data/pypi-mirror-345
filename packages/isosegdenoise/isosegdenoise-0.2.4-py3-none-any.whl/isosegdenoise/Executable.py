'''
This is the file containing the launch point for the isoSegDenoise GUI
'''
# soliDeoGloria

import logging
import argparse
from .app_entry import App #type: ignore
import warnings

warnings.filterwarnings("ignore", message = "The legacy Dask DataFrame implementation is deprecated") 

__all__ = ["run_GUI"]


CLI = argparse.ArgumentParser()
CLI.add_argument("-d", "--directory")
CLI.add_argument("-r1", "--resolution1", type = float)
CLI.add_argument("-r2", "--resolution2", type = float)

CLI_args = CLI.parse_known_args()[0]  
 ## thanks to:
 # https://stackoverflow.com/questions/48796169/how-to-fix-ipykernel-launcher-py-error-unrecognized-arguments-in-jupyter 
 #                  (Nicolas Gervais answer) for pointing the way

directory_in = CLI_args.directory
resolutions_in = [CLI_args.resolution1, CLI_args.resolution2]


#### These final code blocks execute the program
def run_GUI(directory: str = directory_in, resolutions: tuple[float, float] = resolutions_in) -> None:
    '''
    This is the function that launches the GUI. It can receive a directory and resolutions (list of two floats, for X / Y resolutions in 
    micrometers / pixel) in order to directly load a folder, instead of needing to load the folder inside the GUI itself. 
    '''
    App1 = App(directory = directory, resolutions = resolutions)

    '''
    These following lines are the filters to block unwanted logging during normal calculations
    '''
    class package_filterer(logging.Filter):      
        ## https://docs.python.org/3/howto/logging-cookbook.html#filters-contextual   --> Example of using filters
        # The goal for this filter had been to remove messages from the R console --> and other packages
        ## Generally speaking, I want little logging from dependencies during normal operation of the program, and in particular don't want 
        #       repeated / spammed messages from iterated tasks
        # deepcell might be blocked, too (?) --> but it produces very little output when run and it might be useful (?)
        ## I don't like blocking warnings from rpy2, but seems necessary to preven the log from exploding...
        def __init__(self, cellpose = False):
            super().__init__()
            self.cellpose = cellpose

        def filter(self, record):
            if (self.cellpose is True) & (record.levelno == 20):    ## block info messages from cellpose (message spam during normal operation)
                return False

    cellposesilencer1 = logging.getLogger("cellpose.models")
    cellposesilencer2 = logging.getLogger("cellpose.core")
    cellposesilencer3 = logging.getLogger("cellpose.denoise")
    list_cellpose_loggers = [cellposesilencer1, cellposesilencer2, cellposesilencer3]

    for i in list_cellpose_loggers:
        i.addFilter(package_filterer(cellpose = True))

    App1.mainloop()

if __name__ == "__main__":
    run_GUI()