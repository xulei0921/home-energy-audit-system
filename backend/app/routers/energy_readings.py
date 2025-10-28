from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from .. import schemas, dependencies
from ..database import get_db
from ..services import data_processing as data_processing
from ..crud import energy_readings as energy_readings_crud

router = APIRouter()

# 获取能耗读数 by 当前用户
@router.get("/my-energy-reading", response_model=List[schemas.EnergyReadingResponse])
def read_energy_readings(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return energy_readings_crud.get_energy_readings_by_user(db, current_user.id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

# 新增能耗读数
@router.post("/", response_model=schemas.EnergyReadingResponse)
def create_energy_reading(
    reading: schemas.EnergyReadingCreate,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return energy_readings_crud.create_energy_reading(db, reading=reading, user_id=current_user.id)

# 获取能耗分析
@router.get("/analysis")
def get_energy_analysis(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return data_processing.get_energy_analysis(db, user_id=current_user.id)

# 获取与基准数据比较结果
@router.get("/benchmark-comparison")
def get_benchmark_comparison(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return data_processing.compare_with_benchmark(db, user_id=current_user.id)