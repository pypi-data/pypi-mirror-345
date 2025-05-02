import json
from secondbrain import utils
import json
import inspect


params = utils.params


def get_ui():
    if params is None or "uiDatas" not in params:
        return {}
    stack = inspect.stack()
    stack_files = list(reversed([s.filename.replace("\\", "/") for s in stack]))
    match_ui_file = None
    for f in stack_files:
        for v in params["uiDatas"]:
            if v == f:
                match_ui_file = v
                break
        if match_ui_file is not None:
            break

    if match_ui_file is None:
        return {}
    
    for i in range(10):
        try:
            return params["uiDatas"][match_ui_file]
        except Exception as e:
            if i == 9:
                raise e
