import json

def compare_json_files(ocr_file: str, correct_file: str, output_file: str) -> None:
    with open(ocr_file, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    
    with open(correct_file, 'r', encoding='utf-8') as f:
        correct_data = json.load(f)

    # `passbookPagesData` を取り出し、二重リストをフラットにする
    if "passbookPagesData" in ocr_data:
        ocr_data = [item for page in ocr_data["passbookPagesData"] for item in page]  # フラット化
    else:
        raise ValueError("Invalid JSON structure: 'passbookPagesData' key not found")

    if "passbookPagesData" in correct_data:
        correct_data = [item for page in correct_data["passbookPagesData"] for item in page]
    else:
        raise ValueError("Invalid JSON structure: 'passbookPagesData' key not found")

    fields = ["date", "description", "deposit", "withdrawal", "balance"]
    total_entries = len(correct_data) * len(fields)
    total_correct = 0
    total_errors = 0
    discrepancies = []

    field_stats = {field: {"total": 0, "correct": 0} for field in fields}

    for index, (ocr_entry, correct_entry) in enumerate(zip(ocr_data, correct_data)):
        for field in fields:
            field_stats[field]["total"] += 1
            if ocr_entry.get(field) == correct_entry.get(field):
                field_stats[field]["correct"] += 1
                total_correct += 1
            else:
                total_errors += 1
                discrepancies.append({
                    "index": index,
                    "field": field,
                    "ocr_value": ocr_entry.get(field),
                    "correct_value": correct_entry.get(field)
                })

    # 各フィールドの正答率
    field_accuracies = [
        {
            "field": field,
            "total": field_stats[field]["total"],
            "correct": field_stats[field]["correct"],
            "accuracy": (field_stats[field]["correct"] / field_stats[field]["total"] * 100) if field_stats[field]["total"] > 0 else 0
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
        "total_entries": total_entries,
        "total_correct": total_correct,
        "total_errors": total_errors,
        "total_accuracy": total_accuracy,
        "average_accuracy_excluding_description": average_accuracy_excluding_description,
        "field_accuracies": field_accuracies,
        "discrepancies": discrepancies
    }

    # 結果の書き込み
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
        f.flush()

    print(f"Comparison result saved to {output_file}")

# 使用例
ocr_json_path = 'ocr_data.json'
correct_json_path = 'correct_data.json'
output_json_path = 'comparison_result.json'

compare_json_files(ocr_json_path, correct_json_path, output_json_path)
