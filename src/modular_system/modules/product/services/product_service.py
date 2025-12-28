from typing import List, Optional, Dict, Any
from ..models.product import ProductModel
class ProductService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self, organization_id: Optional[int] = None, category_id: Optional[int] = None) -> List[ProductModel]:
        try:
            filters = {}
            if organization_id:
                filters['organization_id'] = organization_id
            if category_id:
                filters['category_id'] = category_id
            
            return [ProductModel(**data) for data in ProductModel.filter(**filters)]
        except Exception as e:
            self.logger.log("product", f"Error getting all items: {e}", "error")
            return []

    def get_by_id(self, item_id: int) -> Optional[ProductModel]:
        try:
            data = ProductModel.get(item_id)
            return ProductModel(**data) if data else None
        except Exception as e:
            self.logger.log("product", f"Error getting item by ID: {e}", "error")
            return None

    def create(self, item: ProductModel) -> Optional[int]:
        try:
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("product", f"Validation errors: {errors}", "warning")
                return None
            
            result = ProductModel.create(
                organization_id=item.organization_id,
                category_id=item.category_id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                is_active=item.is_active
            )
            return result.get('id')
        except Exception as e:
            self.logger.log("product", f"Error creating item: {e}", "error")
            return None

    def update(self, item_id: int, item: ProductModel) -> bool:
        try:
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("product", f"Validation errors: {errors}", "warning")
                return False
            
            result = ProductModel.update_record(
                item_id,
                organization_id=item.organization_id,
                category_id=item.category_id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                is_active=item.is_active
            )
            return result is not None
        except Exception as e:
            self.logger.log("product", f"Error updating item: {e}", "error")
            return False

    def delete(self, item_id: int) -> bool:
        try:
            return ProductModel.delete_record(item_id)
        except Exception as e:
            self.logger.log("product", f"Error deleting item: {e}", "error")
            return False
