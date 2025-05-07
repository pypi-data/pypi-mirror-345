import json
#使用到的专项工具，可以在此提供，以便依赖程序引用

# 1.读取规则或模型文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data
# 2.写入规则或模型文件
def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

