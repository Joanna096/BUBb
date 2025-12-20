import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池管理系統", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 強力優化：解決大標不清楚與指標文字消失問題
st.markdown("""
    <style>
    /* 強制設定背景顏色與標題顏色，確保清晰 */
    .main { background-color: #f9fafb !important; }
    
    /* 大標題樣式：強制深色粗體 */
    .main-title { 
        font-size: 2.5rem !important; 
        font-weight: 800 !important; 
        color: #111827 !important; 
        margin-bottom: 20px;
        text-shadow: none !important;
    }
    
    /* 指標方塊 (Metrics) 優化：強制文字顯示 */
    [data-testid="stMetric"] {
        background-color: white !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
    }
    [data-testid="stMetricLabel"] { 
        font-weight: 700 !important; 
        color: #4b5563 !important; 
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] { 
        color: #111827 !important; 
        font-weight: 800 !important;
    }

    /* 三色狀態標籤 */
    .status-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; }
    .status-none { background-color: #f3f4f6; color: #374151; }       /* 未聯絡 - 灰 */
    .status-pending { background-color: #fffbeb; color: #d97706; }    /* 已聯絡未回覆 - 橘 */
    .status-done { background-color: #f0fdf4; color: #16a34a; }       /* 已聯絡已回覆 - 綠 */
    
    /* 能力標籤 Pills */
    .skill-pill { display: inline-block; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-right: 6px; margin-top: 5px; }
    .skill-guide { background-color: #e0f2fe; color: #0369a1; }
    .skill-admin { background-color: #fef2f2; color: #b91c1c; }
    .skill-power { background-color: #fefce8; color: #a16207; }
    .skill-react { background-color: #f0fdfa; color: #0f766e; }
    
    .seniority-pill { background-color: #eff6ff; color: #1d4ed8; padding: 2px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. 資料處理核心 (解決 KeyError 與匯入同步問題)
DB_FILE = "volunteer_data.csv"

def refresh_data():
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_data():
    req_fields = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "資歷年份", "邀請狀態"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df.columns = [c.strip() for c in df.columns]
            for field in req_fields:
                if field not in df.columns:
                    df[field] = 0 if field in ["引導", "行政", "體力", "應變", "信任度", "資歷年份", "準時率"] else "未聯絡"
            return df
        except:
            return pd.DataFrame(columns=req_fields)
    return pd.DataFrame(columns=req_fields)

df = load_data()

# 4. 頂部大標題與儀表板 (使用自定義 Class 解決不清楚問題)
st.markdown('<h1 class="main-title">志工池管理系統</h1>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="總志工人數", value=f"{len(df)} 人")
with m2:
    p_count = len(df[df["邀請狀態"] == "已聯絡未回覆"])
    st.metric(label="等待回覆中", value=f"{p_count} 筆")
with m3:
    d_count = len(df[df["邀請狀態"] == "已聯絡已回覆"])
    st.metric(label="已確認參加", value=f"{d_count} 筆")
with m4:
    # 確保信任度為數字，解決 nan 問題
    trust_series = pd.to_numeric(df["信任度"], errors='coerce').fillna(0)
    st.metric(label="平均信任度", value=f"{trust_series.mean():.1f} 分")

st.divider()

# 5. 分頁功能
tab1, tab2 = st.tabs(["名單篩選與管理", "批次資料匯入"])

with tab1:
    # 搜尋與篩選區
    c_s1, c_s2 = st.columns([2, 2])
    with c_s1:
        search_q = st.text_input("🔍 搜尋姓名或電話", placeholder="輸入關鍵字...")
    with c_s2:
        selected_skills = st.multiselect("依能力指標篩選", ["引導", "行政", "體力", "應變"])

    status_choice = st.radio("聯絡狀態過濾", ["全部", "未聯絡", "已聯絡未回覆", "已聯絡已回覆"], horizontal=True)

    # 執行過濾邏輯
    display_df = df.copy()
    if status_choice != "全部":
        display_df = display_df[display_df["邀請狀態"] == status_choice]
    if search_q:
        display_df = display_df[display_df["姓名"].str.contains(search_q, na=False) | display_df["電話"].str.contains(search_q, na=False)]
    if selected_skills:
        for sk in selected_skills:
            display_df = display_df[pd.to_numeric(display_df[sk], errors='coerce') > 0]

    st.markdown(f"找到 **{len(display_df)}** 位符合條件的志工")

    # 渲染志工卡片
    for idx, row in display_df.iterrows():
        with st.container(border=True):
            card_c1, card_c2, card_c3 = st.columns([2.5, 2, 1.2])
            
            with card_c1:
                st.markdown(f"### **{row['姓名']}** <span class='seniority-pill'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                
                # 修復後的標籤 HTML 邏輯
                skill_html = ""
                if pd.to_numeric(row['引導'], errors='coerce') > 0: skill_html += f"<span class='skill-pill skill-guide'>引導 Lv.{row['引導']}</span>"
                if pd.to_numeric(row['行政'], errors='coerce') > 0: skill_html += f"<span class='skill-pill skill-admin'>行政 Lv.{row['行政']}</span>"
                if pd.to_numeric(row['體力'], errors='coerce') > 0: skill_html += f"<span class='skill-pill skill-power'>體力 Lv.{row['體力']}</span>"
                if pd.to_numeric(row['應變'], errors='coerce') > 0: skill_html += f"<span class='skill-pill skill-react'>應變 Lv.{row['應變']}</span>"
                st.markdown(skill_html, unsafe_allow_html=True)
                st.caption(f"電話: {row['電話']} | ID: {row['Line ID']}")
            
            with card_c2:
                status = str(row["邀請狀態"])
                cls = "status-none" if status == "未聯絡" else "status-pending" if status == "已聯絡未回覆" else "status-done"
                st.markdown(f"狀態：<span class='status-tag {cls}'>{status}</span>", unsafe_allow_html=True)
                st.write(f"時段: {row['服務時段']}")
            
            with card_c3:
                st_list = ["未聯絡", "已聯絡未回覆", "已聯絡已回覆"]
                current_idx = st_list.index(status) if status in st_list else 0
                new_status = st.selectbox("更新狀態", st_list, index=current_idx, key=f"sel_{idx}")
                
                if new_status != status:
                    df.at[idx, "邀請狀態"] = new_status
                    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
                    refresh_data()
                
                st.link_button("🟢 Line 聯絡", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)

with tab2:
    st.markdown("### 批次匯入 CSV")
    st.warning("請確保 CSV 第一列包含正確標題。匯入後將覆蓋目前的資料庫。")
    up_file = st.file_uploader("選擇 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("✅ 資料已成功寫入！")
        if st.button("點擊重新整理看板"):
            refresh_data()
