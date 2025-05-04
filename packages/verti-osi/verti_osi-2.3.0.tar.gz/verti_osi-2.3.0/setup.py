from setuptools import setup, find_packages

setup(
    name="verti-osi",
    version="2.3.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    author="VTB Wanderer DG",
    author_email="vtb.wanderers63@gmail.com",
    description="A simple Python package",
    url="https://github.com/vtb-wanderers63/py-logging-module",
    # Add other dependencies as needed
    install_requires=["typer", "pyyaml", "jsonschema"],
    entry_points={
        "console_scripts": [
            "verti-osi=vertibit_osi_image_generator.cli:app",  # Corrected entry point
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "vertibit_osi_image_generator": ["config/config.json", "config/docker-ignore/nodejs/.dockerignore", "config/docker-ignore/python/.dockerignore"],
    }
)
