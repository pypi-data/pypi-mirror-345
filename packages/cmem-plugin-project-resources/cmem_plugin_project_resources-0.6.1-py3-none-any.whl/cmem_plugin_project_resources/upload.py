"""copy resources workflow plugin module"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from cmem.cmempy.workspace.projects.resources.resource import create_resource
from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort, Port
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile
from cmem_plugin_base.dataintegration.types import EnumParameterType
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access

MAX_PREVIEW = 100
SCHEMA = FileEntitySchema()


@dataclass
class WorkingMode:
    """Working mode

    activity: used for preview action
    operation_desc: used for ExecutionReport
    output_port: used for port specification
    """

    activity: str
    operation_desc: str
    output_port: Port | None


class WorkingModes(Enum):
    """Working modes"""

    SEND_TO_TASK = 1
    UPLOAD_TO_PROJECT = 2


working_modes: dict[str, WorkingMode] = {
    str(WorkingModes.SEND_TO_TASK): WorkingMode(
        activity="will be send to the next workflow task",
        operation_desc="file(s) send",
        output_port=FixedSchemaPort(schema=SCHEMA),
    ),
    str(WorkingModes.UPLOAD_TO_PROJECT): WorkingMode(
        activity="will be uploaded to the project",
        operation_desc="file(s) uploaded",
        output_port=None,
    ),
}


class Params:
    """Plugin parameters"""

    directory = PluginParameter(
        name="directory",
        label="Directory",
        description="The local directory where the files are located.",
    )
    regex_string = PluginParameter(
        name="regex_string",
        label="File matching regex",
        description="The regex for filtering the file names. "
        "The regex needs to fully match the local name without directory.",
        default_value=".*",
    )
    working_mode = PluginParameter(
        name="working_mode",
        label="Working mode",
        description="Which activity should be done with the selected local files.",
        param_type=EnumParameterType(enum_type=WorkingModes),
        default_value=WorkingModes.SEND_TO_TASK,
        advanced=True,
    )

    def as_list(self) -> list[PluginParameter]:
        """Provide all parameters as list"""
        return [
            getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        ]


@Plugin(
    label="Upload local files",
    plugin_id="cmem_plugin_project_resources-UploadLocalFiles",
    description="Replace a file dataset resource with a local file or "
    "upload multiple local files to a project.",
    documentation=r"""
This plugin allows you to upload multiple local files to the next workflow task.

Be aware that only file based datasets can handle file entities (e.g. JSON, CSV).

As an advanced option, you can change the working mode to UPLOAD_TO_PROJECT, which
allows for blindly adding files to the project space (with a consuming workflow task).
Make sure to use always use the preview function to avoid overloading you project.
""",
    icon=Icon(package=__package__, file_name="upload.svg"),
    actions=[
        PluginAction(
            name="preview_action",
            label=f"Preview (max. {MAX_PREVIEW})",
            description=f"Previews the first {MAX_PREVIEW} files "
            f"based on the current configuration.",
        )
    ],
    parameters=Params().as_list(),
)
class UploadLocalFilesPlugin(WorkflowPlugin):
    """Upload local files to project"""

    def __init__(
        self,
        directory: str,
        regex_string: str = Params.regex_string.default_value,
        working_mode: WorkingModes = WorkingModes.SEND_TO_TASK,
    ) -> None:
        if directory == "":
            raise ValueError("Directory cannot be empty.")
        self.directory = Path(directory)
        if not self.directory.is_absolute():
            raise ValueError("Directory must be an absolute path.")
        self.regex_string = regex_string
        self.working_mode = working_mode
        self.working_mode_data = working_modes[str(working_mode)]
        try:
            self.regex = re.compile(self.regex_string)
        except re.error as error:
            raise ValueError(
                f"Invalid regular expression '{self.regex_string}' ({error!s})."
            ) from error
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = self.working_mode_data.output_port

    def get_files(self) -> list[LocalFile]:
        """Get files from directory which match the regex"""
        if not self.directory.is_dir():
            raise FileNotFoundError(f"Path '{self.directory}' not found or not a directory.")
        files = [
            LocalFile(str(file.absolute()))
            for file in self.directory.glob(pattern="*")
            if file.is_file() and self.regex.fullmatch(file.name)
        ]
        if len(files) == 0:
            raise ValueError(
                f"No files matching regex '{self.regex_string}' "
                f"in directory '{self.directory}' found."
            )
        return files

    def preview_action(self) -> str:
        """Plugin Action to preview the results"""
        all_files = self.get_files()
        previewed_files = all_files[:MAX_PREVIEW]
        activity = self.working_mode_data.activity
        if len(previewed_files) == 1:  # only one file
            output = f"The following file {activity}:\n\n"
        elif len(previewed_files) == len(all_files):  # less or equal than MAX_PREVIEW files
            output = f"The following {len(previewed_files)} files {activity}:\n\n"
        else:  # more than MAX_PREVIEW files
            output = (
                f"The following file(s) {activity} "
                f"(showing only {len(previewed_files)} out of {len(all_files)}):\n\n"
            )
        for file in previewed_files:
            output += f"- {file.path}\n"
        return output

    def execute_send_to_task(self, context: ExecutionContext) -> Entities:
        """execute: Send to task mode"""
        entities = [SCHEMA.to_entity(file) for file in self.get_files()]
        context.report.update(
            ExecutionReport(
                entity_count=len(entities),
                operation="write",
                operation_desc=self.working_mode_data.operation_desc,
                sample_entities=Entities(entities=iter(entities[:10]), schema=SCHEMA),
            )
        )
        return Entities(entities=iter(entities), schema=SCHEMA)

    def execute_upload_to_project(self, context: ExecutionContext) -> None:
        """execute: Upload files to project mode"""
        files = self.get_files()
        for counter, file in enumerate(files, start=1):
            setup_cmempy_user_access(context=context.user)
            with Path(file.path).open("rb") as f:
                create_resource(
                    project_name=context.task.project_id(),
                    resource_name=Path(file.path).name,
                    file_resource=f,
                )
            context.report.update(
                ExecutionReport(
                    entity_count=counter,
                    operation="write",
                    operation_desc=self.working_mode_data.operation_desc,
                )
            )

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities | None:
        """Run the workflow operator."""
        if len(list(inputs)) > 0:
            raise ValueError("This task is not able to consume data from an input port.")
        if str(self.working_mode) == str(WorkingModes.UPLOAD_TO_PROJECT):
            self.execute_upload_to_project(context)
            return None
        return self.execute_send_to_task(context)
