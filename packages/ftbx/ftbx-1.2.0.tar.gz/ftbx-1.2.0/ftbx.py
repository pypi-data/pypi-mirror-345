#!/usr/bin/python3

"""

    PROJECT: flex_toolbox
    FILENAME: toolbox.py
    AUTHOR: David NAISSE
    DATE: September 07, 2023
    DESCRIPTION: terminal command reader

"""

import os
import logging
import sys
from typing import Annotated, List
from rich.logging import RichHandler
import typer

from src.cmd.assert_cmd import assert_command_func
from src.cmd.cancel_cmd import cancel_command_func
from src.cmd.create_cmd import create_command_func
from src.cmd.compare_cmd import compare_command_func
from src.cmd.connect_cmd import connect_command_func
from src.cmd.env_cmd import env_command_func
from src.cmd.fail_cmd import fail_command_func
from src.cmd.init_cmd import init_command_func
from src.cmd.launch_cmd import launch_command_func
from src.cmd.list_cmd import list_command_func
from src.cmd.pull_cmd import pull_command_func
from src.cmd.push_cmd import push_command_func
from src.cmd.query_cmd import query_command_func
from src.cmd.restore_cmd import restore_command_func
from src.cmd.retry_cmd import retry_command_func
from src.cmd.setup_cmd import setup_command_func
from src.cmd.update_cmd import update_command_func
from src.utils import FTBX_LOG_LEVELS
from src.variables import *
from src.cmd.workflow_designer_cmd import workflow_designer_command_func
from src.cmd.metadata_designer_cmd import metadata_designer_command_func

ftbx = typer.Typer()

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(name)s | %(message)s",
    handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)


@ftbx.command(name="assert")
def assert_cmd(
    object_type: Annotated[AssertOptions, typer.Argument()],
    object_name_or_id: Annotated[str, typer.Argument()],
    assertions: Annotated[List[str], typer.Argument(help="operators: [!~, !=, >=, <=, ~, =, <, >]")],
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Asserts some statement(s) or condition(s). Returns 'True' or 'False'.

    - ftbx assert assets 12345 'deleted!=True'\n
    - ftbx assert actions ftbx-script 'concurrentJobsLimit>0'\n
    - ftbx assert actions ftbx-script 'configuration.instance.execution-lock-type=NONE'\n
    """

    assert_command_func(
        object_type=object_type.value,
        object_name_or_id=object_name_or_id,
        assertions=assertions,
        in_=in_,
    )

@ftbx.command(name="cancel")
def cancel_cmd(
    object_type: Annotated[CancelOptions, typer.Argument()],
    object_name_or_id: Annotated[str, typer.Argument()] = None,
    filters: Annotated[List[str], typer.Option(help="ex: 'name=asset_name', 'limit=30'")] = [],
    post_filters: Annotated[List[str], typer.Option(help="ex: 'configuration.instance.execution-lock-type=NONE' 'concurrentJobsLimit>0'")] = [],
    file: Annotated[str, typer.Option(help="ex: 'lists/failed_jobs.csv' 'lists/failed_jobs.json' (from 'ftbx list')")] = None,
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Cancel **failed** object instance(s) in an environment.

    - ftbx cancel jobs 12345 --in 'flex-stg'  # cancel job 12345 in flex-stg\n
    - ftbx cancel workflows --filters 'name=my-workflow' 'limit=20' # cancel 20 workflows\n
    - ftbx cancel jobs --filters 'name=my-jobs' --post-filters 'history.events[-1].stackTrace~Row updated by another transaction'
    """

    cancel_command_func(
        object_type=object_type.value,
        object_name_or_id=object_name_or_id,
        filters=filters,
        post_filters=post_filters,
        in_=in_,
        file=file
    )

@ftbx.command(name="compare")
def compare_cmd(
    object_type: Annotated[CompareOptions, typer.Argument()],
    environments: Annotated[List[str], typer.Argument()],
    filters: Annotated[List[str], typer.Option()] = [],
):
    """
    Compares objects between environments. Saves the result(s) in 'compare_env1_env2/'.

    - ftbx compare actions flex-dev flex-stg flex-prod  # compare all actions\n
    - ftbx compare actions flex-dev flex-stg flex-prod --filters name=ftbx-script\n
    - ftbx compare metadataDefinitions flex-stg flex-prod --filters name=Asset\n
    """

    compare_command_func(
        object_type=object_type.value, environments=environments, filters=filters
    )


@ftbx.command(name="connect")
def connect_cmd(
    env_or_url: Annotated[str, typer.Argument()],
    username: Annotated[str, typer.Argument()] = None,
    password: Annotated[str, typer.Argument()] = None,
    alias: Annotated[str, typer.Option(help="ex: flex-stg, flex-prod")] = None,
    version: Annotated[str, typer.Option(help="ex: 2022.5.7, 2024.4.5")] = "latest",
):
    """
    Connects to an environment. Environment file is located at '~/.ftbx/environments'.

    - ftbx connect 'https://flex_url.com' my_user --alias flex-stg --version 2024.5.0  # first time\n
    - ftbx connect flex-stg # once you successfully connected\n
    """

    connect_command_func(
        env_or_url=env_or_url,
        username=username,
        password=password,
        alias=alias,
        version=version,
    )


@ftbx.command(name="create")
def create_cmd(
    object_type: Annotated[CreateOptions, typer.Argument()],
    plugin: Annotated[CreatePlugins, typer.Argument()],
    object_name: Annotated[str, typer.Argument()],
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Creates templated objects in an environment.

    - ftbx create accounts default 'my-account' --in flex-dev\n
    - ftbx create accountProperties default 'my-account-property' --in flex-dev\n
    - ftbx create actions script 'my-script' --in flex-dev\n
    - ftbx create actions decision 'my-decision' --in flex-dev\n
    - ftbx create wizards launchWorkflow 'my-launch-workflow-wizard' --in flex-dev\n
    - ftbx create workflowDefinitions default 'my-workflow' --in flex-dev\n
    - ftbx create workspaces default 'my-workspace' --in flex-dev
    """

    create_command_func(
        object_type=object_type.value,
        plugin=plugin.value,
        object_name=object_name,
        in_=in_,
    )


@ftbx.command(name="env")
def env_cmd():
    """
    Displays all available environments and their urls, aliases, versions and usernames.\n

    - ftbx env\n
    """

    env_command_func()
    

@ftbx.command(name="fail")
def fail_cmd(
    object_type: Annotated[FailOptions, typer.Argument()],
    object_ids: Annotated[List[str], typer.Argument()] = None,
    from_file: Annotated[str, typer.Option(help="ex: 'lists/failed_jobs.csv")] = None,
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Fail object instances (requires to be connected to the servers and `consul_host` and `consul_token` in `~/.ftbx/environments`).                                  

    - ftbx fail jobs 1234 5678 91011  # fail the 3 jobs in the default environment\n
    - ftbx fail jobs --from-file 'lists/failed_jobs.csv'\n
    - ftbx fail jobs --from-file 'lists/failed_jobs.json'\n
    """

    fail_command_func(
        object_type=object_type.value,
        object_ids=object_ids,
        from_file=from_file,
        in_=in_,
    )


@ftbx.command()
def init():
    """
    Initializes the flex-toolbox. This is the first command you must run upon installation.

    - ftbx init
    """

    init_command_func()


@ftbx.command(name="launch")
def launch_cmd(
    object_type: Annotated[LaunchOptions, typer.Argument()],
    object_name: Annotated[str, typer.Argument()],
    in_: Annotated[str, typer.Option("--in")] = "default",
    params: Annotated[List[str], typer.Option(help="ex: 'assetId=1234' 'workspaceId=303'")] = [],
    from_file: Annotated[str, typer.Option(help="ex: 'payload.json'")] = None,
    use_local: Annotated[bool, typer.Option(help="Whether to push local config before launching the instance")] = False,
    listen: Annotated[bool, typer.Option(help="Whether to get the logs of the launched instance in the terminal")] = False,
):
    """
    Launches a job or workflow with the given parameters.

    - ftbx launch jobs 'ftbx-script' --params assetId=12345 workspaceId=303 --in flex-dev --listen\n
    - ftbx launch workflows 'ftbx-workflow' --params assetId=12345 --in flex-dev\n
    - ftbx launch jobs 'ftbx-script' --use-local --listen\n  # push local config before launching
    """

    launch_command_func(
        object_type=object_type.value,
        object_name=object_name,
        in_=in_,
        params=params,
        from_file=from_file,
        use_local=use_local,
        listen=listen,
    )


@ftbx.command(name="list")
def list_cmd(
    object_type: Annotated[ListOptions, typer.Argument()],
    filters: Annotated[List[str], typer.Option(help="ex: 'status=Running' 'name=asset_name'")] = [], 
    post_filters: Annotated[List[str], typer.Option(help="ex: 'configuration.instance.execution-lock-type=NONE' 'concurrentJobsLimit>0'")] = [],
    from_: Annotated[str, typer.Option("--from")] = "default",
    from_csv: Annotated[str, typer.Option(help="ex: lists/asset_list.csv")] = None,
    name: Annotated[str, typer.Option(help="Name under which the JSON and CSV files should be saved")] = None,
    batch_size: Annotated[int, typer.Option(help="The batch size for the API number of results")] = None
):
    """
    Lists objects from an environment. Saves the results as CSV and JSON files in 'lists/'.

    - ftbx list actions  # list all actions\n
    - ftbx list jobs --filters status=Failed name=ftbx-script --from flex-dev --name 'failed_flex-dev_jobs'\n
    - ftbx list actions --post-filters 'concurrentJobsLimit>0' --from flex-dev  # all actions with concurrency > 0\n
    - ftbx list assets --filters 'fql=(name~PACKAGE and deleted=false)' --name 'live_packages'  # using fql\n
    """

    list_command_func(
        object_type=object_type.value,
        filters=filters,
        post_filters=post_filters,
        from_=from_,
        from_csv=from_csv,
        name=name,
        batch_size=batch_size,
    )


@ftbx.command(name="metadataDesigner")
def metadata_designer_cmd(
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Opens the metadata designer in your default web browser.

    - ftbx metadataDesigner  # in default environment\n
    - ftbx metadataDesigner --in flex-dev
    """

    metadata_designer_command_func(in_=in_)


@ftbx.command(name="pull")
def pull_cmd(
    object_type: Annotated[PullOptions, typer.Argument()],
    object_name_or_id: Annotated[str, typer.Argument()] = None,
    filters: Annotated[List[str], typer.Option(help="ex: 'status=Running' 'name=asset_name'")] = [],
    post_filters: Annotated[List[str], typer.Option(help="ex: 'configuration.instance.execution-lock-type=NONE' 'concurrentJobsLimit>0'")] = [],
    from_: Annotated[List[str], typer.Option("--from")] = ["default"],
    with_dependencies: Annotated[bool, typer.Option("--with-dependencies/--without-dependencies", help="Whether to also pull the objects dependencies")] = False,
):
    """
    Pulls objects from environment(s) as files and folders.

    - ftbx pull jobs 12345 --from flex-dev  # pull job 12345\n
    - ftbx pull all --from flex-dev flex-stg flex-prod # pull every config objects\n
    - ftbx pull actions  # pull all actions\n
    - ftbx pull workflowDefinitions --filters name=ftbx-workflow --from 'flex-dev' --with-dependencies\n
    - ftbx pull workflowDefinitions ftbx-workflow --from 'flex-dev' --with-dependencies  # same as above\n
    """

    pull_command_func(
        object_type=object_type.value,
        object_name_or_id=object_name_or_id,
        filters=filters,
        post_filters=post_filters,
        from_=from_,
        with_dependencies=with_dependencies,
    )


@ftbx.command(name="push")
def push_cmd(
    object_type: Annotated[PushOptions, typer.Argument()],
    object_names: Annotated[List[str], typer.Argument()],
    from_: Annotated[str, typer.Option("--from")] = "default",
    to: Annotated[List[str], typer.Option("--to")] = ["default"],
    retry: Annotated[bool, typer.Option(help="Whether to also retry the given job")] = False,
    listen: Annotated[bool, typer.Option(help="Whether to get the logs of the job in the terminal")] = False,
    push_to_failed_jobs: Annotated[str, typer.Option(help="'all' OR csv file containing failed jobs to push the config to and retry (from 'ftbx list')")] = None,
    with_dependencies: Annotated[bool, typer.Option("--with-dependencies/--without-dependencies", help="Whether to also push the objects dependencies")] = False,
):
    """
    Creates or updates objects in one or multiple environments. Generates backups before pushing.

    - ftbx push actions 12345 --push-to-failed-jobs all  # update action and push to all failed jobs\n
    - ftbx push actions 'ftbx-script' 'ftbx-decision'  # update two actions\n
    - ftbx push actions 'ftbx-script' --from 'flex-dev' --to 'flex-stg' 'flex-prod'  # create action in stg and prod\n
    - ftbx push workflowDefinitions 'ftbx-workflow' --from 'flex-dev' --to 'flex-stg' --with-dependencies  # with dependencies\n
    """

    push_command_func(
        object_type=object_type.value,
        object_names=object_names,
        from_=from_,
        to=to,
        retry=retry,
        listen=listen,
        push_to_failed_jobs=push_to_failed_jobs,
        with_dependencies=with_dependencies,
    )


@ftbx.command(name="query")
def query_cmd(
    method: Annotated[QueryOptions, typer.Argument()],
    url: Annotated[str, typer.Argument(help="ex: 'assets/1234/annotations' 'actions/3332/configuration'")],
    from_: Annotated[str, typer.Option("--from")] = "default",
    payload: Annotated[List[str], typer.Option(help="ex: 'action=enable' 'action=disable' or 'payload.json'")] = [],
    stdout: Annotated[bool, typer.Option(help="Whether to display the result in the terminal")] = False,
):
    """
    Queries an environment, useful as postman replacement. Saves the results in 'query.json'.

    - ftbx query GET assets/12345/annotations\n
    - ftbx query POST actions/3332/actions --payload 'action=disable'  # disable an action\n
    - ftbx query GET collections --from flex-dev\n
    """

    query_command_func(
        method=method.value, url=url, from_=from_, payload=payload, stdout=stdout
    )


@ftbx.command(name="restore")
def restore_cmd(
    object_type: Annotated[RestoreOptions, typer.Argument()],
    object_name: Annotated[str, typer.Argument()],
    backup_name: Annotated[str, typer.Argument()],
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Restores objects to a previous point in time. 

    - ftbx restore actions 'ftbx-script' '2024-08-30 09h50m38s' --in flex-dev\n
    - ftbx restore assets 12345 '2024-07-23 09h50m38s' --in flex-dev\n
    """

    restore_command_func(
        object_type=object_type.value,
        object_name=object_name,
        backup_name=backup_name,
        in_=in_,
    )


@ftbx.command(name="retry")
def retry_cmd(
    object_type: Annotated[RetryOptions, typer.Argument()],
    in_: Annotated[str, typer.Option("--in")] = "default",
    filters: Annotated[List[str], typer.Option(help="ex: 'name=ftbx-script' 'createdFrom=22 Jul 2024'")] = [],
    file: Annotated[str, typer.Option(help="ex: 'lists/failed_jobs.csv' 'lists/failed_jobs.json' (from 'ftbx list')")] = None,
):
    """
    Retries object instances in an environment either from API filters or from a file (csv or json).

    - ftbx retry jobs --in flex-dev # retry all failed jobs\n
    - ftbx retry jobs --filters 'name=ftbx-script' 'createdFrom=22 Jul 2024'\n
    - ftbx retry workflows --file 'lists/failed_workflows.csv' --in flex-dev\n
    """

    retry_command_func(
        object_type=object_type.value, in_=in_, filters=filters, file=file
    )


@ftbx.command(name="setup")
def setup_cmd(
    version: Annotated[str, typer.Option()] = "latest"
):
    """
    Setups the API documentation (in 'docs/') and the SDK (in 'sdks/') for a given flex version.

    - ftbx setup --version latest\n
    - ftbx setup --version 2022.5.7\n
    """

    setup_command_func(version=version)


@ftbx.command(name="update")
def update_cmd():
    """
    Updates the toolbox to the latest version.

    - ftbx update\n
    """

    update_command_func()


@ftbx.command(name="workflowDesigner")
def workflow_designer_cmd(
    workflow_name: Annotated[str, typer.Argument()],
    in_: Annotated[str, typer.Option("--in")] = "default",
):
    """
    Opens the workflow designer for a given workflow in an environment.

    -ftbx workflow_designer 'ftbx-workflow' --in flex-dev\n
    """

    workflow_designer_command_func(workflow_name=workflow_name, in_=in_)


# TODOs:
#     ftbx fail: docstrings, readme
#     ftbx create (all)
#     ftbx test
#     ftbx enable
#     ftbx start
#     ftbx listen
#     1 create objects from CSV
#     sync


def preprocess_args():
    """
    Typer doesn't support whitespace-separated multi-value options.

    We preprocess the sysargv so that:
    - python3 app.py some_command --filters filter1 filter2 filter3 --environments env1 env2 env3

    becomes:
    - python3 app.py some_command --filters filter1 --filters filter2 --filters filter3 --environments env1 --environments env2 --environments env3

    //!\\ DOWNSIDE: options should always be after arguments in the CLI command //!\\
    """

    logger.debug(f"Initial CLI command is: {sys.argv}")

    # get main cmd
    final_cmd = []
    for idx, arg in enumerate(sys.argv):
        if any(arg.startswith(_) for _ in ['-', '--']):
            break
        else:
            final_cmd.append(arg)
    logger.debug(f"Main command is: {final_cmd}")

    # get options and their values
    for idx, arg in enumerate(sys.argv):
        if any(arg.startswith(_) for _ in ['-', '--']):
            opt_values = [] 
            for value in sys.argv[idx+1:]:
                if any(value.startswith(_) for _ in ['-', '--']):
                    break
                else:
                    opt_values.append(value)
            
            if len(opt_values) >= 1:
                [final_cmd.extend([arg, opt_value]) for opt_value in opt_values]
            else:
                final_cmd.append(arg)

    # replace by reformatted
    logger.debug(f"Final command is: {final_cmd}")
    sys.argv = final_cmd
    

def main():
    preprocess_args()
    ftbx()

if __name__ == "__main__":
    main()
