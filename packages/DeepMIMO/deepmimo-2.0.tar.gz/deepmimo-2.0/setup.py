import setuptools

VERSION = '2.0' 
DESCRIPTION = 'DeepMIMO'
LONG_DESCRIPTION = 'DeepMIMOv2 dataset generator library'

# Setting up
setuptools.setup(
        name="DeepMIMO", 
        version=VERSION,
        author="Umut Demirhan, Ahmed Alkhateeb",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
	long_description_content_type="text/markdown",
        license_files = ('LICENSE.md', ),
        install_requires=['numpy',
                          'scipy',
                          'tqdm'
                          ],
        
        keywords=['mmWave', 'MIMO', 'DeepMIMO', 'python', 'Beta'],
        classifiers= [
            "Development Status :: 4 - Beta",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ],
        package_dir={"": "src"},
        packages=setuptools.find_packages(where="src"),
        url='https://deepmimo.net/'
)