from sqlalchemy import text
from modular_system.database.connection import get_engine
from ..models.category import CategoryModel

class CategoryService:
    def __init__(self, module):
        self.module = module

    def get_all(self):
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name FROM categories"))
            return [CategoryModel(id=row[0], name=row[1]) for row in result]

    def create(self, category):
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("INSERT INTO categories (name) VALUES (:name) RETURNING id"),
                {"name": category.name}
            )
            id = result.fetchone()[0]
            conn.commit()
            return id
