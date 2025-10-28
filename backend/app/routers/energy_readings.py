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
# @router.get("/analysis")
# def get_energy_analysis(
#     current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
#     db: Session = Depends(get_db)
# ):
#     return data_processing.get_energy_analysis(db, user_id=current_user.id)

@router.get("/analysis")
def get_energy_analysis(
    user_id: int,
    period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.current_month,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """获取能耗分析 - 支持多时间维度"""
    return data_processing.get_energy_analysis(
        db, user_id, period, start_date, end_date
    )

@router.get("/periods")
def get_analysis_periods():
    """获取可用的分析周期"""
    return {
        "available_periods": [
            {"value": "current_month", "label": "本月", "description": "分析本月数据"},
            {"value": "last_month", "label": "上月", "description": "分析上月完整数据"},
            {"value": "last_3_months", "label": "近三个月", "description": "分析近三个月趋势"},
            {"value": "last_6_months", "label": "近六个月", "description": "分析近六个月趋势"},
            {"value": "current_year", "label": "今年", "description": "分析今年累计数据"},
            {"value": "custom", "label": "自定义", "description": "自定义分析时间段"}
        ]
    }

# 获取与基准数据比较结果
@router.get("/benchmark-comparison")
def get_benchmark_comparison(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return data_processing.compare_with_benchmark(db, user_id=current_user.id)