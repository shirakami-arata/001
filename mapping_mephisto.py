import pandas as pd
import folium
import streamlit as st # これを追加するで！
from streamlit_folium import st_folium # これも地図を埋め込むのに便利やで！

st.set_page_config(layout="wide") # 画面を広く使う設定やで

st.title("CSVデータから地図にプロットするアプリ")
st.write("ここにCSVファイルをアップロードしたら、地図にピン立てます")

# CSVファイルのアップロード機能やで
uploaded_file = st.file_uploader("CSVファイルを選んで！", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSVファイルの読み込み成功！")

        # 列名を選んでもらうUIやで
        st.subheader("緯度と経度の列を選んで！")
        col1, col2 = st.columns(2)
        with col1:
            latitude_col = st.selectbox("緯度の列:", df.columns, index=df.columns.get_loc('Latitude') if 'Latitude' in df.columns else 0)
        with col2:
            longitude_col = st.selectbox("経度の列:", df.columns, index=df.columns.get_loc('Longitude') if 'Longitude' in df.columns else 0)

        st.subheader("マーカーのオプションを選んで！")
        col3, col4 = st.columns(2)
        with col3:
            name_col_options = ['なし'] + list(df.columns)
            selected_name_col = st.selectbox("名前の列 (ポップアップ表示):", name_col_options, index=name_col_options.index('Name') if 'Name' in name_col_options else 0)
            name_col = selected_name_col if selected_name_col != 'なし' else None

        with col4:
            description_col_options = ['なし'] + list(df.columns)
            selected_description_col = st.selectbox("説明の列 (ポップアップ表示):", description_col_options, index=description_col_options.index('Description') if 'Description' in description_col_options else 0)
            description_col = selected_description_col if selected_description_col != 'なし' else None

        # ズームレベルの設定やで
        map_zoom = st.slider("地図の初期ズームレベル:", min_value=1, max_value=20, value=10)

        # 緯度と経度の列がちゃんとあるか確認しとこか
        if latitude_col not in df.columns or longitude_col not in df.columns:
            st.error("選んだ列が見つからへんわ！もう一回確認しいや！")
        elif df.empty:
            st.warning("CSVファイル、空っぽやん！プロットするデータがないで！")
        else:
            # 地図の初期化（中心座標は最初のデータ使うで）
            initial_coords = [df[latitude_col].iloc[0], df[longitude_col].iloc[0]]
            m = folium.Map(location=initial_coords, zoom_start=map_zoom)

            # データフレームの行を順番に見て、マーカーを追加していくで
            for idx, row in df.iterrows():
                lat = row[latitude_col]
                lon = row[longitude_col]

                if pd.isna(lat) or pd.isna(lon):
                    # Streamlitの警告メッセージは `st.warning` とか `st.info` で出すんやで
                    st.info(f"📍 インデックス {idx} のデータに無効な緯度経度があるで。スキップするわ。")
                    continue

                popup_html = ""
                if name_col and name_col in row and pd.notna(row[name_col]):
                    popup_html += f"<b>名前:</b> {row[name_col]}<br>"
                if description_col and description_col in row and pd.notna(row[description_col]):
                    popup_html += f"<b>説明:</b> {row[description_col]}<br>"
                popup_html += f"<b>緯度:</b> {lat}<br><b>経度:</b> {lon}"

                marker_name = row[name_col] if name_col and name_col in row and pd.notna(row[name_col]) else f"地点 {idx+1}"

                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=300), # ポップアップの幅を設定できるで
                    tooltip=marker_name
                ).add_to(m)

            st.subheader("結果の地図やで！")
            # StreamlitにFoliumの地図を表示させるんやで
            st_data = st_folium(m, width=900, height=500) # ここで地図を表示！

    except Exception as e:
        st.error(f"CSVファイルの処理中にエラーが発生したで: {e}")
        st.info("CSVファイルの形式が正しいか、もう一回確認してみてな！")