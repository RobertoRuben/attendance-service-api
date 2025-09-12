from pydantic import BaseModel, Field, ConfigDict


class GradeRequestDTO(BaseModel):
    """
    Data transfer object for grade creation requests.

    :ivar grade_name: The name of the grade.

    Args:
        BaseModel (BaseModel): The base model class.
        ConfigDict (ConfigDict): The configuration dictionary class.
    """

    model_config = ConfigDict(extra="forbid")

    grade_name: str = Field(
        ...,
        description="The name of the grade.",
        examples=["1°", "2°", "3°", "4°", "5°"],
    )
