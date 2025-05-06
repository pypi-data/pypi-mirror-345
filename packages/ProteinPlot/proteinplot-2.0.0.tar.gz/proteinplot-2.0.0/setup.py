from setuptools import setup, find_packages

setup(
    name="ProteinPlot",
    version="2.0.0",
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'matplotlib', 'jupyter', 'plotly', 'seaborn', 'python'], 
    author="Poku-Racz-Denes",
    author_email="denes.dome@gmail.com",
    description="Library for managing .pdb extension, plotting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://protplot.readthedocs.io/en/latest/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",)

