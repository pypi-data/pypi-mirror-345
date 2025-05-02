import argparse
from collections import defaultdict
import datetime
import os


def get_file_list(directory):
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".txt"):
                result.append(os.path.join(root, file).lower())
    return result


def get_keyword_list(keyword_path):
    with open(keyword_path, mode="r", encoding="utf8") as source:
        all_keywords = source.readlines()
        all_keywords = [keyword.strip() for keyword in all_keywords]
    return all_keywords


import os

def find_user_id_in_text_file(all_text_files, keyword):
    matched_files = []

    for filepath in all_text_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line_number, line in enumerate(f, start=1):
                    if keyword in line:
                        matched_files.append({
                            "user_id": keyword,
                            "file_name": filepath,
                            "line_number": line_number,
                        })
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
    
    return matched_files

def group_by_user_id(found_files):
    grouped = defaultdict(list)
    for item in found_files:
        user_id = item["user_id"]
        grouped[user_id].append({
            "file_name": item["file_name"],
            "line_number": item["line_number"]
        })
    return grouped

def write_result_to_file(found_files):
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y-%m-%d")
    grouped_file_by_user_id = group_by_user_id(found_files)
    number_of_user_id = len(grouped_file_by_user_id)
    file_name = f"./{current_time}_ผลการค้นหาพบ user id {number_of_user_id} รายการ.txt"
    with open(file_name, "w", encoding="utf8") as writer:
        for item in found_files:
            line = f"User ID: {item['user_id']} พบในไฟล์ {item['file_name']} บรรทัดที่ {item['line_number']}\n"
            writer.write(line)
    print(f"INFO: Result saved as {file_name}")


def main():
    parser = argparse.ArgumentParser(description="Search line userid from data folder")
    parser.add_argument("-i", "--input_path", help="Path to the data folder")
    parser.add_argument("-k", "--keyword_path", help="Path to the keyword file")
    args = parser.parse_args()
    input_path = args.input_path
    keyword_path = args.keyword_path
    all_text_files = get_file_list(input_path)
    all_keywords = get_keyword_list(keyword_path)

    found_files = []
    for keyword in all_keywords:
        result = find_user_id_in_text_file(all_text_files, keyword)
        found_files.extend(result)
    found_files = [item for item in found_files if len(item) != 0]
    
    write_result_to_file(found_files)


if __name__ == "__main__":
    main()
