# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0
import logging
from collections.abc import MutableMapping
from typing import Any, Dict, Optional
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langgraph.utils.runnable import RunnableCallable

from agntcy_acp import (
    ACPClient,
    ApiClient,
    AsyncACPClient,
    AsyncApiClient,
    ApiClientConfiguration,
)
from agntcy_acp.models import (
    Config,
    RunCreateStateless, 
    RunResult, 
    RunOutput, 
    RunError, 
    RunInterrupt,
)
from agntcy_acp.exceptions import ACPRunException

logger = logging.getLogger(__name__)


def _extract_element(container: Any, path: str) -> Any:
    element = container
    for path_el in path.split("."):
        element = (
            element.get(path_el)
            if isinstance(element, MutableMapping)
            else getattr(element, path_el)
        )

    if element is None:
        raise Exception(f"Unable to extract {path} from state {container}")

    return element


class ACPNode:
    """This class represents a Langgraph Node that holds a remote connection to an ACP Agent
    It can be instantiated and added to any langgraph graph.

    my_node = ACPNode(...)
    sg = StateGraph(GraphState)
    sg.add_node(my_node)
    """

    def __init__(
        self,
        name: str,
        agent_id: str,
        client_config: ApiClientConfiguration,
        input_path: str,
        input_type,
        output_path: str,
        output_type,
        config_path: Optional[str] = None,
        config_type=None,
        auth_header: Optional[Dict] = None,
    ):
        """Instantiate a Langgraph node encapsulating a remote ACP agent

        :param name: Name of the langgraph node
        :param agent_id: Agent ID in the remote server
        :param client_config: Configuration of the ACP Client
        :param input_path: Dot-separated path of the ACP Agent input in the graph overall state
        :param input_type: Pydantic class defining the schema of the ACP Agent input
        :param output_path: Dot-separated path of the ACP Agent output in the graph overall state
        :param output_type: Pydantic class defining the schema of the ACP Agent output
        :param config_path: Dot-separated path of the ACP Agent config in the graph configurable
        :param config_type: Pydantic class defining the schema of the ACP Agent config
        :param auth_header: A dictionary containing auth details necessary to communicate with the node
        """

        self.__name__ = name
        self.agent_id = agent_id
        self.clientConfig = client_config
        self.inputPath = input_path
        self.inputType = input_type
        self.outputPath = output_path
        self.outputType = output_type
        self.configPath = config_path
        self.configType = config_type
        self.auth_header = auth_header

    def get_name(self):
        return self.__name__

    def _extract_input(self, state: Any) -> Any:
        if not state:
            return state
        
        try:
            if self.inputPath:
                state = _extract_element(state, self.inputPath)
        except Exception as e:
            raise Exception(
                f"ERROR in ACP Node {self.get_name()}. Unable to extract input: {e}"
            )

        if isinstance(state, BaseModel):
            return state.model_dump()
        elif isinstance(state, MutableMapping):
            return state
        else:
            return {}

    def _extract_config(self, config: Any) -> Any:
        if not config:
            return config
        
        try:
            if not self.configPath:
                config = {}
            else:
                if "configurable" not in config:
                    logger.error(f"ACP Node {self.get_name()}. Unable to extract config: missing key \"configurable\" in RunnableConfig")
                    return None

                config = _extract_element(config["configurable"], self.configPath)
        except Exception as e:
            logger.info(f"ACP Node {self.get_name()}. Unable to extract config: {e}")
            return None

        if self.configType is not None:
            # Set defaults, etc.
            agent_config = self.configType.model_validate(config)
        else:
            agent_config = config

        if isinstance(agent_config, BaseModel):
            return agent_config.model_dump()
        elif isinstance(agent_config, MutableMapping):
            return agent_config
        else:
            return {}

    def _set_output(self, state: Any, output: Optional[Dict[str, Any]]):
        output_parent = state
        output_state = self.outputType.model_validate(output)

        for el in self.outputPath.split(".")[:-1]:
            if isinstance(output_parent, MutableMapping):
                output_parent = output_parent[el]
            elif hasattr(output_parent, el):
                output_parent = getattr(output_parent, el)
            else:
                raise ValueError("object missing attribute: {el}")
        
        el = self.outputPath.split(".")[-1]
        if isinstance(output_parent, MutableMapping):
            output_parent[el] = output_state
        elif hasattr(output_parent, el):
            setattr(output_parent, el, output_state)
        else:
            raise ValueError("object missing attribute: {el}")
    
    def _prepare_run_create(self, state: Any, config: RunnableConfig) -> RunCreateStateless:
        agent_input = self._extract_input(state)
        if isinstance(agent_input, BaseModel):
            input_to_agent = agent_input.model_dump()
        elif isinstance(agent_input, MutableMapping):
            input_to_agent = agent_input
        else:
            input_to_agent = {}

        agent_config = self._extract_config(config)
        if isinstance(agent_config, BaseModel):
            config_to_agent = agent_config.model_dump()
        elif isinstance(agent_config, MutableMapping):
            config_to_agent = agent_config
        else:
            config_to_agent = {}

        return RunCreateStateless(
            agent_id=self.agent_id,
            input=input_to_agent,
            config=Config(configurable=config_to_agent),
        )
    
    def _handle_run_output(self, state: Any, run_output: RunOutput):
        if isinstance(run_output.actual_instance, RunResult):
            run_result: RunResult = run_output.actual_instance
            self._set_output(state, run_result.values)
        elif isinstance(run_output.actual_instance, RunError):
            run_error: RunError = run_output.actual_instance
            raise ACPRunException(f"Run Failed: {run_error}")
        elif isinstance(run_output.actual_instance, RunInterrupt):
            raise ACPRunException(f"ACP Server returned a unsupporteed interrupt response: {run_output}")
        else:
            raise ACPRunException(f"ACP Server returned a unsupporteed response: {run_output}")

        return state

    def invoke(self, state: Any, config: RunnableConfig) -> Any:
        run_create = self._prepare_run_create(state, config)
        with ACPClient(configuration=self.clientConfig) as acp_client:
            run_output = acp_client.create_and_wait_for_stateless_run_output(run_create)
        
        # output is the same between stateful and stateless
        self._handle_run_output(state, run_output.output)
        return state

    async def ainvoke(self, state: Any, config: RunnableConfig) -> Any:
        run_create = self._prepare_run_create(state, config)
        async with AsyncACPClient(configuration=self.clientConfig) as acp_client:
            run_output = await acp_client.create_and_wait_for_stateless_run_output(run_create)
        
        self._handle_run_output(state, run_output.output)
        return state

    def __call__(self, state, config):
        return RunnableCallable(self.invoke, self.ainvoke)
