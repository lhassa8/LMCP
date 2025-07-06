#!/usr/bin/env python3

import json
from lmcp.types import ToolInfo

# Create a test ToolInfo
tool = ToolInfo(
    name="test",
    description="Test tool",
    input_schema={"type": "object", "properties": {"x": {"type": "number"}}},
    output_schema={"type": "object", "properties": {"result": {"type": "number"}}},
    metadata={}
)

print("Original tool:")
print(f"  output_schema: {tool.output_schema}")
print(f"  output_schema type: {type(tool.output_schema)}")

print("\nmodel_dump() result:")
dumped = tool.model_dump()
print(json.dumps(dumped, indent=2))

print(f"\nDumped output_schema: {dumped.get('output_schema')}")
print(f"Dumped outputSchema: {dumped.get('outputSchema')}")

# Try different model_dump options
print("\nmodel_dump(by_alias=True):")
dumped_alias = tool.model_dump(by_alias=True)
print(json.dumps(dumped_alias, indent=2))