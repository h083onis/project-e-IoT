import pandas as pd
import sys

import feature_extract
import groupbyT

def make_df_day(dir_path_data, path_label, train=True):
    # 閾値rssiのリスト 
    threashold_rssi = [-60, -70, -80, -90, -100]
    
    # Tでグループ化
    df_data = groupbyT.make_Tsec_frame(60, dir_path_data, "4.txt", "2.txt")
    
    # 各rssi閾値で特徴量を計算しjoinしていく
    for i, s in enumerate(threashold_rssi):
        if i == 0:
            df_features = feature_extract.extract_features(df_data, s)
        else:
            tmp_df = feature_extract.extract_features(df_data, s)
            
            # 被るカラムは除去してjoin
            tmp_df = tmp_df.drop(columns=["time", "unique_address_count", "total_count", "unique_ratio_Tsec"])
            df_features = df_features.join(tmp_df)
    
    if train:
        # label人数をjoin    
        df_label = pd.concat([pd.read_csv(path_label + "_lunch.csv"), pd.read_csv(path_label + "_dinner.csv")])
        df_label = df_label.reset_index(drop=True)
        df_label = df_label.drop(columns=["time"])
        df = df_features.join(df_label, how="left")
    
    # timeを左に移動
    df.insert(0, "time", df.pop("time"))
    
    return df


if __name__ == "__main__":
    # コマンドライン引数から日付（例: 1028）を取得
    if len(sys.argv) > 1:
        date_arg = sys.argv[1]  # 引数1を取得（例: "1028"）
        DATA_PATH = f"./data/exdata/{date_arg}/"
        LABEL_PATH = f"./data/make_data/labels/2024{date_arg}"
        
        # 推論時は引数3つめにFalseを入れるとラベル無
        make_df_day(DATA_PATH, LABEL_PATH).to_csv("aaa.csv")
        
    else:
        print("引数を指定してください。")