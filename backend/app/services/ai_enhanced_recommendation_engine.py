from sqlalchemy.orm import Session
from typing import List, Dict, Any
from .. import schemas, models
from .recommendation_engine import RecommendationEngine
import logging
from .ai_service_factory import AIServiceFactory

logger = logging.getLogger(__name__)


class AIEnhancedRecommendationEngine(RecommendationEngine):
    """AI增强的推荐引擎 - 支持多时间维度"""

    def __init__(self, db: Session, user_id: int, ai_provider: str = "tongyi"):
        super().__init__(db, user_id)
        self.ai_service = AIServiceFactory.create_service(ai_provider)
        self.use_ai = self.ai_service is not None
        logger.info(f"AI服务初始化: 使用{ai_provider}，可用性: {self.use_ai}")

    async def generate_ai_recommendations(
            self,
            period: schemas.AnalysisPeriod = schemas.AnalysisPeriod.current_month,
            start_date: schemas.date = None,
            end_date: schemas.date = None
    ) -> List[schemas.RecommendationCreate]:
        """使用AI生成推荐建议 - 支持多时间维度"""

        logger.info(f"开始生成AI建议，AI服务可用: {self.use_ai}，分析周期: {period}")

        if not self.use_ai:
            logger.warning("AI服务不可用，回退到规则引擎")
            return self.generate_recommendations(period, start_date, end_date)

        try:
            # 获取用户数据
            user = self.db.query(models.User).filter(models.User.id == self.user_id).first()
            if not user:
                logger.warning("未找到用户，无法生成AI建议")
                return []

            # 获取能耗分析数据（支持多时间维度）
            from .data_processing import get_energy_analysis
            energy_analysis = get_energy_analysis(self.db, self.user_id, period, start_date, end_date)

            logger.info(f"获取到{energy_analysis.analysis_period}能耗分析数据: 总能耗{energy_analysis.total_consumption}kWh")

            # 添加详细的类型和属性检查
            logger.info(f"energy_analysis 对象类型: {type(energy_analysis)}")

            # 检查数据有效性
            if energy_analysis.total_consumption <= 0:
                logger.warning("能耗数据为零或无效，无法生成AI建议")
                return self._generate_fallback_recommendations()

            # 构建时间范围信息
            time_range_info = self._build_time_range_info(energy_analysis)

            # 构建用户数据
            user_data = {
                "family_size": user.family_size,
                "house_size": user.house_size,
                "full_name": user.full_name,
                "season": self._get_current_season(),
                "analysis_period": energy_analysis.analysis_period,
                "period_days": energy_analysis.period_days,
                "start_date": energy_analysis.start_date.isoformat() if energy_analysis.start_date else None,
                "end_date": energy_analysis.end_date.isoformat() if energy_analysis.end_date else None,
                "time_range_description": time_range_info["description"]
            }

            # 转换能耗数据为字典
            energy_data = {
                "total_consumption": energy_analysis.total_consumption,
                "average_daily_consumption": energy_analysis.average_daily_consumption,
                "cost_analysis": energy_analysis.cost_analysis,
                "comparison_with_benchmark": energy_analysis.comparison_with_benchmark,
                "device_breakdown": energy_analysis.device_breakdown,
                "monthly_trend": energy_analysis.monthly_trend,
                "period_comparison": energy_analysis.period_comparison,
                "time_range": time_range_info
            }

            # 使用AI分析能耗
            logger.info("开始调用AI分析能耗...")
            analysis_result = await self.ai_service.analyze_energy_consumption(
                user_data, energy_data
            )

            logger.info(f"AI分析结果: {analysis_result}")

            if "error" in analysis_result:
                logger.error(f"AI分析失败: {analysis_result['error']}")
                return self.generate_recommendations(period, start_date, end_date)

            # 使用AI生成建议
            logger.info("开始调用AI生成建议...")
            ai_recommendations = await self.ai_service.generate_recommendations(
                analysis_result
            )

            logger.info(f"AI生成建议数量: {len(ai_recommendations)}")

            # 转换为系统推荐格式
            recommendations = []
            for ai_rec in ai_recommendations:
                # recommendation = self._convert_ai_recommendation(ai_rec)
                recommendation = self._convert_ai_recommendation(ai_rec, energy_analysis=energy_analysis)
                if recommendation:
                    recommendations.append(recommendation)

            logger.info(f"转换后的AI建议数量: {len(recommendations)}")

            # 如果AI没有生成建议，回退到规则引擎
            if not recommendations:
                logger.warning("AI未生成有效建议，回退到规则引擎")
                return self.generate_recommendations(period, start_date, end_date)

            # 合并AI建议和规则建议
            rule_based_recommendations = self.generate_recommendations(period, start_date, end_date)
            logger.info(f"规则引擎生成建议数量: {len(rule_based_recommendations)}")

            all_recommendations = recommendations + rule_based_recommendations

            # 去重和排序
            return self._deduplicate_and_rank(all_recommendations)

        except Exception as e:
            logger.error(f"AI推荐生成失败: {e}")
            # 出错时回退到规则引擎
            return self.generate_recommendations(period, start_date, end_date)

    def _build_time_range_info(self, energy_analysis: schemas.EnergyAnalysis) -> Dict:
        """构建时间范围信息"""
        start_date = energy_analysis.start_date
        end_date = energy_analysis.end_date

        if start_date and end_date:
            if start_date.year == end_date.year and start_date.month == end_date.month:
                # 单月分析
                description = f"{start_date.strftime('%Y年%m月')}"
            else:
                # 多个月份分析
                description = f"{start_date.strftime('%Y年%m月')}至{end_date.strftime('%Y年%m月')}"

            # 计算总天数
            total_days = (end_date - start_date).days + 1

            return {
                "description": description,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_days": total_days,
                "period_type": "monthly" if total_days <= 31 else "long_term"
            }
        else:
            return {
                "description": energy_analysis.analysis_period,
                "period_type": "unknown"
            }

    def _generate_fallback_recommendations(self) -> List[schemas.RecommendationCreate]:
        """生成回退建议（当数据不足时）"""
        logger.info("生成回退建议（数据不足）")

        return [
            schemas.RecommendationCreate(
                title="完善能耗数据",
                description="当前能耗数据不足，建议先录入更多的能耗读数以获得准确的节能建议。",
                category=schemas.RecommendationCategory.other,
                estimated_saving=0,
                estimated_cost_saving=0,
                implementation_difficulty=schemas.DifficultyLevel.low,
                source="rule_based"
            ),
            schemas.RecommendationCreate(
                title="通用节能建议",
                description="建议养成随手关灯、合理使用家电的良好习惯。",
                category=schemas.RecommendationCategory.lifestyle,
                estimated_saving=15.0,
                estimated_cost_saving=7.5,
                implementation_difficulty=schemas.DifficultyLevel.low,
                source="rule_based"
            )
        ]

    def _convert_ai_recommendation(self, ai_rec: Dict, energy_analysis: schemas.EnergyAnalysis) -> schemas.RecommendationCreate:
        """转换AI建议为系统格式 - 添加时间范围信息"""

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

            # 构建时间范围描述
            time_range_desc = self._build_time_range_info(energy_analysis)["description"]

            return schemas.RecommendationCreate(
                title=ai_rec.get("title", "节能建议"),
                description=ai_rec.get("description", ""),
                category=category,
                estimated_saving=ai_rec.get("estimated_saving", 0),
                estimated_cost_saving=ai_rec.get("estimated_cost_saving", 0),
                implementation_difficulty=difficulty,
                source="ai_based",
                analysis_period=energy_analysis.analysis_period,
                analysis_start_date=energy_analysis.start_date,
                analysis_end_date=energy_analysis.end_date
            )

        except Exception as e:
            logger.error(f"转换AI建议失败: {e}")
            return None
            # return self.generate_recommendations()

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