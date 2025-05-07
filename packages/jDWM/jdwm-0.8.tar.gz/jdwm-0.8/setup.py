# https://python-packaging.readthedocs.io
from setuptools import setup

setup(
    name="jDWM",
    version="0.8",
    description="A Python implementation of the Dynamic Wake meandering (DWM) model",
    url='https://gitlab.windenergy.dtu.dk/HAWC2Public/jdwm',
    author="Jaime Liew",
    maintainer='Mads M Pedersen',
    maintainer_email='mmpe@dtu.dk',
    license="MIT",
    packages=["jDWM"],
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "numba",
        "tqdm",
        "pytest",
        "pytest-cov",
        # "sphinx",
        # "sphinx_rtd_theme",
        # "sphinxcontrib-napoleon",
    ],
)
