from uuid import UUID
from typing import List, Dict, Union, Optional
from pydantic import StrictStr
from expert_dollup.shared.starlette_injection import CamelModel
from .dynamic_primitive import (
    StringFieldValueDto,
    DecimalFieldValueDto,
    BoolFieldValueDto,
    IntFieldValueDto,
    ReferenceIdDto,
)

ReportDefinitionColumnDictDto = Dict[
    str,
    Union[
        StringFieldValueDto,
        DecimalFieldValueDto,
        BoolFieldValueDto,
        IntFieldValueDto,
        ReferenceIdDto,
        List[ReferenceIdDto],
    ],
]
ReportRowDictDto = Dict[str, ReportDefinitionColumnDictDto]


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


class ReportComputationDto(CamelModel):
    name: str
    expression: str
    unit: Union[StrictStr, AttributeBucketDto, None] = None
    is_visible: bool = True


class StageSummaryDto(CamelModel):
    label: AttributeBucketDto
    summary: ReportComputationDto


class ReportStructureDto(CamelModel):
    datasheet_selection_alias: str
    formula_attribute: AttributeBucketDto
    datasheet_attribute: AttributeBucketDto
    joins_cache: List[ReportJoinDto]
    columns: List[ReportComputationDto]
    group_by: List[AttributeBucketDto]
    order_by: List[AttributeBucketDto]
    stage_summary: StageSummaryDto
    report_summary: List[ReportComputationDto]


class ReportDefinitionDto(CamelModel):
    id: UUID
    project_definition_id: UUID
    name: str
    structure: ReportStructureDto
    distributable: bool
