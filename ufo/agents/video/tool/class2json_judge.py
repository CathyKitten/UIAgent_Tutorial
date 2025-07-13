from pydantic import BaseModel, Field
from enum import Enum
import json
from typing import Optional

# --- (輔助函數，無需修改) ---

def add_additional_properties_false(schema) -> None:
    """
    遞迴地將 "additionalProperties": false 添加到 JSON schema 中的所有 object 定義中。
    """
    if "type" in schema and schema["type"] == "object":
        schema.setdefault("additionalProperties", False)
    if "properties" in schema:
        for prop in schema["properties"].values():
            add_additional_properties_false(prop)
    if "$defs" in schema:
        for definition in schema["$defs"].values():
            add_additional_properties_false(definition)
    if "items" in schema and isinstance(schema["items"], dict):
        add_additional_properties_false(schema["items"])

def remove_titles_recursively(schema) -> None:
    """
    遞迴地從 JSON schema 中的所有對象中刪除 "title" 屬性。
    """
    schema.pop("title", None)
    if "properties" in schema:
        for prop in schema["properties"].values():
            remove_titles_recursively(prop)
    if "$defs" in schema:
        for definition in schema["$defs"].values():
            remove_titles_recursively(definition)
    if "items" in schema and isinstance(schema["items"], dict):
        remove_titles_recursively(schema["items"])

def generate_json_schema(model) -> dict:
    """
    為 Pydantic 模型生成 JSON schema。
    """
    model.model_rebuild(force=True)
    schema = model.model_json_schema()
    add_additional_properties_false(schema)
    schema['additionalProperties'] = False
    remove_titles_recursively(schema)
    return schema

# --- 程式碼修改部分 ---

# 1. 定義一個新的 Pydantic 模型來代表評分結果的結構
class EvaluationScores(BaseModel):
    """
    定義五個評分維度的資料模型，用於規範 JSON 輸出。
    """
    clarity: int = Field(
        ...,
        ge=1, le=5,
        description="Score for clarity, from 1 to 5."
    )
    conciseness: int = Field(
        ...,
        ge=1, le=5,
        description="Score for conciseness, from 1 to 5."
    )
    completeness: int = Field(
        ...,
        ge=1, le=5,
        description="Score for completeness, from 1 to 5."
    )
    sequential_order: int = Field(
        ...,
        ge=1, le=5,
        description="Score for sequential order, from 1 to 5."
    )
    # 使用 'alias' 來處理包含連字符的 JSON key
    text_image_mapping: int = Field(
        ...,
        alias="text-image_mapping",
        ge=1, le=5,
        description="Score for text-image mapping, from 1 to 5."
    )


if __name__ == "__main__":
    jsonfile = generate_json_schema(EvaluationScores)
    print(jsonfile)
    file_path = "../data/steps_schema_questionnaire_score.json"
    with open(file_path, "w") as file:
        json.dump(jsonfile, file, indent=4)
