from typing import List, Optional, Dict, Any
from ..models.discount import CouponModel, DiscountModel
class DiscountService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def validate_coupon(self, code: str, total: float) -> Dict[str, Any]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM coupons 
                    WHERE code = :code AND is_active = 1 
                    AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """), {"code": code}).fetchone()
                
                if not result:
                    return {"success": False, "error": "Invalid or expired coupon"}
                
                discount_type = result[2]
                discount_value = float(result[3])
                min_purchase = float(result[4])
                
                if total < min_purchase:
                    return {"success": False, "error": f"Minimum purchase of {min_purchase} required"}
                
                discount_amount = 0
                if discount_type == 'percentage':
                    discount_amount = (total * discount_value) / 100
                else:
                    discount_amount = discount_value
                    
                return {
                    "success": True, 
                    "discount_amount": discount_amount,
                    "new_total": max(0, total - discount_amount)
                }
        except Exception as e:
            self.logger.log("discount", f"Error validating coupon: {e}", "error")
            return {"success": False, "error": str(e)}

    def get_all(self) -> List[CouponModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM coupons ORDER BY code"))
                items = [CouponModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("discount", f"Error getting all coupons: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[DiscountModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM discounts WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = DiscountModel.from_db_row(row)
                    self.logger.log("discount", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("discount", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: DiscountModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("discount", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO discounts (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("discount", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("discount", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: DiscountModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("discount", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE discounts 
                    SET name = :name, description = :description, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("discount", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("discount", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM discounts WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("discount", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("discount", f"Error deleting item: {e}", "error")
            return False
