import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class AIBaseService(ABC):
    """AI服务基类"""

    def __init__(self):
        self.max_retries = 3  # 最大重试次数
        self.timeout = 30   # 超时时间（秒）

    @abstractmethod
    async def analyze_energy_consumption(self, user_data: Dict, energy_data: Dict) -> Dict:
        """分析能耗数据"""
        pass

    @abstractmethod
    async def generate_recommendations(self, analysis_result: Dict) -> List[Dict]:
        """生成节能建议"""
        pass

    def build_analysis_prompt(self, user_data: Dict, energy_data: Dict) -> str:
        """构建能耗分析提示词"""

        # 用户基本信息
        user_info = f"""
用户信息:
- 家庭人数: {user_data.get('family_size', 1)}人
- 房屋面积: {user_data.get('house_size', 0)}平方米
- 所在季节: {user_data.get('season', '未知')}
"""

        # 能耗数据
        energy_info = f"""
能耗数据:
- 本月总能耗: {energy_data.get('total_consumption', 0):.1f} kWh
- 日均能耗: {energy_data.get('average_daily_consumption', 0):.1f} kWh
- 电费估算: ¥{energy_data.get('cost_analysis', 0):.0f}
- 基准对比: {energy_data.get('comparison_with_benchmark', 0):.1f}%
"""

        # 设备数据
        devices_info = "设备能耗分布:\n"
        for device in energy_data.get('device_breakdown', []):
            devices_info += f"- {device['device_name']}({device['device_type']}): {device['consumption']:.1f} kWh\n"

        # 趋势数据
        trend_info = "月度趋势:\n"
        for trend in energy_data.get('monthly_trend', [])[-3:]:  # 最近3个月
            trend_info += f"- {trend['period']}: {trend['consumption']:.1f} kWh\n"

        prompt = f"""
请作为能源管理专家，分析以下家庭能耗数据并提供专业见解：

{user_info}
{energy_info}
{devices_info}
{trend_info}

请从以下角度进行分析：
1. 整体能效水平评估
2. 主要能耗设备分析
3. 用电习惯识别
4. 季节性影响分析
5. 与同类家庭对比情况

请用JSON格式返回分析结果，包含以下字段：
- overall_assessment: 整体评估
- key_insights: 关键发现列表
- efficiency_level: 能效等级(高/中/低)
- main_consumption_sources: 主要能耗来源分析
- seasonal_impact: 季节性影响分析
"""
        return prompt

    def build_recommendation_prompt(self, analysis_result: Dict) -> str:
        """构建建议生成提示词"""

        prompt = f"""
基于以下能耗分析结果，生成具体可行的节能建议：

分析结果:
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

请生成个性化节能建议，要求：
1. 针对分析中发现的问题
2. 考虑用户家庭实际情况
3. 建议要具体可行
4. 包含预计节能效果
5. 按实施难度分类

请用JSON格式返回建议列表，每个建议包含：
- title: 建议标题
- description: 详细描述
- category: 类别(设备使用/生活习惯/设备升级)
- estimated_saving: 预计节省能耗(kWh/月)
- estimated_cost_saving: 预计节省费用(元/月)
- implementation_difficulty: 实施难度(低/中/高)
- reasoning: 建议依据

返回3-5条最有效的建议。
"""
        return prompt

    def parse_ai_response(self, response: str) -> Dict:
        """解析AI响应"""
        try:
            # 尝试提取JSON部分
            start_idx = response.find('{')  # 找到第一个'{'的位置
            end_idx = response.rfind('}') + 1  # 找到最后一个'}'的位置并+1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]  # 截取JSON字符串
                return json.loads(json_str)     # 解析为字典并返回
            else:
                # 如果没有找到JSON，返回原始响应
                return {"raw_response": response}
        except json.JSONDecodeError as e:
            logger.error(f"解析AI响应失败: {e}")
            return {"error": f"解析失败: {str(e)}", "raw_response": response}