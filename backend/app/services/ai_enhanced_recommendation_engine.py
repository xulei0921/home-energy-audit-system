from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import schemas, models
from .recommendation_engine import RecommendationEngine
import logging
from .ai_service_factory import AIServiceFactory

logger = logging.getLogger(__name__)


class AIEnhancedRecommendationEngine(RecommendationEngine):
    """AI增强的推荐引擎"""

    def __init__(self, db: Session, user_id: int, ai_provider: str = "tongyi"):
        super().__init__(db, user_id)
        self.ai_service = AIServiceFactory.create_service(ai_provider)
        self.use_ai = self.ai_service is not None

    async def generate_ai_recommendations(self) -> List[schemas.RecommendationCreate]:
        """使用AI生成推荐建议"""

        if not self.use_ai:
            logger.warning("AI服务不可用，回退到规则引擎")
            return self.generate_recommendations()

        try:
            # 获取用户数据
            user = self.db.query(models.User).filter(models.User.id == self.user_id).first()
            if not user:
                return []

            # 获取能耗分析数据
            from .data_processing import get_energy_analysis
            energy_analysis = get_energy_analysis(self.db, self.user_id)

            # 构建用户数据
            user_data = {
                "family_size": user.family_size,
                "house_size": user.house_size,
                "full_name": user.full_name,
                "season": self._get_current_season()
            }

            # 转换能耗数据为字典
            energy_data = {
                "total_consumption": energy_analysis.total_consumption,
                "average_daily_consumption": energy_analysis.average_daily_consumption,
                "cost_analysis": energy_analysis.cost_analysis,
                "comparison_with_benchmark": energy_analysis.comparison_with_benchmark,
                "device_breakdown": energy_analysis.device_breakdown,
                "monthly_trend": energy_analysis.monthly_trend
            }

            # 使用AI分析能耗
            analysis_result = await self.ai_service.analyze_energy_consumption(
                user_data, energy_data
            )

            if "error" in analysis_result:
                logger.error(f"AI分析失败: {analysis_result['error']}")
                return self.generate_recommendations()

            # 使用AI生成建议
            ai_recommendations = await self.ai_service.generate_recommendations(
                analysis_result
            )

            # 转换为系统推荐格式
            recommendations = []
            for ai_rec in ai_recommendations:
                recommendation = self._convert_ai_recommendation(ai_rec)
                if recommendation:
                    recommendations.append(recommendation)

            # 合并AI建议和规则建议
            rule_based_recommendations = self.generate_recommendations()
            all_recommendations = recommendations + rule_based_recommendations

            # 去重和排序
            return self._deduplicate_and_rank(all_recommendations)

        except Exception as e:
            logger.error(f"AI推荐生成失败: {e}")
            # 出错时回退到规则引擎
            return self.generate_recommendations()

    def _convert_ai_recommendation(self, ai_rec: Dict) -> schemas.RecommendationCreate:
        """转换AI建议为系统格式"""

        try:
            # 映射类别
            category_mapping = {
                "设备使用": schemas.RecommendationCategory.device_usage,
                "生活习惯": schemas.RecommendationCategory.lifestyle,
                "设备升级": schemas.RecommendationCategory.device_upgrade,
                "其他": schemas.RecommendationCategory.other
            }

            # 映射难度
            difficulty_mapping = {
                "低": schemas.DifficultyLevel.low,
                "中": schemas.DifficultyLevel.medium,
                "高": schemas.DifficultyLevel.high
            }

            category = category_mapping.get(
                ai_rec.get("category", "其他"),
                schemas.RecommendationCategory.other
            )

            difficulty = difficulty_mapping.get(
                ai_rec.get("implementation_difficulty", "中"),
                schemas.DifficultyLevel.medium
            )

            return schemas.RecommendationCreate(
                title=ai_rec.get("title", "节能建议"),
                description=ai_rec.get("description", ""),
                category=category,
                estimated_saving=ai_rec.get("estimated_saving", 0),
                estimated_cost_saving=ai_rec.get("estimated_cost_saving", 0),
                implementation_difficulty=difficulty
            )

        except Exception as e:
            logger.error(f"转换AI建议失败: {e}")
            return None

    def _deduplicate_and_rank(self, recommendations: List[schemas.RecommendationCreate]) -> List[
        schemas.RecommendationCreate]:
        """去重和排序建议"""

        # 基于标题去重
        seen_titles = set()
        unique_recommendations = []

        for rec in recommendations:
            if rec.title not in seen_titles:
                seen_titles.add(rec.title)
                unique_recommendations.append(rec)

        # 按预计节省费用排序
        unique_recommendations.sort(
            key=lambda x: x.estimated_cost_saving or 0,
            reverse=True
        )

        return unique_recommendations

    def _get_current_season(self) -> str:
        """获取当前季节"""
        from datetime import datetime
        month = datetime.now().month

        if month in [3, 4, 5]:
            return "春"
        elif month in [6, 7, 8]:
            return "夏"
        elif month in [9, 10, 11]:
            return "秋"
        else:
            return "冬"