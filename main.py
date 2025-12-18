import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池經營系統", layout="wide", initial_sidebar_state="expanded")

# 2. 簡潔樣式設定 (確保指標文字清晰可見)
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: #333333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 登入邏輯
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## **管理系統登入**")
    pwd = st.text_input("輸入管理員密碼", type="password")
    if st.button("登入", use_container_width=True):
        if pwd == "volunteer2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# 4. 資料處理核心 (解決匯入與欄位問題)
DB_FILE = "volunteer_data.csv"

@st.cache_data
def load_data():
    if os.path.exists(DB_FILE):
        try:
            temp_df = pd.read_csv(DB_FILE)
            temp_df.columns = [c.strip() for c in temp_df.columns]
            # 確保必要欄位存在
            req_cols = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度"]
            for col in req_cols:
                if col not in temp_df.columns:
                    temp_df[col] = 0 if col in ["引導", "行政", "體力", "應變", "信任度"] else "無"
            return temp_df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

# 5. 側邊導覽 (消除 Emoji)
st.sidebar.markdown("### **功能選單**")
menu = st.sidebar.radio("跳轉至", ["經營儀表板", "志工搜尋器", "批次匯入資料"])

if st.sidebar.button("安全登出"):
    st.session_state.authenticated = False
    st.rerun()

# --- 分頁 1：經營儀表板 ---
if menu == "經營儀表板":
    st.markdown("# **經營儀表板**")
    
    if not df.empty:
        # 指標列
        m1, m2, m3, m4 = st.columns(4)
        
        # 總人數
        total_count = len(df)
        m1.metric(label="總志工人數", value=f"{total_count} 人")
        
        # 平均信任度 (轉換數字確保顯示)
        trust_val = pd.to_numeric(df["信任度"], errors='coerce').mean()
        m2.metric(label="平均信任度", value=f"{trust_val:.1f} 分")
        
        # 服務時段統計
        weekend_count = len(df[df["服務時段"].str.contains("週末", na=False)])
        m3.metric(label="週末可出勤人數", value=f"{weekend_count} 人")
        
        # 高標比例
        high_trust = len(df[pd.to_numeric(df["信任度"], errors='coerce') >= 4.5])
        m4.metric(label="優秀志工筆數", value=f"{high_trust} 筆")
        
        st.divider()
        
        # 核心能力分佈 (改為橫條圖)
        st.markdown("### **核心能力平均分佈**")
        skills = ["引導", "行政", "體力", "應變"]
        avg_values = [pd.to_numeric(df[s], errors='coerce').mean() for s in skills]
        
        chart_data = pd.DataFrame({
            "能力項目": skills,
            "平均分數": avg_values
        }).sort_values("平均分數", ascending=True)
        
        # 使用 st.bar_chart 但透過 DataFrame 轉置概念或指定橫向
        # 在 Streamlit 中，最簡單的橫條圖是使用 st.altair_chart 或轉化資料
        st.bar_chart(chart_data, x="平均分數", y="能力項目", color="#4F46E5")
    else:
        st.warning("目前無資料，請先前往批次匯入進行上傳。")

# --- 分頁 2：志工搜尋器 ---
elif menu == "志工搜尋器":
    st.markdown("# **志工搜尋器**")
    search_q = st.text_input("搜尋關鍵字 (姓名或電話)")
    
    if not df.empty:
        f_df = df[df["姓名"].str.contains(search_q, na=False) | df["電話"].str.contains(search_q, na=False)] if search_q else df
        st.markdown(f"找到 **{len(f_df)}** 位符合條件的志工")
        st.dataframe(f_df, use_container_width=True)
    else:
        st.info("請先匯入資料")

# --- 分頁 3：批次匯入 (解決無法更新問題) ---
elif menu == "批次匯入資料":
    st.markdown("# **批次匯入資料**")
    st.markdown("請上傳格式正確的 CSV 檔案。上傳後系統將自動覆蓋舊有資料庫。")
    
    up_file = st.file_uploader("選擇 CSV 檔案", type="csv")
    
    if up_file:
        try:
            new_df = pd.read_csv(up_file)
            # 儲存檔案
            new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
            
            # 重要：清除快取，否則儀表板會一直顯示舊資料
            st.cache_data.clear()
            
            st.success("資料已成功更新！現在請切換回「經營儀表板」查看最新結果。")
            if st.button("立即刷新畫面"):
                st.rerun()
        except Exception as e:
            st.error(f"上傳發生錯誤: {e}")
