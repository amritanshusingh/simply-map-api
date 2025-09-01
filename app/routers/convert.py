
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from app.services import vector_ops
from typing import Optional, List

router = APIRouter()

@router.post("/kml-to-shapefile")
async def kml_to_shapefile(
    file: UploadFile = File(...),
    mode: Optional[str] = Query(None),
    fileDownload: Optional[str] = Query(None)
):
    return vector_ops.convert_kml_to_shapefile(await file.read(), mode, fileDownload)

@router.post("/shapefile-to-kml")
async def shapefile_to_kml(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return vector_ops.convert_shapefile_to_kml(await file.read(), mode)

@router.post("/point-kml-to-line-kml")
async def point_kml_to_line_kml(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return vector_ops.point_kml_to_line_kml(await file.read(), mode)

@router.post("/line-kml-to-polygon-kml")
async def line_kml_to_polygon_kml(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return vector_ops.line_kml_to_polygon_kml(await file.read(), mode)


# --- Merge KMLs endpoint ---
@router.post("/merge-kmls")
async def merge_kmls(
    files: List[UploadFile] = File(..., description="Up to 4 KML files to merge"),
    fileDownload: Optional[str] = Query(None),
    mode: Optional[str] = Query(None)
):
    # Step 1: Validate number of files
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least two KML files are required for merging.")
    if len(files) > 4:
        raise HTTPException(status_code=400, detail="A maximum of 4 KML files can be merged.")

    kml_contents = []
    error_files = []
    for file in files:
        try:
            content = await file.read()
            # Validate KML (delegated to vector_ops)
            vector_ops.validate_kml(content)
            kml_contents.append((file.filename, content))
        except Exception as e:
            if mode == 'DEV':
                error_files.append(f"{file.filename}: {str(e)}")
            else:
                error_files.append(file.filename)

    if error_files:
        if mode == 'DEV':
            raise HTTPException(status_code=400, detail={"error_files": error_files})
        else:
            raise HTTPException(status_code=400, detail=f"Invalid KML in file(s): {', '.join(error_files)}")

    # Step 2: Merge geometries
    try:
        merged_geojson, merged_kml = vector_ops.merge_kml_files([c[1] for c in kml_contents])
    except Exception as e:
        if mode == 'DEV':
            raise HTTPException(status_code=500, detail={"merge_error": str(e)})
        else:
            raise HTTPException(status_code=500, detail="Failed to merge KML files.")

    if fileDownload and fileDownload.upper() == "YES":
        import tempfile
        from fastapi.responses import FileResponse
        # Write merged_kml to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp:
            tmp.write(merged_kml.encode("utf-8") if isinstance(merged_kml, str) else merged_kml)
            tmp.flush()
            tmp_path = tmp.name
        return FileResponse(tmp_path, filename="merged.kml", media_type="application/vnd.google-earth.kml+xml")
    else:
        return merged_geojson
