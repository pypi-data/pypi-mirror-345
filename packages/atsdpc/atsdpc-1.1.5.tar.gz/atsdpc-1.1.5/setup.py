# atsdpc/setup.py
from setuptools import setup, find_packages

setup(
    name='atsdpc',
    version='1.1.5',
    author='Shengqiang Han',
    author_email='2023028101@stu.sdnu.edu.cn',
    description='ATSDPC Clustering Package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/atsdpc',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'scikit-learn',
        'scipy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)