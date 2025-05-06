import json

def format_previous_submodel_to_md(data):
    """
    将 get_previous_submodel 的结果格式化为 Markdown
    """
    md_blocks = []

    for item in data:
        pre_no = item.get("preSubModelNo", "未知编号")
        formatted_json = json.dumps([item], ensure_ascii=False, indent=2)
        md = f"# 前置模型编号：{pre_no}\n```json\n{formatted_json}\n```"
        md_blocks.append(md)

    return "\n\n".join(md_blocks)



def format_submodel_meta_to_md(data, level=1, parent_key=None):
    md_lines = []
    prefix = "#" * level if level <= 6 else "#" * 6

    if isinstance(data, dict):
        for key, value in data.items():
            # 特殊处理 subModelNo 字段
            if level == 1 and key == "subModelNo":
                md_lines.append(f"----- 模型 {value} 的元数据 -----")
                continue

            # 特殊处理 rule 字段
            if level == 1 and key == "rule":
                md_lines.append(f"{prefix} {key}")
                formatted_json = json.dumps(value, ensure_ascii=False, indent=2)
                md_lines.append(f"```json\n{formatted_json}\n```")
                continue

            if isinstance(value, dict) or (isinstance(value, list) and any(isinstance(i, (dict, list)) for i in value)):
                # 嵌套结构：标题 + 递归
                md_lines.append(f"{prefix} {key}")
                md_lines.append(format_submodel_meta_to_md(value, level + 1, key))
            elif isinstance(value, list):
                # 最底层数组：输出一行
                joined = " ".join(str(i) for i in value)
                md_lines.append(f"{key}：{joined}")
            else:
                # 最底层值
                md_lines.append(f"{key}：{value}")

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            title = f"{parent_key}-{idx + 1}" if parent_key else f"项-{idx + 1}"
            md_lines.append(f"{prefix} {title}")
            md_lines.append(format_submodel_meta_to_md(item, level + 1))

    else:
        md_lines.append(f"{prefix} {data}")

    return "\n".join(md_lines)
