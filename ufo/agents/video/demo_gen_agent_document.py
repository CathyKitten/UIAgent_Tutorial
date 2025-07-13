# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import shutil

from typing import Any, Dict, Optional, Tuple

from ufo.agents.agent.basic import BasicAgent
from ufo.agents.states.evaluaton_agent_state import EvaluatonAgentStatus
from ufo.config.config import Config
from ufo.prompter.demo_gen_prompter import DemoGenAgentPrompter
from ufo.utils import json_parser, print_with_color, markdown_parser
from ufo.agents.video.tool.get_request import extract_request_from_md
import os

from ufo.agents.video.tool.gen_document_md import create_help_document
from ufo.agents.video.tool.gen_document_html import create_html_document
from ufo.agents.video.tool.gen_document_html_base64_pic import create_html_document_base64
import json

configs = Config.get_instance().config_data


class TutorialGenAgent(BasicAgent):
    """
    The agent for evaluation.
    """

    def __init__(
        self,
        name: str,
        app_root_name: str,
        is_visual: bool,
        main_prompt: str,
        example_prompt: str,
        api_prompt: str,
    ):
        """
        Initialize the FollowAgent.
        :agent_type: The type of the agent.
        :is_visual: The flag indicating whether the agent is visual or not.
        """

        super().__init__(name=name)

        self._app_root_name = app_root_name
        self.prompter = self.get_prompter(
            is_visual,
            main_prompt,
            example_prompt,
            api_prompt,
            app_root_name,
        )

    def get_prompter(
        self,
        is_visual,
        prompt_template: str,
        example_prompt_template: str,
        api_prompt_template: str,
        root_name: Optional[str] = None,
    ) -> DemoGenAgentPrompter:
        """
        Get the prompter for the agent.
        """

        return DemoGenAgentPrompter(
            is_visual=is_visual,
            prompt_template=prompt_template,
            example_prompt_template=example_prompt_template,
            api_prompt_template=api_prompt_template,
            root_name=root_name,
        )

    def message_constructor(
        self, log_path: str, request: str, eva_all_screenshots: bool = True
    ) -> Dict[str, Any]:
        """
        Construct the message.
        :param log_path: The path to the log file.
        :param request: The request.
        :param eva_all_screenshots: The flag indicating whether to evaluate all screenshots.
        :return: The message.
        """

        agent_prompt_system_message = self.prompter.system_prompt_construction()

        agent_prompt_user_message = self.prompter.user_content_construction(
            log_path=log_path, request=request, eva_all_screenshots=eva_all_screenshots
        )

        agent_prompt_message = self.prompter.prompt_construction(
            agent_prompt_system_message, agent_prompt_user_message
        )

        return agent_prompt_message

    @property
    def status_manager(self) -> EvaluatonAgentStatus:
        """
        Get the status manager.
        """

        return EvaluatonAgentStatus

    def generate(
        self, request: str, log_path: str, output_path: str, eva_all_screenshots: bool = True ,schema: dict = None) -> Tuple[Dict[str, str], float]:
        """
        Evaluate the task completion.
        :param log_path: The path to the log file.
        :return: The evaluation result and the cost of LLM.
        """

        message = self.message_constructor(
            log_path=log_path, request=request, eva_all_screenshots=eva_all_screenshots
        )
        result, cost = self.get_response_schema(
            message=message,schema=schema, namescope="app", use_backup_engine=True
        )



        with open(output_path, "w",encoding="utf-8") as f:
            f.write(result)
            print_with_color(f"Successfully write tutorial content to: {output_path}", color="green")

        return result, cost

    def process_comfirmation(self) -> None:
        """
        Comfirmation, currently do nothing.
        """
        pass


# The following code is used for testing the agent.
if __name__ == "__main__":

    gen_agent = TutorialGenAgent(
        name="tutorial_gen_agent",
        app_root_name="WINWORD.EXE",
        is_visual=True,
        main_prompt=configs["DEMO_PROMPT_DOCUMENT"],
        example_prompt="",
        api_prompt=configs["API_PROMPT"],
    )

    # 路径配置
    base_path = r"C:\Users\v-yuhangxie\OneDrive - Microsoft\qabench\qabench\logs\chunk1"
    json_path = r"C:\Users\v-yuhangxie\OneDrive - Microsoft\qabench\qabench\logs\completed_folders.json"

    # 读取已完成的文件夹列表
    with open(json_path, 'r', encoding='utf-8') as f:
        completed_folders = json.load(f)

    # 遍历每个文件夹
    for folder_name in completed_folders:
        log_path = os.path.join(base_path, folder_name)
        if os.path.isdir(log_path):
            print(f"✅ 正在访问文件夹: {log_path}")
        md_file_path = os.path.join(log_path, "output.md")
        request = extract_request_from_md(md_file_path)


        # 创建 output_folder 路径：log_path 下的 "video_demo"
        output_folder = os.path.join(log_path, "document")
        os.makedirs(output_folder, exist_ok=True)  # 如果不存在就创建

        # 生成两个输出文件的完整路径
        step_output_path = os.path.join(output_folder, "document_demo_step.json")


        with open('./ufo/agents/video/data/steps_schema_document.json', 'r') as file:
            schema = json.load(file)

        results = gen_agent.generate(
            request=request, log_path=log_path, output_path=step_output_path, eva_all_screenshots=True,schema=schema
        )
        print("-----------------------------------")
        # print(results)

        with open(step_output_path, 'r', encoding='utf-8') as f:
            image_step_dict = json.load(f)

        task_title=image_step_dict["task_title"]
        task_title="Help Document: "+task_title


        image_step_path_dict_document = {}
        i = 1
        path="../action_step1.png"
        text=["input file","Let's see how to do this together!"]
        image_step_path_dict_document[path]=text
        for key, value in image_step_dict["steps"].items():
            path = f"../action_step{key}_selected_controls_mouse.png"
            written_explanation = value['written_explanation']
            title = value['title']
            image_step_path_dict_document[path] = [f"step{key}: {title}",f"{written_explanation}"]
            i += 1
        path = "../action_step_final.png"
        image_step_path_dict_document[path]=["output file","You've now successfully completed the task!"]

        document_json_path = os.path.join(output_folder, "document_step.json")
        # 保存为 JSON 文件
        with open(document_json_path, "w", encoding="utf-8") as f:
            json.dump(image_step_path_dict_document, f, ensure_ascii=False, indent=2)



        output_file_document_md = os.path.join(output_folder, "help_document.md")
        output_file_document_html = os.path.join(output_folder, "help_document.html")
        output_file_document_html_base64 = os.path.join(output_folder, "help_document_base64.html")
        create_help_document(document_json_path,task_title,output_file_document_md)
        create_html_document(document_json_path, task_title, output_file_document_html)
        create_html_document_base64(document_json_path, task_title, output_file_document_html_base64)

