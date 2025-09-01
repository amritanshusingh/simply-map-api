
import geopandas as gpd
import fiona
import tempfile
import os
import logging
from io import BytesIO
from shapely.geometry import mapping

def convert_kml_to_shapefile(file_bytes: bytes, mode=None, fileDownload: str = None):
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

        # If fileDownload is YES, return zipped Shapefile as file download
        if fileDownload and fileDownload.upper() == 'YES':
            import zipfile
            from fastapi.responses import FileResponse
            shp_dir = tempfile.mkdtemp()
            shp_path = os.path.join(shp_dir, 'output.shp')
            gdf.to_file(shp_path, driver='ESRI Shapefile')
            # Zip all shapefile components
            zip_path = os.path.join(shp_dir, 'output_shapefile.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for ext in ['shp', 'shx', 'dbf', 'prj', 'cpg']:
                    f = os.path.join(shp_dir, f'output.{ext}')
                    if os.path.exists(f):
                        zipf.write(f, arcname=f'output.{ext}')
            # Clean up temp KML
            os.unlink(tmp_path)
            return FileResponse(zip_path, filename='output_shapefile.zip', media_type='application/zip')

        # Otherwise, return GeoJSON
        geojson = gdf.to_json()
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


# --- New functions for merging KMLs ---
import xml.etree.ElementTree as ET
from fastapi import HTTPException

def validate_kml(file_bytes: bytes):
    """
    Validates if the provided bytes are a valid KML file with at least one geometry.
    Raises Exception if invalid.
    """
    try:
        tree = ET.ElementTree(ET.fromstring(file_bytes.decode('utf-8')))
        root = tree.getroot()
        # KML namespace handling
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        placemarks = root.findall('.//kml:Placemark', ns)
        if not placemarks:
            raise Exception("No Placemark found in KML.")
        # Check for at least one geometry
        has_geom = False
        for pm in placemarks:
            if pm.find('.//kml:Point', ns) is not None or \
               pm.find('.//kml:LineString', ns) is not None or \
               pm.find('.//kml:Polygon', ns) is not None:
                has_geom = True
                break
        if not has_geom:
            raise Exception("No geometry found in KML.")
    except Exception as e:
        raise Exception(f"Invalid KML: {str(e)}")


def merge_kml_files(list_of_kml_bytes):
    """
    Merges multiple KML files into a single GeoJSON and KML string.
    Returns (geojson_dict, kml_string)
    """
    import geopandas as gpd
    import tempfile
    import os
    import fiona
    import pandas as pd
    from fastapi.encoders import jsonable_encoder

    gdfs = []
    temp_files = []
    for kml_bytes in list_of_kml_bytes:
        tmp = tempfile.NamedTemporaryFile(suffix='.kml', delete=False)
        tmp.write(kml_bytes)
        tmp.flush()
        tmp_path = tmp.name
        temp_files.append(tmp_path)
        try:
            gdf = gpd.read_file(tmp_path, driver='KML')
            gdfs.append(gdf)
        except Exception as e:
            for f in temp_files:
                os.unlink(f)
            raise Exception(f"Error reading KML: {e}")

    # Merge all GeoDataFrames
    merged_gdf = pd.concat(gdfs, ignore_index=True)
    merged_gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry')
    merged_gdf.crs = 'EPSG:4326'

    # GeoJSON output
    geojson = jsonable_encoder(merged_gdf.__geo_interface__)

    # KML output
    kml_tmp_dir = tempfile.mkdtemp()
    kml_path = os.path.join(kml_tmp_dir, 'merged.kml')
    merged_gdf.to_file(kml_path, driver='KML')
    with open(kml_path, 'r', encoding='utf-8') as f:
        kml_string = f.read()

    # Cleanup
    for f in temp_files:
        os.unlink(f)
    try:
        os.unlink(kml_path)
        os.rmdir(kml_tmp_dir)
    except Exception:
        pass

    return geojson, kml_string
