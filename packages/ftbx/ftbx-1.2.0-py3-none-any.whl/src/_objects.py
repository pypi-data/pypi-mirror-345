"""

    PROJECT: flex_toolbox
    FILENAME: objects.py
    AUTHOR: David NAISSE
    DATE: August 8th, 2024

    DESCRIPTION: objects class
"""

import datetime
from enum import Enum
import json
import logging
import importlib
import math
import os
import re
import sys
from time import sleep
from typing import Any, List, Optional, Union
import urllib.parse

from tqdm import tqdm

from src.utils import (
    FTBX_LOG_LEVELS,
    colored_text,
    create_folder,
    create_script,
    find_nested_dependencies,
    get_nested_value,
    kebab_to_camel_case,
    merge_script_in_object_config,
    remove_nested_keys,
    render_workflow,
    str_to_bool,
)
from src._environment import Environment


class ObjectType(Enum):
    ACCOUNT_PROPERTIES = "accountProperties"
    ACCOUNTS = "accounts"
    ACTIONS = "actions"
    ASSETS = "assets"
    COLLECTIONS = "collections"
    EVENT_HANDLERS = "eventHandlers"
    EVENTS = "events"
    GROUPS = "groups"
    JOBS = "jobs"
    MESSAGE_TEMPLATES = "messageTemplates"
    METADATA_DEFINITIONS = "metadataDefinitions"
    OBJECT_TYPES = "objectTypes"
    PROFILES = "profiles"
    QUOTAS = "quotas"
    RESOURCES = "resources"
    ROLES = "roles"
    TAG_COLLECTIONS = "tagCollections"
    TASK_DEFINITIONS = "taskDefinitions"
    TASKS = "tasks"
    TAXONOMIES = "taxonomies"
    TIMED_ACTIONS = "timedActions"
    USER_DEFINED_OBJECT_TYPES = "userDefinedObjectTypes"
    USERS = "users"
    VARIANTS = "variants"
    WIZARDS = "wizards"
    WORKFLOW_DEFINITIONS = "workflowDefinitions"
    WORKFLOWS = "workflows"
    WORKSPACES = "workspaces"

    @staticmethod
    def from_string(string: str):
        """
        Returns an ObjectType given a String.

        :param string: the string to convert to ObjectType
        """

        for ot in ObjectType:
            if ot.value == string:
                logger.debug(f"Match found for {string}: {ot}")
                return ot

        raise Exception(f"Cannot find ObjectType that matches '{string}'")


class SubItems:
    ACCOUNT_PROPERTIES = []
    ACCOUNTS = ["metadata", "properties"]
    ACTIONS = ["configuration"]
    ASSETS = ["metadata", "parentGroups", "members"]  # keyframes, annotations, members
    COLLECTIONS = ["metadata"]
    EVENT_HANDLERS = ["configuration"]
    EVENTS = []
    GROUPS = ["members"]
    JOBS = ["configuration", "history"]
    MESSAGE_TEMPLATES = ["body"]
    METADATA_DEFINITIONS = ["definition"]
    OBJECT_TYPES = []
    PROFILES = ["configuration"]
    QUOTAS = []
    RESOURCES = ["configuration"]
    ROLES = []
    TAG_COLLECTIONS = []
    TASK_DEFINITIONS = []
    TASKS = []
    TAXONOMIES = []
    TIMED_ACTIONS = ["configuration"]
    USER_DEFINED_OBJECT_TYPES = ["hierarchy", "relationships"]
    USERS = []
    VARIANTS = []
    WIZARDS = ["configuration"]
    WORKFLOW_DEFINITIONS = ["structure"]
    WORKFLOWS = ["jobs", "variables"]
    WORKSPACES = ["members"]

    @staticmethod
    def from_object_type(object_type: ObjectType):
        """
        Returns a list of sub items given an ObjectType.
        """

        return getattr(SubItems, object_type.name.split(".")[-1])


# this is what dismantles the reponses from the API
# to have a more user-friendly folder structure
# this is also re-used to assemble the object update/create
KEY_TO_FILE_MAP = {
    "asset": "asset.json",
    "assetContext": "assetContext.json",
    "body": "body.html",
    "children": "children.json",
    "configuration.instance": "configuration.json",
    "definition": "definition.json",
    "fileInformation": "fileInformation.json",
    "hierarchy": "hierarchy.json",
    "history": "history.json",
    "jobs.jobs": "jobs.json",
    "members.users": "members.json",
    "metadata.instance": "metadata.json",
    "permissions": "permissions.json",
    "properties.accountProperties": "properties.json",
    "references.objects": "references.json",
    "relationships.relationships": "relationships.json",
    "role": "role.json",
    "structure": "structure.json",
    "variables": "variables.json",
    "workflow": "workflow.json",
    "workflowInstance": "workflowInstance.json",
}

# logger
logging.basicConfig(
    level=FTBX_LOG_LEVELS.get(os.getenv("FTBX_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class Objects:

    def __init__(
        self,
        object_type: ObjectType,
        sub_items: List[str],
        config: dict[str, Any] = {},
        filters: dict[str, Any] = {},
        post_filters: List[str] = [],
        with_dependencies: bool = False,
        mode: str = "partial",
        save_results: bool = False,
    ):
        """
        Initialize an object.

        :param object_type: the object type
        :param sub_items: the list of sub items to get from the object
        :param config: the object config
        :param filters: the filters to apply
        :param post_filters: the post-filters to apply
        :param with_dependencies: whether to retrieve the object depencencies
        :param mode: partial mode with fetch only necessary sub items, full mode with fetch all sub items
        :param save_results: whether to save results locally or not
        """

        self.__dict__ = config
        self.object_type = object_type
        self.sub_items = sub_items
        self.filters = filters
        self.post_filters = post_filters
        self.with_dependencies = with_dependencies
        self.mode = mode
        self.save_results = save_results

        # handle partial retrieval
        if self.mode == "partial":
            final_sub_items = []
            if self.post_filters:
                for sub_item in self.sub_items:
                    for post_filter in self.post_filters:
                        if post_filter.startswith(sub_item):
                            final_sub_items.append(sub_item)
            self.sub_items = list(set(final_sub_items))

        # encode fql is there is
        if self.filters:
            for filter, value in self.filters.items():
                if filter == "fql":
                    # add <sort by> if not already in fql
                    # otherwise elasticsearch returns same objects multiple times
                    if not "sort" in value:
                        self.filters[filter] += " sort by id desc"
                    if not "%" in value:
                        self.filters[filter] = urllib.parse.quote(self.filters[filter])

        # check is object is is instance
        # instance: jobs, tasks, workflows, assets
        if self.object_type in [
            ObjectType.ASSETS,
            ObjectType.EVENTS,
            ObjectType.JOBS,
            ObjectType.TASKS,
            ObjectType.WORKFLOWS,
        ]:
            self.is_instance = True
        else:
            self.is_instance = False

        # logger.debug(f"Finished initializing object: {self.__dict__}")

    def to_dict(self, extra_keys_to_remove: List = []) -> dict:
        """
        Object to dict by removing ftbx-specific attributes or unecessary keys.
        """

        def remove_last_modified(d):
            if isinstance(d, dict):
                return {k: remove_last_modified(v) for k, v in d.items() if k not in ['lastModified', 'lastLoggedIn']}
            elif isinstance(d, list):
                return [remove_last_modified(item) for item in d]
            return d

        d = remove_last_modified(self.__dict__)

        if extra_keys_to_remove:
            remove_nested_keys(d, keys_to_remove=extra_keys_to_remove)

        return {
            k: v
            for k, v in d.items()
            if k
            not in [
                "lastModified",
                "lastLoggedIn",
                "object_type",
                "sub_items",
                "filters",
                "post_filters",
                "with_dependencies",
                "mode",
                "save_results",
                "is_instance",
            ]
        }

    def to_url(
        self,
        environment: Environment,
        ignore_parameters: List[str] = [],
        offset: int = 0,
    ) -> str:
        """
        Transforms objects to api request.

        :param environment: environment to get the actions from
        :param ignore_parameters: ignore given parameters (ex: limit)
        :param offset: offset to be used
        """

        url_parameters = ""
        if self.filters is not None:
            # for accountProperties, no useful filters available through API: skip everything
            if self.object_type != ObjectType.ACCOUNT_PROPERTIES:
                # -------------------------------------------------------------------------------
                for param, value in self.filters.items():
                    if param not in ignore_parameters:
                        url_parameters += f";{param}={value}"

        return f"{environment.url}/api/{self.object_type.value}{url_parameters};offset={offset}"

    def get_from(self, environment: Environment, log: bool = True, batch_size: int = 500) -> List:
        """
        Retrieve objects from an environment.

        :param environment: the environment to retrieve the objects from
        :param log: whether to show the logs in the terminal

        :return: List[Objects]
        """

        objects = []
        offset = 0

        # get total count
        total_objects = environment.session.request(
            method="GET",
            url=self.to_url(environment=environment, ignore_parameters=["limit"])
            + ";limit=1",
        )

        # determine count
        # custom for tagCollections and taxonomies since no totalCount/totalResults in response
        if self.object_type in [ObjectType.TAG_COLLECTIONS, ObjectType.TAXONOMIES]:
            count = 1
        else:
            count = min(
                self.filters.get("limit", sys.maxsize),
                total_objects.get("totalCount", sys.maxsize),
                total_objects.get("totalResults", sys.maxsize),
            )
        logger.debug(f"Found {count} remote matche(s)")

        # iterate
        if count >= 0:
            # sequentially get all items (batch_size at a time)
            for _ in tqdm(
                range(0, math.ceil(count / batch_size)),
                desc=f"Retrieving {count} {self.object_type.value[:-1]}(s) from {environment.name}",
                disable=not log,
            ):
                try:
                    # get batch of objects from API
                    objects_batch = environment.session.request(
                        method="GET",
                        url=self.to_url(
                            environment=environment,
                            offset=offset,
                            ignore_parameters=["limit"],
                        )
                        + f";limit={min(count, batch_size)}",
                    )

                    # most object types go here
                    if self.object_type.value in objects_batch:
                        objects.extend(
                            [
                                Objects(
                                    object_type=self.object_type,
                                    sub_items=self.sub_items,
                                    config=object_config,
                                    filters=self.filters,
                                    post_filters=self.post_filters,
                                    with_dependencies=self.with_dependencies,
                                    mode=self.mode,
                                    save_results=self.save_results,
                                )
                                for object_config in objects_batch[
                                    self.object_type.value
                                ]
                            ]
                        )
                    # taxonomies have different response format
                    else:
                        objects.extend(
                            [
                                Objects(
                                    object_type=self.object_type,
                                    sub_items=self.sub_items,
                                    config=object_config,
                                    filters=self.filters,
                                    post_filters=self.post_filters,
                                    with_dependencies=self.with_dependencies,
                                    mode=self.mode,
                                    save_results=self.save_results,
                                )
                                for object_config in objects_batch
                            ]
                        )

                # skip in case of error coming from API
                except AttributeError:
                    logger.warning(
                        f"API error for batch_size={batch_size} and offset={offset}, skipping..."
                    )

                # incr. offset
                offset = offset + batch_size

        # get sub_items
        if self.sub_items:
            for object in tqdm(
                objects,
                desc=f"Retrieving {self.object_type.value} {self.sub_items} from {environment.name}",
                disable=not log,
            ):
                object.get_sub_items_from(environment=environment)

        # apply post-retrieval filters
        if self.post_filters:
            objects = [
                object
                for object in tqdm(
                    objects,
                    desc=f"Applying post-filters {self.post_filters}",
                    disable=not log,
                )
                if object.meet_post_filters()
            ]

        # find dependencies if config
        if self.with_dependencies and (
            any(
                dependency_root_key in self.sub_items
                for dependency_root_key in ["configuration", "structure"]
            )
            or self.object_type == ObjectType.TASK_DEFINITIONS
        ):
            for object in tqdm(
                objects,
                desc=f"Retrieving {self.object_type.value} dependencies from {environment.name}",
                disable=not log,
            ):
                object.get_dependencies_from(environment=environment)

        # save objects locally
        if self.save_results and len(objects) > 0:
            # TODO: using objects rather than self because override issue here
            for object in tqdm(
                objects,
                desc=f"Saving {objects[0].object_type.value} to {environment.name}",
                disable=not log,
            ):
                # ------------------------------------------------------------
                object.save(environment=environment)

        return objects

    def push_to(
        self,
        environment: Environment,
        with_dependencies_from: Optional[Environment] = None,
    ):
        """
        Push object to an environment.

        :param environment: the environment to push the object to
        :param with_dependencies_from: the environment from which the dependencies must be loaded
        """

        # ------------------------- DYNAMIC IMPORTS BASED ON FLEX VERSION --------------------------

        version_x = re.sub(
            r"\b(\d{4}\.\d{1,2})\.\d{1,2}\b",
            lambda x: x.group(1) + ".x",
            environment.version,
        ).replace(".", "_")
        logger.debug(f"Version: {version_x}")

        version_module_name = f"src.schemas.{version_x}"
        logger.debug(f"Using schemas {version_module_name}")
        version_module = importlib.import_module(version_module_name)

        classes = [
            "AccountPropertyUpdate",
            "AccountUpdate",
            "ActionUpdate",
            "AssetUpdate",
            "CreateCollectionRequest",
            "EventHandlerUpdate",
            "GroupUpdate",
            "MessageTemplateUpdate",
            "MetadataDefinitionUpdate",
            "NewAccount",
            "NewAccountProperty",
            "NewAction",
            "NewAssetPlaceholder",
            "NewEvent",
            "NewEventHandler",
            "NewGroup",
            "NewJob",
            "NewMessageTemplate",
            "NewMetadataDefinition",
            "NewProfile",
            "NewQuota",
            "NewResource",
            "NewRole",
            "NewTaskDefinition",
            "NewTimedAction",
            "NewUser",
            "NewUserDefinedObjectType",
            "NewVariant",
            "NewWizard",
            "NewWorkflow",
            "NewWorkflowDefinition",
            "NewWorkspace",
            "ProfileUpdate",
            "QuotaUpdate",
            "ResourceUpdate",
            "RoleUpdate",
            "TaskDefinitionUpdate",
            "TimedActionUpdate",
            "UpdateCollection",
            "UserDefinedObjectTypeUpdate",
            "UserUpdate",
            "VariantUpdate",
            "WizardUpdate",
            "WorkflowDefinitionUpdate",
            "WorkspaceUpdate",
        ]

        globals().update({name: getattr(version_module, name) for name in classes})

        # commented objects can't be created
        OBJECT_TYPE_CREATE_MAP = {
            ObjectType.ACCOUNT_PROPERTIES: NewAccountProperty,
            ObjectType.ACCOUNTS: NewAccount,
            ObjectType.ACTIONS: NewAction,
            ObjectType.ASSETS: NewAssetPlaceholder,
            ObjectType.COLLECTIONS: CreateCollectionRequest,
            ObjectType.EVENT_HANDLERS: NewEventHandler,
            ObjectType.EVENTS: NewEvent,
            ObjectType.GROUPS: NewGroup,
            ObjectType.JOBS: NewJob,
            ObjectType.MESSAGE_TEMPLATES: NewMessageTemplate,
            ObjectType.METADATA_DEFINITIONS: NewMetadataDefinition,
            # ObjectType.OBJECT_TYPES: None,
            ObjectType.PROFILES: NewProfile,
            ObjectType.QUOTAS: NewQuota,
            ObjectType.RESOURCES: NewResource,
            ObjectType.ROLES: NewRole,
            # ObjectType.TAG_COLLECTIONS: None,
            ObjectType.TASK_DEFINITIONS: NewTaskDefinition,
            # ObjectType.TASKS: None,
            # ObjectType.TAXONOMIES: None,
            ObjectType.TIMED_ACTIONS: NewTimedAction,
            ObjectType.USER_DEFINED_OBJECT_TYPES: NewUserDefinedObjectType,
            ObjectType.USERS: NewUser,
            ObjectType.VARIANTS: NewVariant,
            ObjectType.WIZARDS: NewWizard,
            ObjectType.WORKFLOW_DEFINITIONS: NewWorkflowDefinition,
            ObjectType.WORKFLOWS: NewWorkflow,
            ObjectType.WORKSPACES: NewWorkspace,
        }

        # commented objects can't be updated
        OBJECT_TYPE_UPDATE_MAP = {
            ObjectType.ACCOUNT_PROPERTIES: AccountPropertyUpdate,
            ObjectType.ACCOUNTS: AccountUpdate,
            ObjectType.ACTIONS: ActionUpdate,
            ObjectType.ASSETS: AssetUpdate,
            ObjectType.COLLECTIONS: UpdateCollection,
            ObjectType.EVENT_HANDLERS: EventHandlerUpdate,
            # ObjectType.EVENTS: None,
            ObjectType.GROUPS: GroupUpdate,
            # ObjectType.JOBS: None,
            ObjectType.MESSAGE_TEMPLATES: MessageTemplateUpdate,
            ObjectType.METADATA_DEFINITIONS: MetadataDefinitionUpdate,
            # ObjectType.OBJECT_TYPES: None,
            ObjectType.PROFILES: ProfileUpdate,
            ObjectType.QUOTAS: QuotaUpdate,
            ObjectType.RESOURCES: ResourceUpdate,
            ObjectType.ROLES: RoleUpdate,
            # ObjectType.TAG_COLLECTIONS: None,
            ObjectType.TASK_DEFINITIONS: TaskDefinitionUpdate,
            # ObjectType.TASKS: None,
            # ObjectType.TAXONOMIES: None,
            ObjectType.TIMED_ACTIONS: TimedActionUpdate,
            ObjectType.USER_DEFINED_OBJECT_TYPES: UserDefinedObjectTypeUpdate,
            ObjectType.USERS: UserUpdate,
            ObjectType.VARIANTS: VariantUpdate,
            ObjectType.WIZARDS: WizardUpdate,
            ObjectType.WORKFLOW_DEFINITIONS: WorkflowDefinitionUpdate,
            # ObjectType.WORKFLOWS: None,
            ObjectType.WORKSPACES: WorkspaceUpdate,
        }

        # ------------------------------------------------------------------------------------------

        # push dependencies first
        if with_dependencies_from:
            self.load_and_push_dependencies(
                from_env=with_dependencies_from, to_env=environment
            )

        # try to get object from dest environment
        # for accountProperties, use post-filters since no API filters
        if self.object_type == ObjectType.ACCOUNT_PROPERTIES:
            self.post_filters.append(f"key={self.key}")
        matching_objects = self.get_from(environment=environment, log=False)
        
        if len(matching_objects) > 1:
            logger.error(
                f"Multiple objects detected in {environment.name} for filters {self.filters}. Exiting..."
            )
            sys.exit(1)

        object_exists = bool(len(matching_objects))
        matching_object = matching_objects[0] if object_exists else None

        # backup if match
        if matching_object:
            matching_object.save(environment=environment, backup=True)

        # if it doesn't exist + is not instance, create it
        if not object_exists and not self.is_instance:

            # create if creatable
            if self.object_type in OBJECT_TYPE_CREATE_MAP:
                # this build the object create payload
                args = {}
                for key in OBJECT_TYPE_CREATE_MAP.get(self.object_type).keys:
                    if key in self.__dict__.keys():
                        # for account/visibility, get default from dest env
                        # as the one in the loaded object will be incorrect
                        if key == "account":
                            args[key] = {"id": environment.get_default_account_id()}
                        elif key == "visibility":
                            args[key] = [{"id": environment.get_default_account_id()}]
                        # action type is string so need to fetch it
                        elif key == "type" and self.object_type == ObjectType.ACTIONS:
                            args[key] = self.__dict__.get("type").get("name")
                        else:
                            args[key] = self.__dict__.get(key)
                    else:
                        args[key] = None

                # create
                object_create = OBJECT_TYPE_CREATE_MAP.get(self.object_type)(**args)
                environment.session.request(
                    method="POST",
                    url=f"{environment.url}/api/{self.object_type.value}",
                    data=object_create.__dict__,
                )
                matching_object = self.get_from(environment=environment)[0]

            else:
                logger.warning(
                    f"{self.object_type.value} cannot be created through the API"
                )

        # update if exists
        elif object_exists and not self.is_instance:

            # update if updatable
            if self.object_type in OBJECT_TYPE_UPDATE_MAP:

                # this build the object update payload
                args = {}
                for key in OBJECT_TYPE_UPDATE_MAP.get(self.object_type).keys:
                    if key in self.__dict__.keys():
                        # when an object is enabled, it is impossible to update its account/visibility
                        # so we just fill them with empty values
                        if (
                            key in ["account", "visibility"]
                            and "enabled" in matching_object.__dict__
                            and matching_object.enabled
                        ):
                            args[key] = {}
                        else:
                            args[key] = self.__dict__.get(key)
                    # for empty values, we fill with None
                    else:
                        args[key] = None

                # update
                try:
                    object_update = OBJECT_TYPE_UPDATE_MAP.get(self.object_type)(**args)
                    environment.session.request(
                        method="PUT",
                        url=f"{environment.url}/api/{self.object_type.value}/{self.id}",
                        data=object_update.__dict__,
                    )
                except AttributeError:
                    logger.warning(
                        f"Failed to update definition of {self.object_type.value} with id {self.id}. This failure is not vital as it only targets the {self.object_type.value} definition tab (i.e. visibility, concurrency etc)"
                    )

        if not matching_object and "id" in matching_object.__dict__:
            logger.error(
                "Cannot proceed further are there is no matching object in the destination environment. "
            )
            sys.exit(1)

        # update subItems
        # for resources:
        # - if RESOURCE ALREADY EXISTS, DONT update configuration (risk of data loss)
        # - if RESOURCE WAS JUST CREATED, DO update configuration
        if not (self.object_type == ObjectType.RESOURCES and object_exists):
            logger.debug(f"Sub items are: {self.sub_items}")
            for sub_item in self.sub_items:
                # x or x.instance
                if sub_item in ["configuration", "metadata", "structure", "definition"]:
                    # for workflowDefinitions structure, remove 'action' and 'description' from transitions
                    # since they're not ignored anymore in latest flex versions...
                    if sub_item == "structure":
                        for idx, transition in enumerate(
                            self.structure.get("transitions")
                        ):
                            for k, v in transition.items():
                                if isinstance(v, dict) and "action" in v:
                                    del self.structure["transitions"][idx][k]["action"]
                                if isinstance(v, dict) and "description" in v:
                                    del self.structure["transitions"][idx][k]["description"]
                    # ----------------------------------------------------------------------

                    # only push if sub item exists (ex: wizard configuration can be missing if task)
                    if self.__dict__.get(sub_item):
                        # pass if instance is empty (mostly for templates)
                        if sub_item in ["configuration", "metadata"] and not self.__dict__.get(sub_item).get('instance'):
                            continue

                        environment.session.request(
                            method="PUT",
                            url=f"{environment.url}/api/{self.object_type.value}/{matching_object.id}/{sub_item}",
                            data=(
                                self.__dict__.get(sub_item).get("instance")
                                if sub_item in ["configuration", "metadata"]
                                else self.__dict__.get(sub_item)
                            ),
                        )
                else:
                    logger.debug(
                        f"'{sub_item}' sub item is not pushable through the api"
                    )

        # update task status
        if self.object_type == ObjectType.TASKS:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{matching_object.id}/status",
                data={"status": self.status},
            )

        # try to enable object if not already enabled
        if "enabled" in matching_object.__dict__ and not matching_object.enabled:
            matching_object.enable(environment=environment)

        # try to start resource if not already started
        if (
            matching_object.object_type == ObjectType.RESOURCES
            and matching_object.status != "Started"
        ):
            matching_object.start(environment=environment)

        self.save_results = True
        self.get_from(environment=environment, log=False)

        return matching_object

    def get_sub_items_from(self, environment: Environment):
        """
        Get sub items from an environment.

        :param environment: the environment to get sub items from
        """

        for sub_item in self.sub_items:
            # this prevents the toolbox from retrieving sub items when you use
            # includeMetadata=true for example (huge execution time difference)
            if sub_item not in self.__dict__:
                # ------------------------------------------------------
                try:  # try bcz some metadata are sometimes empty :)
                    if sub_item != "body":
                        self.__dict__[sub_item] = environment.session.request(
                            method="GET",
                            url=f"{environment.url}/api/{self.object_type.value}/{str(self.__dict__['id'] if self.object_type.value != 'collections' else str(self.__dict__['uuid']))}/{sub_item}",
                        )
                    else:
                        self.__dict__[sub_item] = (
                            environment.session.request(
                                "GET",
                                f"{environment.url}/api/{self.object_type.value}/{str(self.__dict__['id'] if self.object_type.value != 'collections' else str(self.__dict__['uuid']))}/{sub_item}",
                            )
                            .content.decode("utf-8", "ignore")
                            .strip()
                        )

                    # date sorting
                    match sub_item:
                        case "jobs":
                            self.__dict__[sub_item]["jobs"] = sorted(
                                self.__dict__[sub_item]["jobs"],
                                key=lambda x: x["start"],
                            )
                        case "history":
                            self.__dict__[sub_item]["events"] = self.__dict__[sub_item][
                                "events"
                            ]
                        case _:
                            pass
                # in case we want to interrupt the command
                except KeyboardInterrupt as ki:
                    raise Exception(ki)
                except:
                    pass

    def get_dependencies_from(self, environment: Environment) -> None:
        """
        Get object dependencies from an environment.

        :param environment: the environment to get the dependencies from
        """

        # workflow defs
        if self.object_type == ObjectType.WORKFLOW_DEFINITIONS and self.__dict__.get(
            "structure"
        ):
            object_config = self.__dict__.get("structure").copy()
        # task defs
        elif self.object_type == ObjectType.TASK_DEFINITIONS:
            object_config = {"wizard": self.__dict__.get("wizard")}
        # else
        elif self.__dict__.get("configuration"):
            object_config = self.__dict__.get("configuration").get("instance").copy()
        else:
            return None

        dependencies = find_nested_dependencies(data=object_config)
        for dependency in dependencies:
            # clone config
            tmp = object_config.copy()
            for subpath in dependency.split("."):
                # index of list
                if subpath.isdigit():
                    tmp = tmp[int(subpath)]
                else:
                    tmp = tmp.get(subpath).copy()

            # get dependency object type
            if "actionType" in tmp:  # actions in workflowDefinitions
                dep_object_type = ObjectType.from_string(string="actions")
            elif "objectType" in tmp:  # tasks in workflowDefinitions
                dep_object_type = ObjectType.from_string(
                    kebab_to_camel_case(tmp.get("objectType").get("name"))
                )
            else:
                dep_object_type = ObjectType.from_string(
                    kebab_to_camel_case(tmp.get("type"))
                )

            # pull dependency
            Objects(
                object_type=dep_object_type,
                sub_items=SubItems.from_object_type(object_type=dep_object_type),
                filters={
                    "name": tmp.get("name"),
                    "exactNameMatch": True,
                },
                with_dependencies=True,
                mode="full",
                save_results=True,
            ).get_from(environment=environment, log=False)

        return None

    def load_and_push_dependencies(
        self, from_env: Environment, to_env: Environment
    ) -> None:
        """
        Push local object dependencies to an environment.

        :param from_env: the environment to load the dependencies from
        :param to_env: the environment to push the dependencies to
        """

        # workflow defs
        if self.object_type == ObjectType.WORKFLOW_DEFINITIONS and self.__dict__.get(
            "structure"
        ):
            object_config = self.__dict__.get("structure")
        # task defs
        elif self.object_type == ObjectType.TASK_DEFINITIONS:
            object_config = {"wizard": self.__dict__.get("wizard")}
        # else
        elif self.__dict__.get("configuration"):
            object_config = self.__dict__.get("configuration").get("instance")
        else:
            return None

        dependencies = find_nested_dependencies(data=object_config)
        logger.debug(f"Dependencies found: {dependencies}")

        for dependency in dependencies:
            # clone config
            tmp = object_config.copy()
            for subpath in dependency.split("."):
                # index of list
                if subpath.isdigit():
                    tmp = tmp[int(subpath)]
                else:
                    tmp = tmp.get(subpath).copy()

            # get dependency object type
            if "actionType" in tmp:  # actions in workflowDefinitions
                dep_object_type = ObjectType.from_string(string="actions")
            elif "objectType" in tmp:  # tasks in workflowDefinitions
                dep_object_type = ObjectType.from_string(
                    kebab_to_camel_case(tmp.get("objectType").get("name"))
                )
            else:
                dep_object_type = ObjectType.from_string(
                    kebab_to_camel_case(tmp.get("type"))
                )

            # load and push dependency
            dep = Objects(
                object_type=dep_object_type,
                sub_items=SubItems.from_object_type(object_type=dep_object_type),
                filters={
                    "name": tmp.get("name"),
                    "exactNameMatch": True,
                },
                with_dependencies=True,
                mode="full",
            ).load_from(environment=from_env)[0]
            pushed_dep = dep.push_to(
                environment=to_env, with_dependencies_from=from_env
            )

            # update self with pushed_dep
            tmp = object_config
            for subpath in dependency.split("."):
                # index of list
                if subpath.isdigit():
                    tmp = tmp[int(subpath)]
                else:
                    tmp = tmp.get(subpath)

            tmp["id"] = pushed_dep.id
            tmp["uuid"] = pushed_dep.uuid

            # for taskDef, enable wizard, update wizardId and assignment
            if self.object_type == ObjectType.TASK_DEFINITIONS:
                pushed_dep.enable(environment=to_env)

                # not needed?
                # self.wizardId = pushed_dep.id
                self.assignment = [to_env.get_default_account_id()]

        return None

    def load_from(
        self, environment: Environment, backup_name: Union[str, None] = None
    ) -> List:
        """
        Load objects from local.
        :param environment: the environment/folder name to load the objects from

        :return: List[Objects]
        """

        objects = []

        # check folder exists
        assert self.object_type.value in os.listdir(path=environment.name)

        # get object dirs
        path_to_objects = os.path.join(environment.name, self.object_type.value)
        object_dirs = os.listdir(path=path_to_objects)

        for object_dir in object_dirs:
            # only load valid objects
            # for backup, change path
            if backup_name:
                object_path = os.path.join(
                    path_to_objects, object_dir, "backup", backup_name
                )
            else:
                object_path = os.path.join(path_to_objects, object_dir)

            is_valid_object = os.path.isfile(
                path=os.path.join(object_path, "_object.json")
            )
            # id to string for instances
            if is_valid_object and object_dir in [
                self.filters.get("name"),
                str(self.filters.get("id")),
            ]:

                logger.debug(f"Loading {object_path}...")
                # load _object.json
                object_config = json.load(
                    open(os.path.join(object_path, "_object.json"))
                )

                # iterate over all objects files
                for object_file in os.listdir(path=object_path):

                    logger.debug(f"Loading {object_path}/{object_file}...")
                    # script.groovy
                    if object_file == "script.groovy":
                        merge_script_in_object_config(
                            script_path=os.path.join(object_path, "script.groovy"),
                            object_config=object_config,
                        )
                    # body.html
                    elif object_file == "body.html":
                        with open(
                            os.path.join(object_path, object_file), "r"
                        ) as html_file:
                            body = html_file.readlines()
                            object_config["body"] = body
                    # any.json
                    elif (
                        ".json" in object_file
                        and object_file != "_object.json"
                        and object_file in [v for v in KEY_TO_FILE_MAP.values()]
                    ):
                        with open(
                            os.path.join(object_path, object_file), "r"
                        ) as json_file:
                            json_config = json.load(json_file)

                            # find json struct in KEY_TO_FILE_MAP
                            key = next(
                                k
                                for k, v in KEY_TO_FILE_MAP.items()
                                if v == object_file
                            )
                            key_parts = key.split(".")

                            # merge in object config
                            if len(key_parts) == 1:
                                object_config[key_parts[0]] = json_config
                            elif len(key_parts) == 2:
                                object_config[key_parts[0]] = {}
                                object_config[key_parts[0]][key_parts[1]] = json_config
                            else:
                                raise Exception(
                                    f"Cannot parse {object_file} because value has more than 2 parts in KEY_TO_FILE_MAP. "
                                )
                    # other files are irrelevant
                    else:
                        pass

                # create and append object
                objects.append(
                    Objects(
                        object_type=self.object_type,
                        sub_items=SubItems.from_object_type(self.object_type),
                        config=object_config,
                        filters=self.filters,
                        post_filters=[],
                        mode="full",
                    )
                )

        return objects

    def meet_post_filters(self) -> bool:
        """
        Whether object corresponds to post filters or not.

        :return: True if object corresponds to filter, False otherwise
        """

        results = []

        # post-filters processing
        for post_filter in self.post_filters:
            # operator
            operator = None
            for op in ["!~", "!=", ">=", "<=", "~", "=", "<", ">"]:
                if op in post_filter:
                    operator = op
                    break

            if not operator:
                logger.warning(f"Couldn't find operator for [{post_filter}], skipping...")
            else:
                key, value = post_filter.split(operator)
                # string to None type
                value = None if value == "None" else value

                # get nested value
                object_value = get_nested_value(self.__dict__, key)

                if isinstance(object_value, bool):
                    value = str_to_bool(str(value))
                elif isinstance(object_value, int):
                    value = int(value if value else 0)
                # todo: handle dates
                # elif isinstance(item_value, str):
                #     try:
                #         value: datetime = datetime.datetime.strptime(value, '%d %b %Y %H:%M:%S %z')
                #         print(value, type(value))
                #         item_value: datetime = datetime.datetime.strptime(item_value, '%d %b %Y %H:%M:%S %z')
                #         print(item_value, type(item_value))
                #     except:
                #         pass

                # switch
                if operator == "=":
                    results.append(True if object_value == value else False)
                elif operator == "!=":
                    results.append(True if object_value != value else False)
                elif operator == ">=":
                    results.append(True if object_value >= value else False)
                elif operator == "<=":
                    results.append(True if object_value <= value else False)
                elif operator == "<":
                    results.append(True if object_value < value else False)
                elif operator == ">":
                    results.append(True if object_value > value else False)
                elif operator == "!~":
                    if isinstance(object_value, str) and value not in object_value:
                        results.append(True)
                    else:
                        results.append(False)
                elif operator == "~":
                    if isinstance(object_value, str) and value in object_value:
                        results.append(True)
                    else:
                        results.append(False)
                else:
                    results.append(False)

        return True if all(r == True for r in results) else False

    def save(self, environment: Environment, backup: bool = False) -> None:
        """
        Save object locally.
        """

        # parent folder
        create_folder(folder_name=environment.name, ignore_error=True)
        create_folder(
            folder_name=os.path.join(environment.name, self.object_type.value),
            ignore_error=True,
        )
        now = datetime.datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss")

        # folder's name
        # events or instances, i.e. jobs, tasks, workflows and assets
        if self.object_type == ObjectType.EVENTS or self.is_instance:
            folder_name = f"{self.__dict__.get('id')}".replace("/", "").replace(":", "")
        elif self.object_type == ObjectType.ACCOUNT_PROPERTIES:
            folder_name = f"{self.__dict__.get('key')}".replace("/", "").replace(
                ":", ""
            )
        else:
            folder_name = f"{self.__dict__.get('name')}".replace("/", "").replace(
                ":", ""
            )

        # create object and backup folders
        create_folder(
            folder_name=os.path.join(
                environment.name, self.object_type.value, folder_name
            ),
            ignore_error=True,
        )
        create_folder(
            folder_name=os.path.join(
                environment.name, self.object_type.value, folder_name, "backup"
            ),
            ignore_error=True,
        )

        # if we are in backup mode, update folder_name
        if backup:
            create_folder(
                folder_name=os.path.join(
                    environment.name, self.object_type.value, folder_name, "backup", now
                ),
                ignore_error=True,
            )
            folder_name = os.path.join(folder_name, "backup", now)

        logger.debug(f"Folder name is {folder_name}")

        # handle configuration
        configuration = get_nested_value(
            obj=self.__dict__, keys="configuration.instance"
        )
        if configuration is not None:

            # groovy script
            groovy_script = get_nested_value(
                obj=self.__dict__, keys="configuration.instance.script-contents"
            )

            # groovy decision
            groovy_decision = get_nested_value(
                obj=self.__dict__, keys="configuration.instance.script_type"
            )

            # jef
            jef_script = get_nested_value(
                obj=self.__dict__,
                keys="configuration.instance.internal-script.script-content",
            )

            # handle script
            if any([groovy_decision, groovy_script, jef_script]):
                create_script(
                    object_name=os.path.join(
                        environment.name, self.object_type.value, folder_name
                    ),
                    object_config=self.__dict__,
                )

            # no script
            else:
                self.save_keys_as_files(
                    environment=environment,
                    folder_name=folder_name,
                    key_filename_map={
                        k: v
                        for k, v in KEY_TO_FILE_MAP.items()
                        if v == "configuration.json"
                    },
                )

        # save useful info as indepent files
        self.save_keys_as_files(
            environment=environment,
            folder_name=folder_name,
            key_filename_map={
                k: v for k, v in KEY_TO_FILE_MAP.items() if v != "configuration.json"
            },
        )

        # handle workflow graph rendering
        structure = get_nested_value(obj=self.__dict__, keys="structure")
        if structure is not None:
            render_workflow(
                workflow_structure=structure,
                save_to=os.path.join(
                    environment.name, self.object_type.value, folder_name
                ),
            )

        # prevent commit loop
        for key in ["lastPollTime", "revision"]:
            if key in self.__dict__:
                self.__dict__.pop(key)

        # save main object
        with open(
            os.path.join(
                environment.name, self.object_type.value, folder_name, "_object.json"
            ),
            "w",
        ) as item_config:
            # we remove keys things that are unecessary and cause flooding in bitbucket
            extra_keys_to_remove = [
                "configuration.id",
                "configuration.instance.internal-script.script-content",
                "configuration.instance.internal-script.script-import",
                "configuration.instance.script-contents",
                "configuration.instance.script",
                "configuration.instance.imports",
                "configuration.instance.script_type.script",
            ]
            # -------------------------------------------------------------------------
            json.dump(obj=self.to_dict(extra_keys_to_remove=extra_keys_to_remove), fp=item_config, indent=2)
            logger.debug(f"Saving object to {item_config}")

    def save_keys_as_files(
        self, environment: Environment, folder_name: str, key_filename_map: dict
    ) -> None:
        """
        Save object keys as files.

        :param key_filename_map: dict containing keys and filename

        :return: None
        """

        # iterate over all keys and create files
        for key, filename in key_filename_map.items():
            value = get_nested_value(obj=self.to_dict(), keys=key)
            if value is not None:
                with open(
                    os.path.join(
                        environment.name, self.object_type.value, folder_name, filename
                    ),
                    "w",
                ) as object_config:
                    # for roles, sort permissions by id to prevent commit loop
                    if filename == "permissions.json":
                        json.dump(obj=sorted(value, key=lambda x: x['id']), fp=object_config, indent=2)
                        del self.__dict__[key]
                    else:
                        json.dump(obj=value, fp=object_config, indent=2)

    def enable(self, environment: Environment) -> bool:
        """
        Enable the object in a given environment.

        :param environment: the env in which to enable the object
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "enable"},
            )
            return True
        except:
            logger.warning(
                f"Failed to enable {self.object_type.value} with id {self.id} (current value: [Enabled={self.enabled if 'enabled' in self.__dict__ else None}]). "
            )
            return False

    def disable(self, environment: Environment) -> bool:
        """
        Disable the object in a given environment.

        :param environment: the env in which to disable the object
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "disable"},
            )
            return True
        except:
            logger.warning(
                f"Failed to disable {self.object_type.value} with id {self.id}. "
            )
            return False

    def delete(self, environment: Environment) -> bool:
        """
        Disable the object in a given environment.

        :param environment: the env in which to disable the object
        """

        try:
            environment.session.request(
                method="DELETE",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}",
            )
            return True
        except:
            logger.warning(
                f"Failed to delete {self.object_type.value} with id {self.id}. "
            )
            return False

    def start(self, environment: Environment) -> bool:
        """
        Start a resource in a given environment.

        :param environment: the env in which to start the resource
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "start"},
            )
            return True
        except:
            logger.warning(
                f"Failed to start {self.object_type.value} with id {self.id} (current value: [Status={self.status if 'status' in self.__dict__ else None}]"
            )
            return False

    def stop(self, environment: Environment) -> bool:
        """
        Stop a resource in a given environment.

        :param environment: the env in which to stop the resource
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "stop"},
            )
            return True
        except:
            logger.warning(
                f"Failed to stop {self.object_type.value} with id {self.id} (current value: [Status={self.status if 'status' in self.__dict__ else None}]"
            )
            return False

    def retry(self, environment: Environment) -> bool:
        """
        Retry an instance in a given environment.

        :param environment: the env in which to retry the instance
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "retry"},
            )
            return True
        except:
            logger.warning(
                f"Failed to retry {self.object_type.value} with id {self.id}. "
            )
            return False

    def cancel(self, environment: Environment) -> bool:
        """
        Retry an instance in a given environment.

        :param environment: the env in which to retry the instance
        """

        try:
            environment.session.request(
                method="POST",
                url=f"{environment.url}/api/{self.object_type.value}/{self.id}/actions",
                data={"action": "cancel"},
            )
            return True
        except:
            logger.warning(
                f"Failed to cancel {self.object_type.value} with id {self.id}. "
            )
            return False

    def listen(self, environment: Environment) -> str:
        """
        Listen to an instance in a given environment.

        :param environment: the env in which to listen the object instance
        """

        logger.info(f"Now listening to [{self.name}] with ID {self.id}")

        job_status = None
        job_logs: List[dict] = []

        # job request
        job_request = Objects(
            object_type=ObjectType.JOBS,
            sub_items=SubItems.JOBS,
            filters={"name": self.name, "id": self.id, "exactNameMatch": True},
            mode="full",
        )

        while job_status != "Completed" and job_status != "Failed":

            # get job
            jobs = job_request.get_from(environment=environment, log=False)
            job = next(iter(jobs))
            job_status = job.status

            # wait for job to start before fetching
            if job_status in ['Pending', 'Queued']:
                sleep(1)
                continue
            # -------------------------------------

            # find new logs
            new_logs = [log for log in job.history.get("events") if log not in job_logs]
            job_logs += new_logs

            # display
            x = 1 if job_logs[0].get("eventType") in ["Pending", "Created"] else -1
            for job_log in new_logs[::x]:
                if job_log.get("time") >= job.__dict__.get('start'):
                    t = job_log.get("time")
                    message = job_log.get("message").split("\n")[0]
                    severity = job_log.get("severity").upper()
                    color = ""

                    if severity == "WARNING":
                        color = "yellow"
                    elif severity == "ERROR":
                        color = "red"

                    print(t, colored_text(text=severity, color=color), message)

            sleep(1)

        job_request.save_results = True
        job_request.get_from(environment=environment, log=False)

        return job_status


def get_object_type_log_fields(object_type: ObjectType):
    """
    Returns a list of ObjectType keys to log.
    """

    match object_type:
        case ObjectType.ACCOUNT_PROPERTIES:
            return ["key", "id", "account.name", "value"]
        case ObjectType.ACTIONS:
            return ["name", "id", "type.name"]
        case ObjectType.ASSETS:
            return ["name", "id", "variant.name", "variant.id"]
        case ObjectType.COLLECTIONS:
            return ["name", "uuid"]
        case ObjectType.EVENT_HANDLERS:
            return [
                "name",
                "id",
                "configuration.instance.action-config.name",
                "configuration.instance.action-config.id",
            ]
        case ObjectType.EVENTS:
            return ["time", "id", "eventType", "message"]
        case ObjectType.GROUPS:
            return ["name", "id", "role.name", "role.id"]
        case ObjectType.JOBS:
            return [
                "name",
                "id",
                "status",
                "progress",
                "actionType.name",
                "asset.id",
                "workflow.id",
            ]
        case ObjectType.RESOURCES:
            return ["name", "id", "resourceType", "resourceSubType", "status"]
        case ObjectType.TASKS:
            return ["name", "id", "status", "asset.name", "asset.id"]
        case ObjectType.TIMED_ACTIONS:
            return ["name", "id", "status", "interval"]
        case ObjectType.USERS:
            return ["displayName", "id", "userType", "email", "lastLoggedIn"]
        case ObjectType.VARIANTS:
            return [
                "name",
                "id",
                "defaultMetadataDefinition.displayName",
                "defaultMetadataDefinition.id",
            ]
        case ObjectType.WORKFLOWS:
            return ["name", "id", "status", "asset.name", "asset.id"]
        case _:
            return ["name", "id"]
