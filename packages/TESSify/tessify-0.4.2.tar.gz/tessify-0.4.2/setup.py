from setuptools import setup, find_packages

setup(
    name='TESSify',
    version='0.4.2',
    author='Arpit Bishnoi',
    author_email='bishnoiarpit29@gmail.com',
    description='A Python package for helping with detecting exoplanet transit dips in TESS light curves.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/arpit290/TESSify',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'lightkurve',
        'numpy',
        'matplotlib',
        'pillow',
    ],
)
