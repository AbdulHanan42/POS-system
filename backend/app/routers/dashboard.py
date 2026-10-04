from collections import defaultdict
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.database import get_session
from app.auth import require_roles
from app.models import Order, Product
from app.schemas import DashboardResponse

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_roles("Administrator", "Manager"))],
)
RANGE_DAYS = {"today": 1, "week": 7, "month": 30}


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    period: Literal["today", "week", "month"] = Query(default="today", alias="range"),
    session: Session = Depends(get_session),
) -> DashboardResponse:
    now = datetime.now(timezone.utc)
    current_start = now - timedelta(days=RANGE_DAYS[period])
    previous_start = current_start - timedelta(days=RANGE_DAYS[period])
    paid_orders = list(
        session.exec(
            select(Order).where(
                Order.status == "paid",
                Order.createdAt >= previous_start,
                Order.createdAt <= now,
            )
        ).all()
    )

    current_orders = [order for order in paid_orders if order.createdAt >= current_start]
    previous_orders = [order for order in paid_orders if order.createdAt < current_start]
    net_sales = sum((order.total for order in current_orders), Decimal("0.00"))
    previous_sales = sum((order.total for order in previous_orders), Decimal("0.00"))
    revenue_change = (
        float((net_sales - previous_sales) / previous_sales * 100)
        if previous_sales
        else 0.0
    )

    sales_by_date: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    for order in current_orders:
        local_day = order.createdAt.astimezone().date()
        sales_by_date[local_day.isoformat()] += order.total

    chart_start = (now.astimezone().date() - timedelta(days=6))
    sales_by_day = []
    for day_offset in range(7):
        day = chart_start + timedelta(days=day_offset)
        sales_by_day.append(
            {
                "date": day.isoformat(),
                "label": day.strftime("%a"),
                "total": float(sales_by_date[day.isoformat()]),
            }
        )

    quantities: dict[str, int] = defaultdict(int)
    for order in current_orders:
        for item in order.items:
            quantities[item["name"]] += int(item["quantity"])
    top_products = [
        {"name": name, "quantity": quantity}
        for name, quantity in sorted(
            quantities.items(), key=lambda product: (-product[1], product[0])
        )[:4]
    ]

    inactive_products = list(
        session.exec(
            select(Product).where(Product.status == "inactive").order_by(Product.name)
        ).all()
    )
    recent_orders = list(
        session.exec(select(Order).order_by(Order.createdAt.desc()).limit(5)).all()
    )

    return DashboardResponse(
        range=period,
        netSales=float(net_sales),
        revenueChange=revenue_change,
        orderCount=len(current_orders),
        dineInOrders=sum(order.type == "Dine in" for order in current_orders),
        averageOrder=float(net_sales / len(current_orders)) if current_orders else 0.0,
        salesByDay=sales_by_day,
        topProducts=top_products,
        lowStockProducts=[{"id": product.id, "name": product.name} for product in inactive_products],
        recentOrders=recent_orders,
    )