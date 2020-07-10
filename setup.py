import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="VariantCalling-ekherman", # Replace with your own username
    version="0.0.1",
    author="Emily Herman",
    author_email="eherman@ualberta.ca",
    description="A Snakemake workflow for SNP calling from raw Illumina data",
    url="https://github.com/stothard-group/variant-calling-pipeline",
    packages=setuptools.find_packages(),
    install_requires=[
        "pysam>=0.15.4",
        "pandas>=0.24.1",
        "numpy>=1.12.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
)