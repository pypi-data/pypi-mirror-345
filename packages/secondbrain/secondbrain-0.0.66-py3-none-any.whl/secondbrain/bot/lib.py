import os
from collections import defaultdict
from pathlib import Path
from secondbrain.reference.bot import ref_bot
from secondbrain.reference.mcp import ref_mcp
from secondbrain.reference.tool import ref_tools
from secondbrain.reference.workflow import ref_workflow


async def get_abilities(cwd, bot_setting):
    config = bot_setting["abilitiesConfig"]
    abilities = []
    mcp_servers = []
    
    bot_config = config["botConfig"]
    for item_id in bot_config:
        item = ref_bot(item_id)
        if item:
            abilities.append(item)
            
    mcp_config = config["mcpConfig"]
    for item_id in mcp_config:
        item = ref_mcp(item_id, mcp_config[item_id], cwd)
        if item:
            mcp_server = await item.__aenter__()
            mcp_servers.append(mcp_server)

    tool_config = config["toolConfig"]
    for item_id in tool_config:
        item_config = tool_config[item_id]
        items = ref_tools(item_id, item_config, cwd)
        abilities.extend(items)
    
    workflow_config = config["workflowConfig"]
    for item_id in workflow_config:
        item_config = workflow_config[item_id]
        item = ref_workflow(item_id, item_config)
        if item:
            abilities.append(item)
    return abilities, mcp_servers


def resolve_relative_path(cwd:str, path_str: str) -> str:
    """返回基于CWD的规范化绝对路径"""
    path = Path(path_str)
    if path.is_absolute():
        return str(path.resolve())
    else:
        return str((Path(cwd) / path_str).resolve())


def read_local_file(file_path: str) -> str:
    """读取本地文件内容"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        import chardet

        with open(file_path, "rb") as f:
            rawdata = f.read()
            encoding = chardet.detect(rawdata)["encoding"]
            return rawdata.decode(encoding)


# 全局忽略列表
IGNORE_LIST = [
  'node_modules',
  '.git',
  '.vscode',
  '.idea',
  'gitServer',
  '.DS_Store',
  '$RECYCLE.BIN',
  '.Trash-1000',
  '.Spotlight-V100',
  '.Trashes',
  '.TemporaryItems',
  '.fseventsd',
  'System Volume Information',
  'pycache',
  'env',
  'venv',
  'target/dependency',
  'build/dependencies',
  'dist',
  'out',
  'bundle',
  'vendor',
  'tmp',
  'temp',
  'deps',
  'pkg',
  'Pods',
  'build',
  '.egg-info',
  '.venv',
  '__pycache__',
  '.vs',
  '.next',
  '.nuxt',
  '.cache',
  '.sass-cache',
  '.gradle',
  '.ipynb_checkpoints',
  '.pytest_cache',
  '.mypy_cache',
  '.tox',
  '.hg',
  '.svn',
  '.bzr',
  '.lock-wscript',
  '.wafpickle-[0-9]*',
  '.lock-waf_[0-9]*',
  '.Python',
  '.jupyter',
  '.vscode-test',
  '.history',
  '.yarn',
  '.yarn-cache',
  '.eslintcache',
  '.parcel-cache',
  '.cache-loader',
  '.nyc_output',
  '.node_repl_history',
  '.pnp.js',
  '.pnp',
  '.obsidian',
  ".husky",
  '.github',
  ".changeset"
]


def should_ignore(path):
    """检查路径是否在忽略列表中"""
    parts = path.split(os.sep)
    return any(part in IGNORE_LIST for part in parts)


def get_files_and_folders(root, recursive: bool):
    """递归获取所有文件和文件夹，并记录属性"""
    items = []

    # 使用 os.walk 遍历目录
    for dirpath, dirnames, filenames in os.walk(root):
        # 排除忽略列表中的路径
        if should_ignore(dirpath):
            continue

        # 记录文件夹
        for dirname in dirnames:
            full_path = os.path.join(dirpath, dirname)
            if not should_ignore(full_path):
                relative_path = os.path.relpath(full_path, root)
                is_empty = not os.listdir(full_path)
                depth = relative_path.count(os.sep)
                items.append(
                    (relative_path, "empty_folder" if is_empty else "folder", depth)
                )

        # 记录文件
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if not should_ignore(full_path):
                relative_path = os.path.relpath(full_path, root)
                depth = relative_path.count(os.sep)
                items.append((relative_path, "file", depth))

        # 如果 recursive 为 False，则只遍历当前目录，不进入子目录
        if not recursive:
            break

    return items


def format_filelist_str(items, limit):
    """根据limit格式化输出"""
    depth_groups = defaultdict(list)
    for item in items:
        depth_groups[item[2]].append(item)

    max_depth = max(depth_groups.keys(), default=0)
    show_list = []
    last_depth = 0

    # 浅层
    current_items = sorted(depth_groups[0], key=lambda x: x[0])
    overflow = len(current_items) > limit
    for item in current_items[:limit]:
        show_list.append(item)

    for depth in range(1, max_depth + 1):
        current_items = depth_groups[depth]
        if len(show_list) + len(current_items) <= limit:
            last_depth = depth
            for item in current_items:
                show_list.append(item)
        else:
            break

    result_str_list = []
    show_list.sort(key=lambda x: x[0])
    for item in show_list:
        if item[1] == "file":
            result_str_list.append(f"{item[0]}")
        elif item[1] == "folder" and item[2] == last_depth:
            result_str_list.append(f"{item[0]}/more...")
        else:
            result_str_list.append(f"{item[0]}/")
    if overflow:
        result_str_list.append("more...")

    return "\n".join(result_str_list)


def get_formatted_filelist_str(root: str, recursive: bool, limit=200):
    items = get_files_and_folders(root, recursive)
    return format_filelist_str(items, limit=limit)
