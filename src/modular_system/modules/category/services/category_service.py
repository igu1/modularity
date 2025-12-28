from typing import List, Optional, Dict, Any
from ..models.category import CategoryModel
class CategoryService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self, organization_id: Optional[int] = None) -> List[CategoryModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = "SELECT * FROM categories"
                params = {}
                if organization_id:
                    query += " WHERE organization_id = :org_id"
                    params['org_id'] = organization_id
                query += " ORDER BY name"
                result = conn.execute(text(query), params)
                items = [CategoryModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("category", f"Retrieved {len(items)} items", "info")
            return items
        except Exception as e:
            self.logger.log("category", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[CategoryModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM categories WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = CategoryModel.from_db_row(row)
                    self.logger.log("category", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("category", f"Error getting item by ID: {e}", "error")
            return None
    def get_by_slug(self, organization_id: int, slug: str) -> Optional[CategoryModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM categories WHERE organization_id = :org_id AND slug = :slug"), 
                                   {'org_id': organization_id, 'slug': slug})
                row = result.fetchone()
                if row:
                    item = CategoryModel.from_db_row(row)
                    return item
            return None
        except Exception as e:
            self.logger.log("category", f"Error getting item by slug: {e}", "error")
            return None
    def create(self, item: CategoryModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("category", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO categories (organization_id, name, slug, description, is_active)
                    VALUES (:organization_id, :name, :slug, :description, :is_active)
                """), {
                    'organization_id': item.organization_id,
                    'name': item.name,
                    'slug': item.slug,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("category", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("category", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: CategoryModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("category", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE categories 
                    SET organization_id = :organization_id, name = :name, 
                        slug = :slug, description = :description, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'organization_id': item.organization_id,
                    'name': item.name,
                    'slug': item.slug,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("category", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("category", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM categories WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("category", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("category", f"Error deleting item: {e}", "error")
            return False
