from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, AliasChoices

from app.models.enums import DataSource


# Body Composition Schemas
class BodyCompositionBase(BaseModel):
    weight: Optional[float] = Field(None, ge=0, description="Weight in kg or lbs")
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Body fat percentage"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Muscle mass percentage"
    )
    bone_density: Optional[float] = Field(None, ge=0, description="Bone density")
    water_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Water percentage"
    )
    visceral_fat: Optional[float] = Field(None, ge=0, description="Visceral fat level")
    bmr: Optional[float] = Field(None, ge=0, description="Basal Metabolic Rate")
    measurement_method: Optional[str] = Field(
        None, description="Measurement method (e.g., DEXA, BIA, Scale)"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    class Config:
        extra = "forbid"


class BodyCompositionCreate(BodyCompositionBase):
    measurement_date: datetime = Field(..., description="Date and time of measurement")
    source: DataSource = Field(
        default=DataSource.MANUAL,
        description="Source of the measurement data (defaults to manual)",
    )


class BodyCompositionResponse(BodyCompositionBase):
    id: str
    user_id: str
    measurement_date: datetime = Field(
        ...,
        serialization_alias="measurement_date",
        validation_alias=AliasChoices("measurement_date", "date_hour"),
    )
    source: DataSource
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


# Response schemas
class BodyCompositionMessageResponse(BaseModel):
    message: str


class BodyCompositionCreateResponse(BodyCompositionMessageResponse):
    composition: BodyCompositionResponse


class BodyCompositionDeleteResponse(BodyCompositionMessageResponse):
    deleted_count: int


class BodyCompositionExportResponse(BaseModel):
    records: list[BodyCompositionResponse]
    total_count: int
    user_id: str


# Bulk Operations Schemas
class BodyCompositionBulkCreate(BaseModel):
    records: List[BodyCompositionCreate] = Field(
        ..., description="List of body composition records to create/update"
    )


class BodyCompositionBulkCreateResponse(BodyCompositionMessageResponse):
    created_count: int
    updated_count: int
    total_processed: int
    records: List[BodyCompositionResponse]
