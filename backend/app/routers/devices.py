from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, dependencies
from ..database import get_db
from ..crud import devices as devices_crud

router = APIRouter()

# 获取设备 by 当前用户
@router.get("/my-devices", response_model=List[schemas.DeviceResponse])
def read_devices(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # devices = crud.get_devices_by_user(db, user_id=user_id, skip=skip, limit=limit)
    devices = devices_crud.get_devices_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return devices

# 新增设备
@router.post("/", response_model=schemas.DeviceResponse)
def create_device(
    device: schemas.DeviceCreate,
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: Session = Depends(get_db)
):
    return devices_crud.create_device(db, device=device, user_id=current_user.id)

# 获取设备 by ID
@router.get("/{device_id}", response_model=schemas.DeviceResponse)
def read_device(
    device_id: int,
    db: Session = Depends(get_db)
):
    db_device = devices_crud.get_device(db, device_id=device_id)

    if db_device is None:
        raise HTTPException(status_code=404, detail="设备不存在")

    return db_device

# 更新设备
@router.put("/{device_id}", response_model=schemas.DeviceResponse)
def update_device(
    device_id: int,
    device_update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    return devices_crud.update_device(db, device_id=device_id, device_update=device_update, user_id=current_user.id)

@router.delete("/{device_id}")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user)
):
    devices_crud.delete_device(db, device_id=device_id, user_id=current_user.id)