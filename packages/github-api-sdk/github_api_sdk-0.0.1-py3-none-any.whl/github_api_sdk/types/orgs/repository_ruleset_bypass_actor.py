

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RepositoryRulesetBypassActor"]


class RepositoryRulesetBypassActor(BaseModel):
    actor_type: Literal["Integration", "OrganizationAdmin", "RepositoryRole", "Team", "DeployKey"]
    """The type of actor that can bypass a ruleset."""

    actor_id: Optional[int] = None
    """The ID of the actor that can bypass a ruleset.

    If `actor_type` is `OrganizationAdmin`, this should be `1`. If `actor_type` is
    `DeployKey`, this should be null. `OrganizationAdmin` is not applicable for
    personal repositories.
    """

    bypass_mode: Optional[Literal["always", "pull_request"]] = None
    """When the specified actor can bypass the ruleset.

    `pull_request` means that an actor can only bypass rules on pull requests.
    `pull_request` is not applicable for the `DeployKey` actor type. Also,
    `pull_request` is only applicable to branch rulesets.
    """
