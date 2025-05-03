from pydantic import UUID4

from galileo_core.helpers.group_integration import share_integration_with_group as core_share_integration_with_group
from galileo_core.schemas.core.integration.group_integration import GroupIntegrationCollaboratorResponse
from promptquality.types.config import PromptQualityConfig


def share_integration_with_group(integration_id: UUID4, group_id: UUID4) -> GroupIntegrationCollaboratorResponse:
    """
    Share an integration with a group.

    Args:
        integration_id (UUID4): The ID of the integration.
        group_id (UUID4): The ID of the group.

    Returns:
        GroupIntegrationCollaboratorResponse: The response from the API.
    """
    config = PromptQualityConfig.get()
    return core_share_integration_with_group(integration_id=integration_id, group_id=group_id, config=config)
