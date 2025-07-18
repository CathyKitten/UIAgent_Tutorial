import os
import json
import base64
import time
from typing import List, Dict, Any
from ufo.llm.openai_utils import send_request_ufo
from colorama import Fore, Style, init


def print_with_color(text: str, color: str = "", end: str = "\n") -> None:
    """
    Print text with specified color using ANSI escape codes from Colorama library.

    :param text: The text to print.
    :param color: The color of the text (options: red, green, yellow, blue, magenta, cyan, white, black).
    """
    color_mapping = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "black": Fore.BLACK,
    }

    selected_color = color_mapping.get(color.lower(), "")
    colored_text = selected_color + text + Style.RESET_ALL

    print(colored_text, end=end)
# --- Helper and Main Logic ---

def image_to_base64(image_path: str) -> str:
    """Encodes an image file to a Base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except FileNotFoundError:
        print(f"Warning: Image file not found at {image_path}")
        return None


def process_and_evaluate_steps(root_directory, model_name,schema):
    """
    Traverses a directory, processes video_step.json files,
    and sends the data for evaluation.
    """
    # Define the JSON schema for the expected response from the model
    with open(schema, 'r') as file:
        schema_judge = json.load(file)

    # Use os.walk to traverse all directories and files
    for root, dirs, files in os.walk(root_directory):
        # We are looking for the specific file 'video_step.json'
        if 'video_step.json' in files:
            # Check if the parent directory is named 'video_demo'
            if os.path.basename(root) == 'video_demo':
                json_path = os.path.join(root, 'video_step.json')
                request_path=os.path.join(root, 'request.json')
                # request_path=r"C:\Users\v-yuhangxie\OneDrive - Microsoft\qabench\qabench\logs\chunk1\add_a_special_character_or_symbol_4f364db0-912b-46b3-8282-2d8dd49c336a\document\request.json"
                with open(request_path, 'r', encoding='utf-8') as f:
                    request_dict = json.load(f)
                    request=request_dict["request"]

                # json_path=r"C:\Users\v-yuhangxie\OneDrive - Microsoft\qabench\qabench\logs\chunk1\add_a_special_character_or_symbol_4f364db0-912b-46b3-8282-2d8dd49c336a\video_demo\video_step.json"
                print(f"\nProcessing file: {json_path}")

                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        steps_data = json.load(f)
                        print(steps_data)
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    print(f"Error reading or parsing {json_path}: {e}")
                    continue

                # Get all steps and exclude the first and last ones
                # .items() preserves insertion order in Python 3.7+
                middle_steps = list(steps_data.items())[1:-1]

                if not middle_steps:
                    print("No middle steps to process. Skipping.")
                    continue

                task_overview=f'''## Task Overview
You are an Excel expert. You are given an original request along with the corresponding instructional video.
Your task is to assign a score from 1 to 5 for each of the five criteria, based on following definitions and scoring guidelines.:

<1> Clarity
Each instructional video step is clearly and explicitly described, with no ambiguity.
Scoring Guide:
1: Every step in the instructional video is unclear, making the tutorial completely incomprehensible.
2: Only 1–2 steps are clear, making it difficult to understand the tutorial as a whole.
3: Only about half of the step descriptions are clear, which hinders understanding of the entire process.
4: Only a few steps are slightly unclear, but they do not affect the overall comprehension of the process.
5: Every step in the instructional video is very clearly described and completely unambiguous.

<2> Conciseness
There are no repeated or unnecessary steps in the instructional video.
Scoring Guide:
1: Almost all steps in the video are irrelevant or repetitive, making it hard for viewers to focus on the task.
2: More than half of the steps are redundant or clearly irrelevant, significantly reducing the efficiency of information delivery.
3: The video contains multiple redundant or unnecessary steps that may affect the viewing experience.
4: The video is generally concise, with only 1–2 minor redundant actions that do not hinder understanding.
5: There are no redundant, repetitive, or unnecessary steps at all.

<3> Completeness
The instructional video steps are complete, with nothing missing or skipped.
Scoring Guide:
1: The video covers almost none of the essential operations, with major steps missing.
2: The video is missing many steps, with most key operations not shown.
3: About half of the steps are missing; the viewer cannot understand the overall task.
4: The video is mostly complete, with 1–2 minor missing steps that do not significantly affect task completion.
5: No steps are missing; all necessary actions to complete the task are covered.

<4> Sequential Order
The steps in the instructional video are presented in a clear and logical sequence, without any disordered or confusing arrangements.
Scoring Guide:
1: The steps are completely out of order, making it impossible to understand the workflow.
2: Several key steps are in the wrong order, resulting in a confusing flow.
3: Some steps are misordered, which creates moderate difficulty in understanding the process.
4: Steps are mostly in a reasonable order, with only minor deviations that don’t hinder understanding.
5: All steps are presented in a logical and coherent sequence.

<5> Text-Image Mapping
The text and images are well-aligned, with each image accurately matching its corresponding textual description.
Scoring Guide:
1: The text and images are almost entirely misaligned, causing severe comprehension issues.
2: More than half of the images do not match the text, significantly hindering understanding.
3: Several mismatches exist, making it difficult to follow some steps by correlating text and images.
4: Overall alignment is good, with only minor mismatches that do not affect comprehension.
5: All text and images are perfectly aligned, creating a smooth and coherent visual-textual experience.

## Output Format
Output as a JSON. Record the score for each criterion in the corresponding field using the following format:
{{
  "clarity": ...,
  "conciseness": ...,
  "completeness": ...,
  "sequential_order": ...,
  "text-image_mapping": ...
}}

##input
Here is the original request: {request}
Here is the operation logs and screenshots:
  '''
                # Construct the message payload for the API
                user_content = [
                    {
                        "type": "text",
                        "text": task_overview
                    }
                ]

                for image_path, description in middle_steps:
                    # Add the text description for the step
                    step_title, step_explanation = description
                    user_content.append({
                        "type": "text",
                        "text": f"Step: {step_title}\nDescription: {step_explanation}"
                    })

                    # Encode and add the image for the step
                    base64_image = image_to_base64(image_path)
                    if base64_image:
                        user_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        })



                message = [
                    {"role": "user", "content": user_content}
                ]
                try_count = 20
                while try_count > 0:
                    try:
                        # Send the request and get the result
                        result_str = send_request_ufo(model_name, message, schema=schema_judge)
                        break
                    except Exception as e:
                        print_with_color(f"Error: {e}", "red")
                        print_with_color("Retrying...", "yellow")
                        try_count -= 1
                        time.sleep(30)
                        continue

                # Print the formatted result
                try:
                    result_json = json.loads(result_str)
                    output_result_file = os.path.join(root, "video_judge_result.json")
                    with open(output_result_file, "w", encoding="utf-8") as f:
                        json.dump(result_json, f, ensure_ascii=False, indent=2)
                    print(result_json)

                except json.JSONDecodeError:
                    print(f"Could not parse model response: {result_str}")


if __name__ == '__main__':
    # IMPORTANT: Set this to the root folder you want to scan.
    root_folder = r"C:\Users\v-yuhangxie\OneDrive - Microsoft\qabench\qabench\logs\chunk1"

    # Specify the model you want to use
    judge_model_name = 'dev-gpt-41-longco-2025-04-14'
    # judge_model_name ="dev-gpt-45-preview"# Or any other available model
    schema="./data/steps_schema_questionnaire_score.json"

    if not os.path.isdir(root_folder):
        print(f"Error: Root directory not found at '{root_folder}'")
    else:
        process_and_evaluate_steps(root_folder, judge_model_name,schema)
