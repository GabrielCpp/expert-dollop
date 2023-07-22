from pydantic import BaseModel
from typing import List, Dict, Union, Optional
from uuid import UUID
from datetime import datetime
from .primitives_dao import PrimitiveWithNoneUnionDao

ReportDefinitionColumnDict = Dict[str, PrimitiveWithNoneUnionDao]
ReportRowDict = Dict[str, ReportDefinitionColumnDict]


class ExpressionDao(BaseModel):
    name: str
    flat_ast: Optional[dict] = None


class AttributeBucketDao(BaseModel):
    bucket_name: str
    attribute_name: str

    def get(self, row: ReportRowDict):
        return row[self.bucket_name][self.attribute_name]


class ReportComputationDao(BaseModel):
    name: str
    expression: ExpressionDao
    label: Optional[AttributeBucketDao] = None
    unit: Union[str, AttributeBucketDao, None] = None
    is_visible: bool = True


class ReportJoinDao(BaseModel):
    from_object: AttributeBucketDao
    on_object: AttributeBucketDao
    alias: str


class SelectionDao(BaseModel):
    from_collection_id: UUID
    from_alias: str
    joins_cache: List[ReportJoinDao]
    formula_attribute: AttributeBucketDao
    datasheet_attribute: AttributeBucketDao


class ReportStructureDao(BaseModel):
    selection: SelectionDao
    columns: List[ReportComputationDao]
    group_by: List[AttributeBucketDao]
    having: ExpressionDao
    order_by: List[AttributeBucketDao]
    stage_summary: ReportComputationDao
    report_summary: List[ReportComputationDao]


class ReportDefinitionDao(BaseModel):
    id: UUID
    project_definition_id: UUID
    name: str
    structure: ReportStructureDao
    distributable: bool


class CompiledReportKeyDao(BaseModel):
    id: UUID
    project_definition_id: UUID
