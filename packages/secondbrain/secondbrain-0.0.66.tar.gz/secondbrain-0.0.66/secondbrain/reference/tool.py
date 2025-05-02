import os
import importlib
from .lib.lib import ModuleManager, wrapped_func
from secondbrain import utils
import json


params = utils.params


def ref_tools(item_id, config=None, working_directory=None, workspace_path=None):
    execution_path_type = config.get("executionPathType", "codeFolder")
    ui_datas = config.get("uiDatas", {})
    
    if workspace_path is None:
        workspace_path = params["workspacePath"]
    tool_base_path = os.path.join(workspace_path, "User/Local/Tool")
    code_folder = os.path.join(tool_base_path, item_id)
    code_folder = os.path.normpath(os.path.abspath(code_folder))
    with open(code_folder + "/info.json", "r", encoding="utf-8") as f:
        name = json.load(f)["name"]
    if execution_path_type == 'codeFolder':
        working_directory = code_folder
        
    if not os.path.exists(code_folder):
        print(f"Tool {name}({item_id}) not found in:" + code_folder + "\n")
        return []

    try:
        with ModuleManager(code_folder) as manager:
            from secondbrain.tool.tool_decorator import all_tools, clear_tools
            clear_tools()
            importlib.import_module("tool")
            export_tools = [tool for tool in all_tools]

    except Exception:
        import traceback
        print(f"Error loading tool {name}({item_id}): \n{traceback.format_exc()}")
        return []

    ret_export_tools = []
    for tool in export_tools:
        tool = wrapped_func(tool, working_directory, ui_datas)
            
        if tool.__doc__ is None:
            tool.__doc__ = "This tool is used to " + tool.__name__.replace("_", " ") + "."
        ret_export_tools.append(tool)

    return ret_export_tools



