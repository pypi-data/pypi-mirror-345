from setuptools import setup, find_packages

setup(
    name='chaff-tools',  
    version='0.0.1',     
    packages=find_packages(),  
    install_requires=[  
        'requests',
        'python-dotenv',
        'beautifulsoup4',
        'numpy',
        'pyyaml',
        'pandas'
    ],
    tests_require=['pytest'],
    # package_data={'tbd': ['data/tbd.json']}
    entry_points={  
        'console_scripts': [
            'cp-batch = chaff_physics.batch:main', # Run contaminate and ready on batch (multiple receptors)
            'cp-extract = chaff_physics.extract:main', # Extract downloaded tldr into a single flat folder
            'cp-contaminate = chaff_physics.contaminate:main', # Create yaml from actives and chaff directory
            'cp-ready = chaff_physics.make_dockopt_ready:main', # Create .tar.gz for given input 
            'cp-splitdb2 = chaff_physics.split_db2:main', # split into train and test for input folder and fraction
            'cp-random-split = chaff_physics.random_split:random_split_cli' # Random split

        ],
    },
    author='Hai Pham, Christopher Patsalis',  
    author_email='pha298392@gmail.com, patsalis@umich.edu',  
    description='Pipeline for contamination, calcuating raco-score, and assessing sensitivty of both physic-based and machine-learning models.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/maomlab/chaff-tools', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10', 
)
