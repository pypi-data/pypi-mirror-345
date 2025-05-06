from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="st-selectable-grid",
    version="0.5.8",
    author="Luke Hoggatt",
    description="A Streamlit component for a selectable grid",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hoggatt/st-selectable-grid",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "st_selectable_grid": ["frontend/build/**/*", "frontend/build/*.*"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "streamlit >= 1.35",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)
