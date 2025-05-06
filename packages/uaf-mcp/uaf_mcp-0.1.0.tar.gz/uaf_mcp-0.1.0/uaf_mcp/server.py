from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field

from api import get_submodel_meta, get_previous_submodel
from transfer import format_submodel_meta_to_md, format_previous_submodel_to_md

# MCP 实例
mcp = FastMCP(
    name="UAF体系工程建模助手",
    instructions="本助手提供建模流程、规范、示例等相关的帮助和指导信息"
)

@mcp.tool(
    name="get_submodel_meta",
    description="获取指定模型编号的元数据信息",
    tags={"建模", "元数据"}
)
async def get_submodel_meta_tool(
    submodel_no: Annotated[str, Field(description="模型编号，例如 '2.17'")]
) -> str:
    raw = get_submodel_meta(submodel_no)
    return format_submodel_meta_to_md(raw)


@mcp.tool(
    name="get_previous_model_data",
    description="根据模型编号，获取其前置模型建模结果",
    tags={"建模", "依赖", "上游模型"}
)
async def get_previous_model_data_tool(
    submodel_no: Annotated[str, Field(description="模型编号，例如 '2.17'")]
) -> str:
    raw = get_previous_submodel(submodel_no)
    return format_previous_submodel_to_md(raw)
