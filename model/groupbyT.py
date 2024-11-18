import pandas as pd
import json

'''
T秒ごとにデータフレームをグループ化する関数

入力 : T(Tに該当する秒数-10,20,30,40,50,60)のいずれか, dir_path(ディレクトリまでのパス), file1, file2(デフォルトNone)

出力

グループnumber                        time            address rssi
            0   2024-10-02 17:56:00+09:00  37:7b:5b:02:28:be  -64
            0   2024-10-02 17:56:00+09:00  ff:0f:00:10:30:60  -79
            0   2024-10-02 17:56:00+09:00  09:41:52:11:0c:3c  -47
            0   2024-10-02 17:56:00+09:00  4b:05:b6:cd:37:00  -56
            0   2024-10-02 17:56:00+09:00  cc:7e:4a:73:96:e8  -89
            ...            ...                ...  ...
         7172   2024-10-07 17:28:00+09:00  65:b7:1e:ca:60:13  -79
         7172   2024-10-07 17:28:00+09:00  fc:06:7a:a3:32:97  -64
         7172   2024-10-07 17:28:00+09:00  c7:30:1e:7e:44:4a  -58
         7172   2024-10-07 17:28:00+09:00  40:1c:5a:77:2d:6f  -57
         7172   2024-10-07 17:28:00+09:00  e3:45:79:4c:0d:fb  -80

'''


def make_Tsec_frame(T, dir_path, file1, file2=None):
    records1 = []
    filepath1 = dir_path + file1
    # ファイルを行ごとに読み込む
    with open(filepath1, 'r') as f:
        for line in f:
            try:
                # 各行をJSONとしてパース
                entry = json.loads(line.strip())
                time = entry["time"]  # 各スキャン時刻
                for device in entry["scanned_device"]:
                    device_record = {"address": device["address"], "rssi": device["rssi"], "time": time}
                    records1.append(device_record)
            except json.JSONDecodeError:
                # JSONパースエラーが発生した場合はスキップ
                print(f"Error parsing line: {line.strip()}")
    records2 = []
    #　２ファイル目もある場合
    if file2 is not None:
        filepath2 = dir_path + file2
        with open(filepath2, 'r') as f:
            for line in f:
                try:
                    # 各行をJSONとしてパース
                    entry = json.loads(line.strip())
                    time = entry["time"]  # 各スキャン時刻
                    for device in entry["scanned_device"]:
                        device_record = {"address": device["address"], "rssi": device["rssi"], "time": time}
                        records2.append(device_record)
                except json.JSONDecodeError:
                    # JSONパースエラーが発生した場合はスキップ
                    print(f"Error parsing line: {line.strip()}")
                
    df = pd.DataFrame(records1 + records2)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values(by="time")

    # 指定された秒数ごとにグループ化
    df_grouped = df.set_index('time').resample(f'{T}S').agg(list).reset_index()
    df_grouped = df_grouped[(df_grouped['time'].dt.hour < 14) | ((df_grouped['time'].dt.minute == 14) & (df_grouped['time'].dt.minute == 00)) 
                            | ((df_grouped['time'].dt.hour >= 17) & (df_grouped['time'].dt.hour < 20))].reset_index()
    
    df_grouped = df_grouped.explode(['address', 'rssi'])
    # 必要なカラムだけを選択
    df_grouped = df_grouped[['time','address', 'rssi']]
    return df_grouped
