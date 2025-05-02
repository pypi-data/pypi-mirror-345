import os
from .view import ViewCls, WorkflowCls
import time
from secondbrain import utils
import json
from typing import Union


socket = utils.socket
params = utils.params


class TabCls:
    def open_workflow(self, workflow_id: str, wait_for_open=True) -> WorkflowCls:
        item_path = os.path.join(
            params["workspacePath"], "User", "Local", 'Workflow', workflow_id
        )
        if not os.path.isabs(item_path):
            item_path = os.path.abspath(item_path)
        info_path = os.path.join(item_path, "info.json")
        with open(info_path, "r", encoding="utf-8") as f:
            info = json.load(f)
        location = ["LocalWorkflow", item_path]
        socket.post("add-tab", {"location": location, "name": info["name"]})
        if wait_for_open:
            self.wait_for_tab_open(location)
        return WorkflowCls(location)
    
    def open_tab(self, location: list[str], wait_for_open=True):
        info_path = os.path.join(location[1], "info.json")
        if os.path.exists(info_path):
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)
            socket.post("add-tab", {"location": location, "name": info["name"]})
        else:
            socket.post("add-tab", {"location": location, "name": location[1]})
        if wait_for_open:
            self.wait_for_tab_open(location)
        return ViewCls(location)

    def wait_for_tab_open(self, location: Union[list[str], ViewCls]):
        times = 0
        while not self.is_tab_open(location):
            time.sleep(0.01)
            times += 1
            if times > 1000:
                raise Exception("Tab open timeout")

    def get_active(self) -> list[str]:
        result = socket.post_and_recv_result("get-active-tab", {})
        return result

    def get_all(self) -> list[list[str]]:
        results = socket.post_and_recv_result("get-all-tabs", {})
        return results

    def close_tab(self, location: Union[list[str], ViewCls]):
        if isinstance(location, ViewCls):
            location = location.location
        self.wait_for_tab_open(location)
        socket.post("close-tab", {"location": location})

    def switch_tab(self, location: Union[list[str], ViewCls]):
        if isinstance(location, ViewCls):
            location = location.location
        self.wait_for_tab_open(location)
        socket.post("switchTab", {"location": location})

    def is_tab_open(self, location: Union[list[str], ViewCls]):
        if isinstance(location, ViewCls):
            location = location.location
        result = socket.post_and_recv_result("is-tab-open", {"location": location})
        return result

    def pin_tab(self, location: Union[list[str], ViewCls]):
        if isinstance(location, ViewCls):
            location = location.location
        self.wait_for_tab_open(location)
        socket.post("pin-tab", {"location": location})

    def unpin_tab(self, location: Union[list[str], ViewCls]):
        if isinstance(location, ViewCls):
            location = location.location
        self.wait_for_tab_open(location)
        socket.post("unpin-tab", {"location": location})
