import setuptools

VERSION = '3.2.9'
DESCRIPTION = 'DeepMIMOv3'
LONG_DESCRIPTION = """

This package contains Python code for DeepMIMOv3 generator library. 

Install the lastest v3 package with: `pip install deepmimo==3`
"""

# Setting up
setuptools.setup(
    name="DeepMIMO",
    version=VERSION,
    author="Umut Demirhan, Ahmed Alkhateeb",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license_files=('LICENSE.md',),
    install_requires=[
        'numpy',
        'scipy',
        'tqdm',
        'matplotlib',
    ],
    keywords=['mmWave', 'MIMO', 'DeepMIMO', 'python', 'Beta'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    url='https://deepmimo.net/'
)
