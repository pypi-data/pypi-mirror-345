import time
from typing import Union
from secondbrain import utils


socket = utils.socket


class ViewCls:

    def __init__(self, location: list[str], nodeIds: list[str] = []):
        self.location = location
        self.nodeIds = nodeIds
        self.is_in_workflow = len(nodeIds) > 0
        self.is_tab = len(nodeIds) == 0

    def __getitem__(self, key):
        return self.location[key]

    def wait_for_tab_open(self):
        times = 0
        while not self.is_tab_open():
            time.sleep(0.01)
            times += 1
            if times > 1000:
                raise Exception("Tab open timeout")

    def close_tab(self):
        assert self.is_tab
        self.wait_for_tab_open()
        socket.post("close-tab", {"location": self.location})

    def set_activate(self):
        assert self.is_tab
        self.wait_for_tab_open()
        socket.post("switchTab", {"location": self.location})

    def is_tab_open(self):
        assert self.is_tab
        result = socket.post_and_recv_result("is-tab-open", {"location": self.location})
        return result

    def pin_tab(self):
        assert self.is_tab
        self.wait_for_tab_open()
        socket.post("pin-tab", {"location": self.location})

    def unpin_tab(self):
        assert self.is_tab
        self.wait_for_tab_open()
        socket.post("unpin-tab", {"location": self.location})


class WorkflowCls(ViewCls):

    def layout_arrangement(self):
        # NetworkX layout arrangement，直接用python的布局即可，虽然没有输入输出port的，但是用节点坐标，再缩放几倍一般情况就可以了
        pass

    def run(self, wait_for_end=False):
        result = socket.post_and_recv_result(
            "workflow-run", {"location": self.location, "wait_for_end": wait_for_end}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]  # task_id

    def stop(self):
        result = socket.post_and_recv_result(
            "workflow-stop", {"location": self.location}
        )
        if not result["ok"]:
            raise Exception(result["value"])

    def get_state(self):
        result = socket.post_and_recv_result(
            "workflow-get-state", {"location": self.location}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_nodes(self):
        result = socket.post_and_recv_result(
            "workflow-get-graph-nodes", {"location": self.location}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_edges(self):
        result = socket.post_and_recv_result(
            "workflow-get-graph-edges", {"location": self.location}
        )
        return result["value"]

    def add_text_node(self, text: str, position="center"):
        result = socket.post_and_recv_result(
            "workflow-add-text-node",
            {"location": self.location, "text": text, "position": position},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        time.sleep(0.01)
        return result["value"]  # node

    def add_markdown_node(self, text: str, position="center"):
        result = socket.post_and_recv_result(
            "workflow-add-markdown-node",
            {"location": self.location, "text": text, "position": position},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        time.sleep(0.01)
        return result["value"]  # node

    def add_file_node(self, file_path: str, position="center"):
        is_step = False
        if file_path.lower().endswith(".py"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "ps_workflow" in content:
                    is_step = True
        if is_step:
            return self.add_step_file_node(file_path, position)
        result = socket.post_and_recv_result(
            "workflow-add-file-node",
            {"location": self.location, "file_path": file_path, "position": position},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        time.sleep(0.01)
        return result["value"]  # node

    def add_step_file_node(self, file_path: str, position="center"):
        result = socket.post_and_recv_result(
            "workflow-add-step-file-node",
            {"location": self.location, "file_path": file_path, "position": position},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        time.sleep(0.01)
        return result["value"]  # node

    def add_edge(
        self, from_node_id: str, from_port_id: str, to_node_id: str, to_port_id: str
    ):
        result = socket.post_and_recv_result(
            "workflow-add-edge",
            {
                "location": self.location,
                "source": {"cell": from_node_id, "port": from_port_id},
                "target": {"cell": to_node_id, "port": to_port_id},
            },
        )
        if not result["ok"]:
            raise Exception(result["value"])
        time.sleep(0.01)
        return result["value"]  # edge

    def get_node_info(self, node: Union[str, object]):
        if isinstance(node, object):
            node_id = node["id"]
        result = socket.post_and_recv_result(
            "workflow-get-node-info", {"location": self.location, "node_id": node_id}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_node_state(self, node: Union[str, object]):
        if isinstance(node, object):
            node_id = node["id"]
        result = socket.post_and_recv_result(
            "workflow-get-node-state", {"location": self.location, "node_id": node_id}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_node_log(self, node: Union[str, object]):
        if isinstance(node, object):
            node_id = node["id"]
        result = socket.post_and_recv_result(
            "workflow-get-node-log", {"location": self.location, "node_id": node_id}
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_node_input_data(self, node: Union[str, object], port: str):
        if isinstance(node, object):
            node_id = node["id"]
        result = socket.post_and_recv_result(
            "workflow-get-node-input-data",
            {"location": self.location, "node_id": node_id, "port": port},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def get_node_output_data(self, node: Union[str, object], port: str):
        if isinstance(node, object):
            node_id = node["id"]
        result = socket.post_and_recv_result(
            "workflow-get-node-output-data",
            {"location": self.location, "node_id": node_id, "port": port},
        )
        if not result["ok"]:
            raise Exception(result["value"])
        return result["value"]

    def parse_node_data(self, data: Union[dict, list]):
        if isinstance(data, list):
            return [parse_data(d) for d in data]
        return parse_data(data)
