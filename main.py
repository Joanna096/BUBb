import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池管理系統", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 優化：將標題與指標文字改為白色
st.markdown("""
    <style>
    /* 設定深色背景，讓白色文字突出 */
    .main { background-color: #0e1117 !important; }
    
    /* 大標題樣式：改為純白色 */
    .main-title { 
        font-size: 2.8rem !important; 
        font-weight: 800 !important; 
        color: #ffffff !important; 
        margin-bottom: 10px;
        letter-spacing: -0.05rem;
    }
    
    /* 描述文字也設為淺灰色以維持對齊 */
    .sub-title {
        color: #a1a1aa !important;
        margin-bottom: 30px;
    }
    
    /* 指標方塊 (Metrics) 優化：文字改為白色 */
    [data-testid="stMetric"] {
        background-color: #1f2937 !important;
        padding: 25px !important;
        border-radius: 16px !important;
        border: 1px solid #374151 !important;
    }
    [data-testid="stMetricLabel"] { 
        font-weight: 700 !important; 
        color: #d1d5db !important; 
        font-size: 1.1rem !important;
    }
    [data-testid="stMetricValue"] { 
        color: #ffffff !important; 
        font-weight: 800 !important;
    }

    /* 狀態標籤 */
    .status-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; }
    .status-none { background-color: #374151; color: #d1d5db; }
    .status-pending { background-color: #78350f; color: #fde68a; }
    .status-done { background-color: #064e3b; color: #a7f3d0; }
    
    /* 能力標籤 */
    .skill-pill { display: inline-block; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-right: 6px; margin-top: 5px; }
    .skill-guide { background-color: #0c4a6e; color: #e0f2fe; }
    .skill-admin { background-color: #7f1d1d; color: #fee2e2; }
    .skill-power { background-color: #713f12; color: #fefce8; }
    .skill-react { background-color: #064e3b; color: #f0fdf4; }
    
    .seniority-pill { background-color: #1e3a8a; color: #dbeafe; padding: 2px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. 資料處理
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

# 4. 頂部大標題 (白色文字)
st.markdown('<h1 class="main-title">志工池管理系統</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Volunteer Management System</p>', unsafe_allow_html=True)

# 儀表板數據
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
    trust_series = pd.to_numeric(df["信任度"], errors='coerce').fillna(0)
    st.metric(label="平均信任度", value=f"{trust_series.mean():.1f} 分")

st.divider()

# 5. 分頁功能
tab1, tab2 = st.tabs(["名單篩選與管理", "批次資料匯入"])

with tab1:
    c_s1, c_s2 = st.columns([2, 2])
    with c_s1:
        search_q = st.text_input("🔍 搜尋姓名或電話")
    with c_s2:
        selected_skills = st.multiselect("依能力指標篩選", ["引導", "行政", "體力", "應變"])

    status_choice = st.radio("聯絡狀態過濾", ["全部", "未聯絡", "已聯絡未回覆", "已聯絡已回覆"], horizontal=True)

    display_df = df.copy()
    if status_choice != "全部":
        display_df = display_df[display_df["邀請狀態"] == status_choice]
    if search_q:
        display_df = display_df[display_df["姓名"].str.contains(search_q, na=False) | display_df["電話"].str.contains(search_q, na=False)]
    if selected_skills:
        for sk in selected_skills:
            display_df = display_df[pd.to_numeric(display_df[sk], errors='coerce') > 0]

    st.markdown(f"找到 **{len(display_df)}** 位符合條件的志工")

    for idx, row in display_df.iterrows():
        with st.container(border=True):
            card_c1, card_c2, card_c3 = st.columns([2.5, 2, 1.2])
            with card_c1:
                st.markdown(f"### **{row['姓名']}** <span class='seniority-pill'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
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
    up_file = st.file_uploader("選擇 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("✅ 資料已成功寫入！")
        if st.button("點擊重新整理看板"):
            refresh_data()
