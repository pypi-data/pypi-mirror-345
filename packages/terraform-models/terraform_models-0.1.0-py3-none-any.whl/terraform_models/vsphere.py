import re

from pydantic import BaseModel, field_validator

TARGET_PATH_REGEX = re.compile(rf"^InfraLab/SaaS/(?P<team_name>\w+)$")


class VSphereCloneVirtualMachine(BaseModel):
    source_vm_name: str
    target_vm_folder: str
    datacenter_name: str = None
    source_vm_folder: str = None
    cluster_name: str = None
    datastore_name: str = None
    target_vm_name: str = None
    network_name: str = None

    @field_validator('target_vm_folder')
    def folder_must_match_regex(cls, v):
        if not TARGET_PATH_REGEX.match(v):
            raise ValueError(f"'target_vm_folder' must be under InfraLab/SaaS/<GROUP_NAME>")
        return v
