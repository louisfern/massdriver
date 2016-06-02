from setuptools import setup, find_packages

setup(
    name="massdriver",
    version="1.0",
    packages=find_packages(),
    scripts=[],  # no scripts for now
    # listing dependencies
    # install_requires = [
    #     'numpy>=1.7', 'bitarray', 'matplotlib', 'serial', 'h5py',
    # ],
    author="Louis Fernandes",
    description="This project uses historical traffic data from the state of Massachusetts to provide insight into the safest routes to travel.",
    requires=['numpy', 'pandas', 'matplotlib']
)
