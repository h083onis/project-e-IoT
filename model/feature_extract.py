import pandas as pd
import numpy as np
import mk_dataframe

# 特徴量を抽出する関数
def extract_features(df, S):
    
    # ユニークなアドレス数を計算
    unique_address_counts = df.groupby(df.index)['address'].nunique()

    # 総数（全件数）を計算
    total_counts = df.groupby(df.index)['address'].count()
    
    # RSSIがSを超えるユニークなBDアドレスの数
    df_over_s = df[df['rssi'] > S]
    
    # S[db]以上でユニークなアドレス数を計算
    unique_address_counts_s = df_over_s.groupby(df_over_s.index)['address'].nunique()

    # S[db]以上で総数（全件数）を計算
    total_counts_s = df_over_s.groupby(df_over_s.index)['address'].count()
    
    # 元のデータフレームの形にインデックスを揃える (欠損部分はNaNで補完)
    unique_address_counts_s = unique_address_counts_s.reindex(total_counts.index)
    total_counts_s = total_counts_s.reindex(total_counts.index)
    
    # DataFrameを作成
    unique_df = pd.DataFrame({
        'unique_address_count': unique_address_counts,
        'total_count': total_counts,
        'unique_ratio_Tsec': unique_address_counts / total_counts
    })

    over_s_df = pd.DataFrame({
        'unique_address_count_overS': unique_address_counts_s,
        'total_count_overS': total_counts_s,
        'unique_ratio_Tsec_overS': unique_address_counts_s / total_counts_s
    })
    
    # インデックスが一致するところで結合
    df_features = unique_df.join(over_s_df)

    # 欠損値がある場合はNaNとして残す
    df_features.fillna(np.nan, inplace=True)
    
    
    return df_features


PATH = './data/4.txt'

df = mk_dataframe.make_Tsec_frame(60, PATH)
print(df)
print(extract_features(df, -60)) 