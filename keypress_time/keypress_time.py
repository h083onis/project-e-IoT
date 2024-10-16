import csv
import os
import keyboard
from datetime import datetime

# 昼間と夜間の判定
def get_time_period():
    current_hour = datetime.now().hour
    if 10 <= current_hour < 15:
        return "lunch"
    else:
        return "dinner"

# ファイル名の生成
def generate_csv_filename():
    date_str = datetime.now().strftime('%Y-%m-%d')
    time_period = get_time_period()
    return f'{date_str}_{time_period}.csv'

# ヘッダーを設定
header = ['Timestamp']

# 最初のファイルを作成または既存のファイルに追記
csv_file = generate_csv_filename()
file_exists = os.path.isfile(csv_file)
mode = 'a' if file_exists else 'w'

with open(csv_file, mode=mode, newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(header)

print("Enterを押すと時間が記録されます．'Esc'を押すとプログラムが終了します.")

# キー入力を監視する関数
def record_time():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time])
    print(f"Time recorded: {current_time}")

# エンターキーが押されたときにrecord_time関数を呼び出す
keyboard.add_hotkey('enter', record_time)

# エスケープキーが押されたときにプログラムを終了する
keyboard.wait('esc')

print("Program terminated.")
