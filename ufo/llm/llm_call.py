# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from typing import Any, Dict, List, Tuple

from ufo.utils import print_with_color

from ..config.config import Config
from .base import BaseService
from .openai_utils import send_request_ufo,send_request_ufo_cost
import time

configs = Config.get_instance().config_data


def get_completion(
        messages, agent: str = "APP", use_backup_engine: bool = True, configs=configs
) -> Tuple[str, float]:
    """
    Get completion for the given messages.
    :param messages: List of messages to be used for completion.
    :param agent: Type of agent. Possible values are 'hostagent', 'appagent' or 'backup'.
    :param use_backup_engine: Flag indicating whether to use the backup engine or not.
    :return: A tuple containing the completion response and the cost.
    """

    # responses, cost = get_completions(
    #     messages, agent=agent, use_backup_engine=use_backup_engine, n=1, configs=configs
    # )
    # # print(messages)
    # return responses[0], cost
    responses = ""
    try_count = 20
    while try_count > 0:
        try:
            # 'dev-gpt-4o-vision-2024-05-13'
            model_name = 'dev-gpt-41-longco-2025-04-14'
            responses = send_request_ufo(
                model_name, messages
            )

            return responses, 0
        except Exception as e:
            print_with_color(f"Error: {e}", "red")
            print_with_color("Retrying...", "yellow")
            try_count -= 1
            time.sleep(8)
            continue


    return responses, 0


def get_completion_schema(
        messages, schema,agent: str = "APP", use_backup_engine: bool = True, configs=configs
) -> Tuple[str, float]:
    """
    Get completion for the given messages.
    :param messages: List of messages to be used for completion.
    :param agent: Type of agent. Possible values are 'hostagent', 'appagent' or 'backup'.
    :param use_backup_engine: Flag indicating whether to use the backup engine or not.
    :return: A tuple containing the completion response and the cost.
    """

    # responses, cost = get_completions(
    #     messages, agent=agent, use_backup_engine=use_backup_engine, n=1, configs=configs
    # )
    # # print(messages)
    # return responses[0], cost
    responses = ""
    try_count = 20
    while try_count > 0:
        try:
            # 'dev-gpt-4o-vision-2024-05-13'
            model_name = 'dev-gpt-41-longco-2025-04-14'
            responses = send_request_ufo(
                model_name, messages,schema
            )
            return responses, 0
        except Exception as e:
            print_with_color(f"Error: {e}", "red")
            print_with_color("Retrying...", "yellow")
            try_count -= 1
            time.sleep(8)
            continue
    return responses, 0

def get_completion_schema_cost(
        messages, schema,agent: str = "APP", use_backup_engine: bool = True, configs=configs
) -> Tuple[str, float]:
    """
    Get completion for the given messages.
    :param messages: List of messages to be used for completion.
    :param agent: Type of agent. Possible values are 'hostagent', 'appagent' or 'backup'.
    :param use_backup_engine: Flag indicating whether to use the backup engine or not.
    :return: A tuple containing the completion response and the cost.
    """


    responses = ""
    try_count = 20
    while try_count > 0:
        try:
            # 'dev-gpt-4o-vision-2024-05-13'
            model_name = 'dev-gpt-41-longco-2025-04-14'
            result,prompt_tokens,completion_tokens,cost,time_taken_seconds = send_request_ufo_cost(
                model_name, messages,schema
            )
            return result,prompt_tokens,completion_tokens,cost,time_taken_seconds
        except Exception as e:
            print_with_color(f"Error: {e}", "red")
            print_with_color("Retrying...", "yellow")
            try_count -= 1
            time.sleep(8)
            continue
    return responses, 0

def get_completions(
    messages,
    agent: str = "APP",
    use_backup_engine: bool = True,
    n: int = 1,
    configs=configs,
) -> Tuple[list, float]:
    """
    Get completions for the given messages.
    :param messages: List of messages to be used for completion.
    :param agent: Type of agent. Possible values are 'hostagent', 'appagent' or 'backup'.
    :param use_backup_engine: Flag indicating whether to use the backup engine or not.
    :param n: Number of completions to generate.
    :return: A tuple containing the completion responses and the cost.
    """

    if agent.lower() in ["host", "hostagent"]:
        agent_type = "HOST_AGENT"
    elif agent.lower() in ["app", "appagent"]:
        agent_type = "APP_AGENT"
    elif agent.lower() in ["openaioperator", "openai_operator", "operator"]:
        agent_type = "OPERATOR"
    elif agent.lower() == "prefill":
        agent_type = "PREFILL_AGENT"
    elif agent.lower() == "filter":
        agent_type = "FILTER_AGENT"
    elif agent.lower() == "backup":
        agent_type = "BACKUP_AGENT"
    else:
        raise ValueError(f"Agent {agent} not supported")

    api_type = configs[agent_type]["API_TYPE"]
    try:
        api_type_lower = api_type.lower()
        service = BaseService.get_service(
            api_type_lower, configs[agent_type]["API_MODEL"].lower()
        )
        if service:
            print(len(messages))
            for message in messages:
                # for  m in message:
                #     print(m)
                #     print("---------------------------------------------------")
                # print(message)
                print(message.keys())
                for key, value in message.items():
                    print(key)

                    if isinstance(value, dict):
                        for k,v in value.items():
                            print(key)
                            print(value)
                            print("11111111111111111111111111111111111111111")
                    else:
                        print(value)
                    print("------------------------------------------")
                print("###################################################")

            # print(messages)
            # print(messages.keys())

            response, cost = service(configs, agent_type=agent_type).chat_completion(
                messages, n
            )
            return response, cost
        else:
            raise ValueError(f"API_TYPE {api_type} not supported")
    except Exception as e:
        if use_backup_engine:
            print_with_color(f"The API request of {agent_type} failed: {e}.", "red")
            print_with_color(f"Switching to use the backup engine...", "yellow")
            return get_completions(
                messages, agent="backup", use_backup_engine=False, n=n
            )
        else:
            raise e