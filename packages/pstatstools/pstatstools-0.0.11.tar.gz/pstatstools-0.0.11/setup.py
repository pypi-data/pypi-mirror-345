from setuptools import setup, find_packages
import os

setup(
    name="pstatstools",
    version=os.environ.get("VERSION"),
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "statsmodels",
        "pandas",
        "jinja2"
    ],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
