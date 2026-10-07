from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth import (
    create_customer_session,
    customer_response,
    get_current_customer,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.models import Customer, CustomerAddress, CustomerSession
from app.schemas import (
    CustomerAddressCreate,
    CustomerAddressRead,
    CustomerAddressUpdate,
    CustomerLogin,
    CustomerOrderRead,
    CustomerRead,
    CustomerRegister,
    CustomerSessionRead,
    CustomerUpdate,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/register", response_model=CustomerSessionRead, status_code=status.HTTP_201_CREATED)
def register_customer(
    customer_data: CustomerRegister,
    session: Session = Depends(get_session),
) -> CustomerSession:
    existing = session.exec(
        select(Customer).where(Customer.email == customer_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    customer = Customer(
        name=customer_data.name,
        email=customer_data.email,
        phone=customer_data.phone,
        passwordHash=hash_password(customer_data.password),
        status="active",
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)

    token, expires_at = create_customer_session(session, customer)
    session.commit()
    session.refresh(customer)

    return CustomerSessionRead(
        accessToken=token,
        tokenType="bearer",
        expiresAt=expires_at,
        customer=CustomerRead.model_validate(customer),
    )


@router.post("/login", response_model=CustomerSessionRead)
def login_customer(
    credentials: CustomerLogin,
    session: Session = Depends(get_session),
) -> CustomerSession:
    customer = session.exec(
        select(Customer).where(Customer.email == credentials.email)
    ).first()
    if customer is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(credentials.password, customer.passwordHash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if customer.status != "active":
        raise HTTPException(status_code=403, detail="Account is inactive")

    token, expires_at = create_customer_session(session, customer)
    session.commit()
    session.refresh(customer)

    return CustomerSessionRead(
        accessToken=token,
        tokenType="bearer",
        expiresAt=expires_at,
        customer=CustomerRead.model_validate(customer),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_customer(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    customer_sessions = session.exec(
        select(CustomerSession).where(
            CustomerSession.customerId == customer.id,
            CustomerSession.revokedAt.is_(None),
        )
    ).all()
    for cs in customer_sessions:
        cs.revokedAt = datetime.now(timezone.utc)
    session.add_all(customer_sessions)
    session.commit()


@router.get("/me", response_model=CustomerRead)
def get_current_customer_profile(
    customer: Customer = Depends(get_current_customer),
):
    return CustomerRead.model_validate(customer)


@router.patch("/me", response_model=CustomerRead)
def update_customer_profile(
    update_data: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    if update_data.name is not None:
        customer.name = update_data.name
    if update_data.phone is not None:
        customer.phone = update_data.phone
    
    session.add(customer)
    session.commit()
    session.refresh(customer)
    
    return CustomerRead.model_validate(customer)


@router.get("/addresses", response_model=list[CustomerAddressRead])
def list_addresses(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    addresses = session.exec(
        select(CustomerAddress).where(CustomerAddress.customerId == customer.id)
    ).all()
    return [CustomerAddressRead.model_validate(addr) for addr in addresses]


@router.post("/addresses", response_model=CustomerAddressRead, status_code=status.HTTP_201_CREATED)
def create_address(
    address_data: CustomerAddressCreate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    # If setting as default, unset other defaults
    if address_data.isDefault:
        existing_addresses = session.exec(
            select(CustomerAddress).where(CustomerAddress.customerId == customer.id)
        ).all()
        for addr in existing_addresses:
            addr.isDefault = False
        session.add_all(existing_addresses)
    
    address = CustomerAddress(
        customerId=customer.id,
        label=address_data.label,
        address=address_data.address,
        zone=address_data.zone,
        isDefault=address_data.isDefault,
    )
    session.add(address)
    session.commit()
    session.refresh(address)
    
    return CustomerAddressRead.model_validate(address)


@router.patch("/addresses/{address_id}", response_model=CustomerAddressRead)
def update_address(
    address_id: int,
    update_data: CustomerAddressUpdate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    address = session.exec(
        select(CustomerAddress).where(
            CustomerAddress.id == address_id,
            CustomerAddress.customerId == customer.id,
        )
    ).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    if update_data.label is not None:
        address.label = update_data.label
    if update_data.address is not None:
        address.address = update_data.address
    if update_data.zone is not None:
        address.zone = update_data.zone
    if update_data.isDefault is not None:
        if update_data.isDefault:
            # Unset other defaults
            existing_addresses = session.exec(
                select(CustomerAddress).where(
                    CustomerAddress.customerId == customer.id,
                    CustomerAddress.id != address_id,
                )
            ).all()
            for addr in existing_addresses:
                addr.isDefault = False
            session.add_all(existing_addresses)
        address.isDefault = update_data.isDefault
    
    session.add(address)
    session.commit()
    session.refresh(address)
    
    return CustomerAddressRead.model_validate(address)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    address = session.exec(
        select(CustomerAddress).where(
            CustomerAddress.id == address_id,
            CustomerAddress.customerId == customer.id,
        )
    ).first()
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    
    session.delete(address)
    session.commit()


@router.get("/orders", response_model=list[CustomerOrderRead])
def list_customer_orders(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    from app.models import Order
    
    orders = session.exec(
        select(Order).where(
            Order.customerId == customer.id,
            Order.source == "website",
        ).order_by(Order.createdAt.desc())
    ).all()
    return [CustomerOrderRead.model_validate(order) for order in orders]
