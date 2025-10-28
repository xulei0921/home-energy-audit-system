from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from .. import models, schemas
from typing import List, Dict
from datetime import date, datetime, timedelta

def calculate_monthly_trend(db: Session, user_id: int, months:int = 6) -> List[Dict]:
    """计算月度能耗趋势"""
    end_date = date.today()
    start_date = end_date - timedelta(days=30*months)

    monthly_data = db.query(
        extract('year', models.EnergyReading.reading_date).label('year'),
        extract('month', models.EnergyReading.reading_date).label('month'),
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).group_by(
        'year', 'month'
    ).order_by('year', 'month').all()

    trend = []
    for data in monthly_data:
        trend.append({
            'period': f"{int(data.year)}-{int(data.month):02d}",
            'consumption': float(data.total_consumption),
            'cost': float(data.total_cost) if data.total_cost else 0
        })
    return trend

def get_device_breakdown(db: Session, user_id: int, start_date: date, end_date: date) -> List[Dict]:
    """获取设备能耗分解"""
    device_data = db.query(
        models.Device.name,
        models.Device.device_type,
        func.sum(models.EnergyReading.reading_value).label('total_consumption')
    ).join(
        models.EnergyReading, models.EnergyReading.device_id == models.Device.id
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.device
    ).group_by(
        models.Device.id, models.Device.name, models.Device.device_type
    ).all()

    breakdown = []
    for data in device_data:
        breakdown.append({
            'device_name': data.name,
            'device_type': data.device_type.value,
            'consumption': float(data.total_consumption)
        })

    return breakdown

def get_season_from_date(target_date: date) -> schemas.Season:
    """根据日期确定季节"""
    month = target_date.month
    if month in [3, 4, 5]:
        return schemas.Season.spring
    elif month in [6, 7, 8]:
        return schemas.Season.summer
    elif month in [9, 10, 11]:
        return schemas.Season.autumn
    else:
        return schemas.Season.winter

def get_house_size_range(house_size: float) -> str:
    """根据房屋面积确定范围"""
    if house_size <= 60:
        return "0-60"
    elif house_size <= 90:
        return "60-90"
    elif house_size <= 120:
        return "90-120"
    else:
        return "120+"

def compare_with_benchmark(db: Session, user_id: int) -> schemas.BenchmarkComparison:
    """与基准数据比较"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    # 获取最近一个月的总能耗
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    monthly_consumption = db.query(
        func.sum(models.EnergyReading.reading_value)
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).scalar() or 0

    # 获取对应的基准数据
    season = get_season_from_date(end_date)
    house_size_range = get_house_size_range(user.house_size or 90)

    benchmark = db.query(models.EnergyBenchmark).filter(
        models.EnergyBenchmark.family_size == user.family_size,
        models.EnergyBenchmark.season == season,
        models.EnergyBenchmark.house_size_range == house_size_range
    ).first()

    if not benchmark:
        return None

    benchmark_consumption = benchmark.average_consumption
    difference_percentage = ((monthly_consumption - benchmark_consumption) / benchmark_consumption) * 100

    return schemas.BenchmarkComparison(
        user_consumption=float(monthly_consumption),
        benchmark_consumption=float(benchmark_consumption),
        difference_percentage=float(difference_percentage),
        season=season,
        family_size=user.family_size,
        house_size_range=house_size_range
    )

def get_energy_analysis(db: Session, user_id: int) -> schemas.EnergyAnalysis:
    """获取完整的能耗分析"""
    # 最近30天的数据
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    # 总能耗
    total_consumption_result = db.query(
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).first()

    total_consumption = float(total_consumption_result.total_consumption or 0)
    total_cost = float(total_consumption_result.total_cost or 0)
    average_daily = total_consumption / 30

    # 基准比较
    benchmark_comparison = compare_with_benchmark(db, user_id)

    # 月度趋势
    monthly_trend = calculate_monthly_trend(db, user_id)

    # 设备分解
    device_breakdown = get_device_breakdown(db, user_id, start_date, end_date)

    return schemas.EnergyAnalysis(
        total_consumption=total_consumption,
        average_daily_consumption=average_daily,
        comparison_with_benchmark=benchmark_comparison.difference_percentage if benchmark_comparison else 0,
        cost_analysis=total_cost,
        monthly_trend=monthly_trend,
        device_breakdown=device_breakdown
    )