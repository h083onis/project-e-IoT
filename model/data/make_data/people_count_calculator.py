# -*- coding: utf-8 -*-
"""
people_count_calculator.py

決済情報とトレー返却日時から，特定の時間（1分単位）における利用者の人数をカウントするプログラム

入力 : PDFファイルのパス

出力 (例)

                               time  people_count
            0   2024-10-01 11:00:00             0
            1   2024-10-01 11:01:00           416
            2   2024-10-01 11:02:00           416
            3   2024-10-01 11:03:00           416
            4   2024-10-01 11:04:00           416
            ..                  ...           ...
            536 2024-10-01 19:56:00           416
            537 2024-10-01 19:57:00           416
            538 2024-10-01 19:58:00           416
            539 2024-10-01 19:59:00           416
            540 2024-10-01 20:00:00           416
            
            [541 rows x 2 columns]

実行例 (10月28日の場合)：python3 people_count_calculator.py 1028

"""


import json
import pandas as pd
import extract_payment_times
from datetime import datetime, timedelta
import argparse


# 決済情報のPDFファイルから利用日時を読み込んでDataFrameとして返す関数
def load_payment_times_from_pdf(pdf_file_paths):
    json_data = extract_payment_times.extract_from_multiple_pdfs(pdf_file_paths)
    payment_times = json.loads(json_data)["payment_times"]
    payment_times = [datetime.strptime(dt, "%Y-%m-%d %H:%M") for dt in payment_times]
    payment_df = pd.DataFrame(payment_times, columns=['time'])

    # 同じ時間に複数の決済があれば、actionをその数にする
    payment_df = payment_df.groupby('time').size().reset_index(name='action')
    payment_df['action'] = payment_df['action']  # ここでactionが決済数
    # print(payment_df)
    payment_df.to_csv("./labels/aaa.csv", index=False)
    return payment_df


# トレー返却データのCSVファイルから時間を読み込んでDataFrameとして返す関数
def load_return_times_from_csv(csv_file_path):
    # CSVファイルを読み込む
    return_df = pd.read_csv(csv_file_path, parse_dates=['Timestamp(lunch)', 'Timestamp(dinner)'])
    # lunchとdinnerのTimestamp列を1つにまとめる
    lunch_times = return_df['Timestamp(lunch)'].dropna()
    dinner_times = return_df['Timestamp(dinner)'].dropna()

    # lunchとdinnerのデータを1つの列に結合
    combined_times = pd.concat([lunch_times, dinner_times])

    # 1日分(昼と夜)のトレー返却時間のDataFrameを作成
    return_df = pd.DataFrame(combined_times, columns=['time'])
    
    # 同じ時間に複数のトレー返却があれば、actionをその数にする
    return_df = return_df.groupby('time').size().reset_index(name='action')
    return_df['action'] = -return_df['action']  # トレー返却で利用者が減る (-数)
    
    return return_df


# 特定の時間(1分単位)の利用者人数を算出する関数
def calculate_people_count(payment_df, return_df, start_time, end_time):    
    # 1. 両方のDataFrameを結合
    combined_df = pd.concat([payment_df, return_df]).sort_values('time').reset_index(drop=True)

    # 2. 同じ時間に対してactionを集計する -> 人数の増減がわかる & 対象の時間に区切る
    combined_df = combined_df.groupby('time').agg({'action': 'sum'}).reset_index()
    combined_df = combined_df[combined_df['time'] <= end_time]
    combined_df = combined_df[combined_df['time'] >= start_time]
    
    # 3. 1分ごとの時間を生成
    time_index = pd.date_range(start=start_time, end=end_time, freq='T')
    people_count_df = pd.DataFrame(time_index, columns=['time'])
    
    # 4. 各時間帯の利用者数を計算
    people_count_df['people_count'] = 0
    current_people_count = 0  # 初期人数は0

    # 5. それぞれの時間帯の利用者数を更新
    for i in range(len(people_count_df)):
        current_time = people_count_df['time'].iloc[i]
        
        # 現在の時間より前のtimeでの累積人数の増減を計算
        relevant_actions = combined_df[combined_df['time'] <= current_time]

        if not relevant_actions.empty:
            # 時間に従ってactionを累積
            current_people_count = relevant_actions['action'].sum()

        # 最後にcurrent_people_countを設定
        people_count_df.at[i, 'people_count'] = current_people_count
        
    
    return people_count_df


# メイン処理
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="1日分の利用者人数を算出")
    parser.add_argument("date", type=str, help="日付をMMDD形式で指定 (例: 1028)")
    args = parser.parse_args()
    
    # 日付を変換
    date_str = args.date
    month = int(date_str[:2])
    day = int(date_str[2:])
    year = 2024  # 必要に応じて他の年を指定可能

    # 情報のパス
    pdf_file_paths = [f'./payment_data/{year}{date_str}-1.pdf',
                      f'./payment_data/{year}{date_str}-2.pdf',
                      f'./payment_data/{year}{date_str}-3.pdf']
    csv_file_path = f'./count_data/tray_return{year}{date_str}.csv'
    
    payment_df = load_payment_times_from_pdf(pdf_file_paths)
    return_df = load_return_times_from_csv(csv_file_path)
    
    start_time = datetime(year, month, day, 11, 0)
    end_time = datetime(year, month, day, 14, 0)
    
    people_count_df = calculate_people_count(payment_df, return_df, start_time, end_time)

    # 結果を保存 lunch
    output_csv_path = f'./labels/{year}{date_str}_lunch.csv'
    people_count_df.to_csv(output_csv_path, index=False)
    print(f"CSVファイルとして保存しました: {output_csv_path}")
    
    
    start_time = datetime(year, month, day, 17, 0)
    end_time = datetime(year, month, day, 20, 0)
    
    people_count_df = calculate_people_count(payment_df, return_df, start_time, end_time)

    # 結果を保存 lunch
    output_csv_path = f'./labels/{year}{date_str}_dinner.csv'
    people_count_df.to_csv(output_csv_path, index=False)
    print(f"CSVファイルとして保存しました: {output_csv_path}")