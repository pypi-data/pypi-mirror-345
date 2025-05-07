from setuptools import setup, find_packages

__version__ = '0.0.0-beta'  # Define the version here

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opensim_py",
    version=__version__,
    author="Bas",
    author_email="basilio.goncalves7@gmail.com",
    description=f"An attempt to create a python package for opensim",
    long_description=f"{long_description}\n\nVersion: {__version__}",
    long_description_content_type="text/markdown",
    url="https://github.com/basgoncalves/opensim_py.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "numpy-stl",
        "pandas",
        "c3d",
        "pyperclip",
        "customtkinter",
        "matplotlib",
        "febio-python",
        "vedo",
        "scipy",
        "scikit-learn"
    ],
    
    package_data={
        'opensim': ['*.json', '*.ins', '*.txt', '*.mot', '*.c3d', '*.stl', '*.py', '*.dll', '*.so', '*.lib', '*.h', '*.png', '*.jpg', '*.exe'],
    },
    python_requires='>=3.8',
    
    include_package_data=True,
)