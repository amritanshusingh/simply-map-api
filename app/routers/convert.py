from fastapi import APIRouter, UploadFile, File, Query
from app.services import vector_ops
from typing import Optional

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
