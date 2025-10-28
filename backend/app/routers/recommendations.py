from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from .. import schemas, dependencies, models
from ..database import get_db
from ..crud import recommendations as recommendations_crud

from ..services.ai_enhanced_recommendation_engine import AIEnhancedRecommendationEngine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# 获取建议 by 当前用户
@router.get("/my-recommendations", response_model=List[schemas.RecommendationResponse])
def read_recommendations(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    category: Optional[schemas.RecommendationCategory] = None,
    is_implemented: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return recommendations_crud.get_recommendations_by_user(
        db,
        user_id=current_user.id,
        category=category,
        is_implemented=is_implemented,
        skip=skip,
        limit=limit
    )

# 新增能耗建议
@router.post("/", response_model=schemas.RecommendationResponse)
def create_recommendation(
    recommendation: schemas.RecommendationCreate,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return recommendations_crud.create_recommendation(db, recommendation=recommendation, user_id=current_user.id)

# 更新能耗建议
@router.put("/{recommendation_id}", response_model=schemas.RecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_update: schemas.RecommendationUpdate,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return recommendations_crud.update_recommendation(
        db,
        recommendation_id=recommendation_id,
        recommendation_update=recommendation_update,
        user_id=current_user.id
    )

# 修改节能建议是否实施状态
@router.post("/{recommendation_id}/implement")
def mark_recommendation_implemented(
    recommendation_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    recommendation = recommendations_crud.update_recommendation(
        db,
        recommendation_id=recommendation_id,
        recommendation_update=schemas.RecommendationUpdate(is_implemented=True),
        user_id=current_user.id
    )

    return recommendation



@router.post("/ai/generate", response_model=List[schemas.RecommendationResponse])
async def generate_ai_recommendations(
        user_id: int,
        ai_provider: str = "tongyi",
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db)
):
    """使用AI生成节能建议"""

    try:
        engine = AIEnhancedRecommendationEngine(db, user_id, ai_provider)
        ai_recommendations = await engine.generate_ai_recommendations()

        # 保存AI建议到数据库
        saved_recommendations = []
        for rec_data in ai_recommendations:
            # 标记为AI生成
            db_rec = recommendations_crud.create_recommendation(db, rec_data, user_id)
            db_rec.source = "ai_based"
            db.commit()
            db.refresh(db_rec)
            saved_recommendations.append(db_rec)

        return saved_recommendations

    except Exception as e:
        logger.error(f"AI建议生成失败: {e}")
        raise HTTPException(status_code=500, detail="AI建议生成失败")


@router.get("/sources", response_model=Dict)
def get_recommendation_sources(user_id: int, db: Session = Depends(get_db)):
    """获取建议来源统计"""

    from sqlalchemy import func

    # 统计不同来源的建议数量
    source_stats = db.query(
        models.Recommendation.source,
        func.count(models.Recommendation.id).label('count')
    ).filter(
        models.Recommendation.user_id == user_id
    ).group_by(
        models.Recommendation.source
    ).all()

    # 获取可用的AI提供商
    from ..services.ai_service_factory import AIServiceFactory
    available_providers = AIServiceFactory.get_available_providers()

    return {
        "source_stats": {stat.source: stat.count for stat in source_stats},
        "available_ai_providers": available_providers
    }