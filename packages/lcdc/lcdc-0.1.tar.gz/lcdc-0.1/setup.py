from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='lcdc',
    version='0.1',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license='MIT',
    install_requires=["scikit-learn", 
                      "numpy",
                      "pyarrow",
                      "matplotlib", 
                      "PyWavelets",
                      "datasets",
                      "tqdm",
                      "strenum"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)