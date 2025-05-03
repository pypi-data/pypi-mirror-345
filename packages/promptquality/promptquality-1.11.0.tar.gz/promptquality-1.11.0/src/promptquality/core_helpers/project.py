from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.project import get_project as core_get_project
from galileo_core.schemas.core.project import ProjectResponse, ProjectType
from promptquality.types.config import PromptQualityConfig


def get_project(project_id: Optional[UUID4] = None, project_name: Optional[str] = None) -> Optional[ProjectResponse]:
    config = PromptQualityConfig.get()
    return core_get_project(
        project_id=project_id, project_name=project_name, project_type=ProjectType.llm_monitor, config=config
    )
