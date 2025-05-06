from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name='coolpy',
    version='0.0.63',
    description='Muon ionization simulation program',
    py_modules=["quadrupole"],
    package_dir={'': 'src'},
    classifiers =[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        #"Operating System :: iOS",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    install_requires = [
        "blessings ~= 1.7",
        'numpy',
        'matplotlib',
        'scipy',
        'shapely',
    ],
    
    extras_require = {
        "dev": [
            "pytest>=3.7",
        ],
      },
      
    url = "https://github.com/BerndStechauner/coolpy",
    author = "Bernd Stechauner",
    author_email = "bernd.stechauner@cern.ch",
)


