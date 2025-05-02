import os
from .lib.lib import ModuleManager, wrapped_func
import json
from secondbrain import utils
from functools import lru_cache

bot_index = 0
params = utils.params


@lru_cache(maxsize=128)
def ref_bot(item_id, config=None, workspace_path=None):
    global bot_index
    if workspace_path is None:
        workspace_path = params["workspacePath"]
    tool_base_path = os.path.join(workspace_path, "User/Local/Bot")
    code_folder = os.path.join(tool_base_path, item_id)
    code_folder = os.path.normpath(os.path.abspath(code_folder))
    with open(code_folder + "/info.json", "r", encoding="utf-8") as f:
        name = json.load(f)["name"]
            
    if not os.path.exists(code_folder):
        print(f"Bot {name}({item_id}) not found in:" + code_folder + "\n")
        return None

    try:
        with ModuleManager(code_folder) as manager:
            random_name = "bot_" + str(bot_index)
            bot_index += 1
            function_code = f"""
def {random_name}(command:str) -> str:
    \"\"\"Receives any command string and returns the string result after the AI role ({name} expert) deeply thinks and executes the command.
    The AI role ({name} expert) is skilled at using various tools and provides professional and more accurate results.

    Args:
        command (str): The command string that the AI role ({name} expert) needs to execute.

    Returns:
        str: The result after the AI role ({name} expert) executes the command.
    \"\"\"
    import asyncio
    from secondbrain import bot
    from secondbrain import utils
    import tempfile
    import sys

    with tempfile.NamedTemporaryFile(delete=True, mode='w+t') as temp_file:
        sys.stdout = temp_file  # 将输出重定向到临时文件，防止影响AI结果
        result = asyncio.run(bot.get_chat_response("botSetting.json", command))
        sys.stdout = sys.__stdout__  # 恢复标准输出
    return result
"""
            exec(function_code)
            tool = eval(random_name)
            tool = wrapped_func(tool, code_folder)

            return tool
    except Exception:
        import traceback
        print(f"Error loading bot {name}({item_id}): \n{traceback.format_exc()}")
        return None
