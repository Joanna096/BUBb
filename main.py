import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池管理系統", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS 樣式優化
st.markdown("""
    <style>
    .main { background-color: #f9fafb; }
    h1, h2, h3 { font-weight: 800 !important; color: #111827 !important; }
    [data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e5e7eb; }
    
    /* 聯絡狀態標籤樣式 */
    .status-tag { padding: 4px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
    .status-none { background-color: #f3f4f6; color: #374151; }       /* 未聯絡 */
    .status-pending { background-color: #fffbeb; color: #d97706; }    /* 已聯絡未回覆 */
    .status-done { background-color: #f0fdf4; color: #16a34a; }       /* 已聯絡已回覆 */
    
    /* 能力標籤樣式 */
    .skill-pill { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-right: 5px; margin-bottom: 5px; }
    .skill-guide { background-color: #e0f2fe; color: #0369a1; }
    .skill-admin { background-color: #fef2f2; color: #b91c1c; }
    .skill-power { background-color: #fefce8; color: #a16207; }
    .skill-react { background-color: #f0fdfa; color: #0f766e; }
    
    .seniority-pill { background-color: #eff6ff; color: #1d4ed8; padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 3. 資料核心處理
DB_FILE = "volunteer_data.csv"

def refresh_data():
    st.cache_data.clear()
    st.rerun()

@st.cache_data
def load_data():
    required_fields = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "資歷年份", "邀請狀態"]
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            df.columns = [c.strip() for c in df.columns]
            for field in required_fields:
                if field not in df.columns:
                    df[field] = 0 if field in ["引導", "行政", "體力", "應變", "信任度", "資歷年份", "準時率"] else "未聯絡"
            return df
        except:
            return pd.DataFrame(columns=required_fields)
    return pd.DataFrame(columns=required_fields)

df = load_data()

# 4. 頂部儀表板
st.markdown("# **志工池管理系統**")
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("**總志工人數**", f"{len(df)} 人")
with m2:
    p_count = len(df[df["邀請狀態"] == "已聯絡未回覆"])
    st.metric("**等待回覆中**", f"{p_count} 筆")
with m3:
    d_count = len(df[df["邀請狀態"] == "已聯絡已回覆"])
    st.metric("**已確認參加**", f"{d_count} 筆")
with m4:
    avg_t = pd.to_numeric(df["信任度"], errors='coerce').mean()
    st.metric("**平均信任度**", f"{avg_t:.1f} 分")

st.divider()

# 5. 功能分頁
tab1, tab2 = st.tabs(["名單篩選與管理", "批次資料匯入"])

with tab1:
    # 搜尋與能力篩選
    c_s1, c_s2 = st.columns([2, 2])
    with c_s1:
        search_q = st.text_input("搜尋姓名或電話", placeholder="輸入關鍵字...")
    with c_s2:
        selected_skills = st.multiselect("依能力指標篩選", ["引導", "行政", "體力", "應變"])

    # 聯絡狀態過濾
    status_choice = st.radio("聯絡狀態過濾", ["全部", "未聯絡", "已聯絡未回覆", "已聯絡已回覆"], horizontal=True)

    # 執行篩選
    display_df = df.copy()
    if status_choice != "全部":
        display_df = display_df[display_df["邀請狀態"] == status_choice]
    if search_q:
        display_df = display_df[display_df["姓名"].str.contains(search_q, na=False) | display_df["電話"].str.contains(search_q, na=False)]
    if selected_skills:
        for sk in selected_skills:
            display_df = display_df[pd.to_numeric(display_df[sk], errors='coerce') > 0]

    st.markdown(f"找到 **{len(display_df)}** 位符合條件的志工")

    # 志工卡片列表
    for idx, row in display_df.iterrows():
        with st.container(border=True):
            card_c1, card_c2, card_c3 = st.columns([2.5, 2, 1.2])
            
            with card_c1:
                st.markdown(f"### **{row['姓名']}** <span class='seniority-pill'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                
                # 動態生成能力標籤 HTML (修復 SyntaxError)
                skill_html = ""
                if pd.to_numeric(row['引導'], errors='coerce') > 0:
                    skill_html += f"<span class='skill-pill skill-guide'>引導 Lv.{row['引導']}</span>"
                if pd.to_numeric(row['行政'], errors='coerce') > 0:
                    skill_html += f"<span class='skill-pill skill-admin'>行政 Lv.{row['行政']}</span>"
                if pd.to_numeric(row['體力'], errors='coerce') > 0:
                    skill_html += f"<span class='skill-pill skill-power'>體力 Lv.{row['體力']}</span>"
                if pd.to_numeric(row['應變'], errors='coerce') > 0:
                    skill_html += f"<span class='skill-pill skill-react'>應變 Lv.{row['應變']}</span>"
                st.markdown(skill_html, unsafe_allow_html=True)
                
                st.caption(f"電話: {row['電話']} | ID: {row['Line ID']}")
            
            with card_c2:
                status = row["邀請狀態"]
                cls = "status-none" if status == "未聯絡" else "status-pending" if status == "已聯絡未回覆" else "status-done"
                st.markdown(f"狀態：<span class='status-tag {cls}'>{status}</span>", unsafe_allow_html=True)
                st.write(f"時段: {row['服務時段']}")
            
            with card_c3:
                # 狀態切換選單
                st_list = ["未聯絡", "已聯絡未回覆", "已聯絡已回覆"]
                current_idx = st_list.index(status) if status in st_list else 0
                new_status = st.selectbox("變更狀態", st_list, index=current_idx, key=f"sel_{idx}")
                
                if new_status != status:
                    df.at[idx, "邀請狀態"] = new_status
                    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
                    refresh_data()
                
                st.link_button("🟢 Line 聯絡", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)

with tab2:
    st.markdown("### **批次匯入 CSV 檔案**")
    st.write("請確保 CSV 欄位名稱包含：姓名、電話、Line ID、引導、行政、體力、應變、資歷年份、邀請狀態等。")
    up_file = st.file_uploader("選擇 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("資料匯入成功！")
        if st.button("立即刷新看板數據"):
            refresh_data()
