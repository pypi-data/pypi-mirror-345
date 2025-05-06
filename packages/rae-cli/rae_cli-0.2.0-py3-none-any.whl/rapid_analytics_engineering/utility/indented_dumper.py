import yaml

from typing import Any


class IndentedDumper(yaml.Dumper):
    """Custom YAML dumper to ensure correct indentation for lists."""

    def increase_indent(self, flow=False, indentless=False) -> Any:
        return super(IndentedDumper, self).increase_indent(flow, False)
