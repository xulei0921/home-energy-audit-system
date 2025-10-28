import os
from typing import Optional
from .ai_base_service import AIBaseService
from .tongyi_service import TongYiService  # 新增导入


# ... 可以注释或删除其他付费服务的导入

class AIServiceFactory:
    """AI服务工厂"""

    @staticmethod
    def create_service(provider: str = "tongyi") -> Optional[AIBaseService]:  # 默认改为tongyi
        """创建AI服务实例"""

        # 优先使用通义千问
        if provider == "tongyi" and os.getenv("DASHSCOPE_API_KEY"):
            return TongYiService()
        # 注释掉原有的付费服务选项
        # elif provider == "openai" and os.getenv("OPENAI_API_KEY"):
        #    return OpenAIService()
        else:
            # 默认回退到通义千问
            if os.getenv("DASHSCOPE_API_KEY"):
                return TongYiService()

        return None

    @staticmethod
    def get_available_providers() -> list:
        """获取可用的AI服务提供商"""
        providers = []
        if os.getenv("DASHSCOPE_API_KEY"):
            providers.append("tongyi")  # 添加通义千问
        # 注释掉其他付费服务
        # if os.getenv("OPENAI_API_KEY"):
        #     providers.append("openai")
        return providers

    @staticmethod
    def get_provider_info() -> dict:
        """获取提供商信息"""
        return {
            "tongyi": {
                "name": "阿里云通义千问",
                "type": "优惠付费",
                "description": "阿里云提供，新用户有免费额度，成本效益高",
                "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
            }
        }