from setuptools import setup, find_packages

setup(
    name="geotiff_tiler_res",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21",
        "rasterio>=1.3",
        "geopandas>=0.10",
        "shapely>=1.8",
        "matplotlib>=3.5",
        "tqdm>=4.60",
    ],
    entry_points={
        "console_scripts": [
            "geotiff-tiler=geotiff_tiler.cli:main",
        ],
    },
    author="potacessium",
    author_email="kyush.naxa@gmail.com",
    description="A tool to export georeferenced GeoTIFF tiles and labels from raster and classification data.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/knaxa/geotiff_tiler",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)