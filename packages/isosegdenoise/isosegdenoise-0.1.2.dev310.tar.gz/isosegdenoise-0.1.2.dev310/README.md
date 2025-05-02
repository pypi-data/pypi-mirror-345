# isoSegDenoise Python3.10

## This is a version of isoSegDenoise intended for Python3.9 (goal PyPI version == 0.1.310) with extremely strictly defined dependencies

Purpose:  to be a more stable / easy to install version of the package due to avoiding dependencies conflicts as packages update. HOWEVER -- this means that no bugfixes, updates, or security maintenance will occur for the dependencies of the program! 
Once this version of the program is released, I also intend to infrequently (if ever) update the code in the this repository. Most effort will go into the main branch of isoSegDenoise, which is intended to better keep up-to-date with Python / dependency versions.

## Installation

Once released on PyPI, run: 

    pip install isosegdenoise==0.1.310

Inside a fresh Python 3.10  environment.

Or save this branch locally, navigate to the directory where you saved it and run:

    pip install .


## License, acknowledgements, etc.

This is just a version of the main branch of isoSegDenoise, so a lot of information has been removed from it (such as the docs, notebooks, standard README, etc.). Look at the main branch from much of these. However, information about the licenses of this branch can also be found in the txt files with filenames that start with LICENSE.