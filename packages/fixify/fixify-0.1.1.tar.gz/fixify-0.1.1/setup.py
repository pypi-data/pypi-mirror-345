from setuptools import setup, find_packages
import os

# Safely open README.md
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="fixify",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'IPython', 'together', 'Click',
    ],
    author='YellowForest',
    description='Terminal AI for Code Explanation & Correction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    python_requires='>=3.6',
)
