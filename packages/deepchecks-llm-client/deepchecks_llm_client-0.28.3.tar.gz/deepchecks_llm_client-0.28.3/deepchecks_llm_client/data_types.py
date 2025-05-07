import enum
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pytz

__all__ = ["EnvType", "AnnotationType", "Interaction", "Step", "Application",
           "ApplicationType", "ApplicationVersion", "ApplicationVersionSchema",
           "LogInteraction", "InteractionType", "BuiltInInteractionType", "UserValueProperty",
           "PropertyColumnType", "UserValuePropertyType", "InteractionCompleteEvents",
           "InteractionTypeVersionData", "CreateInteractionTypeVersionData", "UpdateInteractionTypeVersionData"]

logging.basicConfig()
logger = logging.getLogger(__name__)


class EnvType(str, enum.Enum):
    PROD = "PROD"
    EVAL = "EVAL"
    PENTEST = "PENTEST"


class AnnotationType(str, enum.Enum):
    GOOD = "good"
    BAD = "bad"
    UNKNOWN = "unknown"


class PropertyColumnType(str, enum.Enum):
    CATEGORICAL = "categorical"
    NUMERIC = "numeric"


@dataclass
class Interaction:
    user_interaction_id: str
    input: str
    information_retrieval: str
    history: str
    full_prompt: str
    expected_output: str
    action: str
    tool_response: str
    output: str
    topic: str
    builtin_properties: Dict[str, Any]
    user_value_properties: Dict[str, Any]
    custom_prompt_properties: Dict[str, Any]
    custom_prompt_properties_reasons: Dict[str, Any]
    created_at: datetime
    interaction_datetime: datetime
    is_completed: bool
    interaction_type: str
    session_id: str
    metadata: Optional[Dict[str, str]]
    tokens: Optional[int]


@dataclass
class Step:
    name: str
    value: str

    def to_json(self):
        return {
            self.name: self.value
        }

    @classmethod
    def as_jsonl(cls, steps):
        if steps is None:
            return None
        return [step.to_json() for step in steps]


@dataclass
class UserValueProperty:
    """Data class representing user provided property"""
    name: str
    value: Any
    reason: Optional[str] = None


@dataclass
class LogInteraction:
    """A dataclass representing an interaction.

    Attributes
    ----------
    input : str
        Input data
    output : str
        Output data
    expected_output : str, optional
        Full expected output data, defaults to None
    full_prompt : str, optional
        Full prompt data, defaults to None
    annotation : AnnotationType, optional
        Annotation type of the interaction, defaults to None
    user_interaction_id : str, optional
        Unique identifier of the interaction, defaults to None
    steps : list of Step, optional
        List of steps taken during the interaction, defaults to None
    user_value_properties : list of UserValueProperty, optional
        Additional user value properties, defaults to None
    information_retrieval : str, optional
        Information retrieval, defaults to None
    history : str, optional
        History (for instance "chat history"), defaults to None
    annotation_reason : str, optional
        Reason for the annotation, defaults to None
    started_at : datetime or float, optional
        Timestamp the interaction started at. Datetime format is deprecated, use timestamp instead
    finished_at : datetime or float, optional
        Timestamp the interaction finished at. Datetime format is deprecated, use timestamp instead
    vuln_type : str, optional
        Type of vulnerability (Only used in case of EnvType.PENTEST and must be sent there), defaults to None
    vuln_trigger_str : str, optional
        Vulnerability trigger string (Only used in case of EnvType.PENTEST and is optional there), defaults to None
    session_id: str, optional
        The identifier for the session associated with this interaction.
        If not provided, a session ID will be automatically generated.
    interaction_type: str, optional
        The type of interaction.
        None is deprecated. If not provided, the interaction type will default to the application’s default type.
    metadata: Dict[str, str], optional
        Metdata for the interaction.
    tokens: int, optional
        Token count for the interaction.
    """

    input: Optional[str] = None
    output: Optional[str] = None
    expected_output: Optional[str] = None
    action: Optional[str] = None
    tool_response: Optional[str] = None
    full_prompt: Optional[str] = None
    annotation: Optional[Union[AnnotationType, str]] = None
    user_interaction_id: Optional[Union[str, int]] = None
    steps: Optional[List[Step]] = None
    user_value_properties: Optional[List[UserValueProperty]] = None
    information_retrieval: Optional[Union[str, List[str]]] = None
    history: Optional[Union[str, List[str]]] = None
    annotation_reason: Optional[str] = None
    started_at: Optional[Union[datetime, float]] = None
    finished_at: Optional[Union[datetime, float]] = None
    vuln_type: Optional[str] = None
    vuln_trigger_str: Optional[str] = None
    topic: Optional[str] = None
    is_completed: bool = True
    interaction_type: Optional[str] = None
    session_id: Optional[Union[str, int]] = None
    metadata: Optional[Dict[str, str]] = None
    tokens: Optional[int] = None

    def to_json(self):
        if isinstance(self.started_at, datetime) or isinstance(self.finished_at, datetime):
            logger.warning(
                "Deprecation Warning: Usage of datetime for started_at/finished_at is deprecated, use timestamp instead."
            )
            self.started_at = self.started_at.timestamp() if self.started_at else datetime.now(tz=pytz.UTC).timestamp()
            self.finished_at = self.finished_at.timestamp() if self.finished_at else None
        if self.interaction_type is None:
            logger.warning(
                "Deprecation Warning: The value 'None' for 'interaction_type' is deprecated. "
                "Please specify an explicit interaction type."
            )

        data = {
            "input": self.input,
            "output": self.output,
            "expected_output": self.expected_output,
            "action": self.action,
            "tool_response": self.tool_response,
            "full_prompt": self.full_prompt,
            "information_retrieval": self.information_retrieval
            if self.information_retrieval is None or isinstance(self.information_retrieval, list)
            else [self.information_retrieval],
            "history": self.history
            if self.history is None or isinstance(self.history, list)
            else [self.history],
            "annotation": (
                None if self.annotation is None else
                self.annotation.value if isinstance(self.annotation, AnnotationType)
                else str(self.annotation).lower().strip()
            ),
            "user_interaction_id": str(self.user_interaction_id) if self.user_interaction_id is not None else None,
            "steps": [step.to_json() for step in self.steps] if self.steps else None,
            "custom_props": {prop.name: prop.value for prop in self.user_value_properties} if self.user_value_properties else None,
            "custom_props_reasons": {
                prop.name: prop.reason for prop in self.user_value_properties if prop.reason
            } if self.user_value_properties else None,
            "annotation_reason": self.annotation_reason,
            "vuln_type": self.vuln_type,
            "vuln_trigger_str": self.vuln_trigger_str,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "is_completed": self.is_completed,
            "session_id": str(self.session_id) if self.session_id is not None else None,
            "interaction_type": self.interaction_type,
            "metadata": self.metadata,
            "tokens": self.tokens,
        }
        if self.topic is not None:
            data["topic"] = self.topic

        return data


@dataclass
class UserValuePropertyType:
    display_name: str
    type: Union[PropertyColumnType, str]
    description: Union[str, None] = None


class ApplicationType(str, enum.Enum):
    QA = "Q&A"
    OTHER = "OTHER"
    SUMMARIZATION = "SUMMARIZATION"
    GENERATION = "GENERATION"
    CLASSIFICATION = "CLASSIFICATION"
    FEATURE_EXTRACTION = "FEATURE EXTRACTION"
    TOOL_USE = "Tool Use"


class BuiltInInteractionType(str, enum.Enum):
    QA = "Q&A"
    OTHER = "Other"
    SUMMARIZATION = "Summarization"
    CLASSIFICATION = "Classification"
    GENERATION = "Generation"
    FEATURE_EXTRACTION = "Feature Extraction"
    TOOL_USE = "Tool Use"


class InteractionCompleteEvents(str, enum.Enum):
    TOPICS_COMPLETED = "topics_completed"
    PROPERTIES_COMPLETED = "properties_completed"
    SIMILARITY_COMPLETED = "similarity_completed"
    LLM_PROPERTIES_COMPLETED = "llm_properties_completed"
    ANNOTATION_COMPLETED = "annotation_completed"
    DC_EVALUATION_COMPLETED = "dc_evaluation_completed"


@dataclass
class ApplicationVersionSchema:
    name: str
    description: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None

    def to_json(self):
        return {
            "name": self.name,
            "description": self.description,
            "additional_fields": [
                {"name": key, "value": value}
                for key, value in self.additional_fields.items()
            ] if self.additional_fields else []
        }


@dataclass
class ApplicationVersion:
    """A dataclass representing an Application Version.

    Attributes
    ----------
    id : int
        Version id
    name : str
        Version name
    ai_model : str
        AI model used within this version
    created_at : datetime
        Version created at timestamp
    updated_at : datetime
        Version updated at timestamp
    custom : list of dict
        Additional details about the version as key-value pairs
        This member is deprecated. It will be removed in future versions. Use additional_fields instead.
    additional_fields : list of dict
        Additional details about the version as key-value pairs
    """

    id: int
    name: str
    ai_model: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    custom: Optional[List[Dict[str, Any]]] = None
    additional_fields: Optional[Dict[str, Any]] = None


@dataclass
class Application:
    id: int
    name: str
    kind: ApplicationType
    created_at: datetime
    updated_at: datetime
    in_progress: bool
    versions: List[ApplicationVersion]
    interaction_types: List[str]
    description: Optional[str] = None
    log_latest_insert_time_epoch: Optional[int] = None
    n_of_llm_properties: Optional[int] = None
    n_of_interactions: Optional[int] = None
    notifications_enabled: Optional[bool] = None


APP_KIND_TO_INTERACTION_TYPE = {
    ApplicationType.QA: BuiltInInteractionType.QA,
    ApplicationType.OTHER: BuiltInInteractionType.OTHER,
    ApplicationType.SUMMARIZATION: BuiltInInteractionType.SUMMARIZATION,
    ApplicationType.CLASSIFICATION: BuiltInInteractionType.CLASSIFICATION,
    ApplicationType.GENERATION: BuiltInInteractionType.GENERATION,
    ApplicationType.FEATURE_EXTRACTION: BuiltInInteractionType.FEATURE_EXTRACTION,
    ApplicationType.TOOL_USE: BuiltInInteractionType.TOOL_USE,
}


@dataclass
class InteractionTypeVersionData:
    """A dataclass representing interaction type version data.

    Attributes
    ----------
    id : int
        Interaction type version data id
    interaction_type_id : int
        Interaction type id
    application_version_id : int
        Application version id
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict
        Additional metadata parameters
    created_at : datetime
        Created at timestamp
    updated_at : datetime
        Updated at timestamp
    """
    id: int
    interaction_type_id: int
    application_version_id: int
    model: Optional[str] = None
    prompt: Optional[str] = None
    metadata_params: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None


@dataclass
class CreateInteractionTypeVersionData:
    """A dataclass for creating interaction type version data.

    Attributes
    ----------
    interaction_type_id : int
        Interaction type id
    application_version_id : int
        Application version id
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict
        Additional metadata parameters
    """
    interaction_type_id: int
    application_version_id: int
    model: Optional[str] = None
    prompt: Optional[str] = None
    metadata_params: Dict[str, Any] = None

    def to_json(self):
        return {
            "interaction_type_id": self.interaction_type_id,
            "application_version_id": self.application_version_id,
            "model": self.model,
            "prompt": self.prompt,
            "metadata_params": self.metadata_params or {},
        }


@dataclass
class UpdateInteractionTypeVersionData:
    """A dataclass for updating interaction type version data.

    Attributes
    ----------
    model : str or None
        Model name
    prompt : str or None
        Prompt template
    metadata_params : dict or None
        Additional metadata parameters
    """
    model: Optional[str] = None
    prompt: Optional[str] = None
    metadata_params: Optional[Dict[str, Any]] = None

    def to_json(self):
        return {
            "model": self.model,
            "prompt": self.prompt,
            "metadata_params": self.metadata_params,
        }


@dataclass
class InteractionType:
    id: int
    name: str
