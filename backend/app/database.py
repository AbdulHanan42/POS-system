import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import event, inspect, text
from sqlalchemy.orm import with_loader_criteria
from sqlmodel import Session, SQLModel, create_engine

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is required. Copy backend/.env.example to backend/.env "
        "and configure your PostgreSQL credentials."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def tenant_models():
    from app.models import (
        Category,
        Customer,
        CustomerAddress,
        DeliveryZone,
        InventoryMovement,
        InventoryStock,
        ModifierGroup,
        Order,
        Product,
        Purchase,
        RestaurantSettings,
        RestaurantTable,
        StaffMember,
    )

    return (
        Category,
        Customer,
        CustomerAddress,
        DeliveryZone,
        Product,
        RestaurantTable,
        StaffMember,
        RestaurantSettings,
        ModifierGroup,
        InventoryStock,
        InventoryMovement,
        Purchase,
        Order,
    )


@event.listens_for(Session, "do_orm_execute")
def apply_tenant_filter(execute_state) -> None:
    tenant_id = execute_state.session.info.get("tenant_id")
    if tenant_id is None or not execute_state.is_select:
        return
    statement = execute_state.statement
    for model in tenant_models():
        statement = statement.options(
            with_loader_criteria(
                model,
                lambda row: row.tenantId == tenant_id,
                include_aliases=True,
            )
        )
    execute_state.statement = statement


@event.listens_for(Session, "before_flush")
def assign_tenant_on_insert(session, flush_context, instances) -> None:
    tenant_id = session.info.get("tenant_id")
    if tenant_id is None:
        return
    scoped_models = tenant_models()
    for instance in session.new:
        if isinstance(instance, scoped_models):
            instance.tenantId = tenant_id


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def create_db_and_tables() -> None:
    from app.models import (
        AuthSession,
        Category,
        Customer,
        CustomerAddress,
        CustomerSession,
        InventoryMovement,
        InventoryStock,
        ModifierGroup,
        Order,
        Purchase,
        Product,
        RestaurantSettings,
        RestaurantTable,
        StaffMember,
        Tenant,
        UserAccount,
    )

    SQLModel.metadata.create_all(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO tenant (name, slug, created_at) "
                "VALUES (:name, :slug, CURRENT_TIMESTAMP) "
                "ON CONFLICT (slug) DO NOTHING"
            ),
            {"name": "Legacy Workspace", "slug": "legacy-workspace"},
        )
        legacy_tenant_id = connection.execute(
            text("SELECT id FROM tenant WHERE slug = :slug"),
            {"slug": "legacy-workspace"},
        ).scalar_one()

        for model in tenant_models():
            table_name = model.__tablename__
            existing_columns = {
                column["name"]
                for column in inspect(connection).get_columns(table_name)
            }
            if "tenant_id" not in existing_columns:
                connection.execute(
                    text(f'ALTER TABLE "{table_name}" ADD COLUMN tenant_id INTEGER')
                )
            connection.execute(
                text(
                    f'UPDATE "{table_name}" SET tenant_id = :tenant_id '
                    "WHERE tenant_id IS NULL"
                ),
                {"tenant_id": legacy_tenant_id},
            )
            connection.execute(
                text(
                    f'ALTER TABLE "{table_name}" '
                    "ALTER COLUMN tenant_id SET NOT NULL"
                )
            )

        for model in (Category, ModifierGroup):
            table_name = model.__tablename__
            indexes = inspect(connection).get_indexes(table_name)
            for index in indexes:
                if index["unique"] and index["column_names"] == ["name"]:
                    connection.execute(
                        text(f'DROP INDEX IF EXISTS "{index["name"]}"')
                    )
            index_name = f"uq_{table_name}_tenant_name"
            connection.execute(
                text(
                    f'CREATE UNIQUE INDEX IF NOT EXISTS "{index_name}" '
                    f'ON "{table_name}" (tenant_id, name)'
                )
            )

        connection.execute(
            text(
                'CREATE UNIQUE INDEX IF NOT EXISTS "uq_restaurantsettings_tenant_id" '
                'ON "restaurantsettings" (tenant_id)'
            )
        )

        settings_columns = {
            column["name"]
            for column in inspect(connection).get_columns(RestaurantSettings.__tablename__)
        }
        for column_name, column_type in {
            "public_description": "VARCHAR(500) NOT NULL DEFAULT ''",
            "logo_url": "VARCHAR(500) NOT NULL DEFAULT ''",
            "hero_image_url": "VARCHAR(500) NOT NULL DEFAULT ''",
            "opening_hours": "VARCHAR(500) NOT NULL DEFAULT ''",
            "website_enabled": "BOOLEAN NOT NULL DEFAULT TRUE",
            "ordering_open": "BOOLEAN NOT NULL DEFAULT TRUE",
        }.items():
            if column_name not in settings_columns:
                connection.execute(text(
                    f'ALTER TABLE "{RestaurantSettings.__tablename__}" '
                    f'ADD COLUMN "{column_name}" {column_type}'
                ))

        columns = {
            column["name"]
            for column in inspect(connection).get_columns(Order.__tablename__)
        }
        if "kitchen_status" not in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    "ADD COLUMN kitchen_status VARCHAR(20) NOT NULL DEFAULT 'queued'"
                )
            )
        if "discount" not in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    "ADD COLUMN discount NUMERIC(10, 2) NOT NULL DEFAULT 0"
                )
            )
        if "tax_rate" not in columns:
            connection.execute(
                text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    "ADD COLUMN tax_rate NUMERIC(5, 4) NOT NULL DEFAULT 0.1000"
                )
            )
        for column_name, column_type in {
            "customer_phone": "VARCHAR(30)",
            "customer_id": "INTEGER",
            "source": "VARCHAR(20) NOT NULL DEFAULT 'pos'",
            "public_tracking_token": "VARCHAR(64)",
        }.items():
            if column_name not in columns:
                connection.execute(text(
                    f'ALTER TABLE "{Order.__tablename__}" '
                    f'ADD COLUMN "{column_name}" {column_type}'
                ))
        
        # Add foreign key for customer_id if it exists
        if "customer_id" in columns:
            foreign_keys = [fk["constrained_columns"] for fk in inspect(connection).get_foreign_keys(Order.__tablename__)]
            has_customer_fk = any("customer_id" in fk for fk in foreign_keys)
            if not has_customer_fk:
                connection.execute(
                    text(
                        f'ALTER TABLE "{Order.__tablename__}" '
                        'ADD CONSTRAINT fk_order_customer_id FOREIGN KEY ("customer_id") REFERENCES "customer" (id)'
                    )
                )
        
        # Ensure Customer table has proper structure if it exists
        customer_table = "customer"
        if inspect(connection).has_table(customer_table):
            customer_columns = {column["name"] for column in inspect(connection).get_columns(customer_table)}
            
            # Ensure tenant_id column exists for Customer
            if "tenant_id" not in customer_columns:
                connection.execute(text(f'ALTER TABLE "{customer_table}" ADD COLUMN tenant_id INTEGER NOT NULL DEFAULT 1'))
                connection.execute(text(f'UPDATE "{customer_table}" SET tenant_id = 1 WHERE tenant_id IS NULL'))
                connection.execute(text(f'ALTER TABLE "{customer_table}" ALTER COLUMN tenant_id SET NOT NULL'))
                
                # Add foreign key for tenant_id
                customer_fks = [fk["constrained_columns"] for fk in inspect(connection).get_foreign_keys(customer_table)]
                has_tenant_fk = any("tenant_id" in fk for fk in customer_fks)
                if not has_tenant_fk:
                    connection.execute(
                        text(
                            f'ALTER TABLE "{customer_table}" '
                            'ADD CONSTRAINT fk_customer_tenant_id FOREIGN KEY (tenant_id) REFERENCES tenant (id)'
                        )
                    )
                
                # Add unique constraint for tenant_id + email
                indexes = inspect(connection).get_indexes(customer_table)
                has_unique_constraint = any(idx.get("unique") and set(idx.get("column_names", [])) == {"tenant_id", "email"} for idx in indexes)
                if not has_unique_constraint:
                    connection.execute(
                        text(
                            'CREATE UNIQUE INDEX IF NOT EXISTS "uq_customer_tenant_email" '
                            f'ON "{customer_table}" (tenant_id, email)'
                        )
                    )
        
        # Ensure CustomerSession table has proper structure if it exists
        customer_session_table = "customersession"
        if inspect(connection).has_table(customer_session_table):
            session_columns = {column["name"] for column in inspect(connection).get_columns(customer_session_table)}
            
            # Add foreign key for customer_id if it doesn't exist
            session_fks = [fk["constrained_columns"] for fk in inspect(connection).get_foreign_keys(customer_session_table)]
            has_customer_fk = any("customer_id" in fk for fk in session_fks)
            if not has_customer_fk:
                connection.execute(
                    text(
                        f'ALTER TABLE "{customer_session_table}" '
                        'ADD CONSTRAINT fk_customersession_customer_id FOREIGN KEY ("customer_id") REFERENCES "customer" (id)'
                    )
                )
