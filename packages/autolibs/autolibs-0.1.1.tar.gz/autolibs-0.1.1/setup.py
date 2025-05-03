from setuptools import setup, find_packages

setup(
    name='autolibs',
    version='0.1.1',
    description='Auto-import numpy, pandas, matplotlib, seaborn, and other libraries',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='HARI_PRASAD_S',
    author_email='hariprasad2k06@gmail.com',
    url='https://github.com/hsnaidu/autolibs',
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'seaborn',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
