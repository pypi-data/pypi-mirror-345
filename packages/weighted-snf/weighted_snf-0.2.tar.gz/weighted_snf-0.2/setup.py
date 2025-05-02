from setuptools import setup, find_packages

setup(
    name='weighted_snf',             # Package name
    version='0.2',                   # Package version
    packages=find_packages(),        # Find all packages in the current directory
    install_requires=[               # External dependencies
        'numpy',                      # Add more dependencies as needed
        'scipy',
        'sklearn',
        'pandas',
        'boruta',
    ],
    description='A package for adaptive weighted similarity network fusion (AWSNF)',
    long_description=open('README.md').read(), 
    long_description_content_type='text/markdown',
    author='Sevinj Yolchuyeva',
    author_email='sevinj.yolchuyeva@crchudequebec.ulaval.ca', 
    classifiers=[                    # Classifiers to help with categorization
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
