from setuptools import setup, find_packages
from adafri import __version__
DESCRIPTION = 'Adafri python module'
LONG_DESCRIPTION = 'Adafri python module helper'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="adafri", 
        version=__version__,
        author="Ibrahima Touré",
        author_email="ibrahima.toure.dev@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[], # add any additional packages that 
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=[],
        classifiers= []
)