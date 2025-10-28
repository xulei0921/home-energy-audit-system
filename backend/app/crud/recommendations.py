from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas, models

# 获取节能建议 by 当前用户
def get_recommendations_by_user(
    db: Session,
    user_id: int,
    category: Optional[schemas.RecommendationCategory] = None,
    is_implemented: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    query = db.query(models.Recommendation).filter(models.Recommendation.user_id == user_id)

    if category:
        query = query.filter(models.Recommendation.category == category)

    if is_implemented is not None:
        query = query.filter(models.Recommendation.is_implemented == is_implemented)

    return query.offset(skip).limit(limit).all()

# 新增节能建议
def create_recommendation(db: Session, recommendation: schemas.RecommendationCreate, user_id: int):
    db_recommendation = models.Recommendation(**recommendation.model_dump(), user_id=user_id)

    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)

    return db_recommendation

# 更新节能建议
def update_recommendation(db: Session, recommendation_id: int, recommendation_update: schemas.RecommendationUpdate, user_id: int):
    db_recommendation = db.query(models.Recommendation).filter(models.Recommendation.id == recommendation_id)

    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="建议不存在"
        )

    if db_recommendation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限更新此建议"
        )

    update_data = recommendation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recommendation, field, value)

    db.commit()
    db.refresh(db_recommendation)

    return db_recommendation