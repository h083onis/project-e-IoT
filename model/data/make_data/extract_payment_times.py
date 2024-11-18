# -*- coding: utf-8 -*-
"""
extract_payment_times.py

決済情報のPDFから利用日時を抽出する関数

入力 : PDFファイルのパス

出力 (例)

            {
                "payment_times": [
                    "2024-10-28 11:02",
                    "2024-10-28 11:03",
                    "2024-10-28 11:03",
                    "2024-10-28 11:03",
                    "2024-10-28 11:04",
                    "2024-10-28 11:04",
                    "2024-10-28 11:05",
                    "2024-10-28 11:06",
                    "2024-10-28 11:06",
                    "2024-10-28 11:07",
                    "2024-10-28 11:07",
                    ...
                    "2024-10-28 19:27",
                    "2024-10-28 19:28",
                    "2024-10-28 19:31",
                    "2024-10-28 19:32",
                    "2024-10-28 19:33",
                    "2024-10-28 19:34",
                    "2024-10-28 19:35",
                    "2024-10-28 19:35",
                    "2024-10-28 19:36",
                    "2024-10-28 19:38",
                    "2024-10-28 19:39",
                    "2024-10-28 19:39",
                    "2024-10-28 19:40",
                    "2024-10-28 19:40",
                    "2024-10-28 19:42"
                ]
            }
        
"""


import re
import json
import PyPDF2
from datetime import datetime


# 決済情報のPDFから利用日時を抽出する関数
def extract_payment_times_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

    payment_times = []

    # 各決済情報を区切るパターン
    pattern_split = r"-{32}"
    # 利用日時が書かれている場合
    pattern_date_on = r"利用日時：(\d{4})年(\d{2})月(\d{2})日 (\d{2}):(\d{2})"
    # 日時がそのまま書かれている場合 (曜日を柔軟に対応)
    pattern_date_off = r"(\d{4})年(\d{1,2})月\s?(\d{1,2})日（[日月火水木金土]）(\d{1,2}):(\d{2})"
    # "担当者ログイン"を検出するパターン
    pattern_login = r"担当者ログイン"
    
    pattern_gomi = r"･{32}"

    # 決済情報のセクションごとに処理
    sections = re.split(pattern_split, text)
    for section in sections:
        section = section.strip()
        if not section:
            continue

        # "担当者ログイン"があるか確認
        if re.search(pattern_login, section):
            continue  # 担当者ログインがある場合、このセクションをスキップ
                # "担当者ログイン"があるか確認
        if re.search(pattern_gomi, section):
            continue  # ゴミがある場合、このセクションをスキップ

        # "利用日時："があるかどうか確認
        date_match_on = re.search(pattern_date_on, section)
        if date_match_on:
            year, month, day, hour, minute = date_match_on.groups()
        else:
            # "利用日時："がない場合、一般の日時フォーマットを探す
            date_match_off = re.search(pattern_date_off, section)
            if date_match_off:
                year, month, day, hour, minute = date_match_off.groups()
            else:
                continue  # 日時情報がない場合はスキップ

        # 日付情報を統一フォーマットに変換
        date_time = datetime(int(year), int(month), int(day), int(hour), int(minute))
        formatted_date_time = date_time.strftime("%Y-%m-%d %H:%M")

        # リストに追加
        payment_times.append(formatted_date_time)
        
    print(len(payment_times))    
    return payment_times


# レジ3台の決済情報をまとめる関数
def extract_from_multiple_pdfs(pdf_file_paths):
    all_payment_times = []
    for pdf_file_path in pdf_file_paths:
        payment_times = extract_payment_times_from_pdf(pdf_file_path)
        all_payment_times.extend(payment_times)

    # 日時順に並び替え（重複はそのまま保持）
    all_payment_times.sort()
    
    # JSON形式に変換して出力
    result = {"payment_times": all_payment_times}
    json_data = json.dumps(result, ensure_ascii=False, indent=4)
    # print(json_data)
    
    return json_data


# # 使用例
# pdf_file_paths = [
#     './payment_data/20241029-1.pdf',
#     # './payment_data/20241028-2.pdf',
#     # './payment_data/20241028-3.pdf'
# ]


# # 出力を生成
# json_output = extract_from_multiple_pdfs(pdf_file_paths)

# #　結果を表示
# print(json_output)

