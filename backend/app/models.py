from sqlalchemy import Column, JSON, Integer, String,Float, Boolean, DateTime, Text, Enum, ForeignKey, Date
from sqlalchemy.sql import func
from .database import Base
import enum

class DeviceType(enum.Enum):
    air_conditioner = "air_conditioner"
    refrigerator = "refrigerator"
    television = "television"
    washing_machine = "washing_machine"
    water_heater = "water_heater"
    lighting = "lighting"
    computer = "computer"
    other = "other"

class ReadingType(enum.Enum):
    total = "total"
    device = "device"

class RecommendationCategory(enum.Enum):
    device_usage = "device_usage"
    lifestyle = "lifestyle"
    device_upgrade = "device_upgrade"
    other = "other"

class DifficultyLevel(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Season(enum.Enum):
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    family_size = Column(Integer, default=1)
    house_size = Column(Float, comment="房屋面积(平方米)")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    power_rating = Column(Float, nullable=False, comment="额定功率(W)")
    daily_usage_hours = Column(Float, default=0, comment="日均使用小时数")
    location = Column(String(50), comment="设备位置")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class EnergyReading(Base):
    __tablename__ = "energy_readings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    reading_value = Column(Float, nullable=False, comment="能耗读数(kWh)")
    reading_type = Column(Enum(ReadingType), nullable=False)
    reading_date = Column(Date, nullable=False)
    cost = Column(Float, comment="电费(元)")
    created_at = Column(DateTime, default=func.now())

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(RecommendationCategory), nullable=False)
    estimated_saving = Column(Float, comment="预计节省(kWh/月)")
    estimated_cost_saving = Column(Float, comment="预计节省费用(元/月)")
    implementation_difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.medium)
    is_implemented = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # 新增字段
    source = Column(String(20), default="rule_based", comment="建议来源: rule_based, ai_based")  # 新增
    confidence_score = Column(Float, default=1.0, comment="置信度评分")  # 新增
    ai_analysis = Column(JSON, comment="AI分析元数据")  # 新增

class EnergyBenchmark(Base):
    __tablename__ = "energy_benchmarks"

    id = Column(Integer, primary_key=True, index=True)
    family_size = Column(Integer, nullable=False)
    house_size_range = Column(String(50), nullable=False, comment="面积范围")
    season = Column(Enum(Season), nullable=False)
    average_consumption = Column(Float, nullable=False, comment="平均能耗(kWh/月)")
    created_at = Column(DateTime, default=func.now())