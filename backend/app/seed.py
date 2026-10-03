from sqlmodel import Session, select

from app.database import engine
from app.models import Category, Product, RestaurantTable

DEFAULT_PRODUCTS = [
    {
        "name": "Classic Burger",
        "category": "Mains",
        "price": 12.50,
        "status": "active",
        "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=640&q=80",
        "description": "Chargrilled beef, cheddar, lettuce, tomato, and house sauce.",
    },
    {
        "name": "Margherita Pizza",
        "category": "Pizza",
        "pizzaCategory": "Regular",
        "price": 14.00,
        "prices": {"small": 10.00, "medium": 14.00, "large": 18.00},
        "status": "active",
        "image": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=640&q=80",
        "description": "San Marzano tomato, mozzarella, basil, and olive oil.",
    },
    {
        "name": "Truffle Mushroom Pizza",
        "category": "Pizza",
        "pizzaCategory": "Signature",
        "price": 18.00,
        "prices": {"small": 14.00, "medium": 18.00, "large": 23.00},
        "status": "active",
        "image": "https://images.unsplash.com/photo-1579751626657-72bc17010498?w=640&q=80",
        "description": "Wild mushrooms, truffle cream, mozzarella, and fresh herbs.",
    },
    {
        "name": "Caesar Salad",
        "category": "Starters",
        "price": 8.50,
        "status": "active",
        "image": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=640&q=80",
        "description": "Crisp romaine, parmesan, croutons, and Caesar dressing.",
    },
    {
        "name": "Iced Tea",
        "category": "Drinks",
        "price": 3.50,
        "status": "inactive",
        "image": "https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=640&q=80",
        "description": "Fresh brewed black tea served over ice with lemon.",
    },
]

DEFAULT_TABLES = [
    {"name": "Table 1", "seats": 2, "status": "available"},
    {"name": "Table 2", "seats": 4, "status": "occupied"},
    {"name": "Table 3", "seats": 6, "status": "reserved"},
]

DEFAULT_CATEGORIES = [
    {"name": "Starters", "description": "Small plates and appetizers."},
    {"name": "Mains", "description": "Main courses."},
    {"name": "Pizza", "description": "Pizza with size-based pricing.", "isPizza": True},
    {"name": "Desserts", "description": "Sweet finishes."},
    {"name": "Drinks", "description": "Hot and cold beverages."},
]


def seed_products() -> None:
    with Session(engine) as session:
        for product_data in DEFAULT_PRODUCTS:
            existing = session.exec(
                select(Product).where(Product.name == product_data["name"])
            ).first()
            if existing is None:
                session.add(Product(**product_data))
        session.commit()


def seed_tables() -> None:
    with Session(engine) as session:
        if session.exec(select(RestaurantTable)).first() is None:
            session.add_all(RestaurantTable(**table_data) for table_data in DEFAULT_TABLES)
            session.commit()


def seed_categories() -> None:
    with Session(engine) as session:
        if session.exec(select(Category)).first() is not None:
            return

        category_data = list(DEFAULT_CATEGORIES)
        for product in session.exec(select(Product)).all():
            if not any(
                item["name"].casefold() == product.category.casefold()
                for item in category_data
            ):
                category_data.append({"name": product.category})

        for item in category_data:
            session.add(Category(**item))
        session.commit()