from setuptools import setup

setup(
    name='nuclear_helper',
    version='1.1.0',
    description='A package to compute the hotspot structure of a tetrahedral alpha-clustered oxygen',
    url='https://github.com/MatasMarek/nuclear_helper',
    author='Marek Matas',
    author_email='marek.matas@fjfi.cvut.cz',
    license='GNU GENERAL PUBLIC LICENSE',
    packages=['nuclear_helper'],
    install_requires=['scipy',
                      'numpy',
                      'matplotlib'
                      ],

    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.9',
    ],
)