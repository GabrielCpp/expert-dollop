from uuid import UUID
from typing import List, Dict, Union, Optional
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


class AttributeBucketDto(CamelModel):
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDictDto):
        return row[self.bucket_name][self.attribute_name]


class ReportColumnDto(CamelModel):
    name: str
    expression: str
    is_visible: bool = True
    unit_id: Optional[str] = None
    unit: Optional[AttributeBucketDto] = None


class ReportComputationDto(CamelModel):
    expression: str
    unit_id: Optional[str] = None


class StageGroupingDto(CamelModel):
    label: AttributeBucketDto
    summary: ReportComputationDto


class ReportStructureDto(CamelModel):
    datasheet_selection_alias: str
    formula_attribute: AttributeBucketDto
    datasheet_attribute: AttributeBucketDto
    joins_cache: List[ReportJoinDto]
    columns: List[ReportColumnDto]
    group_by: List[AttributeBucketDto]
    order_by: List[AttributeBucketDto]
    stage: StageGroupingDto


class ReportDefinitionDto(CamelModel):
    id: UUID
    project_def_id: UUID
    name: str
    structure: ReportStructureDto
