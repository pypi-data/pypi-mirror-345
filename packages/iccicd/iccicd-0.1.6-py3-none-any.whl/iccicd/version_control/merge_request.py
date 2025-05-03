from pydantic import BaseModel


class MergeRequest(BaseModel, frozen=True):

    source_branch: str = ""
    target_branch: str = ""
    title: str = ""
    description: str = ""
    remove_source_branch: bool = False
    squash_on_merge: bool = False
