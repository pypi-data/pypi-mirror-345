from setuptools import setup, find_packages

setup(
    name='weighted_snf',             
    version='0.3',
    packages=find_packages(),
    install_requires=[               
        'numpy',
        'scipy',
        'scikit-learn',  # Correctly specify scikit-learn
        'boruta',
    ],
    description='A package for adaptive weighted similarity network fusion',  
    long_description=open('README.md').read(),  
    long_description_content_type='text/markdown',  
    author='Sevinj Yolchuyeva',
    author_email='sevinj.yolchuyeva@crchudequebec.ulaval.ca', 
    classifiers=[                    
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',         
)
