"""Operations routers — inventory, warehouses, vendors."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from app.core.deps import DbSession, OptionalUser
from app.schemas.common import OPENAPI_ERROR_RESPONSES
from app.schemas.operations import (
    InventoryBalancesResponse,
    InventorySummaryResponse,
    VendorsResponse,
    WarehousesResponse,
)
from app.services.operations_service import OperationsService

router = APIRouter(
    prefix="/operations",
    tags=["Operations"],
    responses=OPENAPI_ERROR_RESPONSES,
)


@router.get("/inventory/summary", response_model=InventorySummaryResponse)
def inventory_summary(db: DbSession, _user: OptionalUser) -> InventorySummaryResponse:
    return OperationsService(db).inventory_summary()


@router.get("/inventory/balances", response_model=InventoryBalancesResponse)
def inventory_balances(
    db: DbSession,
    _user: OptionalUser,
    limit: Optional[int] = Query(default=100, ge=1, le=500),
) -> InventoryBalancesResponse:
    return OperationsService(db).inventory_balances(limit=limit)


@router.get("/warehouses", response_model=WarehousesResponse)
def list_warehouses(db: DbSession, _user: OptionalUser) -> WarehousesResponse:
    return OperationsService(db).warehouses()


@router.get("/vendors", response_model=VendorsResponse)
def list_vendors(db: DbSession, _user: OptionalUser) -> VendorsResponse:
    return OperationsService(db).vendors()
