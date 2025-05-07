from pydantic import BaseModel, Field, computed_field, field_validator
from enum import Enum
from .types import FindingStatus, FindingType, AssessmentCategory, AssessmentTechnique, Expertise, Access, ElapsedTime, \
    Equipment, KnowledgeOfTarget, FindingModelType, RiskModel, TestBasicResultType  # noqa
from cyclarity_sdk.sdk_models import ExecutionMetadata, MessageType
from cwe2.database import Database as CWEDatabase
from typing import Optional

''' Finding API'''


class TestResult(BaseModel):
    # main result table fields
    class Config:
        """
        Allow extra attributes so that baseclasses can define dynamic instance variables
        Without needing to prepend them with underscore (self._var)
        """

        extra = "allow"
    topic: str = Field(description="Subject")
    type: TestBasicResultType = Field(description="The type of the finding")
    purpose: str = Field(description="purpose of the test")

    # line
    description: Optional[str] = Field(None, description="description")

    def as_text(self):
        nl = "\n"
        text = ""

        text += f"\n\n--- {self.type.value} ---\n"
        text += f"TOPIC: {self.topic}\n"
        text += f"Purpose: {self.purpose}\n"
        if self.description:
            text += f"\nDescription:\n{self.description.replace(nl, f'{nl}    ')}\n\n"

        # Add extra attributes dynamically
        extra_fields = {key: value for key, value in self.model_extra.items()} if hasattr(self, "model_extra") else {}

        if extra_fields:
            text += "__Extra Fields__\n"
            for key, value in extra_fields.items():
                text += f"  {key}: {value}\n"
            text += "\n"
        return text


class PTFinding(TestResult):
    status: FindingStatus = Field(description="status of the finding")
    type: FindingType = Field(description="The type of the finding")
    assessment_category: AssessmentCategory = Field(AssessmentCategory.PENTEST, description="assessment category")  # noqa
    assessment_technique: AssessmentTechnique = Field(AssessmentTechnique.NETWORK_ANALYSIS, description="assessment technique")  # noqa
    preconditions: Optional[str] = Field(None, description="precondition for the test")  # noqa
    steps: Optional[str] = Field(None, description="steps performed for executing the test")  # noqa
    threat: Optional[str] = Field(None, description="threat description")
    recommendations: Optional[str] = Field(None, description="recommendations")
    expertise: Optional[Expertise] = Field(None, description="expertise needed by the attack in order to manipulate it")  # noqa
    access: Optional[Access] = Field(None, description="access needed in order to perform this attack")  # noqa
    time: Optional[ElapsedTime] = Field(None, description="the estimated time it takes to execute the exploit")  # noqa
    equipment: Optional[Equipment] = Field(None, description="required equipment level needed in order to execute the exploit")  # noqa
    knowledge_of_target: Optional[KnowledgeOfTarget] = Field(None, description="")  # noqa
    cwe_number: Optional[int] = Field(None, description="cwe num")

    # Custom validator that checks if different fields are matching 'RiskModel'
    @field_validator('expertise', 'access', 'time', 'equipment',
                     'knowledge_of_target', mode="before")
    def convert_enum_attributes_to_model(cls, v, info):
        """
        Convert enums values to pydantic model
        """
        field_to_enum_mapping = {
            'expertise': Expertise,
            'access': Access,
            'time': ElapsedTime,
            'equipment': Equipment,
            'knowledge_of_target': KnowledgeOfTarget
        }
        enum_class = field_to_enum_mapping.get(info.field_name)
        if not enum_class:
            raise ValueError(f"No enum class found for field "
                             f"{info.field_name}")
        if isinstance(v, dict):
            # Cover the case where the information is already a dict.
            return RiskModel(**v)
        if isinstance(v, str):
            try:
                return getattr(enum_class, v)
            except AttributeError:
                raise ValueError(f"{v} is not a valid value for enum class"
                                 f" {enum_class} and field {info.field_name}")
        return v

    @computed_field
    @property
    def cwe_description(self) -> str:
        try:
            cwe_db = CWEDatabase()
            weakness = cwe_db.get(self.cwe_number)
            return weakness.description
        except Exception:
            return ""  # not available

    @computed_field
    @property
    def sum(self) -> int:
        risk_sum = 0
        for field_name, field_value in self:
            if isinstance(field_value, Enum) and isinstance(
                    field_value.value, RiskModel):
                risk_sum += field_value.value.risk_value
        return risk_sum

    @computed_field
    @property
    def attack_difficulty(self) -> str:
        if self.type != FindingType.FINDING:
            return ""
        elif self.sum < 14:
            return "Very Low"
        elif self.sum < 20:
            return "Low"
        elif self.sum < 25:
            return "Moderate"
        elif self.sum < 35:
            return "High"
        return "Very High"

    def as_text(self):
        nl = "\n"
        text = super().as_text()

        text += f"Status: {self.status.value}\n"
        text += f"Assessment Category: {self.assessment_category.value} | Assessment_Technique: {self.assessment_technique.value}\n"

        if self.preconditions:
            text += f"\nPreconditions:\n{self.preconditions.replace(nl, f'{nl}    ')}\n"
        if self.steps:
            text += f"\nSteps:\n{self.steps.replace(nl, f'{nl}    ')}\n"
        if self.threat:
            text += f"\nThreat:\n{self.threat.replace(nl, f'{nl}    ')}\n"
        if self.recommendations:
            text += f"\nRecomendations:\n{self.recommendations.replace(nl, f'{nl}    ')}\n"

        if self.type == FindingType.FINDING:
            text += f"Attack Difficulty: {self.attack_difficulty}\n" if self.attack_difficulty else ''
            text += f"Expertise: {self.expertise.value.level}\n" if self.expertise else ''
            text += f"Access: {self.access.value.level}\n" if self.access else ''
            text += f"Time: {self.time.value.level}\n" if self.time else ''
            text += f"Equipment: {self.equipment.value.level}\n" if self.equipment else ''
            text += f"Knowledge of Target: {self.knowledge_of_target.value.level}\n" if self.knowledge_of_target else ''
            text += f"CWE: {self.cwe_number}\n" if self.cwe_number else ''

        return text


class Finding(BaseModel):
    metadata: ExecutionMetadata
    finding_model_type: FindingModelType = FindingModelType.PT_FINDING
    data: PTFinding | TestResult
    type: MessageType = MessageType.FINDING

    @computed_field
    @property
    def subtype(self) -> FindingType | TestBasicResultType:
        return self.data.type
