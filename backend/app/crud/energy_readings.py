from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from .. import models, schemas
from sqlalchemy import extract

# 获取能耗数据 by 当前用户
def get_energy_readings_by_user(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.EnergyReading).filter(models.EnergyReading.user_id == user_id)

    if start_date:
        query = query.filter(models.EnergyReading.reading_date >= start_date)

    if end_date:
        query = query.filter(models.EnergyReading.reading_date <= end_date)

    return query.offset(skip).limit(limit).all()

# 新增能耗数据
def create_energy_reading(db: Session, reading:schemas.EnergyReadingCreate, user_id: int):
    db_reading = models.EnergyReading(**reading.model_dump(), user_id=user_id)

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    return db_reading

# 获取月度能耗
def get_monthly_consumption(db: Session, user_id: int, year: int, month: int):
    return db.query(models.EnergyReading).filter(
        models.EnergyReading.user_id == user_id,
        extract('year', models.EnergyReading.reading_date) == year,
        extract('month', models.EnergyReading.reading_date) == month
    ).all()