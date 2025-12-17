import streamlit as st
import pandas as pd
import os

# 設定頁面資訊
st.set_page_config(page_title="志工池管理系統", layout="wide")

# --- 登入功能 ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🛡️ 志工池管理系統後台")
        password = st.text_input("請輸入管理員密碼", type="password")
        if st.button("登入"):
            if password == "volunteer2025":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("密碼錯誤，請重試。")
        return False
    return True

if check_password():
    # --- 資料初始化 ---
    DB_FILE = "volunteer_data.csv"
    if not os.path.exists(DB_FILE):
        # 建立空的模擬資料
        df_init = pd.DataFrame(columns=[
            "姓名", "電話", "Line ID", "服務時段", 
            "引導", "行政", "體力", "應變", 
            "準時率", "信任度", "評價備註"
        ])
        df_init.to_csv(DB_FILE, index=False, encoding="utf-8-sig")

    df = pd.read_csv(DB_FILE)

    # --- 側邊欄 ---
    st.sidebar.title("🛠️ 功能選單")
    if st.sidebar.button("登出"):
        st.session_state.authenticated = False
        st.rerun()

    st.sidebar.divider()
    st.sidebar.subheader("數據管理")
    uploaded_file = st.sidebar.file_uploader("匯入志工 CSV", type="csv")
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        df = pd.concat([df, new_df]).drop_duplicates(subset=["電話"], keep="last")
        df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.sidebar.success("資料已匯入！")

    # --- 主介面 ---
    st.title("📋 志工池經營看板")
    
    # 篩選器
    col1, col2 = st.columns(2)
    with col1:
        search_name = st.text_input("搜尋姓名")
    with col2:
        min_trust = st.slider("最低信任度篩選", 0.0, 5.0, 0.0)

    # 過濾資料
    display_df = df.copy()
    if search_name:
        display_df = display_df[display_df["姓名"].str.contains(search_name)]
    display_df = display_df[display_df["信任度"] >= min_trust]

    # 顯示表格與 Line 按鈕
    st.subheader(f"目前志工名單 ({len(display_df)} 人)")
    
    # 使用 Streamlit Data Editor 讓主辦方可以直接在網頁修改
    edited_df = st.data_editor(display_df, use_container_width=True, num_rows="dynamic")
    
    if st.button("儲存修改"):
        df.update(edited_df)
        df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("資料已儲存！")

    st.divider()
    
    # 快速聯絡區塊
    st.subheader("📢 快速聯絡")
    contact_cols = st.columns(4)
    for i, row in display_df.iterrows():
        with contact_cols[i % 4]:
            st.write(f"**{row['姓名']}**")
            line_id = str(row['Line ID'])
            if line_id != "nan":
                st.link_button(f"與 {row['姓名']} 對話", f"https://line.me/R/ti/p/~{line_id}")
            else:
                st.caption("未提供 Line ID")
