# 使い方
1. 検証用の https://github.com/blueish-co/omni-taxbiz/pull/226 を立ち上げ、通帳データを読み取る
2. 1. の実行完了後に吐き出された`passbook_structured.json`をこのプログラム（passbook-accuracy-check）内に'ocr_data.json'としておく。
3. 正解データを`correct_data.json`としておく。
4. ```python compare_bank_json.py``` を実行する
5. `comparison_result.json`で精度を確認する。


# 行数が一致していない場合
以下のコードで差分のオブジェクトを埋める。埋めた状態で再度```python compare_bank_json.py``` を実行する。
```
      {
        "balance": "差分調整",
        "date": "差分調整",
        "deposit": "差分調整",
        "description": "差分調整",
        "withdrawal": "差分調整"
      }
```
