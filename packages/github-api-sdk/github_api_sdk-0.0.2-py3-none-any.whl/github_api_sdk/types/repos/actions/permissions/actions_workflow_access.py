

from typing_extensions import Literal

from ....._models import BaseModel

__all__ = ["ActionsWorkflowAccess"]


class ActionsWorkflowAccess(BaseModel):
    access_level: Literal["none", "user", "organization"]
    """
    Defines the level of access that workflows outside of the repository have to
    actions and reusable workflows within the repository.

    `none` means the access is only possible from workflows in this repository.
    `user` level access allows sharing across user owned private repositories only.
    `organization` level access allows sharing across the organization.
    """
