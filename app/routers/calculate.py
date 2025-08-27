from fastapi import APIRouter, UploadFile, File, Query
from app.services import calculate_ops
from typing import Optional

router = APIRouter()

@router.post("/difference")
async def calculate_difference(file1: UploadFile = File(...), file2: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_difference(await file1.read(), await file2.read(), mode)

@router.post("/addition")
async def calculate_addition(file1: UploadFile = File(...), file2: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_addition(await file1.read(), await file2.read(), mode)

@router.post("/union")
async def calculate_union(file1: UploadFile = File(...), file2: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_union(await file1.read(), await file2.read(), mode)

@router.post("/intersection")
async def calculate_intersection(file1: UploadFile = File(...), file2: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_intersection(await file1.read(), await file2.read(), mode)

@router.post("/slope")
async def calculate_slope(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_slope(await file.read(), mode)

@router.post("/aspect")
async def calculate_aspect(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_aspect(await file.read(), mode)

@router.post("/hillshade")
async def calculate_hillshade(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_hillshade(await file.read(), mode)

@router.post("/ruggedness")
async def calculate_ruggedness(file: UploadFile = File(...), mode: Optional[str] = Query(None)):
    return await calculate_ops.calculate_ruggedness(await file.read(), mode)
