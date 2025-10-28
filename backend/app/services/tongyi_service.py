import os
from openai import AsyncOpenAI
from typing import Dict, List, Any
import json
from .ai_base_service import AIBaseService
# from ..routers.recommendations import logger
import logging
logger = logging.getLogger(__name__)

class TongYiService(AIBaseService):
    """通义千问服务实现"""

    def __init__(self):
        super().__init__()
        # 从环境变量获取配置
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url = os.getenv("ALI_BASE_URL")
        self.model = os.getenv("DEFAULT_ALI_MODEL", "qwen-plus")

        # 初始化异步客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        logger.info(f"通义千问服务初始化成功，模型: {self.model}")

    async def analyze_energy_consumption(self, user_data: Dict, energy_data: Dict) -> Dict:
        """使用通义千问分析能耗数据"""

        prompt = self.build_analysis_prompt(user_data, energy_data)
        logger.info(f"分析提示词长度: {len(prompt)}")

        try:
            logger.info(f"调用通义千问API, 模型: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的能源管理专家，擅长分析家庭能耗数据并提供专业的节能建议。
请严格按照JSON格式返回分析结果，包含以下字段：
- overall_assessment: 整体评估
- key_insights: 关键发现列表
- efficiency_level: 能效等级(高/中/低)
- main_consumption_sources: 主要能耗来源分析
- seasonal_impact: 季节性影响分析
请确保返回纯JSON格式，不要包含其他文本。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,  # 较低的温度值保证分析结果更稳定可靠
                response_format={"type": "json_object"}  # 要求返回JSON格式
            )

            result = response.choices[0].message.content
            return self.parse_ai_response(result)

        except Exception as e:
            return {"error": f"通义千问分析失败: {str(e)}"}

    async def generate_recommendations(self, analysis_result: Dict) -> List[Dict]:
        """使用通义千问生成节能建议"""

        prompt = self.build_recommendation_prompt(analysis_result)
        logger.info(f"建议生成提示词长度: {len(prompt)}")

        try:
            logger.info(f"调用通义千问生成模型，模型: {self.model}")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的节能顾问，能够提供具体可行的家庭节能建议。
请严格按照JSON格式返回建议列表，包含以下字段：
- recommendations: 建议列表，每个建议包含：
  - title: 建议标题
  - description: 详细描述
  - category: 类别(设备使用/生活习惯/设备升级)
  - estimated_saving: 预计节省能耗(kWh/月)
  - estimated_cost_saving: 预计节省费用(元/月)
  - implementation_difficulty: 实施难度(低/中/高)
  - reasoning: 建议依据
请确保返回纯JSON格式，不要包含其他文本。"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7,  # 稍高的温度值让建议更具创造性
                response_format={"type": "json_object"}  # 要求返回JSON格式
            )

            result = response.choices[0].message.content
            parsed_result = self.parse_ai_response(result)
            logger.info(f"解析后的建议结果: {parsed_result}")

            # 从解析结果中提取建议列表
            return parsed_result.get("recommendations", [])

        except Exception as e:
            print(f"通义千问建议生成失败: {e}")
            return []