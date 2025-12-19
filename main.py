import streamlit as st
import pandas as pd
import os

# 1. 頁面基本配置：關閉側邊欄以達到儀表板感
st.set_page_config(page_title="志工池管理系統", layout="wide", initial_sidebar_state="collapsed")

# 2. 自定義 CSS：打造截圖中的現代 UI (移除 Emoji，大標粗體)
st.markdown("""
    <style>
    .main { background-color: #f8faff; }
    [data-testid="stMetric"] { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    [data-testid="stMetricLabel"] { font-weight: bold !important; color: #64748b !important; font-size: 1.1rem !important; }
    .seniority-tag { background-color: #f1f5f9; color: #64748b; padding: 2px 10px; border-radius: 8px; font-size: 0.85rem; }
    .status-invite { background-color: #fdf2f8; color: #db2777; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; }
    h1, h2, h3 { font-weight: 800 !important; color: #1e293b !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 核心資料處理：加入自動修復功能防止 KeyError
DB_FILE = "volunteer_data.csv"

def load_data():
    # 定義所有必要欄位
    required_cols = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "資歷年份", "邀請狀態"]
    
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # 自動清理欄位名稱空格
            df.columns = [c.strip() for c in df.columns]
            # 檢查並補足缺失欄位
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0 if col in ["引導", "行政", "體力", "應變", "信任度", "資歷年份", "準時率"] else "未提供"
            return df
        except:
            pass
            
    # 若檔案不存在或損毀，生成初始化模擬資料
    data = [
        {"姓名": "黃俊宏", "電話": "0918303408", "邀請狀態": "未邀請", "資歷年份": 2, "服務時段": "平日午", "引導": 2, "行政": 4, "體力": 2, "應變": 5, "準時率": 84, "信任度": 4.1, "Line ID": "hj_hong"},
        {"姓名": "王雅婷", "電話": "0931249506", "邀請狀態": "已邀請未回覆", "資歷年份": 5, "服務時段": "週末全天", "引導": 3, "行政": 3, "體力": 2, "應變": 4, "準時率": 97, "信任度": 3.9, "Line ID": "yating_w"}
    ]
    df_init = pd.DataFrame(data)
    df_init.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
    return df_init

df = load_data()

# 4. 頂部大標與導覽
st.markdown("# **志工池管理**")
st.markdown("Volunteer Management System")

# 5. 經營儀表板：橫向四大格
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("**志工總數**", len(df), help="位登錄志工")
with m_col2:
    avg_trust = pd.to_numeric(df["信任度"], errors='coerce').mean()
    st.metric("**平均信任度**", f"{avg_trust:.1f}", help="滿分 5 分")
with m_col3:
    invite_count = len(df[df["邀請狀態"] != "未邀請"])
    st.metric("**活動參與**", invite_count, help="筆邀請紀錄")
with m_col4:
    avg_ontime = pd.to_numeric(df["準時率"], errors='coerce').mean()
    st.metric("**平均準時率**", f"{avg_ontime:.0f}%", help="整體表現")

st.divider()

# 6. 核心功能分頁佈局
col_filter, col_list = st.columns([1, 3.5])

with col_filter:
    st.markdown("### **篩選條件**")
    st.markdown("**可服務日**")
    day_cols = st.columns(2)
    day_cols[0].button("平日", use_container_width=True)
    day_cols[1].button("週末", use_container_width=True)
    
    st.markdown("**能力標籤**")
    st.multiselect("過濾技能", ["引導", "行政", "體力", "應變"], default=["引導", "行政"])

with col_list:
    search_q = st.text_input("搜尋關鍵字", placeholder="搜尋志工姓名、電話或 Line ID...")
    
    # 根據搜尋過濾
    display_df = df[df["姓名"].str.contains(search_q)] if search_q else df
    
    # 渲染志工卡片
    for idx, row in display_df.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"### **{row['姓名']}** &nbsp; <span class='seniority-tag'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                st.write(f"電話：{row['電話']} | 狀態：<span class='status-invite'>{row['邀請狀態']}</span>", unsafe_allow_html=True)
            with c2:
                # 聯絡與更新狀態
                st.link_button("🟢 聯絡", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)
                if st.button(f"設為已邀請", key=f"inv_{idx}"):
                    df.at[idx, "邀請狀態"] = "已邀請未回覆"
                    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
                    st.rerun()

            # 顯示能力標籤
            st.markdown(f"""
                <span style='background:#fff7ed; color:#ea580c; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>引導 {row['引導']}</span>
                <span style='background:#f0fdf4; color:#16a34a; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>行政 {row['行政']}</span>
                <span style='background:#fdf2f8; color:#db2777; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>應變 {row['應變']}</span>
            """, unsafe_allow_html=True)
            
            # 進度條指標
            p1, p2 = st.columns(2)
            p1.write(f"準時率: {row['準時率']}%")
            p1.progress(int(row['準時率']) / 100 if str(row['準時率']).isdigit() else 0.8)
            p2.write(f"信任指標: {row['信任度']} / 5.0")
            p2.progress(float(row['信任度']) / 5.0)
