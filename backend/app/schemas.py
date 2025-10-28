from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum
# 设备类型枚举
class DeviceType(str, Enum):
    air_conditioner = "air_conditioner"
    refrigerator = "refrigerator"
    television = "television"
    washing_machine = "washing_machine"
    water_heater = "water_heater"
    lighting = "lighting"
    computer = "computer"
    other = "other"

# 数据读取类型枚举
class ReadingType(str, Enum):
    total = "total"
    device = "device"

# 建议类型枚举
class RecommendationCategory(str, Enum):
    device_usage = "device_usage"
    lifestyle = "lifestyle"
    device_upgrade = "device_upgrade"
    other = "other"

# 实施难度枚举
class DifficultyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

# 季节枚举
class Season(str, Enum):
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"

# 用户模型 - 基础
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    family_size: Optional[int] = 1
    house_size: Optional[float] = None

# 用户模型 - 创建
class UserCreate(UserBase):
    password: str

# 用户模型 - 更新
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    family_size: Optional[int] = None
    house_size: Optional[float] = None

# 用户模型 - 响应
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 设备模型 - 基础
class DeviceBase(BaseModel):
    name: str
    device_type: DeviceType
    power_rating: float
    daily_usage_hours: Optional[float] = 0
    location: Optional[str] = None
    is_active: Optional[bool] = True

# 设备模型 - 创建
class DeviceCreate(DeviceBase):
    pass

# 设备模型 - 更新
class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[DeviceType] = None
    power_rating: Optional[float] = None
    daily_usage_hours: Optional[float] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None

# 设备模型 - 响应
class DeviceResponse(DeviceBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 能耗读数模型 - 基础
class EnergyReadingBase(BaseModel):
    reading_value: float
    reading_type: ReadingType
    reading_date: date
    cost: Optional[float] = None
    device_id: Optional[int] = None

# 能耗读数模型 - 创建
class EnergyReadingCreate(EnergyReadingBase):
    pass

# 能耗读数模型 - 更新
class EnergyReadingUpdate(BaseModel):
    reading_value: Optional[float] = None
    reading_type: Optional[ReadingType] = None
    reading_date: Optional[date] = None
    cost: Optional[float] = None
    device_id: Optional[int] = None

# 能耗读数模型 - 响应
class EnergyReadingResponse(EnergyReadingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 建议模型 - 基础
class RecommendationBase(BaseModel):
    title: str
    description: str
    category: RecommendationCategory
    estimated_saving: Optional[float] = None
    estimated_cost_saving: Optional[float] = None
    implementation_difficulty: Optional[DifficultyLevel] = DifficultyLevel.medium
    device_id: Optional[int] = None

# 建议模型 - 创建
class RecommendationCreate(RecommendationBase):
    pass

# 建议模型 - 更新
class RecommendationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RecommendationCategory] = None
    estimated_saving: Optional[float] = None
    estimated_cost_saving: Optional[float] = None
    implementation_difficulty: Optional[DifficultyLevel] = None
    is_implemented: Optional[bool] = None
    device_id: Optional[int] = None

# 建议模型 - 响应
class RecommendationResponse(RecommendationBase):
    id: int
    user_id: int
    is_implemented: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token模型 - 响应
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# 分析结果模型
class EnergyAnalysis(BaseModel):
    total_consumption: float
    average_daily_consumption: float
    comparison_with_benchmark: float  #百分比
    cost_analysis: float
    monthly_trend: List[dict]
    device_breakdown: List[dict]

class BenchmarkComparison(BaseModel):
    user_consumption: float
    benchmark_consumption: float
    difference_percentage: float
    season: Season
    family_size: int
    house_size_range: str