"""Setup for the chocobo package."""

import setuptools
import os

if os.path.exists('requirements.txt'):
    with open('requirements.txt') as f:
        required_packages = f.read().splitlines()
else:
    required_packages = [
        'opencv-python',
        'opencv-python-headless',
        'scikit-image',
        'setuptools',
        'pytest',
        'pillow',
    ]

setuptools.setup(
    author='Sarthak, Harshit',
    author_email="sarthak6jan16@gmail.com",
    name='snapdedup',
    license="MIT",
    description='Python Library to process and compare images.',
    version='0.0.2',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Sarthak-Gholap/snapdedup',
    packages=setuptools.find_packages(),
    python_requires=">=3.11",
    install_requires=required_packages,
    keywords=[
        'image', 'deduplication', 'image processing', 'duplicate images',
        'image comparison', 'image similarity', 'image hash', 'image matching',
        'duplicate image finder', 'image uniqueness',
        'image optimization', 'image deduplication tool',
        'image dedupe', 'image analysis', 'fast deduplication', 'image library'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
)