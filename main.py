import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. 頁面配置
st.set_page_config(page_title="志工池經營系統", layout="wide", initial_sidebar_state="expanded")

# 2. 簡潔樣式
st.markdown("""
    <style>
    [data-testid="stMetric"] { background-color: #f8f9fa; padding: 20px; border-radius: 8px; border: 1px solid #dee2e6; }
    .status-tag { padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .seniority-tag { background-color: #e0e7ff; color: #4338ca; padding: 2px 8px; border-radius: 20px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. 登入邏輯
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("# **管理系統登入**")
    pwd = st.text_input("輸入管理員密碼", type="password")
    if st.button("登入", use_container_width=True):
        if pwd == "volunteer2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# 4. 資料處理核心
DB_FILE = "volunteer_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            temp_df = pd.read_csv(DB_FILE)
            temp_df.columns = [c.strip() for c in temp_df.columns]
            
            # --- 新增功能：檢查並補足新欄位 ---
            new_required_cols = {
                "邀請狀態": "未邀請", 
                "資歷年份": 1,
                "姓名": "無", "電話": "無", "Line ID": "無", "服務時段": "無",
                "引導": 0, "行政": 0, "體力": 0, "應變": 0, "信任度": 0
            }
            for col, default in new_required_cols.items():
                if col not in temp_df.columns:
                    temp_df[col] = default
            return temp_df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

# 儲存資料的函式
def save_data(df_to_save):
    df_to_save.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
    st.cache_data.clear()

df = load_data()

# 5. 側邊導覽
st.sidebar.markdown("### **功能選單**")
menu = st.sidebar.radio("跳轉至", ["經營儀表板", "志工搜尋器", "批次匯入資料"])

# --- 分頁 1：經營儀表板 ---
if menu == "經營儀表板":
    st.markdown("# **經營儀表板**")
    if not df.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("總志工人數", f"{len(df)} 人")
        m2.metric("待回覆邀請", len(df[df["邀請狀態"] == "已邀請未回覆"]))
        m3.metric("已確認參與", len(df[df["邀請狀態"] == "已邀請已回覆"]))
        m4.metric("平均資歷", f"{df['資歷年份'].mean():.1f} 年")
        
        st.divider()
        st.markdown("### **能力與資歷分佈**")
        # 橫條圖：顯示平均能力
        skills = ["引導", "行政", "體力", "應變"]
        avg_values = [pd.to_numeric(df[s], errors='coerce').mean() for s in skills]
        chart_data = pd.DataFrame({"能力項目": skills, "平均分數": avg_values})
        st.bar_chart(chart_data, x="平均分數", y="能力項目", color="#4F46E5")

# --- 分頁 2：志工搜尋器 (新增標籤功能) ---
elif menu == "志工搜尋器":
    st.markdown("# **志工搜尋器**")
    
    # 搜尋與篩選列
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        search_q = st.text_input("搜尋姓名或電話")
    with col_s2:
        status_filter = st.selectbox("邀請狀態篩選", ["全部", "未邀請", "已邀請未回覆", "已邀請已回覆"])

    if not df.empty:
        # 執行過濾
        f_df = df.copy()
        if search_q:
            f_df = f_df[f_df["姓名"].str.contains(search_q, na=False) | f_df["電話"].str.contains(search_q, na=False)]
        if status_filter != "全部":
            f_df = f_df[f_df["邀請狀態"] == status_filter]

        st.markdown(f"找到 **{len(f_df)}** 位志工")

        # 以卡片形式顯示 (新增標籤顯示)
        for idx, row in f_df.iterrows():
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 1.5])
                
                with c1:
                    # 顯示姓名與資歷標籤
                    st.markdown(f"### **{row['姓名']}** <span class='seniority-tag'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                    st.write(f"📞 {row['電話']} | 💬 ID: {row['Line ID']}")
                
                with c2:
                    # 顯示狀態標籤
                    status = row["邀請狀態"]
                    color = "#6b7280" if status == "未邀請" else "#f59e0b" if status == "已邀請未回覆" else "#10b981"
                    st.markdown(f"狀態：<span style='color:{color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
                    st.write(f"能力：引導 {row['引導']} | 行政 {row['行政']}")

                with c3:
                    # 狀態切換按鈕
                    new_status = st.selectbox("更改狀態", ["未邀請", "已邀請未回覆", "已邀請已回覆"], index=["未邀請", "已邀請未回覆", "已邀請已回覆"].index(status), key=f"status_{idx}")
                    if new_status != status:
                        df.at[idx, "邀請狀態"] = new_status
                        save_data(df)
                        st.rerun()
                    
                    st.link_button("🟢 Line 聯絡", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)

# --- 分頁 3：批次匯入 ---
elif menu == "批次匯入資料":
    st.markdown("# **批次匯入資料**")
    up_file = st.file_uploader("選擇 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.cache_data.clear()
        st.success("資料已成功更新！")
