# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# $env:PYTHONPATH="C:\Users\v-yuhangxie\UIAgent_Tutorial"; python .\ufo\agents\video\demo_gen_agent_video.py
import shutil

from typing import Any, Dict, Optional, Tuple

from ufo.agents.agent.basic import BasicAgent
from ufo.agents.states.evaluaton_agent_state import EvaluatonAgentStatus
from ufo.config.config import Config
from ufo.prompter.demo_gen_prompter import DemoGenAgentPrompter
from ufo.utils import json_parser, print_with_color, markdown_parser
from ufo.agents.video.tool.get_request import extract_and_clean_requests
import os
from ufo.agents.video.tool.gen_video import create_video_with_subtitles_and_audio

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

    gen_agent_judge = TutorialGenAgent(
        name="tutorial_gen_agent",
        app_root_name="WINWORD.EXE",
        is_visual=True,
        main_prompt=configs["DEMO_PROMPT_JUDGE"],
        example_prompt="",
        api_prompt=configs["API_PROMPT"],
    )

    gen_agent = TutorialGenAgent(
        name="tutorial_gen_agent",
        app_root_name="WINWORD.EXE",
        is_visual=True,
        main_prompt=configs["DEMO_PROMPT_VIDEO"],
        example_prompt="",
        api_prompt=configs["API_PROMPT"],
    )

    # 路径配置
    base_path = r"C:\Users\v-yuhangxie\UFO_ssb_0708\logs\20250716_bing_search_complete"
    copy_path=r"C:\Users\v-yuhangxie\OneDrive - Microsoft\log_result\20250716_bing_search_completed"
    # 检查 base_path 是否存在
    if not os.path.isdir(base_path):
        print(f"错误: 基础路径 '{base_path}' 不存在或不是一个文件夹。")
    else:
        # ⭐️ 1. 新增起始點和處理旗標
        start_folder = "bing_search_query_410003024"
        start_processing = False  # 初始設為 False，直到找到起始點
        # 遍历 base_path 下的所有项目
        for folder_name in os.listdir(base_path):
            log_path = os.path.join(base_path, folder_name)

            # 确保当前项目是一个文件夹
            if os.path.isdir(log_path):
                print(f"✅ 正在访问文件夹: {log_path}")
            md_file_path = os.path.join(log_path, "output.md")
            if not os.path.exists(md_file_path):
                print(f"{md_file_path} 不存在，跳过")
                continue
            request = extract_and_clean_requests(md_file_path)

            # # ⭐️ 2. 檢查是否到達了指定的起始資料夾
            # if folder_name == start_folder:
            #     print(f"🚀 已找到起始點: {folder_name}。開始處理後續所有資料夾。")
            #     start_processing = True
            #
            #
            # # ⭐️ 3. 只有當旗標為 True 時，才執行判斷和複製邏輯
            # if not start_processing:
            #     print(f"⏭️  跳過資料夾: {folder_name} (尚未到達起始點)")
            #     continue


            # 创建 output_folder 路径：log_path 下的 "video_demo"
            output_folder = os.path.join(log_path, "video")
            os.makedirs(output_folder, exist_ok=True)  # 如果不存在就创建

            # 生成两个输出文件的完整路径
            step_output_path = os.path.join(output_folder, "video_demo_step.json")

            with open('./ufo/agents/video/data/steps_schema_video.json', 'r') as file:
                schema = json.load(file)

            # results = gen_agent.generate(
            #     request=request, log_path=log_path, output_path=step_output_path, eva_all_screenshots=True,schema=schema
            # )


            step_judge_output_path = os.path.join(output_folder, "step_judge.json")

            with open('./ufo/agents/video/data/steps_schema_judge.json', 'r') as file:
                schema_judge = json.load(file)

            result_judge = gen_agent_judge.generate(
                request=request, log_path=log_path, output_path=step_judge_output_path, eva_all_screenshots=True, schema=schema_judge
            )
            print("-----------------------------------")

            with open(step_judge_output_path, 'r') as file:
                judge_result = json.load(file)

            if judge_result["judge"]==True:
                print(f"🟢 判斷結果為 True。準備複製資料夾 '{folder_name}'...")

                source_folder = log_path
                destination_folder = os.path.join(copy_path, folder_name)

                try:
                    # 使用 shutil.copytree 複製整個資料夾
                    # dirs_exist_ok=True 參數可以在目標資料夾已存在時覆蓋內容 (Python 3.8+)
                    shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)
                    print(f"✅ 資料夾 '{folder_name}' 已成功複製到 '{copy_path}'")
                except Exception as e:
                    print(f"❌ 複製資料夾 '{folder_name}' 時出錯: {e}")
            else:
                print(f"🔴 判斷結果為 False 或無效。跳過複製資料夾 '{folder_name}'。")



            # # Windows用戶請確保此路徑有效
            # TITLE_FONT_PATH = 'C:/Windows/Fonts/arialbd.ttf'  # Arial (粗體)
            # SUBTITLE_FONT_PATH = 'C:/Windows/Fonts/arial.ttf'  # Arial (常規)
            #
            # with open(step_output_path, 'r', encoding='utf-8') as f:
            #     image_step_dict = json.load(f)
            #
            #
            #
            # # 创建新字典，使用 i 从 1 开始编号
            # image_step_path_dict_video = {}
            # i = 1
            # path=os.path.join(log_path, f"action_step1.png")
            # text="Here’s the original Excel file that we’ll be working with."
            # image_step_path_dict_video[path]={"voiceover_script":text,"title":"Original Excel File"}
            # for key, value in image_step_dict["steps"].items():
            #     path = os.path.join(log_path, f"action_step{key}_selected_controls_mouse.png")
            #     image_step_path_dict_video[path]={}
            #     voiceover_script=value['voiceover_script']
            #     title = value['title']
            #     image_step_path_dict_video[path]['voiceover_script'] = f"Step{i}: {voiceover_script}"
            #     image_step_path_dict_video[path]['title'] = f"Step{key}: {title}"
            #     i += 1
            # path = os.path.join(log_path, f"action_step_final.png")
            # image_step_path_dict_video[path]={"voiceover_script":"You've now successfully completed the task!","title":"Output Excel File"}
            #
            # video_json_path = os.path.join(output_folder, "video_step.json")
            # # 保存为 JSON 文件
            # with open(video_json_path, "w", encoding="utf-8") as f:
            #     json.dump(image_step_path_dict_video, f, ensure_ascii=False, indent=2)
            #
            # request_output_path = os.path.join(output_folder, "request.json")
            # with open(request_output_path, "w", encoding="utf-8") as f:
            #     request_dict={"request":request}
            #     json.dump(request_dict, f, ensure_ascii=False, indent=2)
            #
            #
            #
            # output_file_video = os.path.join(output_folder, "video_demo.mp4")
            # output_audio_folder= os.path.join(output_folder, "audio")
            #
            # md_file_path = os.path.join(log_path, "output.md")
            # if not os.path.exists(md_file_path):
            #     print(f"{md_file_path} 不存在，跳过")
            #     continue
            #
            # eval_log_file_path = os.path.join(log_path, "evaluation.log")
            # request = extract_and_clean_requests(eval_log_file_path)
            #
            #
            # print("\n--- 開始創建帶字幕和配音的視頻 ---")
            # full_request="The task is: "+request
            # ending_sentence="Thank you for watching!"
            #
            # video_title = image_step_dict["video_title"]
            # thematic_opening_line = image_step_dict["thematic_opening_line"]
            # initial_image_file = "./ufo/agents/video/data/title_background.jpg"
            #
            # try:
            #     create_video_with_subtitles_and_audio(
            #         # 開頭場景參數
            #         video_title=video_title,
            #         thematic_opening_line=thematic_opening_line,
            #         initial_image_path=initial_image_file,
            #         # 其他參數
            #         image_text_map=image_step_path_dict_video,
            #         output_video_path=output_file_video,
            #         output_audio_folder=output_audio_folder,
            #         fps=24,
            #         title_font_path=TITLE_FONT_PATH,
            #         subtitle_font_path=SUBTITLE_FONT_PATH,
            #         # 這是後續內容的字體大小
            #         title_font_size=38,
            #         subtitle_font_size=32,
            #         # 這是為新開頭場景指定的字體大小
            #         opening_title_font_size=39,
            #         opening_task_font_size=27,
            #         lang='en',
            #         ending_sentence=ending_sentence
            #     )
            #
            #     print("\n--- 視頻創建完成 ---")
            # except FileNotFoundError as e:
            #     print(f"\n錯誤: 創建失敗。請檢查文件路徑是否正確: {e}")
            # except Exception as e:
            #     print(f"\n發生未知錯誤: {e}")
