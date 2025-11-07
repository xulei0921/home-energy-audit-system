from sqlalchemy.orm import Session
from sqlalchemy import func, extract, text
from .. import models, schemas
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_date_range_for_period(period: schemas.AnalysisPeriod,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None) -> Tuple[date, date]:
    """根据分析周期获取日期范围"""

    today = date.today()

    if period == schemas.AnalysisPeriod.current_month:
        # 当月第一天到今天
        start_date = today.replace(day=1)
        end_date = today
    elif period == schemas.AnalysisPeriod.last_month:
        # 上个月的第一天到最后一天
        first_day_current_month = today.replace(day=1)
        last_month_last_day = first_day_current_month - timedelta(days=1)
        start_date = last_month_last_day.replace(day=1)
        end_date = last_month_last_day
    elif period == schemas.AnalysisPeriod.last_3_months:
        # 近3个月
        start_date = today - timedelta(days=90)
        end_date = today
    elif period == schemas.AnalysisPeriod.last_6_months:
        # 近6个月
        start_date = today - timedelta(days=180)
        end_date = today
    elif period == schemas.AnalysisPeriod.current_year:
        # 今年第一天到今天
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif period == schemas.AnalysisPeriod.custom and start_date and end_date:
        # 自定义日期范围
        start_date = start_date
        end_date = end_date
    else:
        # 默认使用当月
        start_date = today.replace(day=1)
        end_date = today

    return start_date, end_date

# def calculate_monthly_trend(db: Session, user_id: int, months:int = 6) -> List[Dict]:
#     """计算月度能耗趋势"""
#     end_date = date.today()
#     start_date = end_date - timedelta(days=30*months)
#
#     monthly_data = db.query(
#         extract('year', models.EnergyReading.reading_date).label('year'),
#         extract('month', models.EnergyReading.reading_date).label('month'),
#         func.sum(models.EnergyReading.reading_value).label('total_consumption'),
#         func.sum(models.EnergyReading.cost).label('total_cost')
#     ).filter(
#         models.EnergyReading.user_id == user_id,
#         models.EnergyReading.reading_date >= start_date,
#         models.EnergyReading.reading_type == models.ReadingType.total
#     ).group_by(
#         'year', 'month'
#     ).order_by('year', 'month').all()
#
#     trend = []
#     for data in monthly_data:
#         trend.append({
#             'period': f"{int(data.year)}-{int(data.month):02d}",
#             'consumption': float(data.total_consumption),
#             'cost': float(data.total_cost) if data.total_cost else 0
#         })
#     return trend

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

# def compare_with_benchmark(db: Session, user_id: int) -> schemas.BenchmarkComparison:
#     """与基准数据比较"""
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if not user:
#         return None
#
#     # 获取最近一个月的总能耗
#     end_date = date.today()
#     start_date = end_date - timedelta(days=30)
#
#     monthly_consumption = db.query(
#         func.sum(models.EnergyReading.reading_value)
#     ).filter(
#         models.EnergyReading.user_id == user_id,
#         models.EnergyReading.reading_date >= start_date,
#         models.EnergyReading.reading_date <= end_date,
#         models.EnergyReading.reading_type == models.ReadingType.total
#     ).scalar() or 0
#
#     # 获取对应的基准数据
#     season = get_season_from_date(end_date)
#     house_size_range = get_house_size_range(user.house_size or 90)
#
#     benchmark = db.query(models.EnergyBenchmark).filter(
#         models.EnergyBenchmark.family_size == user.family_size,
#         models.EnergyBenchmark.season == season,
#         models.EnergyBenchmark.house_size_range == house_size_range
#     ).first()
#
#     if not benchmark:
#         return None
#
#     benchmark_consumption = benchmark.average_consumption
#     difference_percentage = ((monthly_consumption - benchmark_consumption) / benchmark_consumption) * 100
#
#     return schemas.BenchmarkComparison(
#         user_consumption=float(monthly_consumption),
#         benchmark_consumption=float(benchmark_consumption),
#         difference_percentage=float(difference_percentage),
#         season=season,
#         family_size=user.family_size,
#         house_size_range=house_size_range
#     )

# def get_energy_analysis(db: Session, user_id: int) -> schemas.EnergyAnalysis:
#     """获取完整的能耗分析"""
#     # 最近30天的数据
#     end_date = date.today()
#     start_date = end_date - timedelta(days=30)
#
#     # 总能耗
#     total_consumption_result = db.query(
#         func.sum(models.EnergyReading.reading_value).label('total_consumption'),
#         func.sum(models.EnergyReading.cost).label('total_cost')
#     ).filter(
#         models.EnergyReading.user_id == user_id,
#         models.EnergyReading.reading_date >= start_date,
#         models.EnergyReading.reading_date <= end_date,
#         models.EnergyReading.reading_type == models.ReadingType.total
#     ).first()
#
#     total_consumption = float(total_consumption_result.total_consumption or 0)
#     total_cost = float(total_consumption_result.total_cost or 0)
#     average_daily = total_consumption / 30
#
#     # 基准比较
#     benchmark_comparison = compare_with_benchmark(db, user_id)
#
#     # 月度趋势
#     monthly_trend = calculate_monthly_trend(db, user_id)
#
#     # 设备分解
#     device_breakdown = get_device_breakdown(db, user_id, start_date, end_date)
#
#     return schemas.EnergyAnalysis(
#         total_consumption=total_consumption,
#         average_daily_consumption=average_daily,
#         comparison_with_benchmark=benchmark_comparison.difference_percentage if benchmark_comparison else 0,
#         cost_analysis=total_cost,
#         monthly_trend=monthly_trend,
#         device_breakdown=device_breakdown
#     )

def get_energy_analysis(db: Session, user_id: int,
                        period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.current_month,
                        start_date: Optional[date] = None,
                        end_date: Optional[date] = None
                        ) -> schemas.EnergyAnalysis:
    """获取完整的能耗分析 - 支持多时间维度"""

    logger.info(f"get_energy_analysis 调用参数: user_id={user_id}, period={period}, start_date={start_date}, end_date={end_date}")

    # 获取日期范围
    analysis_start_date, analysis_end_date = get_date_range_for_period(period, start_date, end_date)
    period_days = (analysis_end_date - analysis_start_date).days + 1

    logger.info(f"分析周期: {period}, 日期范围: {analysis_start_date} 到 {analysis_end_date}, 天数: {period_days}")

    # 总能耗
    total_consumption_result = db.query(
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= analysis_start_date,
        models.EnergyReading.reading_date <= analysis_end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).first()

    total_consumption = float(total_consumption_result.total_consumption or 0)
    total_cost = float(total_consumption_result.total_cost or 0)
    average_daily = total_consumption / period_days if period_days > 0 else 0

    # 基准比较
    benchmark_comparison = compare_with_benchmark(db, user_id, analysis_end_date)

    # 月度趋势
    monthly_trend = calculate_trend_for_period(db, user_id, period, analysis_start_date, analysis_end_date)

    # 设备分解
    device_breakdown = get_device_breakdown(db, user_id, analysis_start_date, analysis_end_date)

    # 周期对比分析
    period_comparison = calculate_period_comparison(db, user_id, period, analysis_start_date, analysis_end_date)

    # 生成分析周期描述
    period_description = generate_period_description(period, analysis_start_date, analysis_end_date)

    return schemas.EnergyAnalysis(
        total_consumption=total_consumption,
        average_daily_consumption=average_daily,
        comparison_with_benchmark=benchmark_comparison.difference_percentage if benchmark_comparison else 0,
        cost_analysis=total_cost,
        monthly_trend=monthly_trend,
        device_breakdown=device_breakdown,
        analysis_period=period_description,
        period_days=period_days,
        start_date=analysis_start_date,
        end_date=analysis_end_date,
        period_comparison=period_comparison
    )

def calculate_trend_for_period(db: Session, user_id: int, period: schemas.AnalysisPeriod,
                               start_date: date, end_date: date) -> List[Dict]:
    """根据周期计算趋势数据"""

    if period in [schemas.AnalysisPeriod.current_month, schemas.AnalysisPeriod.last_month]:
        # 月度数据按天显示
        return calculate_daily_trend(db, user_id, start_date, end_date)
    elif period in [schemas.AnalysisPeriod.last_3_months, schemas.AnalysisPeriod.last_6_months]:
        # 季度数据按周显示
        return calculate_weekly_trend(db, user_id, start_date, end_date)
    else:
        # 长期数据按月显示
        return calculate_monthly_trend(db, user_id, start_date, end_date)

def calculate_daily_trend(db: Session, user_id: int, start_date: date, end_date: date) -> List[Dict]:
    """计算日趋势"""
    daily_data = db.query(
        models.EnergyReading.reading_date,
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).group_by(
        models.EnergyReading.reading_date
    ).order_by(models.EnergyReading.reading_date).all()

    trend = []
    for data in daily_data:
        trend.append({
            'period': data.reading_date.strftime('%m-%d'),
            'consumption': float(data.total_consumption),
            'cost': float(data.total_cost) if data.total_cost else 0
        })

    return trend

def calculate_weekly_trend(db: Session, user_id: int, start_date: date, end_date: date) -> List[Dict]:
    """计算周趋势"""
    weekly_data = db.query(
        extract('year', models.EnergyReading.reading_date).label('year'),
        extract('week', models.EnergyReading.reading_date).label('week'),
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).group_by(text('year'), text('week')).order_by(text('year'), text('week')).all()

    trend = []
    for data in weekly_data:
        trend.append({
            'period': f"{int(data.year)}-W{int(data.week):02d}",
            'consumption': float(data.total_consumption),
            'cost': float(data.total_cost) if data.total_cost else 0
        })

    return trend

def calculate_monthly_trend(db: Session, user_id: int, start_date: date, end_date: date) -> List[Dict]:
    """计算月趋势"""
    monthly_data = db.query(
        extract('year', models.EnergyReading.reading_date).label('year'),
        extract('month', models.EnergyReading.reading_date).label('month'),
        func.sum(models.EnergyReading.reading_value).label('total_consumption'),
        func.sum(models.EnergyReading.cost).label('total_cost')
    ).filter(
        models.EnergyReading.user_id == user_id,
        models.EnergyReading.reading_date >= start_date,
        models.EnergyReading.reading_date <= end_date,
        models.EnergyReading.reading_type == models.ReadingType.total
    ).group_by(text('year'), text('month')).order_by(text('year'), text('month')).all()

    trend = []
    for data in monthly_data:
        trend.append({
            'period': f"{int(data.year)}-{int(data.month):02d}",
            'consumption': float(data.total_consumption),
            'cost': float(data.total_cost) if data.total_cost else 0
        })

    return trend

def calculate_period_comparison(db: Session, user_id: int, period: schemas.AnalysisPeriod,
                                current_start: date, current_end: date) -> Optional[Dict]:
    """计算与上个周期的对比"""

    try:
        # 计算当前周期的日均能耗
        current_days = (current_end - current_start).days + 1
        current_consumption_result = db.query(
            func.sum(models.EnergyReading.reading_value).label('total_consumption')
        ).filter(
            models.EnergyReading.user_id == user_id,
            models.EnergyReading.reading_date >= current_start,
            models.EnergyReading.reading_date <= current_end,
            models.EnergyReading.reading_type == models.ReadingType.total
        ).first()

        current_total = float(current_consumption_result.total_consumption or 0)
        current_daily = current_total / current_days if current_days > 0 else 0

        # 计算上个周期的日期范围
        if period == schemas.AnalysisPeriod.current_month:
            # 对比上个月
            prev_start= (current_start.replace(day=1) - timedelta(days=1)).replace(day=1)
            prev_end = current_start - timedelta(days=1)
        elif period == schemas.AnalysisPeriod.last_month:
            # 对比上上个月
            prev_start = (current_start - timedelta(days=current_start.day)).replace(day=1)
            prev_end = current_start - timedelta(days=1)
        elif period == schemas.AnalysisPeriod.last_3_months:
            # 对比前3个月
            prev_start = current_start - timedelta(days=90)
            prev_end = current_start - timedelta(days=1)
        elif period == schemas.AnalysisPeriod.last_6_months:
            # 对比前6个月
            prev_start = current_start - timedelta(days=180)
            prev_end = current_start - timedelta(days=1)
        # elif period == schemas.AnalysisPeriod.current_year:
        #     # 对比今年
        #     prev_start = current_start.replace(month=1, day=1)
        #     prev_end =
        else:
            # 其他周期暂不对比
            return None

        prev_days = (prev_end - prev_start).days + 1
        prev_consumption_result = db.query(
            func.sum(models.EnergyReading.reading_value).label('total_consumption')
        ).filter(
            models.EnergyReading.user_id == user_id,
            models.EnergyReading.reading_date >= prev_start,
            models.EnergyReading.reading_date <= prev_end,
            models.EnergyReading.reading_type == models.ReadingType.total
        ).first()

        prev_total = float(prev_consumption_result.total_consumption or 0)
        prev_daily = prev_total / prev_days if prev_days > 0 else 0

        # 计算变化百分比
        if prev_daily > 0:
            change_percentage = ((current_daily - prev_daily) / prev_daily) * 100
        else:
            change_percentage = 0 if current_daily == 0 else 100

        return {
            'current_daily_consumption': current_daily,
            'previous_daily_consumption': prev_daily,
            'change_percentage': change_percentage,
            'change_direction': 'increase' if change_percentage > 0 else 'decrease',
            'comparison_period': f"{prev_start.strftime('%Y-%m-%d')} 至 {prev_end.strftime('%Y-%m-%d')}"
        }

    except Exception as e:
        logger.error(f"周期对比计算失败: {e}")
        return None

def generate_period_description(period: schemas.AnalysisPeriod, start_date: date, end_date: date) -> str:
    """生成分析周期描述"""
    description = {
        schemas.AnalysisPeriod.current_month: '本月分析',
        schemas.AnalysisPeriod.last_month: '上月分析',
        schemas.AnalysisPeriod.last_3_months: '近三个月分析',
        schemas.AnalysisPeriod.last_6_months: '近六个月分析',
        schemas.AnalysisPeriod.current_year: '今年分析',
        schemas.AnalysisPeriod.custom: f"自定义分析 ({start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')})"
    }
    return description.get(period, "能耗分析")


def compare_with_benchmark(db: Session, user_id: int, target_date: date = None) -> schemas.BenchmarkComparison:
    """与基准数据比较 - 支持指定日期"""

    if target_date is None:
        target_date = date.today()

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    # 获取目标日期前30天的数据
    end_date = target_date
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
    season = get_season_from_date(target_date)
    house_size_range = get_house_size_range(user.house_size or 90)

    benchmark = db.query(models.EnergyBenchmark).filter(
        models.EnergyBenchmark.family_size == user.family_size,
        models.EnergyBenchmark.house_size_range == house_size_range,
        models.EnergyBenchmark.season == season
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