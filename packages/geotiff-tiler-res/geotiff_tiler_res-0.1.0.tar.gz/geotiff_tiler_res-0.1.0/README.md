GeoTIFF Tiler
A Python package to export georeferenced GeoTIFF tiles and labels from raster and classification data.
Installation
Install via pip:
pip install geotiff_tiler

Usage
Run the command-line tool:
geotiff-tiler /path/to/input_dir /path/to/output_dir --tile-size 1024 --stride 512 --class-value-field road_type

Arguments

input_dir: Directory containing subdirectories with .tif and .geojson files.
output_dir: Directory to save output tiles.
--tile-size: Size of each tile in pixels (default: 1024).
--stride: Step size between tiles in pixels (default: 512).
--class-value-field: Field name for class values in vector data (default: "road_type").
--no-resume: Disable resuming existing tiles.

Programmatic Usage
from geotiff_tiler import export_geotiff_tiles, process_directory

# Process a directory
process_directory(
    input_dir="/path/to/input",
    output_dir="/path/to/output",
    tile_size=1024,
    stride=512,
    class_value_field="road_type",
    resume=True
)

# Export tiles for a single raster
stats = export_geotiff_tiles(
    in_raster="input.tif",
    out_folder="output",
    in_class_data="classes.geojson",
    tile_size=1024,
    stride=512,
    class_value_field="road_type"
)

Dependencies

numpy>=1.21
rasterio>=1.3
geopandas>=0.10
shapely>=1.8
matplotlib>=3.5
tqdm>=4.60

License
MIT License
