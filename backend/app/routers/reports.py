from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models import Order
from app.schemas import (
    SalesReportBreakdown,
    SalesReportDay,
    SalesReportProduct,
    SalesReportRead,
    SalesReportSummary,
    SalesReportTransaction,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales", response_model=SalesReportRead)
def get_sales_report(
    period: Literal["today", "week", "month", "custom"] = Query(
        default="week", alias="range"
    ),
    start_date: date | None = Query(default=None, alias="startDate"),
    end_date: date | None = Query(default=None, alias="endDate"),
    session: Session = Depends(get_session),
) -> SalesReportRead:
    today = datetime.now().astimezone().date()
    if period == "today":
        report_start = report_end = today
    elif period == "week":
        report_start, report_end = today - timedelta(days=6), today
    elif period == "month":
        report_start, report_end = today - timedelta(days=29), today
    else:
        report_start = start_date or today
        report_end = end_date or today

    if report_start > report_end:
        raise HTTPException(status_code=422, detail="startDate must be on or before endDate")
    if (report_end - report_start).days > 365:
        raise HTTPException(status_code=422, detail="Report date range cannot exceed 366 days")

    local_timezone = datetime.now().astimezone().tzinfo
    start_at = datetime.combine(report_start, time.min, tzinfo=local_timezone)
    end_at = datetime.combine(report_end + timedelta(days=1), time.min, tzinfo=local_timezone)
    orders = list(
        session.exec(
            select(Order)
            .where(Order.createdAt >= start_at, Order.createdAt < end_at)
            .where(Order.status.in_(["paid", "refunded"]))
            .order_by(Order.createdAt.desc())
        ).all()
    )

    paid_orders = [order for order in orders if order.status == "paid"]
    refunded_orders = [order for order in orders if order.status == "refunded"]
    gross_sales = sum((order.total for order in paid_orders), Decimal("0.00"))
    refunds = sum((order.total for order in refunded_orders), Decimal("0.00"))
    discounts = sum((order.discount for order in paid_orders), Decimal("0.00"))
    daily_sales: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    daily_refunds: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    daily_counts: dict[str, int] = defaultdict(int)
    product_quantities: dict[str, int] = defaultdict(int)
    product_sales: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    payment_sales: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    payment_counts: dict[str, int] = defaultdict(int)
    channel_sales: dict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
    channel_counts: dict[str, int] = defaultdict(int)

    for order in paid_orders:
        day_key = order.createdAt.astimezone().date().isoformat()
        daily_sales[day_key] += order.total
        daily_counts[day_key] += 1
        payment_sales[order.paymentMethod] += order.total
        payment_counts[order.paymentMethod] += 1
        channel_sales[order.type] += order.total
        channel_counts[order.type] += 1
        for item in order.items:
            name = item["name"]
            quantity = int(item["quantity"])
            product_quantities[name] += quantity
            product_sales[name] += Decimal(str(item["price"])) * quantity

    for order in refunded_orders:
        day_key = order.createdAt.astimezone().date().isoformat()
        daily_refunds[day_key] += order.total

    days = []
    current_day = report_start
    while current_day <= report_end:
        day_key = current_day.isoformat()
        days.append(
            SalesReportDay(
                date=day_key,
                label=current_day.strftime("%b %d"),
                sales=float(daily_sales[day_key]),
                refunds=float(daily_refunds[day_key]),
                orderCount=daily_counts[day_key],
            )
        )
        current_day += timedelta(days=1)

    top_products = [
        SalesReportProduct(name=name, quantity=quantity, sales=float(product_sales[name]))
        for name, quantity in sorted(
            product_quantities.items(), key=lambda product: (-product[1], product[0])
        )[:10]
    ]
    payment_methods = [
        SalesReportBreakdown(name=name, orderCount=count, sales=float(payment_sales[name]))
        for name, count in sorted(payment_counts.items(), key=lambda item: item[0])
    ]
    order_types = [
        SalesReportBreakdown(name=name, orderCount=count, sales=float(channel_sales[name]))
        for name, count in sorted(channel_counts.items(), key=lambda item: item[0])
    ]
    recent_orders = [
        SalesReportTransaction(
            id=order.id,
            createdAt=order.createdAt,
            customer=order.customer,
            type=order.type,
            paymentMethod=order.paymentMethod,
            status=order.status,
            total=float(order.total),
        )
        for order in orders[:100]
    ]

    return SalesReportRead(
        range=period,
        startDate=report_start.isoformat(),
        endDate=report_end.isoformat(),
        summary=SalesReportSummary(
            grossSales=float(gross_sales),
            refunds=float(refunds),
            netSales=float(gross_sales - refunds),
            discounts=float(discounts),
            orderCount=len(paid_orders),
            refundCount=len(refunded_orders),
            averageOrder=float(gross_sales / len(paid_orders)) if paid_orders else 0.0,
        ),
        salesByDay=days,
        topProducts=top_products,
        paymentMethods=payment_methods,
        orderTypes=order_types,
        recentOrders=recent_orders,
    )