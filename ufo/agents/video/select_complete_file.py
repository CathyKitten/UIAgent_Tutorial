import os
import json

base_path = r"C:\Users\v-yuhangxie\OneDrive - Microsoft\log_result\2025_0712_qabench"
completed_folders = []

for subdir in os.listdir(base_path):
    subdir_path = os.path.join(base_path, subdir)
    log_path = os.path.join(subdir_path, "evaluation.log")
    i=1

    if os.path.isdir(subdir_path) and os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    print(i)
                    i=i+1
                    try:
                        data = json.loads(line.strip())
                        print(data)
                        print(data.get("complete"))
                        if data.get("complete") == "yes":
                            completed_folders.append(subdir)
                            break  # 如果只要判断一次就够，可以提前跳出
                    except json.JSONDecodeError as e:
                        continue  # 某行不合法就跳过
        except Exception as e:
            print(f"跳过 {subdir}，因读取或解析失败：{e}")

# 输出 JSON 文件
output_file = r"C:\Users\v-yuhangxie\OneDrive - Microsoft\log_result\2025_0712_qabench\completed_folders.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(completed_folders, f, indent=2, ensure_ascii=False)

print(f"已找到 {len(completed_folders)} 个完成任务的子文件夹，保存至 {output_file}")
