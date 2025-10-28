from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

from .. import models, schemas
from typing import List
from datetime import date, timedelta
from . import data_processing as data_processing
from ..crud import recommendations as recommendations_crud

class RecommendationEngine:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def generate_recommendations(self) -> List[schemas.RecommendationCreate]:
        """生成个性化节能建议"""
        recommendations = []

        # 分析用户数据
        analysis = data_processing.get_energy_analysis(self.db, self.user_id)
        user = self.db.query(models.User).filter(models.User.id == self.user_id).first()
        devices = self.db.query(models.Device).filter(models.Device.user_id == self.user_id).all()

        # 基于基准比较的建议
        if analysis.comparison_with_benchmark > 20:
            recommendations.append(self._create_high_consumption_recommendation(
                analysis.comparison_with_benchmark
            ))

        # 基于设备使用的建议
        device_recommendation = self._generate_device_recommendations(devices, analysis)
        recommendations.extend(device_recommendation)

        # 基于生活习惯的建议
        lifestyle_recommendations = self._generate_lifestyle_recommendations(user, analysis)
        recommendations.extend(lifestyle_recommendations)

        return recommendations

    def _create_high_consumption_recommendation(self, excess_percentage: float) -> schemas.RecommendationCreate:
        """创建高能耗警告建议"""
        return schemas.RecommendationCreate(
            title="能耗偏高提醒",
            description=f"您的家庭能耗比相似家庭高出{excess_percentage:.1f}%。建议检查家中大功率电器的使用情况，并考虑优化用电习惯。",
            category=schemas.RecommendationCategory.lifestyle,
            estimated_saving=50.0,
            estimate_cost_saving=25.0,
            implementation_difficulty=schemas.DifficultyLevel.medium
        )

    def _generate_device_recommendations(self, devices: List[schemas.DeviceResponse], analysis: schemas.EnergyAnalysis) -> List[schemas.RecommendationCreate]:
        """基于设备生成建议"""
        recommendations = []

        # 分析高能耗设备
        high_consumption_devices = []
        for device in devices:
            device_consumption = sum(
                item['consumption'] for item in analysis.device_breakdown
                if item['device_name'] == device.name
            )
            if device_consumption > 50:
                high_consumption_devices.append((device, device_consumption))

        for device, consumption in high_consumption_devices:
            if device.device_type == models.DeviceType.air_conditioner:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议将温度设置在26℃以上，定期清理过滤网，并在外出时关闭空调。",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.2,
                    estimated_cost_saving=consumption * 0.2 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.water_heater:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议将水温设置在45~50℃，使用前1小时开启，使用后及时关闭。",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.15,
                    estimated_cost_saving=consumption * 0.15 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.refrigerator:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议：1. 冷藏室温度设为4~5℃，冷冻室设为-18℃；2. 减少开门次数，每次开门时间控制在30秒内；3. 定期清理冷凝器灰尘；4. 食材不要堆放过满",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.12,
                    estimated_cost_saving=consumption * 0.12 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.television:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议：1. 将屏幕亮度调至50%-70%; 2. 音量控制在50%以内；3. 看完电视后直接关闭电源",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.15,
                    estimated_cost_saving=consumption * 0.15 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.washing_machine:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议：1. 尽量积攒足量衣物（80%负载）再洗，避免少量衣物多次运行；2. 优先用冷水洗（仅油污严重时用温水），可减少50%以上加热能耗；3. 选择节能程序（如‘ eco 模式’），缩短洗涤时间并降低转速；4. 定期清理过滤器（防止堵塞增加电机负担），脱水后及时断电。",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.2,  # 预计节省20%（基于行业数据）
                    estimated_cost_saving=consumption * 0.2 * 0.5,  # 按0.5元/kWh计算
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.lighting:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议：1. 将传统白炽灯/节能灯更换为LED灯（节能80%，寿命延长5-10倍）；2. 安装智能开关或调光器，人走灯灭，亮度按需调节（如客厅50%-70%，卧室30%-50%）；3. 优先利用自然光，白天减少开灯时间；4. 定期清洁灯具（积灰会降低30%亮度，导致不自觉调亮）。",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.3,  # 预计节省30%（LED替换+习惯优化）
                    estimated_cost_saving=consumption * 0.3 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))
            elif device.device_type == models.DeviceType.computer:
                recommendations.append(schemas.RecommendationCreate(
                    title=f"优化{device.name}使用",
                    description=f"您的{device.name}月耗电{consumption:.1f}kWh。建议：1. 启用电源管理（台式机设为10分钟无操作进入休眠，笔记本设为5分钟）；2. 不用时直接关机（避免待机，台式机待机功率约5-15W，笔记本2-5W）；3. 降低屏幕亮度至50%-70%，关闭键盘背光（若有）；4. 运行大型程序时集中处理，避免后台闲置进程过多。",
                    category=schemas.RecommendationCategory.device_usage,
                    estimated_saving=consumption * 0.25,  # 预计节省25%（电源管理+习惯优化）
                    estimated_cost_saving=consumption * 0.25 * 0.5,
                    implementation_difficulty=schemas.DifficultyLevel.low,
                    device_id=device.id
                ))

        return recommendations

    def _generate_lifestyle_recommendations(self, user: models.User, analysis: schemas.EnergyAnalysis) -> List[schemas.RecommendationCreate]:
        """基于生活习惯生成建议"""
        recommendations = []

        # 根据家庭规模和生活习惯给出建议
        if user.family_size >= 3:
            recommendations.append(schemas.RecommendationCreate(
                title="集中用电优化",
                description="考虑到您家庭成员较多，建议合理安排用电时间，避免高峰时段同时使用多个大功率电器。",
                category=schemas.RecommendationCategory.lifestyle,
                estimated_saving=30.0,
                estimated_cost_saving=15.0,
                implementation_difficulty=schemas.DifficultyLevel.medium
            ))
        # 根据房屋面积给出建议
        if user.house_size and user.house_size > 100:
            recommendations.append(schemas.RecommendationCreate(
                title="分区用电策略",
                description="考虑到您的房屋面积较大，建议实施分区用电，不使用的房间及时关闭空调和照明。",
                category=schemas.RecommendationCategory.lifestyle,
                estimated_saving=40.0,
                estimated_cost_saving=20.0,
                implementation_difficulty=schemas.DifficultyLevel.medium
            ))

        # 通用建议
        recommendations.extend([
            schemas.RecommendationCreate(
                title="使用节能灯具",
                description="将传统白炽灯更换为LED节能灯，可节省约80%的照明用电。",
                category=schemas.RecommendationCategory.device_upgrade,
                estimated_saving=15.0,
                estimated_cost_saving=7.5,
                implementation_difficulty=schemas.DifficultyLevel.low
            ),
            schemas.RecommendationCreate(
                title="待机功耗管理",
                description="不使用电器时完全关闭电源，避免待机功耗。可使用智能插座辅助管理。",
                category=schemas.RecommendationCategory.device_usage,
                estimated_saving=10.0,
                estimated_cost_saving=5.0,
                implementation_difficulty=schemas.DifficultyLevel.low
            )
        ])

        return recommendations

def generate_user_recommendations(db: Session, user_id: int) -> List[schemas.RecommendationResponse]:
    """为用户生成并保存节能建议"""
    engine = RecommendationEngine(db, user_id)
    new_recommendations = engine.generate_recommendations()

    saved_recommendations = []
    for rec_data in new_recommendations:
        # 检查是否已存在类似建议
        existing = db.query(models.Recommendation).filter(
            models.Recommendation.title == rec_data.title,
            models.Recommendation.user_id == user_id
        ).first()

        if not existing:
            # saved_rec = crud.create_recommendation(db, rec_data, user_id)
            saved_rec = recommendations_crud.create_recommendation(db, rec_data, user_id)
            saved_recommendations.append(saved_rec)

    return saved_recommendations