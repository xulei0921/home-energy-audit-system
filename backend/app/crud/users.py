from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from .. import models, schemas
from ..utils import get_password_hash, verify_password

# 获取用户 by ID
def get_user_by_id(db: Session, id: int):
    """根据ID获取用户"""
    return db.query(models.User).filter(models.User.id == id).first()

# 获取用户 by 用户名
def get_user_by_username(db: Session, username: str):
    """根据用户名获取用户"""
    return db.query(models.User).filter(models.User.username == username).first()

# 获取用户 by 邮箱
def get_user_by_email(db: Session, email: str):
    """根据邮箱获取用户"""
    return db.query(models.User).filter(models.User.email == email).first()

# 创建用户
def create_user(db: Session, user: schemas.UserCreate):
    """创建新用户"""
    # 检查用户名是否已存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户对象
    db_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = get_password_hash(user.password),
        full_name = user.full_name,
        family_size = user.family_size,
        house_size = user.house_size
    )

    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

# 验证用户
def authenticate_user(db: Session, username: str, password: str):
    """验证用户凭据"""
    user = get_user_by_username(db, username)

    if not user:
        return False

    if not verify_password(password, user.hashed_password):
        return False

    return user

# 更新用户信息
def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    """更新用户信息"""
    db_user = get_user_by_id(db, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user