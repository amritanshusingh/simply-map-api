
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
