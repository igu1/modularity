from typing import List, Optional, Dict, Any
from ..models.organization import OrganizationModel

class OrganizationService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger

    def get_all(self) -> List[OrganizationModel]:
        try:
            return [OrganizationModel(**data) for data in OrganizationModel.all()]
        except Exception as e:
            self.logger.log("base", f"Error getting all organizations: {e}", "error")
            return []

    def get_by_id(self, item_id: int) -> Optional[OrganizationModel]:
        try:
            data = OrganizationModel.get(item_id)
            return OrganizationModel(**data) if data else None
        except Exception as e:
            self.logger.log("base", f"Error getting organization by ID: {e}", "error")
            return None

    def get_by_slug(self, slug: str) -> Optional[OrganizationModel]:
        try:
            data = OrganizationModel.get_by(slug=slug)
            return OrganizationModel(**data) if data else None
        except Exception as e:
            self.logger.log("base", f"Error getting organization by slug: {e}", "error")
            return None

    def create(self, item: OrganizationModel) -> Optional[int]:
        try:
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("base", f"Validation errors: {errors}", "warning")
                return None
            
            result = OrganizationModel.create(
                name=item.name,
                slug=item.slug,
                domain=item.domain,
                description=item.description,
                is_active=item.is_active
            )
            return result.get('id')
        except Exception as e:
            self.logger.log("base", f"Error creating organization: {e}", "error")
            return None

    def update(self, item_id: int, item: OrganizationModel) -> bool:
        try:
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("base", f"Validation errors: {errors}", "warning")
                return False
            
            result = OrganizationModel.update_record(
                item_id,
                name=item.name,
                slug=item.slug,
                domain=item.domain,
                description=item.description,
                is_active=item.is_active
            )
            return result is not None
        except Exception as e:
            self.logger.log("base", f"Error updating organization: {e}", "error")
            return False

    def delete(self, item_id: int) -> bool:
        try:
            return OrganizationModel.delete_record(item_id)
        except Exception as e:
            self.logger.log("base", f"Error deleting organization: {e}", "error")
            return False
