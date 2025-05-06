from __future__ import annotations

import enum
from typing import Optional, TypeVar

from pydantic import BaseModel

from kognic.io.model.scene.abstract.base_scene import BaseScene
from kognic.openlabel.models import OpenLabelAnnotation

SceneUuid = str
InputUuid = str

Scene = TypeVar("Scene", bound=BaseScene)


class SceneWithPreAnnotation(BaseModel):
    scene: Scene
    pre_annotation: Optional[OpenLabelAnnotation] = None


class InputCreationStage(enum.Enum):
    SCENE = "scene"
    PRE_ANNOTATION = "pre-annotation"
    INPUT_FROM_SCENE = "input-from-scene"


class InputCreationStatus(enum.Enum):
    CREATED = "created"
    FAILED = "failed"
    PROCESSING = "processing"


class InputCreationError(BaseModel):
    stage: InputCreationStage
    message: str


class InputCreationResult(BaseModel):
    scene_uuid: SceneUuid
    status: InputCreationStatus
    external_id: Optional[str] = None
    input_uuid: Optional[InputUuid] = None  # Only defined if an input was created
    error: Optional[InputCreationError] = None  # Only defined if an error occured

    def combine(self, other: InputCreationResult) -> InputCreationResult:
        return InputCreationResult(
            scene_uuid=self.scene_uuid,
            status=other.status,
            external_id=self.external_id or other.external_id,
            input_uuid=self.input_uuid or other.input_uuid,
            error=self.error or other.error,
        )

    def add_external_id(self, external_id: str) -> InputCreationResult:
        return InputCreationResult(
            scene_uuid=self.scene_uuid,
            status=self.status,
            external_id=external_id,
            input_uuid=self.input_uuid,
            error=self.error,
        )
