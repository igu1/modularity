from typing import List, Optional, Dict, Any
from ..models.organization import OrganizationModel
class OrganizationService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self) -> List[OrganizationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM organizations ORDER BY name"))
                items = [OrganizationModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("organization", f"Retrieved {len(items)} items", "info")
            return items
        except Exception as e:
            self.logger.log("organization", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[OrganizationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM organizations WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = OrganizationModel.from_db_row(row)
                    self.logger.log("organization", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("organization", f"Error getting item by ID: {e}", "error")
            return None
    def get_by_slug(self, slug: str) -> Optional[OrganizationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM organizations WHERE slug = :slug"), {'slug': slug})
                row = result.fetchone()
                if row:
                    item = OrganizationModel.from_db_row(row)
                    return item
            return None
        except Exception as e:
            self.logger.log("organization", f"Error getting item by slug: {e}", "error")
            return None
    def create(self, item: OrganizationModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("organization", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO organizations (name, slug, domain, description, is_active)
                    VALUES (:name, :slug, :domain, :description, :is_active)
                """), {
                    'name': item.name,
                    'slug': item.slug,
                    'domain': item.domain,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("organization", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("organization", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: OrganizationModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("organization", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE organizations 
                    SET name = :name, slug = :slug, domain = :domain, 
                        description = :description, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'name': item.name,
                    'slug': item.slug,
                    'domain': item.domain,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("organization", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("organization", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM organizations WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("organization", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("organization", f"Error deleting item: {e}", "error")
            return False
