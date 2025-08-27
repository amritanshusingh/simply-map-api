def generate_buffer(file_bytes: bytes, distance: float, mode=None, fileDownload: str = None):
    import geopandas as gpd
    import tempfile
    import os
    import logging
    import zipfile
    from fastapi.responses import FileResponse
    try:
        # Try reading as KML
        with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            kml_path = tmp.name
        try:
            gdf = gpd.read_file(kml_path, driver='KML')
            os.unlink(kml_path)
        except Exception:
            # Not KML, try Shapefile
            os.unlink(kml_path)
            with tempfile.TemporaryDirectory() as shp_dir:
                shp_path = os.path.join(shp_dir, 'input.shp')
                # Write bytes to .zip and extract
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as zf:
                    zf.write(file_bytes)
                    zf.flush()
                    zip_path = zf.name
                import zipfile as zfmod
                with zfmod.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(shp_dir)
                os.unlink(zip_path)
                gdf = gpd.read_file(shp_path)

        # Reproject to metric CRS for buffering
        gdf = gdf.to_crs(epsg=3857)
        gdf['geometry'] = gdf.buffer(distance)
        gdf = gdf.to_crs(epsg=4326)

        if fileDownload and str(fileDownload).upper() == 'YES':
            out_dir = tempfile.mkdtemp()
            out_shp = os.path.join(out_dir, 'buffer.shp')
            gdf.to_file(out_shp, driver='ESRI Shapefile')
            zip_path = os.path.join(out_dir, 'buffer_shapefile.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for ext in ['shp', 'shx', 'dbf', 'prj', 'cpg']:
                    f = os.path.join(out_dir, f'buffer.{ext}')
                    if os.path.exists(f):
                        zipf.write(f, arcname=f'buffer.{ext}')
            return FileResponse(zip_path, filename='buffer_shapefile.zip', media_type='application/zip')

        geojson = gdf.to_json()
        return {"status": "ok", "geojson": geojson}
    except Exception as e:
        logging.exception("Buffer generation failed")
        if mode == 'DEV':
            return {"status": "error", "detail": str(e)}
        return {"status": "error", "detail": "Failed to generate buffer."}

def generate_square_grid(file_bytes: bytes, cell_size: float, mode=None):
    # TODO: generate square grid
    return {"status": "ok", "geojson": {}}

def generate_points_grid(file_bytes: bytes, cell_size: float, mode=None):
    # TODO: generate points grid
    return {"status": "ok", "geojson": {}}

def generate_outer_most_boundary(file_bytes: bytes, mode=None):
    # TODO: generate outer-most boundary
    return {"status": "ok", "geojson": {}}

def generate_digital_elevation_model(file_bytes: bytes, mode=None):
    # TODO: generate DEM (async)
    return {"status": "ok", "raster": {}}

def generate_contours(file_bytes: bytes, interval: float, mode=None):
    # TODO: generate contours
    return {"status": "ok", "geojson": {}}

def generate_streams(file_bytes: bytes, mode=None):
    # TODO: generate streams
    return {"status": "ok", "geojson": {}}

def generate_solar_radiation_index(file_bytes: bytes, mode=None):
    # TODO: generate solar radiation index
    return {"status": "ok", "raster": {}}
