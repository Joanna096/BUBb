import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池管理經營系統", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 優化：定義三種狀態的顏色標籤
st.markdown("""
    <style>
    .main { background-color: #f9fafb; }
    h1, h2, h3 { font-weight: 800 !important; color: #111827 !important; }
    [data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e5e7eb; }
    
    /* 狀態標籤顏色定義 */
    .status-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
    .status-none { background-color: #f3f4f6; color: #374151; }       /* 未聯絡 - 灰色 */
    .status-pending { background-color: #fffbeb; color: #d97706; }    /* 已聯絡未回覆 - 橘色 */
    .status-done { background-color: #f0fdf4; color: #16a34a; }       /* 已聯絡已回覆 - 綠色 */
    
    .seniority-pill { background-color: #eff6ff; color: #1d4ed8; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 3. 資料處理 (修復匯入更新與欄位問題)
DB_FILE = "volunteer_data.csv"

# 清除快取並重新載入
def refresh_data():
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_data():
    required_fields = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "資歷年份", "邀請狀態"]
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df.columns = [c.strip() for c in df.columns]
        for field in required_fields:
            if field not in df.columns:
                df[field] = 0 if field in ["引導", "行政", "體力", "應變", "信任度", "資歷年份", "準時率"] else "未聯絡"
        return df
    return pd.DataFrame(columns=required_fields)

df = load_data()

# 4. 頂部標題與儀表板
st.markdown("# **志工池管理系統**")
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("**總志工人數**", f"{len(df)} 人")
with col_m2:
    pending_count = len(df[df["邀請狀態"] == "已聯絡未回覆"])
    st.metric("**等待回覆中**", f"{pending_count} 筆")
with col_m3:
    done_count = len(df[df["邀請狀態"] == "已聯絡已回覆"])
    st.metric("**已確認參加**", f"{done_count} 筆")
with col_m4:
    avg_trust = pd.to_numeric(df["信任度"], errors='coerce').mean()
    st.metric("**平均信任度**", f"{avg_trust:.1f} 分")

st.divider()

# 5. 功能選單
tab1, tab2 = st.tabs(["👥 志工名單管理", "📥 批次匯入資料"])

# --- 分頁 1：志工名單 ---
with tab1:
    search_q = st.text_input("🔍 搜尋姓名或電話", placeholder="輸入關鍵字搜尋...")
    
    # 狀態篩選器
    status_choice = st.multiselect("顯示狀態", ["未聯絡", "已聯絡未回覆", "已聯絡已回覆"], default=["未聯絡", "已聯絡未回覆", "已聯絡已回覆"])
    
    display_df = df[df["邀請狀態"].isin(status_choice)]
    if search_q:
        display_df = display_df[display_df["姓名"].str.contains(search_q, na=False) | display_df["電話"].str.contains(search_q, na=False)]

    for idx, row in display_df.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            
            with c1:
                st.markdown(f"### **{row['姓名']}** <span class='seniority-pill'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                st.write(f"📞 {row['電話']} | 💬 ID: {row['Line ID']}")
            
            with c2:
                # 狀態與顏色邏輯
                status = row["邀請狀態"]
                cls = "status-none" if status == "未聯絡" else "status-pending" if status == "已聯絡未回覆" else "status-done"
                st.markdown(f"當前狀態：<span class='status-tag {cls}'>{status}</span>", unsafe_allow_html=True)
                st.write(f"服務偏好：{row['服務時段']}")
            
            with c3:
                # 狀態更新下拉選單
                new_status = st.selectbox("切換狀態", ["未聯絡", "已聯絡未回覆", "已聯絡已回覆"], 
                                          index=["未聯絡", "已聯絡未回覆", "已聯絡已回覆"].index(status), 
                                          key=f"status_select_{idx}")
                
                if new_status != status:
                    df.at[idx, "邀請狀態"] = new_status
                    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
                    refresh_data()
                
                st.link_button("🟢 線上聯絡", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)

# --- 分頁 2：匯入資料 (解決無法更新問題) ---
with tab2:
    st.markdown("### **批次匯入志工 CSV**")
    st.info("請確保 CSV 包含：姓名、電話、Line ID、資歷年份、邀請狀態 (可選)")
    up_file = st.file_uploader("選擇檔案", type="csv")
    
    if up_file:
        try:
            # 讀取並保存
            new_df = pd.read_csv(up_file)
            new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
            st.success("🎉 資料已成功寫入資料庫！")
            if st.button("點擊重新整理看板"):
                refresh_data()
        except Exception as e:
            st.error(f"匯入失敗，請檢查格式: {e}")
