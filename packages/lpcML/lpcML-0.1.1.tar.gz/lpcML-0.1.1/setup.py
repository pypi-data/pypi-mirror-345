from pathlib import Path
import setuptools

def get_long_description():
    long_description=''
    with open(Path(Path(__file__).parent,'README.md'), 'r') as fh:
        long_description=fh.read()
    return long_description

setuptools.setup(
    name='lpcML',
    version='0.1.1',
    description='LPC ML is a machine learning workflow developed to optimize and analyze the impact of different design parameters on laser power converters (LPCs) solar cells',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Julian Garcia Fernandez ',
    author_email='julian.garcia.fernandez2@usc.es',
    url='https://gitlab.citius.usc.es/julian.garcia.fernandez/lpcML',
    setup_requires=['setuptools'],
    install_requires=['torch','pytorch_lightning','wandb','numpy','pandas','scikit-learn','torcheval','pathlib'],
    package_dir={"":"src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    classifiers=[
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
    ],
)

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools
