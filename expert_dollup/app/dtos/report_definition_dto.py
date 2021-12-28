from uuid import UUID
from typing import List, Dict, Union
from expert_dollup.shared.starlette_injection import CamelModel

ReportColumnDictDto = Dict[str, Union[str, float, bool, int, UUID, List[UUID], None]]
ReportRowDictDto = Dict[str, ReportColumnDictDto]


class ReportJoinDto(CamelModel):
    from_object_name: str
    from_property_name: str
    join_on_collection: str
    join_on_attribute: str
    alias_name: str
    warn_about_idle_items: bool
    same_cardinality: bool
    allow_dicard_element: bool


class ReportColumnDto(CamelModel):
    name: str
    expression: str
    is_visible: bool = True


class AttributeBucketDto(CamelModel):
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDictDto):
        return row[self.bucket_name][self.attribute_name]


class ReportStructureDto(CamelModel):
    datasheet_selection_alias: str
    formula_attribute: AttributeBucketDto
    datasheet_attribute: AttributeBucketDto
    stage_attribute: AttributeBucketDto
    joins_cache: List[ReportJoinDto]
    columns: List[ReportColumnDto]
    group_by: List[AttributeBucketDto]
    order_by: List[AttributeBucketDto]


class ReportDefinitionDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    structure: ReportStructureDto
