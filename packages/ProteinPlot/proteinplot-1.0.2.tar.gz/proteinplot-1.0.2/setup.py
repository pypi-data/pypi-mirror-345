from setuptools import setup, find_packages

setup(
    name="ProteinPlot",   # Replace with your package name
    version="1.0.2",
    packages=find_packages(),  # Finds `my_library/`
    install_requires=['numpy', 'pandas', 'matplotlib', 'jupyter', 'plotly'],  # Add dependencies here
    author="Poku-Racz-Denes",
    author_email="your.email@example.com",
    description="Library for managing .pdb extension, plotting",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_library",  # Optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Adjust based on your needs
)

