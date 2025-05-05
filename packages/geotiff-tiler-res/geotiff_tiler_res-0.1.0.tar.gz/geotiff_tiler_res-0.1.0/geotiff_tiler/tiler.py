import xml.etree.ElementTree as ET
from pathlib import Path
import math
import os
import warnings
import json
import matplotlib.pyplot as plt
from shapely.geometry import box, mapping
from rasterio import features
from rasterio.windows import Window
import rasterio
import numpy as np
import geopandas as gpd
from tqdm import tqdm

def is_completely_black(image_data, threshold=0, tolerance=0.001):
    """Check if a tile is completely black (or very close to it)."""
    black_pixels = np.sum(np.all(image_data <= threshold, axis=0))
    total_pixels = image_data.shape[1] * image_data.shape[2]
    if total_pixels == 0:
        return True
    black_percentage = black_pixels / total_pixels
    return black_percentage > (1 - tolerance)

def create_overview_image(
    src, tile_coordinates, output_path, tile_size, stride, geojson_path=None
):
    """Create an overview image showing all tiles and their status, with optional GeoJSON export."""
    overview_scale = max(1, int(max(src.width, src.height) / 2000))
    overview_width = src.width // overview_scale
    overview_height = src.height // overview_scale
    overview_data = src.read(
        out_shape=(src.count, overview_height, overview_width),
        resampling=rasterio.enums.Resampling.average,
    )
    if overview_data.shape[0] >= 3:
        rgb = np.moveaxis(overview_data[:3], 0, -1)
    else:
        rgb = np.stack([overview_data[0], overview_data[0], overview_data[0]], axis=-1)
    for i in range(rgb.shape[-1]):
        band = rgb[..., i]
        non_zero = band[band > 0]
        if len(non_zero) > 0:
            p2, p98 = np.percentile(non_zero, (2, 98))
            rgb[..., i] = np.clip((band - p2) / (p98 - p2), 0, 1)
    plt.figure(figsize=(12, 12))
    plt.imshow(rgb)
    if geojson_path:
        features = []
    for tile in tile_coordinates:
        x_min = int((tile["x"]) / overview_scale)
        y_min = int((tile["y"]) / overview_scale)
        width = int(tile_size / overview_scale)
        height = int(tile_size / overview_scale)
        color = "lime" if tile["has_features"] else "red"
        if "is_black" in tile and tile["is_black"]:
            color = "blue"
        rect = plt.Rectangle(
            (x_min, y_min), width, height, fill=False, edgecolor=color, linewidth=0.5
        )
        plt.gca().add_patch(rect)
        if width > 20 and height > 20:
            plt.text(
                x_min + width / 2,
                y_min + height / 2,
                str(tile["index"]),
                color="white",
                ha="center",
                va="center",
                fontsize=8,
            )
        if geojson_path:
            minx, miny, maxx, maxy = tile["bounds"]
            polygon = box(minx, miny, maxx, maxy)
            overlap = 0
            if stride < tile_size:
                overlap = tile_size - stride
            feature = {
                "type": "Feature",
                "geometry": mapping(polygon),
                "properties": {
                    "index": tile["index"],
                    "has_features": tile["has_features"],
                    "bounds_pixel": [tile["x"], tile["y"], tile["x"] + tile_size, tile["y"] + tile_size],
                    "tile_size_px": tile_size,
                    "stride_px": stride,
                    "overlap_px": overlap,
                },
            }
            if "is_black" in tile:
                feature["properties"]["is_black"] = tile["is_black"]
            for key, value in tile.items():
                if key not in ["x", "y", "index", "has_features", "bounds", "is_black"]:
                    feature["properties"][key] = value
            features.append(feature)
    plt.title("Tile Overview (Green = Has Features, Red = Empty, Blue = Black)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Overview image saved to {output_path}")
    if geojson_path:
        geojson_collection = {
            "type": "FeatureCollection",
            "features": features,
            "properties": {
                "crs": src.crs.to_string() if hasattr(src.crs, "to_string") else str(src.crs),
                "total_tiles": len(features),
                "source_raster_dimensions": [src.width, src.height],
            },
        }
        with open(geojson_path, "w") as f:
            json.dump(geojson_collection, f)
        print(f"GeoJSON saved to {geojson_path}")
    return output_path

def export_geotiff_tiles(
    in_raster,
    out_folder,
    in_class_data,
    tile_size=256,
    stride=128,
    class_value_field="class",
    buffer_radius=0,
    max_tiles=None,
    quiet=False,
    all_touched=True,
    create_overview=False,
    skip_empty_tiles=True,
    skip_black_tiles=True,
    black_threshold=5,
    black_tolerance=0.001,
    subdir_name="",
    resume=False
):
    """
    Export georeferenced GeoTIFF tiles and labels from raster and classification data.
    Supports resuming by skipping existing tiles.

    Args:
        in_raster (str): Path to input GeoTIFF raster.
        out_folder (str): Output directory for tiles.
        in_class_data (str): Path to classification data (GeoJSON or raster).
        tile_size (int): Size of each tile in pixels (default: 256).
        stride (int): Step size between tiles in pixels (default: 128).
        class_value_field (str): Field name for class values in vector data (default: "class").
        buffer_radius (float): Buffer radius for vector features (default: 0).
        max_tiles (int): Maximum number of tiles to generate (default: None).
        quiet (bool): Suppress detailed logging (default: False).
        all_touched (bool): Include all pixels touched by vector features (default: True).
        create_overview (bool): Generate overview image of tiles (default: False).
        skip_empty_tiles (bool): Skip tiles with no features (default: True).
        skip_black_tiles (bool): Skip completely black tiles (default: True).
        black_threshold (int): Pixel value threshold for black tiles (default: 5).
        black_tolerance (float): Tolerance for black tile detection (default: 0.001).
        subdir_name (str): Subdirectory name for outputs (default: "").
        resume (bool): Resume processing by skipping existing tiles (default: False).
    """
    image_dir = os.path.join(out_folder, "images")
    label_dir = os.path.join(out_folder, "labels")
    ann_dir = os.path.join(out_folder, "annotations")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)
    os.makedirs(ann_dir, exist_ok=True)

    is_class_data_raster = False
    if isinstance(in_class_data, str):
        file_ext = Path(in_class_data).suffix.lower()
        if file_ext in [".tif", ".tiff", ".img", ".jp2", ".png", ".bmp", ".gif"]:
            try:
                with rasterio.open(in_class_data) as src:
                    is_class_data_raster = True
                    if not quiet:
                        print(f"Detected in_class_data as raster: {in_class_data}")
                        print(f"Raster CRS: {src.crs}")
                        print(f"Raster dimensions: {src.width} x {src.height}")
            except Exception:
                is_class_data_raster = False
                if not quiet:
                    print(f"Unable to open {in_class_data} as raster, trying as vector")

    with rasterio.open(in_raster) as src:
        if not quiet:
            print(f"\nRaster info for {in_raster}:")
            print(f"  CRS: {src.crs}")
            print(f"  Dimensions: {src.width} x {src.height}")
            print(f"  Resolution: {src.res}")
            print(f"  Bands: {src.count}")
            print(f"  Bounds: {src.bounds}")

        num_tiles_x = math.ceil((src.width - tile_size) / stride) + 1
        num_tiles_y = math.ceil((src.height - tile_size) / stride) + 1
        total_tiles = num_tiles_x * num_tiles_y
        if max_tiles is None:
            max_tiles = total_tiles

        class_to_id = {}
        if is_class_data_raster:
            with rasterio.open(in_class_data) as class_src:
                if class_src.crs != src.crs:
                    warnings.warn(
                        f"CRS mismatch: Class raster ({class_src.crs}) doesn't match input raster ({src.crs}). "
                        f"Results may be misaligned."
                    )
                sample_data = class_src.read(
                    1,
                    out_shape=(1, min(class_src.height, 1000), min(class_src.width, 1000)),
                )
                unique_classes = np.unique(sample_data)
                unique_classes = unique_classes[unique_classes > 0]
                if not quiet:
                    print(f"Found {len(unique_classes)} unique classes in raster: {unique_classes}")
                class_to_id = {int(cls): i + 1 for i, cls in enumerate(unique_classes)}
        else:
            try:
                gdf = gpd.read_file(in_class_data)
                if not quiet:
                    print(f"Loaded {len(gdf)} features from {in_class_data}")
                    print(f"Vector CRS: {gdf.crs}")
                if gdf.crs != src.crs:
                    if not quiet:
                        print(f"Reprojecting features from {gdf.crs} to {src.crs}")
                    gdf = gdf.to_crs(src.crs)
                if buffer_radius > 0:
                    gdf["geometry"] = gdf.buffer(buffer_radius)
                    if not quiet:
                        print(f"Applied buffer of {buffer_radius} units")
                if class_value_field in gdf.columns:
                    unique_classes = gdf[class_value_field].unique()
                    if not quiet:
                        print(f"Found {len(unique_classes)} unique classes: {unique_classes}")
                    class_to_id = {cls: i + 1 for i, cls in enumerate(unique_classes)}
                else:
                    if not quiet:
                        print(f"WARNING: '{class_value_field}' not found in vector data. Using default class ID 1.")
                    class_to_id = {1: 1}
            except Exception as e:
                raise ValueError(f"Error processing vector data: {e}")

        pbar = tqdm(
            total=min(total_tiles, max_tiles),
            desc="Generating tiles",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        )

        stats = {
            "total_tiles": 0,
            "tiles_with_features": 0,
            "black_tiles_skipped": 0,
            "feature_pixels": 0,
            "errors": 0,
            "tile_coordinates": [],
        }

        tile_index = 0
        saved_tile_counter = 0
        if resume:
            print("Resume mode enabled. Checking for existing tiles...")
            existing_tiles = set(os.listdir(image_dir))
            if existing_tiles:
                print(f"Found {len(existing_tiles)} existing tiles in {image_dir}")
                saved_tile_counter = max([int(f.split('_')[1].split('.')[0]) for f in existing_tiles if f.startswith('tile_')] + [-1]) + 1
                tile_index = saved_tile_counter
                print(f"Resuming from tile index {tile_index} (tile_{saved_tile_counter:06d}.tif)")
            else:
                print(f"No existing tiles found in {image_dir}. Starting from tile index 0.")
        else:
            print("Resume mode disabled. Starting tile generation from scratch.")

        for y in range(num_tiles_y):
            for x in range(num_tiles_x):
                if tile_index >= max_tiles:
                    break

                tile_prefix = f"tile_{saved_tile_counter:06d}"
                if resume and f"{tile_prefix}.tif" in existing_tiles:
                    tile_index += 1
                    saved_tile_counter += 1
                    pbar.update(1)
                    continue

                window_x = x * stride
                window_y = y * stride
                if window_x + tile_size > src.width:
                    window_x = src.width - tile_size
                if window_y + tile_size > src.height:
                    window_y = src.height - tile_size
                window = Window(window_x, window_y, tile_size, tile_size)
                window_transform = src.window_transform(window)
                minx = window_transform[2]
                maxy = window_transform[5]
                maxx = minx + tile_size * window_transform[0]
                miny = maxy + tile_size * window_transform[4]
                window_bounds = box(minx, miny, maxx, maxy)

                if create_overview:
                    tile_info = {
                        "index": tile_index,
                        "x": window_x,
                        "y": window_y,
                        "bounds": [minx, miny, maxx, maxy],
                        "has_features": False,
                        "is_black": False
                    }
                    stats["tile_coordinates"].append(tile_info)

                label_mask = np.zeros((tile_size, tile_size), dtype=np.uint8)
                has_features = False
                image_data = src.read(window=window)

                if skip_black_tiles and is_completely_black(image_data, threshold=black_threshold, tolerance=black_tolerance):
                    if create_overview and tile_index < len(stats["tile_coordinates"]):
                        stats["tile_coordinates"][tile_index]["is_black"] = True
                    stats["black_tiles_skipped"] += 1
                    pbar.update(1)
                    tile_index += 1
                    continue

                if is_class_data_raster:
                    with rasterio.open(in_class_data) as class_src:
                        src_bounds = src.bounds
                        class_bounds = class_src.bounds
                        if (
                            src_bounds.left > class_bounds.right
                            or src_bounds.right < class_bounds.left
                            or src_bounds.bottom > class_bounds.top
                            or src_bounds.top < class_bounds.bottom
                        ):
                            warnings.warn("Class raster and input raster do not overlap.")
                        else:
                            window_class = rasterio.windows.from_bounds(minx, miny, maxx, maxy, class_src.transform)
                            try:
                                label_data = class_src.read(1, window=window_class, boundless=True, out_shape=(tile_size, tile_size))
                                if class_to_id:
                                    remapped_data = np.zeros_like(label_data)
                                    for orig_val, new_val in class_to_id.items():
                                        remapped_data[label_data == orig_val] = new_val
                                    label_mask = remapped_data
                                else:
                                    label_mask = label_data
                                if np.any(label_mask > 0):
                                    has_features = True
                                    stats["feature_pixels"] += np.count_nonzero(label_mask)
                            except Exception as e:
                                pbar.write(f"Error reading class raster window: {e}")
                                stats["errors"] += 1
                else:
                    window_features = gdf[gdf.intersects(window_bounds)]
                    if len(window_features) > 0:
                        for idx, feature in window_features.iterrows():
                            if class_value_field in feature:
                                class_val = feature[class_value_field]
                                class_id = class_to_id.get(class_val, 1)
                            else:
                                class_id = 1
                            geom = feature.geometry.intersection(window_bounds)
                            if not geom.is_empty:
                                try:
                                    feature_mask = features.rasterize(
                                        [(geom, class_id)],
                                        out_shape=(tile_size, tile_size),
                                        transform=window_transform,
                                        fill=0,
                                        all_touched=all_touched,
                                    )
                                    label_mask = np.maximum(label_mask, feature_mask)
                                    if np.any(feature_mask):
                                        has_features = True
                                        if create_overview and tile_index < len(stats["tile_coordinates"]):
                                            stats["tile_coordinates"][tile_index]["has_features"] = True
                                except Exception as e:
                                    pbar.write(f"Error rasterizing feature {idx}: {e}")
                                    stats["errors"] += 1

                if skip_empty_tiles and not has_features:
                    pbar.update(1)
                    tile_index += 1
                    continue

                image_path = os.path.join(image_dir, f"{tile_prefix}.tif")
                label_path = os.path.join(label_dir, f"{tile_prefix}.tif")
                xml_path = os.path.join(ann_dir, f"{tile_prefix}.xml")

                image_profile = src.profile.copy()
                image_profile.update(
                    {
                        "height": tile_size,
                        "width": tile_size,
                        "count": image_data.shape[0],
                        "transform": window_transform,
                        "compress": "JPEG",
                        "photometric": "YCBCR" if image_data.shape[0] == 3 else "MINISBLACK",
                    }
                )

                try:
                    with rasterio.open(image_path, "w", **image_profile) as dst:
                        dst.write(image_data)
                    stats["total_tiles"] += 1
                except Exception as e:
                    pbar.write(f"ERROR saving image GeoTIFF: {e}")
                    stats["errors"] += 1

                label_profile = {
                    "driver": "GTiff",
                    "height": tile_size,
                    "width": tile_size,
                    "count": 1,
                    "dtype": "uint8",
                    "crs": src.crs,
                    "transform": window_transform,
                }

                try:
                    with rasterio.open(label_path, "w", **label_profile) as dst:
                        dst.write(label_mask.astype(np.uint8), 1)
                    if has_features:
                        stats["tiles_with_features"] += 1
                        stats["feature_pixels"] += np.count_nonzero(label_mask)
                except Exception as e:
                    pbar.write(f"ERROR saving label GeoTIFF: {e}")
                    stats["errors"] += 1

                if not is_class_data_raster and "gdf" in locals() and len(window_features) > 0:
                    root = ET.Element("annotation")
                    ET.SubElement(root, "folder").text = "images"
                    ET.SubElement(root, "filename").text = f"{tile_prefix}.tif"
                    size = ET.SubElement(root, "size")
                    ET.SubElement(size, "width").text = str(tile_size)
                    ET.SubElement(size, "height").text = str(tile_size)
                    ET.SubElement(size, "depth").text = str(image_data.shape[0])
                    geo = ET.SubElement(root, "georeference")
                    ET.SubElement(geo, "crs").text = str(src.crs)
                    ET.SubElement(geo, "transform").text = str(window_transform).replace("\n", "")
                    ET.SubElement(geo, "bounds").text = f"{minx}, {miny}, {maxx}, {maxy}"
                    for idx, feature in window_features.iterrows():
                        if class_value_field in feature:
                            class_val = feature[class_value_field]
                        else:
                            class_val = "object"
                        geom = feature.geometry.intersection(window_bounds)
                        if not geom.is_empty:
                            minx_f, miny_f, maxx_f, maxy_f = geom.bounds
                            col_min, row_min = ~window_transform * (minx_f, maxy_f)
                            col_max, row_max = ~window_transform * (maxx_f, miny_f)
                            xmin = max(0, min(tile_size, int(col_min)))
                            ymin = max(0, min(tile_size, int(row_min)))
                            xmax = max(0, min(tile_size, int(col_max)))
                            ymax = max(0, min(tile_size, int(row_max)))
                            if xmax > xmin and ymax > ymin:
                                obj = ET.SubElement(root, "object")
                                ET.SubElement(obj, "name").text = str(class_val)
                                ET.SubElement(obj, "difficult").text = "0"
                                bbox = ET.SubElement(obj, "bndbox")
                                ET.SubElement(bbox, "xmin").text = str(xmin)
                                ET.SubElement(bbox, "ymin").text = str(ymin)
                                ET.SubElement(bbox, "xmax").text = str(xmax)
                                ET.SubElement(bbox, "ymax").text = str(ymax)
                    tree = ET.ElementTree(root)
                    tree.write(xml_path)

                pbar.update(1)
                pbar.set_description(
                    f"Generated: {stats['total_tiles']}, With features: {stats['tiles_with_features']}, Black skipped: {stats['black_tiles_skipped']}"
                )
                tile_index += 1
                saved_tile_counter += 1

                if stats["total_tiles"] % 100 == 0 and stats["total_tiles"] > 0:
                    with open(os.path.join(out_folder, "progress.json"), "w") as f:
                        json.dump(stats, f)

            if tile_index >= max_tiles:
                break

        pbar.close()

        with open(os.path.join(out_folder, "progress.json"), "w") as f:
            json.dump(stats, f)

        if create_overview and stats["tile_coordinates"]:
            try:
                overview_filename = "overview.png"
                create_overview_image(
                    src,
                    stats["tile_coordinates"],
                    os.path.join(out_folder, overview_filename),
                    tile_size,
                    stride,
                )
            except Exception as e:
                print(f"Failed to create overview image: {e}")

        if not quiet:
            print("\n------- Export Summary -------")
            print(f"Total tiles exported: {stats['total_tiles']}")
            print(f"Tiles with features: {stats['tiles_with_features']} ({stats['tiles_with_features']/max(1, stats['total_tiles'])*100:.1f}%)")
            print(f"Black tiles skipped: {stats['black_tiles_skipped']}")
            if stats['black_tiles_skipped'] > 0:
                black_percentage = stats['black_tiles_skipped'] / (stats['total_tiles'] + stats['black_tiles_skipped']) * 100
                print(f"Percentage of black tiles: {black_percentage:.1f}%")
            if stats["tiles_with_features"] > 0:
                print(f"Average feature pixels per tile: {stats['feature_pixels']/stats['tiles_with_features']:.1f}")
            if stats["errors"] > 0:
                print(f"Errors encountered: {stats['errors']}")
            print(f"Output saved to: {out_folder}")
            if stats["total_tiles"] > 0:
                print("\n------- Georeference Verification -------")
                sample_image = os.path.join(image_dir, "tile_000000.tif")
                sample_label = os.path.join(label_dir, "tile_000000.tif")
                if os.path.exists(sample_image):
                    try:
                        with rasterio.open(sample_image) as img:
                            print(f"Image CRS: {img.crs}")
                            print(f"Image transform: {img.transform}")
                            print(f"Image has georeference: {img.crs is not None and img.transform is not None}")
                            print(f"Image dimensions: {img.width}x{img.height}, {img.count} bands, {img.dtypes[0]} type")
                    except Exception as e:
                        print(f"Error verifying image georeference: {e}")
                if os.path.exists(sample_label):
                    try:
                        with rasterio.open(sample_label) as lbl:
                            print(f"Label CRS: {lbl.crs}")
                            print(f"Label transform: {lbl.transform}")
                            print(f"Label has georeference: {lbl.crs is not None and lbl.transform is not None}")
                            print(f"Label dimensions: {lbl.width}x{lbl.height}, {lbl.count} bands, {lbl.dtypes[0]} type")
                    except Exception as e:
                        print(f"Error verifying label georeference: {e}")

        return stats