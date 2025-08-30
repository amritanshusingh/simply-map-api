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

def generate_outer_most_boundary(file_bytes: bytes, mode=None, fileDownload: str = None):
    import geopandas as gpd
    import tempfile
    import os
    from shapely.geometry import shape
    from osgeo import ogr
    # Step 1: Parse the KML and extract all coordinates from all geometries using OGR
    with tempfile.NamedTemporaryFile(suffix='.kml', delete=False) as tmp:
        tmp.write(file_bytes)
        tmp.flush()
        kml_path = tmp.name
    all_coords = []
    try:
        driver = ogr.GetDriverByName('KML')
        datasource = driver.Open(kml_path, 0)  # 0 means read-only
        if not datasource:
            raise RuntimeError("Could not open KML file with OGR")
        for i in range(datasource.GetLayerCount()):
            layer = datasource.GetLayerByIndex(i)
            for feature in layer:
                geom_ref = feature.GetGeometryRef()
                if geom_ref is None:
                    continue
                geom = shape(eval(geom_ref.ExportToJson()))
                if geom.is_empty or not geom.is_valid:
                    continue
                if geom.geom_type == 'Polygon':
                    all_coords.extend(list(geom.exterior.coords))
                elif geom.geom_type == 'MultiPolygon':
                    for poly in geom.geoms:
                        if poly.is_valid and not poly.is_empty:
                            all_coords.extend(list(poly.exterior.coords))
                elif geom.geom_type == 'LineString':
                    all_coords.extend(list(geom.coords))
                elif geom.geom_type == 'MultiLineString':
                    for line in geom.geoms:
                        if line.is_valid and not line.is_empty:
                            all_coords.extend(list(line.coords))
                elif geom.geom_type == 'Point':
                    all_coords.append(geom.coords[0])
                elif geom.geom_type == 'MultiPoint':
                    for pt in geom.geoms:
                        if pt.is_valid and not pt.is_empty:
                            all_coords.append(pt.coords[0])
    finally:
        os.unlink(kml_path)

    # Step 2: Compute convex hull from all_coords
    from shapely.geometry import MultiPoint
    import geopandas as gpd
    import json
    import math
    # Sanitize all_coords: only keep valid 2D float tuples
    def is_valid_coord(c):
        if not isinstance(c, (tuple, list)) or len(c) < 2:
            return False
        try:
            x, y = float(c[0]), float(c[1])
            if math.isnan(x) or math.isnan(y) or math.isinf(x) or math.isinf(y):
                return False
            return True
        except Exception:
            return False

    clean_coords = [(float(c[0]), float(c[1])) for c in all_coords if is_valid_coord(c)]

    if len(clean_coords) < 3:
        msg = 'Not enough valid points to form a polygon.'
        if mode == 'DEV':
            return {"status": "error", "detail": msg, "coord_count": len(clean_coords)}
        return {"status": "error", "detail": msg}

    hull = MultiPoint(clean_coords).convex_hull
    out_gdf = gpd.GeoDataFrame(geometry=[hull], crs="EPSG:4326")
    geojson = out_gdf.to_json()
    if fileDownload and str(fileDownload).upper() == 'YES':
        import zipfile
        from fastapi.responses import FileResponse
        import tempfile
        import os
        out_dir = tempfile.mkdtemp()
        out_shp = os.path.join(out_dir, 'outer_boundary.shp')
        out_gdf.to_file(out_shp, driver='ESRI Shapefile')
        zip_path = os.path.join(out_dir, 'outer_boundary_shapefile.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for ext in ['shp', 'shx', 'dbf', 'prj', 'cpg']:
                f = os.path.join(out_dir, f'outer_boundary.{ext}')
                if os.path.exists(f):
                    zipf.write(f, arcname=f'outer_boundary.{ext}')
        return FileResponse(zip_path, filename='outer_boundary_shapefile.zip', media_type='application/zip')
    if mode == 'DEV':
        return {"status": "ok", "coord_count": len(clean_coords), "hull_type": hull.geom_type, "geojson": json.loads(geojson)}
    return {"status": "ok", "geojson": geojson}

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
