import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.auth import (
    create_customer_session,
    get_current_customer,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.email import (
    send_customer_registration_confirmation,
    send_customer_registration_otp,
)
from app.models import Customer, CustomerAddress, CustomerRegistration, CustomerSession
from app.schemas import (
    CustomerAddressCreate,
    CustomerAddressRead,
    CustomerAddressUpdate,
    CustomerLogin,
    CustomerOrderRead,
    CustomerRead,
    CustomerRegister,
    CustomerRegistrationEmail,
    CustomerRegistrationStarted,
    CustomerRegistrationVerify,
    CustomerSessionRead,
    CustomerUpdate,
)

router = APIRouter(prefix="/customers", tags=["customers"])
REGISTRATION_OTP_LIFETIME = timedelta(minutes=10)
REGISTRATION_OTP_RESEND_DELAY = timedelta(seconds=60)
REGISTRATION_OTP_MAX_ATTEMPTS = 5


def _registration_otp_hash(otp: str) -> str:
    return hash_password(otp)


def _lock_customer_registration(session: Session, email: str) -> None:
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtextextended(:email, 0))"),
        {"email": email},
    )


@router.post(
    "/register",
    response_model=CustomerRegistrationStarted,
    status_code=status.HTTP_202_ACCEPTED,
)
def register_customer(
    customer_data: CustomerRegister,
    session: Session = Depends(get_session),
) -> CustomerRegistrationStarted:
    _lock_customer_registration(session, customer_data.email)

    existing = session.exec(
        select(Customer).where(Customer.email == customer_data.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    registration = session.exec(
        select(CustomerRegistration).where(
            CustomerRegistration.email == customer_data.email
        )
    ).first()
    now = datetime.now(timezone.utc)
    if registration and registration.lastSentAt:
        last_sent_at = registration.lastSentAt
        if last_sent_at.tzinfo is None:
            last_sent_at = last_sent_at.replace(tzinfo=timezone.utc)
        if now - last_sent_at < REGISTRATION_OTP_RESEND_DELAY:
            raise HTTPException(
                status_code=429,
                detail="A verification code was just sent. Please wait before requesting another.",
            )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    if not send_customer_registration_otp(
        customer_data.email,
        customer_data.name,
        otp,
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="We could not send your verification code. Please try again later.",
        )

    password_hash = hash_password(customer_data.password)
    otp_hash = _registration_otp_hash(otp)
    if registration is None:
        registration = CustomerRegistration(
            name=customer_data.name,
            email=customer_data.email,
            phone=customer_data.phone,
            passwordHash=password_hash,
            otpHash=otp_hash,
            expiresAt=now + REGISTRATION_OTP_LIFETIME,
            lastSentAt=now,
        )
    else:
        registration.name = customer_data.name
        registration.phone = customer_data.phone
        registration.passwordHash = password_hash
        registration.otpHash = otp_hash
        registration.expiresAt = now + REGISTRATION_OTP_LIFETIME
        registration.attempts = 0
        registration.lastSentAt = now

    session.add(registration)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        registration = session.exec(
            select(CustomerRegistration).where(
                CustomerRegistration.email == customer_data.email
            )
        ).first()
        if registration is None:
            raise

        registration.name = customer_data.name
        registration.phone = customer_data.phone
        registration.passwordHash = password_hash
        registration.otpHash = otp_hash
        registration.expiresAt = now + REGISTRATION_OTP_LIFETIME
        registration.attempts = 0
        registration.lastSentAt = now
        session.add(registration)
        session.commit()

    return CustomerRegistrationStarted(
        email=customer_data.email,
        message="Verification code sent to your email.",
    )


@router.post("/register/verify", response_model=CustomerSessionRead)
def verify_customer_registration(
    verify_data: CustomerRegistrationVerify,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
) -> CustomerSessionRead:
    registration = session.exec(
        select(CustomerRegistration).where(
            CustomerRegistration.email == verify_data.email
        )
    ).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="No pending registration was found")

    now = datetime.now(timezone.utc)
    expires_at = registration.expiresAt
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise HTTPException(status_code=400, detail="Verification code expired. Request a new code.")
    if registration.attempts >= REGISTRATION_OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts. Request a new code.")

    if not verify_password(verify_data.otp, registration.otpHash):
        registration.attempts += 1
        session.add(registration)
        session.commit()
        raise HTTPException(status_code=400, detail="Invalid verification code")

    existing = session.exec(
        select(Customer).where(Customer.email == registration.email)
    ).first()
    if existing:
        session.delete(registration)
        session.commit()
        raise HTTPException(status_code=409, detail="Email already registered")

    customer = Customer(
        name=registration.name,
        email=registration.email,
        phone=registration.phone,
        passwordHash=registration.passwordHash,
        status="active",
    )
    session.add(customer)
    session.delete(registration)
    session.commit()
    session.refresh(customer)

    token, token_expires_at = create_customer_session(session, customer)
    session.commit()
    session.refresh(customer)
    background_tasks.add_task(
        send_customer_registration_confirmation,
        customer.email,
        customer.name,
    )

    return CustomerSessionRead(
        accessToken=token,
        tokenType="bearer",
        expiresAt=token_expires_at,
        customer=CustomerRead.model_validate(customer),
    )


@router.post("/register/resend", response_model=CustomerRegistrationStarted)
def resend_customer_registration_otp(
    request_data: CustomerRegistrationEmail,
    session: Session = Depends(get_session),
) -> CustomerRegistrationStarted:
    _lock_customer_registration(session, request_data.email)

    registration = session.exec(
        select(CustomerRegistration).where(
            CustomerRegistration.email == request_data.email
        )
    ).first()
    if registration is None:
        raise HTTPException(status_code=404, detail="No pending registration was found")

    now = datetime.now(timezone.utc)
    if registration.lastSentAt:
        last_sent_at = registration.lastSentAt
        if last_sent_at.tzinfo is None:
            last_sent_at = last_sent_at.replace(tzinfo=timezone.utc)
        if now - last_sent_at < REGISTRATION_OTP_RESEND_DELAY:
            raise HTTPException(
                status_code=429,
                detail="Please wait 60 seconds between verification code requests.",
            )

    otp = f"{secrets.randbelow(1_000_000):06d}"
    if not send_customer_registration_otp(
        registration.email,
        registration.name,
        otp,
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="We could not send your verification code. Please try again later.",
        )

    registration.otpHash = _registration_otp_hash(otp)
    registration.expiresAt = now + REGISTRATION_OTP_LIFETIME
    registration.attempts = 0
    registration.lastSentAt = now
    session.add(registration)
    session.commit()
    return CustomerRegistrationStarted(
        email=registration.email,
        message="A new verification code was sent to your email.",
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
