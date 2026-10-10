import os
import unittest
from decimal import Decimal
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")

from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine

from app.models import InventoryStock, Product, RestaurantSettings, Tenant
from app.routers.public import public_menu, public_session, public_site


class PublicStorefrontTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        SQLModel.metadata.create_all(
            self.engine,
            tables=[
                Tenant.__table__,
                Product.__table__,
                InventoryStock.__table__,
                RestaurantSettings.__table__,
            ],
        )
        self.session = Session(self.engine)
        self.restaurant_a = Tenant(name="Restaurant A", slug="restaurant-a")
        self.restaurant_b = Tenant(name="Restaurant B", slug="restaurant-b")
        self.session.add_all([self.restaurant_a, self.restaurant_b])
        self.session.commit()

        products = [
            Product(
                tenantId=self.restaurant_a.id,
                name="A published",
                category="Mains",
                price=Decimal("10.00"),
                status="active",
            ),
            Product(
                tenantId=self.restaurant_a.id,
                name="A out of stock",
                category="Mains",
                price=Decimal("11.00"),
                status="active",
            ),
            Product(
                tenantId=self.restaurant_b.id,
                name="B published",
                category="Pizza",
                price=Decimal("12.00"),
                status="active",
            ),
        ]
        self.session.add_all(products)
        self.session.flush()
        self.session.add_all([
            InventoryStock(
                tenantId=self.restaurant_a.id,
                productId=products[0].id,
                quantity=2,
            ),
            InventoryStock(
                tenantId=self.restaurant_a.id,
                productId=products[1].id,
                quantity=0,
            ),
            InventoryStock(
                tenantId=self.restaurant_b.id,
                productId=products[2].id,
                quantity=3,
            ),
        ])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_explicit_slug_isolates_only_published_products(self):
        public_session("restaurant-a", self.session)
        products_a = public_menu(self.session)
        self.assertEqual([product.name for product in products_a], ["A published"])

        other_session = Session(self.engine)
        public_session("restaurant-b", other_session)
        products_b = public_menu(other_session)
        self.assertEqual([product.name for product in products_b], ["B published"])
        self.assertTrue(
            {product.id for product in products_a}.isdisjoint(
                product.id for product in products_b
            )
        )
        other_session.close()

    def test_configured_default_resolves_and_is_returned_by_site(self):
        with patch.dict(os.environ, {"PUBLIC_STOREFRONT_SLUG": "restaurant-b"}):
            public_session(None, self.session)
            site = public_site(self.session)
            self.assertEqual(site.tenantSlug, "restaurant-b")
            self.assertEqual([product.name for product in public_menu(self.session)], ["B published"])

    def test_missing_default_does_not_fall_back_to_another_tenant(self):
        with patch.dict(os.environ, {"PUBLIC_STOREFRONT_SLUG": ""}):
            with self.assertRaises(HTTPException) as raised:
                public_session(None, self.session)
        self.assertEqual(raised.exception.status_code, 503)

    def test_unknown_slug_returns_not_found(self):
        with self.assertRaises(HTTPException) as raised:
            public_session("unknown-workspace", self.session)
        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
