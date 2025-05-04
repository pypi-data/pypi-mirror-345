"""list resources workflow plugin module"""

import re
from collections.abc import Sequence

from cmem.cmempy.workspace.projects.resources import get_resources
from cmem_plugin_base.dataintegration.context import ExecutionContext
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.utils import setup_cmempy_user_access


@Plugin(
    label="List project files",
    plugin_id="cmem_plugin_project_resources-List",
    description="List file resources from the project.",
    documentation=r"""List file resources from the current project based on a regular expression.

The project-relative path of each file of the current project is tested against a given
regular expression.
The project resource is listed in the output, if the expression matches this path.
The output entities have the following paths:

- `name` - the plain file name of the resource (example: `file.txt`)
- `fullPath` - the project-relative path including directories but no leading slash
  (example: `directory/file.txt`)
- `modified` - modified timestamp (example: `2025-03-10T15:38:41.023Z`)
- `size` - size of the file in bytes (example: `123345`)

The regular expression has to match the `fullPath` of the file and is case sensitive.

Given this list of example files of a project:

```
dataset.csv
my-dataset.xml
json/example.json
json/example_new.json
json/data.xml
```

Here are some regular expressions with the expected result:

- The regex `dataset\.csv` lists only the first file.
- The regex `json/.*` lists all files in the `json` sub-directory.
- The regex `new` lists nothing.
- The regex `.*new.*` list the file `json/example_new.json`
(and all other files with `new` in the path)

We recommend to test your regular expression before using it.
[regex101.com](https://regex101.com) is a proper service to test your regular expressions.
[This deep-link](https://regex101.com/?testString=dataset.csv%0Amy-dataset.xml%0Ajson/example.json%0Ajson/example_new.json%0Ajson/data.xml&regex=.*new.*)
provides a test bed using the example files and the last expression from the list.
""",
    icon=Icon(package=__package__, file_name="list.svg"),
    parameters=[
        PluginParameter(
            name="files_regex",
            label="File matching regex",
            description="The regex for filtering the file names. "
            "The regex needs to match the full path (i.e. from beginning to end, "
            "including sub-directories) in order for the file to be deleted.",
        ),
    ],
)
class ListResourcePlugin(WorkflowPlugin):
    """List project resources"""

    def __init__(self, files_regex: str) -> None:
        try:
            self.files_regex = re.compile(files_regex)
        except re.error as error:
            raise ValueError(f"Invalid regular expression '{files_regex}' ({error!s}).") from error
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = FixedSchemaPort(schema=self.get_schema())

    @staticmethod
    def get_schema() -> EntitySchema:
        """Provide the list schema"""
        return EntitySchema(
            type_uri="",
            paths=[
                EntityPath(path="name", is_single_value=True),
                EntityPath(path="fullPath", is_single_value=True),
                EntityPath(path="modified", is_single_value=True),
                EntityPath(path="size", is_single_value=True),
            ],
        )

    @staticmethod
    def get_project_resources(context: ExecutionContext) -> list[dict]:
        """Get project resources"""
        setup_cmempy_user_access(context=context.user)
        all_resources: list[dict] = get_resources(project_name=context.task.project_id())
        return all_resources

    def match_full_path(self, full_path: str) -> bool:
        """Match a single file path against the regex"""
        return self.files_regex.fullmatch(full_path) is not None

    def filter_resources(self, resources: list[dict]) -> list[dict]:
        """Filter resources by given configuration"""
        return [_ for _ in resources if self.match_full_path(_["fullPath"])]

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.log.info(f"Listing project resources matching regex '{self.files_regex}'")
        if len(list(inputs)) > 0:
            raise ValueError("This task is not able to consume data from an input port.")
        all_resources = self.get_project_resources(context)
        filtered_resources = self.filter_resources(all_resources)
        entities = [
            Entity(
                uri="",
                values=[
                    [str(_.get("name"))],
                    [str(_.get("fullPath"))],
                    [str(_.get("modified", ""))],
                    [str(_.get("size", ""))],
                ],
            )
            for _ in filtered_resources
        ]
        return Entities(entities=iter(entities), schema=self.get_schema())
