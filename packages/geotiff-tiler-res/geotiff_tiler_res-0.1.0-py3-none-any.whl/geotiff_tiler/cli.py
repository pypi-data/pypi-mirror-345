import os
from .tiler import export_geotiff_tiles
import argparse

def process_directory(input_dir, output_dir, tile_size=1024, stride=512, class_value_field="road_type", resume=True):
    """
    Processes all subdirectories within the input directory, exporting GeoTIFF tiles
    for each subdirectory containing .tif and .geojson files, with all outputs saved
    in centralized images/, labels/, and annotations/ folders.

    Args:
        input_dir (str): The path to the input directory containing subdirectories.
        output_dir (str): The path to the output directory where results will be saved.
        tile_size (int): Size of each tile in pixels.
        stride (int): Step size between tiles in pixels.
        class_value_field (str): Field name for class values in vector data.
        resume (bool): Resume processing by skipping existing tiles.
    """
    global_tile_index = 0

    for subdir in os.listdir(input_dir):
        subdir_path = os.path.join(input_dir, subdir)

        if os.path.isdir(subdir_path):
            tiff_files = [f for f in os.listdir(subdir_path) if f.endswith(('.tif', '.tiff'))]
            geojson_files = [f for f in os.listdir(subdir_path) if f.endswith('.geojson')]

            if not tiff_files or not geojson_files:
                print(f"Skipping {subdir}: Missing .tif or .geojson files.")
                continue

            for tiff in tiff_files:
                for geojson in geojson_files:
                    raster_path = os.path.join(subdir_path, tiff)
                    vector_path = os.path.join(subdir_path, geojson)
                    print(f"Processing {tiff} with {geojson} in subdirectory: {subdir}")

                    try:
                        stats = export_geotiff_tiles(
                            in_raster=raster_path,
                            out_folder=output_dir,
                            in_class_data=vector_path,
                            tile_size=tile_size,
                            stride=stride,
                            buffer_radius=0,
                            create_overview=True,
                            class_value_field=class_value_field,
                            skip_black_tiles=True,
                            resume=resume
                        )
                        print(f"Successfully processed {subdir}/{tiff} with {geojson}. Stats: {stats}")
                        global_tile_index += stats["total_tiles"]
                    except Exception as e:
                        print(f"Error processing {subdir}/{tiff} with {geojson}: {e}")

    print("Processing complete.")

def main():
    parser = argparse.ArgumentParser(description="Export GeoTIFF tiles from raster and classification data.")
    parser.add_argument("input_dir", help="Input directory containing subdirectories with .tif and .geojson files")
    parser.add_argument("output_dir", help="Output directory for tiles")
    parser.add_argument("--tile-size", type=int, default=1024, help="Size of each tile in pixels")
    parser.add_argument("--stride", type=int, default=512, help="Step size between tiles in pixels")
    parser.add_argument("--class-value-field", default="road_type", help="Field name for class values in vector data")
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Disable resuming existing tiles")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    process_directory(
        args.input_dir,
        args.output_dir,
        tile_size=args.tile_size,
        stride=args.stride,
        class_value_field=args.class_value_field,
        resume=args.resume
    )

if __name__ == "__main__":
    main()