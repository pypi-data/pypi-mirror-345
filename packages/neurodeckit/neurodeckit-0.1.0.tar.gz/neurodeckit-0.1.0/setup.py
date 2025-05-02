from setuptools import setup, find_packages

with open("README.md", "r", errors="ignore", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='neurodeckit',
    version='0.1.0',  
    author='LC.Pan',
    author_email='panlincong@tju.edu.cn',
    description='Full chain toolkit for EEG signal decoding',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/PLC-TJU/NeuroDecKit',
    packages=find_packages(),  
    install_requires=[
        'braindecode',
        'einops',
        'geoopt',
        'h5py',
        'joblib',
        'mne',
        'numpy',
        'pandas',
        'pooch',
        'psutil',
        'pynvml',
        'pyriemann==0.6',
        'scikit_learn',
        'scipy',
        'skorch',
        'statsmodels',
        'torch',
        'torchsummary',
    ],  
    keywords=['python', 'package'],
    classifiers=[
        'Programming Language :: Python :: 3',
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
