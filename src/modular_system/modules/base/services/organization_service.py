from typing import List, Optional
from ..models.organization import OrganizationModel

class OrganizationService:
    def __init__(self, mod): self.mod = mod
    def get_all(self) -> List[OrganizationModel]: return [OrganizationModel(**d) for d in OrganizationModel.all()]
    def get_by_id(self, rid: int) -> Optional[OrganizationModel]:
        d = OrganizationModel.get(rid)
        return OrganizationModel(**d) if d else None
    def get_by_slug(self, slug: str) -> Optional[OrganizationModel]:
        d = OrganizationModel.get_by(slug=slug)
        return OrganizationModel(**d) if d else None
    def create(self, item: OrganizationModel) -> Optional[int]:
        ok, errs = item.validate()
        return OrganizationModel.create(**item.to_dict()).get('id') if ok else None
    def update(self, rid: int, item: OrganizationModel) -> bool:
        ok, errs = item.validate()
        return OrganizationModel.update_record(rid, **item.to_dict()) is not None if ok else False
    def delete(self, rid: int) -> bool: return OrganizationModel.delete_record(rid)
