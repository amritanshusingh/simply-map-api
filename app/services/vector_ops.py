
import geopandas as gpd
import fiona
import tempfile
import os
import logging
from io import BytesIO
from shapely.geometry import mapping

def convert_kml_to_shapefile(file_bytes: bytes, mode=None):
    try:
        # Write KML to a temporary file (fiona/geopandas require a file path for KML)
        with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            tmp_path = tmp.name

        # Read KML into GeoDataFrame
        gdf = gpd.read_file(tmp_path, driver='KML')

        # Always reproject to EPSG:4326
        if gdf.crs is None or gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

        # Convert to GeoJSON
        geojson = gdf.to_json()

        # Clean up temp file
        os.unlink(tmp_path)

        return {"status": "ok", "geojson": geojson}
    except Exception as e:
        logging.exception("KML to Shapefile conversion failed")
        if mode == 'DEV':
            return {"status": "error", "detail": str(e)}
        return {"status": "error", "detail": "Failed to convert KML to GeoJSON."}

def convert_shapefile_to_kml(file_bytes: bytes, mode=None):
    # TODO: parse Shapefile from memory and return as KML
    return {"status": "ok", "kml": {}}

def point_kml_to_line_kml(file_bytes: bytes, mode=None):
    # TODO: convert point KML to line KML
    return {"status": "ok", "kml": {}}

def line_kml_to_polygon_kml(file_bytes: bytes, mode=None):
    # TODO: convert line KML to polygon KML
    return {"status": "ok", "kml": {}}
