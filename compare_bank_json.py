import json

def check_line_counts(ocr_file_path, correct_file_path):
    with open(ocr_file_path, 'r', encoding='utf-8') as ocr_file:
        ocr_lines = ocr_file.readlines()
    
    with open(correct_file_path, 'r', encoding='utf-8') as correct_file:
        correct_lines = correct_file.readlines()

    return {
        "ocr_line_count": len(ocr_lines),
        "correct_line_count": len(correct_lines),
        "line_count_match": len(ocr_lines) == len(correct_lines)
    }

def compare_json_files(ocr_file: str, correct_file: str, output_file: str) -> None:
    line_count_result = check_line_counts(ocr_file, correct_file)

    if line_count_result['line_count_match']:
        print("✅ 行数が一致しています。")
    else:
        print("⚠️ 行数が一致しません！")

    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    with open(correct_file, 'r', encoding='utf-8') as f:
        correct_data = json.load(f)

    if "passbookPagesData" in ocr_data:
        ocr_data = [item for page in ocr_data["passbookPagesData"] for item in page]
    else:
        raise ValueError("Invalid JSON structure: 'passbookPagesData' key not found")

    if "passbookPagesData" in correct_data:
        correct_data = [item for page in correct_data["passbookPagesData"] for item in page]
    else:
        raise ValueError("Invalid JSON structure: 'passbookPagesData' key not found")

    fields = ["date", "description", "deposit", "withdrawal", "balance"]
    total_entries = 0
    total_correct = 0
    total_errors = 0
    discrepancies = []
    diff_adjustment_count = {field: 0 for field in fields}  # "差分調整" のカウント

    field_stats = {field: {"total": 0, "correct": 0} for field in fields}

    for index, (ocr_entry, correct_entry) in enumerate(zip(ocr_data, correct_data)):
        for field in fields:
            ocr_value = ocr_entry.get(field)
            correct_value = correct_entry.get(field)

            # "差分調整" を含む場合は比較対象から除外し、カウントする
            if ocr_value == "差分調整" or correct_value == "差分調整":
                diff_adjustment_count[field] += 1
                continue  # このフィールドはスキップ

            field_stats[field]["total"] += 1
            total_entries += 1

            if ocr_value == correct_value:
                field_stats[field]["correct"] += 1
                total_correct += 1
            else:
                total_errors += 1
                discrepancies.append({
                    "index": index,
                    "field": field,
                    "ocr_value": ocr_value,
                    "correct_value": correct_value
                })

    # 各フィールドの正答率
    field_accuracies = [
        {
            "field": field,
            "total": field_stats[field]["total"],
            "correct": field_stats[field]["correct"],
            "accuracy": (field_stats[field]["correct"] / field_stats[field]["total"] * 100) if field_stats[field]["total"] > 0 else 0,
            "diff_adjustment_count": diff_adjustment_count[field]  # 差分調整の出現回数を追加
        }
        for field in fields
    ]

    total_accuracy = (total_correct / total_entries) * 100 if total_entries > 0 else 0

    # descriptionを除いたフィールドの平均正答率
    fields_excluding_description = [field for field in fields if field != "description"]
    total_correct_excluding_description = sum(field_stats[field]["correct"] for field in fields_excluding_description)
    total_entries_excluding_description = sum(field_stats[field]["total"] for field in fields_excluding_description)
    average_accuracy_excluding_description = (total_correct_excluding_description / total_entries_excluding_description * 100) if total_entries_excluding_description > 0 else 0

    result = {
        "ocr_line_count": line_count_result['ocr_line_count'], # 読み取りデータの行数
        "correct_line_count": line_count_result['correct_line_count'],  # 正解データの行数
        "total_correct": total_correct, # 正解数合計
        "total_errors": total_errors, # 不一致の合計
        "total_accuracy": total_accuracy, # 正解率
        "average_accuracy_excluding_description": average_accuracy_excluding_description, # 摘要を除いた正解率
        "field_accuracies": field_accuracies, # フィールドごとの正解率
        "discrepancies": discrepancies, #不一致の詳細
        "diff_adjustment_summary": diff_adjustment_count  # 差分調整の合計
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        f.flush()

    print(f"Comparison result saved to {output_file}")

# 使用例
ocr_json_path = 'ocr_data.json'
correct_json_path = 'correct_data.json'
output_json_path = 'comparison_result.json'

compare_json_files(ocr_json_path, correct_json_path, output_json_path)
