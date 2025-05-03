from pydantic import UUID4

from galileo_core.helpers.user_integration import share_integration_with_user as core_share_integration_with_user
from galileo_core.schemas.core.integration.user_integration import UserIntegrationCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_integration_with_user(integration_id: UUID4, user_id: UUID4) -> UserIntegrationCollaboratorResponse:
    config = PromptQualityConfig.get()
    return core_share_integration_with_user(integration_id=integration_id, user_id=user_id, config=config)
