from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status

# 获取设备 by 当前用户
def get_devices_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Device).filter(models.Device.user_id == user_id).offset(skip).limit(limit).all()

# 获取设备 by ID
def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

# 新增设备
def create_device(db: Session, device: schemas.DeviceCreate, user_id: int):
    # 创建设备对象
    db_device = models.Device(**device.model_dump(), user_id=user_id)

    # 保存设备
    db.add(db_device)
    db.commit()
    db.refresh(db_device)

    return db_device

# 更新设备
def update_device(db: Session, device_id: int, device_update: schemas.DeviceUpdate, user_id: int):
    db_device = get_device(db, device_id)

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 检查权限（只能更新自己的设备）
    if db_device.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此物品"
        )

    # 更新字段
    update_data = device_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_device, key, value)

    db.commit()
    db.refresh(db_device)

    return db_device

# 删除设备
def delete_device(db: Session, device_id: int, user_id: int):
    db_device = get_device(db, device_id)

    if not db_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在"
        )

    # 检查权限
    if db_device.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除此设备"
        )

    db.delete(db_device)
    db.commit()

    return db_device