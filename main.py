import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="志工池管理經營看板", layout="wide")

# --- 登入邏輯 (保持不變) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 登入管理後台")
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("進入系統"):
        if pwd == "volunteer2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 資料處理 ---
DB_FILE = "volunteer_data.csv"
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "評價備註"])

df = load_data()

# --- 介面設計 ---
st.title("📋 志工池經營看板")

# 側邊欄：功能選單
with st.sidebar:
    st.header("數據管理")
    uploaded_file = st.file_uploader("匯入 CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("匯入成功！")
    
    if st.button("登出"):
        st.session_state.authenticated = False
        st.rerun()

# 核心功能：志工搜尋器
st.subheader("🔍 志工搜尋器")
c1, c2, c3 = st.columns([2, 2, 3])
with c1:
    search_q = st.text_input("搜尋姓名或電話")
with c2:
    target_skill = st.selectbox("核心能力篩選", ["全部", "引導", "行政", "體力", "應變"])
with c3:
    min_score = st.slider("最低能力評分 (1-5)", 1, 5, 1)

# 過濾邏輯
filtered_df = df.copy()
if search_q:
    filtered_df = filtered_df[filtered_df["姓名"].str.contains(search_q) | filtered_df["電話"].str.contains(search_q)]
if target_skill != "全部":
    filtered_df = filtered_df[filtered_df[target_skill] >= min_score]

# 顯示數據表格
st.write(f"📊 符合篩選條件： {len(filtered_df)} 人")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# 關鍵：快速聯絡按鈕區塊 (與 TypeScript 版風格對齊)
st.subheader("📢 快速聯絡卡片")
if len(filtered_df) > 0:
    # 每列顯示 2 個卡片
    cols = st.columns(2)
    for idx, row in filtered_df.iterrows():
        with cols[idx % 2]:
            with st.container(border=True):
                st.write(f"### {row['姓名']} ⭐")
                st.write(f"📞 {row['電話']} | 💬 ID: {row['Line ID']}")
                st.write(f"💪 能力值：引導 Lv.{row['引導']} | 體力 Lv.{row['體力']}")
                
                # Line 按鈕
                line_url = f"https://line.me/R/ti/p/~{row['Line ID']}"
                st.link_button(f"🟢 聯絡 {row['姓名']}", line_url, use_container_width=True)
else:
    st.warning("目前沒有符合條件的志工，請嘗試調整篩選條件或匯入資料。")
