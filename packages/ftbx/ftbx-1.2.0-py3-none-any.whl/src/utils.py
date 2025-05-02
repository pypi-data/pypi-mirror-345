"""

PROJECT: flex_toolbox
FILENAME: utils.py
AUTHOR: David NAISSE
DATE: August 5th, 2024

DESCRIPTION: util functions
"""

import ast
import os
from typing import List
import pandas as pd
import re
import logging
import shutil
import stat
import subprocess
import requests
import graphviz
from rich.logging import RichHandler


FTBX_LOG_LEVELS = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(funcName)s | %(message)s",
    handlers=[RichHandler()],
)
logger = logging.getLogger(__name__)


def create_folder(folder_name: str, ignore_error: bool = False):
    """
    Create folder or return error if already exists.

    :param folder_name: folder name
    :param ignore_error: whether to ignore folder already exists or not

    :return: True if created, False if error
    """

    try:
        os.mkdir(folder_name)
        return True
    except FileExistsError:
        if ignore_error:
            return True
        else:
            logger.info(f"Folder {folder_name} already exists. ")
            return False


def create_script(object_name, object_config):
    """
    Create groovy script with according imports and plugins.

    :param object_name: script name
    :param object_config: script config
    :return:
    """

    imports = [
        (
            "import com.ooyala.flex.plugins.PluginCommand\n"
            if "miov2" not in str(object_config["objectType"]["href"])
            else "import tv.nativ.mio.api.plugin.command.PluginCommand\n"
        )
    ]
    script = "class Script extends PluginCommand {\n    <&code>\n}"

    # jef
    try:
        imports.extend(
            [
                "import " + imp["value"] + "\n"
                for imp in object_config["configuration"]["instance"][
                    "internal-script"
                ]["script-import"]
            ]
        )
    except:
        pass

    try:
        imports.extend(
            [
                "import " + imp["value"] + "\n"
                for imp in object_config["configuration"]["instance"]["imports"][
                    "import"
                ]
            ]
        )
    except:
        pass

    # groovy decision
    try:
        script = script.replace(
            "<&code>",
            object_config["configuration"]["instance"]["script_type"]["script"].replace(
                "\n", "\n    "
            ),
        )
    except:
        pass

    try:
        script = script.replace(
            "<&code>",
            object_config["configuration"]["instance"]["internal-script"][
                "script-content"
            ].replace("\n", "\n    "),
        )
    except:
        pass

    # groovy script
    try:
        script = script.replace(
            "<&code>",
            object_config["configuration"]["instance"]["script-contents"][
                "script"
            ].replace("\n", "\n    "),
        )
    except:
        script = script.replace("<&code>", "")

    # using replace \r because of API resp discrepancies
    content = f"{''.join(imports)}\n{script}".replace("\r", "")

    with open(os.path.join(object_name, "script.groovy"), "w") as groovy_file:
        groovy_file.write(content)

    return content


def find_nested_dependencies(data, parent_key="", separator="."):
    """
    Find dependencies in a JSON item config.


    :param data:
    :param parent_key:
    :param separator:
    :return:
    """

    paths = []

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            if "id" in value:
                paths.append(new_key)
            paths.extend(find_nested_dependencies(value, new_key, separator))

        if isinstance(value, list):
            for idx, list_item in enumerate(value):
                if new_key != "transitions":
                    paths.extend(
                        find_nested_dependencies(
                            value[idx], new_key + f".{idx}", separator
                        )
                    )

    # remove actionType and objectType as we don't want to pull these
    filtered_paths = list(filter(lambda x: not re.compile(r".*Type.*").match(x), paths))

    return filtered_paths


def get_nested_value(obj, keys):
    """
    Get nested value for a given key separater by '.'

    :param obj: obj to search the value in
    :param keys: sequence of keys separater by '.'
    """

    for key in keys.split("."):
        if "[" in key and "]" in key:
            if "[text]" in key:
                return str(obj[key.split("[text]")[0]])
            elif re.search(r"\[-?\d+\]", key):
                match = int(re.search(r"\[-?\d+\]", key).group(0)[1:-1])
                # skip if error from API
                try:
                    obj = obj[key.split("[")[0]][match]
                except:
                    return None
        elif isinstance(obj, dict) and key in obj:
            obj = obj[key]
        else:
            return None
    return obj


def kebab_to_camel_case(string):
    """
    Kebab to Camel Case.

    :param string: string to convert
    :return:
    """

    words = string.split("-")
    camel_case_words = [words[0]] + [word.capitalize() for word in words[1:]]
    camel_case = "".join(camel_case_words)

    return camel_case + "s"


def render_workflow(workflow_structure: dict, save_to: str):
    """
    Render workflows using graphviz.

    :param workflow_structure: dict of workflows
    :param save_to: where to save the workflow graphs
    """

    # Init. graph
    graph = graphviz.Digraph(name=f"graph", directory=f"{save_to}")

    try:
        # Create nodes with images
        for node in workflow_structure["nodes"]:
            label, style, color = config_node(node)
            graph.node(
                name=escape(node["name"]),
                label=label,
                shape="box",
                style=style,
                fillcolor=color,
            )

        # Create edges with names
        for transition in workflow_structure["transitions"]:
            graph.edge(
                escape(transition["from"]["name"]),
                escape(transition["to"]["name"]),
                label=transition["name"] if not None else None,
            )
    except KeyError:
        pass

    # Render graph
    graph.render(filename=f"graph", engine="dot", format="png")


def config_node(node: dict) -> tuple[str, str, str]:
    """
    Build node label with name, image and style.

    :param node: json dict of the node
    """

    # Init. node image and reformat node name
    node_image = ""
    node_name = escape(node.get("name"))
    node_style = "filled"
    node_color = ""
    node_action = ""

    # Style map nodes
    if "objectType" in node:
        # Workflow
        if node["objectType"]["name"] == "workflow-definition":
            node_image = os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-icons", "workflow.png"
            )
            node_color = "GhostWhite"
        # Wizard
        elif node["objectType"]["name"] == "wizard":
            node_image = os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-icons", "wizard.png"
            )
            node_color = "Yellow"
        # Resource
        elif node["objectType"]["name"] == "resource":
            if node["resourceSubType"] == "Inbox":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "resource-inbox.png"
                )
                node_color = "Lavender"
            else:
                node_image = os.path.join(
                    os.path.expanduser("~"),
                    ".ftbx",
                    "flex-icons",
                    "resource-hot-folder.png",
                )
                node_color = "LightBlue"
        # Event Handler
        elif node["objectType"]["name"] == "event-handler":
            node_image = os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-icons", "event-handler.png"
            )
            node_color = "Grey"
        # Launch Action
        elif node["objectType"]["name"] == "action":
            node_image = os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-icons", "workflow.png"
            )
            node_color = "GhostWhite"
            try:
                node_name = escape(
                    node["configuration"]["instance"]["workflows"][0]["Workflow"][
                        "name"
                    ]
                )
            except KeyError:
                node_name = escape(
                    node["configuration"]["instance"]["Workflow"]["name"]
                )
        # Timed Action
        elif node["objectType"]["name"] == "timed-action":
            node_image = os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-icons", "timed-action.png"
            )
            node_color = "DarkGrey"

    # Style workflow nodes
    elif "type" in node:
        if node["type"] == "ACTION":
            node_image = os.path.join(
                os.path.expanduser("~"),
                ".ftbx",
                "flex-icons",
                node["action"]["type"].lower() + ".png",
            )
            node_color = "GhostWhite"
            node_action = escape(node["action"]["name"])
        else:
            if node["type"] == "START":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "start.png"
                )
                node_color = "LightGreen"
            if node["type"] == "END":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "end.png"
                )
                node_color = "LightCoral"
            if node["type"] == "FORK":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "fork.png"
                )
            if node["type"] == "JOIN":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "join.png"
                )
            if node["type"] == "TASK":
                node_image = os.path.join(
                    os.path.expanduser("~"), ".ftbx", "flex-icons", "task.png"
                )
                node_color = "LightYellow"

    # Build label
    node_label = f"""<<table cellspacing="0" border="0" cellborder="0"><tr><td><img src="{node_image}" /></td><td> {node_name if not node_action else node_action}</td></tr></table>>"""

    return node_label, node_style, node_color


def str_to_bool(string: str):
    """
    Converts strings to bool ()

    :param string: from [false, False, true, True]
    :return:
    """

    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        raise ValueError(
            f"String is not a valid boolean (input: {string}, expected: [false, False, true, True])"
        )


def escape(string: str) -> str:
    """
    Custom string escape

    :param string:
    :return:
    """

    return re.sub(r"[^a-zA-Z0-9-_ ]", "", string)


def merge_script_in_object_config(script_path: str, object_config: dict) -> None:
    """
    Merge script.groovy in object config.

    :param script_path: path to script.groovy
    """

    imports = []
    jars = []

    # jobs
    if "action" in object_config:
        plugin = object_config.get("action").get("pluginClass")
    # actions
    else:
        plugin = object_config.get("pluginClass")

    with open(script_path, "r") as groovy_file:
        script_content = re.sub(
            r"import\s+.*?PluginCommand\n", "", groovy_file.read()
        ).strip()

        # get imports
        for line in script_content.split("\n"):
            if line.startswith("import") and "PluginCommand" not in line:
                imports.append({"value": line[7:], "isExpression": False})
                script_content = script_content.replace(line + "\n", "")

        # get code
        last_char = script_content.rindex("}")
        script_content = (
            script_content[: last_char - 1]
            .replace("class Script extends PluginCommand {", "")
            .strip()
        )

        # reformat \r, \t and \s in code
        script_content = re.sub(r"\t{1,}", reformat_tabs, script_content)
        script_content = re.sub(r" {4,}", reformat_spaces, script_content)

        # jef
        if plugin == "tv.nativ.mio.plugins.actions.jef.JEFActionProxyCommand":
            try:
                jars = object_config["configuration"]["instance"]["internal-script"][
                    "internal-jar-url"
                ]
            except:
                pass

            object_config["configuration"]["instance"]["internal-script"] = {}
            object_config["configuration"]["instance"]["internal-script"][
                "script-content"
            ] = script_content

            # imports
            if imports:
                object_config["configuration"]["instance"]["internal-script"][
                    "script-import"
                ] = imports

            # jars
            if jars:
                object_config["configuration"]["instance"]["internal-script"][
                    "internal-jar-url"
                ] = jars

        # groovy
        else:
            try:
                jars = object_config["configuration"]["instance"]["imports"]["jar-url"]
            except:
                pass

            # groovy script
            if plugin == "tv.nativ.mio.plugins.actions.script.GroovyScriptCommand":
                object_config["configuration"]["instance"]["script-contents"] = {}
                object_config["configuration"]["instance"]["script"] = script_content

            # groovy decision
            elif (
                plugin
                == "tv.nativ.mio.plugins.actions.decision.ScriptedDecisionCommand"
                or "tv.nativ.mio.plugins.actions.decision.multi.ScriptedMultiDecisionCommand"
                or "tv.nativ.mio.plugins.actions.wait.ScriptedWaitCommand"
            ):
                object_config["configuration"]["instance"]["script_type"] = {}
                object_config["configuration"]["instance"]["script_type"][
                    "script"
                ] = script_content
            else:
                raise Exception(f"Cannot recognize plugin {plugin}. Exiting...")

            # imports and jars
            if imports or jars:
                object_config["configuration"]["instance"]["imports"] = {}

                if imports:
                    object_config["configuration"]["instance"]["imports"][
                        "import"
                    ] = imports
                if jars:
                    object_config["configuration"]["instance"]["imports"][
                        "jar-url"
                    ] = jars


def reformat_tabs(match):
    """
    Reformat tabs for groovy scripts by removing one \t out of many.

    :param match:
    :return:
    """

    return match.group(0)[1:]


def reformat_spaces(match):
    """
    Reformat spaces for groovy scripts by removing one "    " out of many.

    :param match:
    :return:
    """

    return match.group(0)[4:]


def update_toolbox_resources():
    """
    Update toolbox resources by downloading the repo from bitbucket and extracting [flex-icons, flex-templates].
    """
    try:
        logger.info("Ensuring bitbucket.org is added to SSH known hosts...")
        known_hosts_path = os.path.expanduser("~/.ssh/known_hosts")
        os.makedirs(os.path.dirname(known_hosts_path), exist_ok=True)

        # Check if Bitbucket is already in known_hosts
        result = subprocess.run(
            ["ssh-keygen", "-F", "bitbucket.org"], capture_output=True, text=True
        )
        if "bitbucket.org" in result.stdout:
            logger.info("bitbucket.org fingerprints are already in SSH known hosts.")
        else:
            # Fetch and add fingerprints
            result = subprocess.run(
                ["ssh-keyscan", "bitbucket.org"],
                capture_output=True,
                text=True,
                check=True,
            )
            fingerprints = result.stdout.strip()

            # Append the raw fingerprints to a temp known_hosts file
            temp_known_hosts = os.path.join(
                os.path.dirname(known_hosts_path), "temp_known_hosts"
            )
            with open(temp_known_hosts, "w") as temp_file:
                temp_file.write(fingerprints + "\n")

            # Hash the fingerprints before adding to temp known_hosts
            subprocess.run(
                ["ssh-keygen", "-H", "-f", temp_known_hosts],
                check=True,
                capture_output=True,
            )

            # Append hashed fingerprints to the actual known_hosts
            with open(temp_known_hosts, "r") as temp_file:
                hashed_fingerprints = temp_file.read()

            if os.path.exists(known_hosts_path):
                with open(known_hosts_path, "r") as file:
                    existing_content = file.read()
            else:
                existing_content = ""

            if hashed_fingerprints not in existing_content:
                with open(known_hosts_path, "a") as known_hosts_file:
                    known_hosts_file.write(hashed_fingerprints)
                    logger.info(
                        "Added hashed bitbucket.org fingerprints to SSH known hosts."
                    )
            else:
                logger.info(
                    "bitbucket.org fingerprints are already in SSH known hosts."
                )

            # Cleanup temporary file
            os.remove(temp_known_hosts)

            # Cleanup backup files created by ssh-keygen
            backup_files = [known_hosts_path + ".old", temp_known_hosts + ".old"]
            for backup_file in backup_files:
                if os.path.exists(backup_file):
                    os.remove(backup_file)

        logger.info("Now fetching resources (icons, templates) from bitbucket...")
        subprocess.run(
            [
                "git",
                "clone",
                "--quiet",
                "git@bitbucket.org:ooyalaflex/flex-toolbox.git",
                os.path.join(os.path.expanduser("~"), ".ftbx", "flex-toolbox"),
            ],
            check=True,
        )
        logger.debug("flex-toolbox bitbucket repository has been cloned successfully")

        # flex-icons
        shutil.copytree(
            os.path.join(
                os.path.expanduser("~"), ".ftbx", "flex-toolbox", "flex-icons"
            ),
            os.path.join(os.path.expanduser("~"), ".ftbx", "flex-icons"),
            dirs_exist_ok=True,
        )
        logger.info(
            "flex-icons have been updated successfully ('~/.ftbx/flex-icons/'). "
        )

        # templates
        shutil.copytree(
            os.path.join(os.path.expanduser("~"), ".ftbx", "flex-toolbox", "templates"),
            os.path.join(os.path.expanduser("~"), ".ftbx", "templates"),
            dirs_exist_ok=True,
        )
        logger.info(
            "flex-templates have been updated successfully ('~/.ftbx/templates/')."
        )

        # delete temp repo
        shutil.rmtree(
            os.path.join(os.path.expanduser("~"), ".ftbx", "flex-toolbox"),
            onerror=on_shutil_rm_error,
        )
        logger.debug("Temporary repository deleted successfully. ")
    except Exception as e:
        logger.warning(
            f"Could not fetch icons nor templates due to an error: {e}. This will prevent you from rendering workflow graphs as images and using the `ftbx create` commands."
        )


def on_shutil_rm_error(func, path, exc_info):
    """Windows is garbage, but still have to deal with it."""

    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)


def convert_to_native_type(string: str):
    """
    Converts a string to its most likely type.

    :param string: a string
    """

    try:
        # int first
        return int(string)
    except ValueError:
        try:
            # float
            return float(string)
        except ValueError:
            # finally bool
            if string.lower() == "true":
                return True
            elif string.lower() == "false":
                return False
            else:
                # default to str
                return string


def download_file(url: str, destination: str):
    """
    Download a file from a URL.

    :param url: url from which to get the file
    :param destination: downloaded file path
    """

    # get the file
    response = requests.get(url, stream=True, timeout=2)

    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def clean_filename(filename: str):
    """
    Clean filename of special characters.

    :param filename: filename to clean
    """

    filename = (
        filename.replace("\\", "-")
        .replace(":", "-")
        .replace("/", "-")
        .replace("*", "-")
        .replace("?", "Q")
        .replace('"', "-")
        .replace("<=", "LTE")
        .replace("<", "LT")
        .replace(">=", "GTE")
        .replace(">", "GT")
    )

    return filename


def flatten_dict(input_dict, parent_key="", sep="."):
    """
    Flatten a nested dict recursively to get a dict with one key per nested item.*

    :param input_dict: input dictionary
    :param parent_key: parent key (or subdict) to flatten
    :param sep: separator between keys
    """

    flattened_dict = {}

    # for each k/v
    for k, v in input_dict.items():
        # get current key path
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        # handle item type
        # if item is dict, flatten subdict
        if isinstance(v, dict):
            flattened_dict.update(flatten_dict(v, new_key, sep=sep))
        # if item is list, flatten each item in the list
        elif isinstance(v, list):
            for i, list_item in enumerate(v):
                if isinstance(list_item, dict):
                    flattened_dict.update(
                        flatten_dict(
                            list_item, f"{new_key}.{list_item.get('name')}", sep=sep
                        )
                    )
                else:
                    flattened_dict[f"{new_key}.{list_item.get('name')}"] = v

        # neither list nor dict, add to flattened dict
        else:
            if isinstance(v, str) and "\n" in v:
                multiline = v.replace("\t", "").split("\n")
                for idx, line in enumerate(multiline):
                    flattened_dict[f"{new_key}{sep}line{'{:05d}'.format(idx)}"] = (
                        line.strip()
                    )
            else:
                flattened_dict[new_key] = v

    return flattened_dict


def colored_text(text: str, color: str = ""):
    """
    Print text in terminal, with colors.

    :param text: text to print
    :param color: color to use

    """

    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
    }
    reset_color = "\033[0m"

    if color.lower() in colors:
        return f"{colors[color.lower()]}{text}{reset_color}"
    else:
        return text


def compare_dicts_list(dict_list, environments: list, exclude_keys=None):
    """
    Compare a list of flattened dicts and returns a dataframe containing only differences.

    :param dict_list: list of flattened dicts
    :param environments: list of environments
    :param exclude_keys: keys to exclude from returned dataframe (contain-type match)
    """

    # check dict_list is a list of dict
    if not dict_list or not all(isinstance(d, dict) for d in dict_list):
        raise ValueError("Input should be a non-empty list of dictionaries.")

    # keys that are removed by default
    if exclude_keys is None:
        exclude_keys = [
            r"id",
            r"Id",
            r"assignment",
            r"objectType",
            r"externalIds",
            r"href",
            r"icons",
            r"created",
            r"lastModified",
            r"visibility",
            r"owner",
            r"createdBy",
            r"account.",
            r"revision",
            r"deleted",
            r"latestVersion",
            r"plugin",
            r"configuration.instance.recipients",
            r"isExpression",
            r"description",
            r"secret",
            r"properties.message",
            r"username",
            r"password",
            r"layout",
            r".url",
            r"metadata.definition",
            r"saml-configuration",
            r"external-authentication-workspace",
            r"external-authentication-endpoint",
            r"configuration.definition",
            r"useLatestAvailableVersion",
            r"latestPluginVersion",
            r"prevPluginVersion",
            r"lastPollTime",
        ]

    # make a set of all unique keys found in all flattened dicts
    unique_keys = set()
    for d in dict_list:
        unique_keys.update(d.keys())

    # for each key in the unique keys set, compare the values between flattened dicts
    comparison_data = {}
    for key in unique_keys:
        # exclude useless keys
        if any(exclude_key in key for exclude_key in exclude_keys):
            continue

        # compare values between flattened dict
        values = [d.get(key) if d.get(key) else None for d in dict_list]
        if len(set(values)) > 1:
            comparison_data[key] = values

    # make it a dataframe
    diff_df = pd.DataFrame(comparison_data)
    diff_df = diff_df.transpose()
    diff_df = diff_df.sort_index()
    try:
        diff_df.columns = [e.name for e in environments]
    except Exception as ex:
        # here means no differences
        if "Expected axis has 0 elements" in str(ex):
            diff_df = None
        else:
            raise Exception(ex)

    return diff_df


def get_sdk_version_mapping() -> dict:
    """
    Get updated version mapping from flex api doc.
    """

    session = requests.session()

    # get from flex api doc
    response = session.get("https://help.dalet.com/daletflex/apis/version_mapping.js")

    content_str = response.content.decode("utf-8")
    content_str = content_str.replace("const version_mapping = ", "")
    content_str = content_str.rstrip(";")
    content_str = content_str.replace("null", "None")
    version_mapping = ast.literal_eval(content_str)

    return version_mapping


def filters_to_dict(filters: List):
    """
    Converts filters cmd args to dict
    """

    filters_dict = {}

    for filter in filters:
        filters_dict[filter.split("=")[0]] = convert_to_native_type(
            "=".join(filter.split("=")[1:])
        )

    return filters_dict


def remove_nested_keys(d, keys_to_remove):
    """
    Removes nested keys from a dictionary based on dot-separated key paths.

    Args:
        d (dict): The nested dictionary to modify
        keys_to_remove (list): List of dot-separated key paths to remove
    """
    for key_path in keys_to_remove:
        parts = key_path.split(".")
        current = d
        # Navigate through nested dictionaries
        for part in parts[:-1]:
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                break
        else:
            current.pop(parts[-1], None)
