from fastapi import APIRouter, UploadFile, File, Query
from app.services import generate_ops
from typing import Optional

router = APIRouter()

@router.post("/buffer")
async def generate_buffer(
    file: UploadFile = File(...),
    distance: float = Query(...),
    mode: Optional[str] = Query(None),
    fileDownload: Optional[str] = Query(None)
):
    return generate_ops.generate_buffer(await file.read(), distance, mode, fileDownload)

@router.post("/square-grid")
async def square_grid(file: UploadFile = File(...), cell_size: float = Query(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_square_grid(await file.read(), cell_size, mode)

@router.post("/points-grid")
async def points_grid(file: UploadFile = File(...), cell_size: float = Query(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_points_grid(await file.read(), cell_size, mode)

@router.post("/outer-most-boundary")
async def outer_most_boundary(
    file: UploadFile = File(...),
    mode: Optional[str] = Query(None),
    fileDownload: Optional[str] = Query(None)
):
    return generate_ops.generate_outer_most_boundary(await file.read(), mode, fileDownload)

@router.post("/digital-elevation-model")
async def digital_elevation_model(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_digital_elevation_model(await file.read(), mode)

@router.post("/contours")
async def generate_contours(file: UploadFile = File(...), interval: float = Query(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_contours(await file.read(), interval, mode)

@router.post("/streams")
async def generate_streams(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_streams(await file.read(), mode)

@router.post("/solar-radiation-index")
async def solar_radiation_index(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return generate_ops.generate_solar_radiation_index(await file.read(), mode)
