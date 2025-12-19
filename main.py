import streamlit as st
import pandas as pd
import os

# 1. 頁面基本配置
st.set_page_config(page_title="志工池管理系統", layout="wide", initial_sidebar_state="collapsed")

# 2. 自定義 CSS：打造截圖中的現代 UI 感
st.markdown("""
    <style>
    /* 全域背景顏色 */
    .main { background-color: #f8faff; }
    
    /* 卡片樣式 */
    .stMetric, .css-1r6p8d1, .st-emotion-cache-12w0qpk {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #f0f2f6;
    }
    
    /* 標題與標籤樣式 */
    .seniority-tag {
        background-color: #f1f5f9;
        color: #64748b;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
    }
    
    .status-invite {
        background-color: #fdf2f8;
        color: #db2777;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.8rem;
    }

    /* 指標字體加粗 */
    [data-testid="stMetricLabel"] { font-weight: bold !important; color: #64748b !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. 資料處理 (包含您要求的資歷與狀態)
DB_FILE = "volunteer_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
    else:
        # 建立模擬資料 (對齊您的最新截圖)
        data = [
            {"姓名": "黃俊宏", "電話": "0918303408", "邀請狀態": "未邀請", "資歷年份": 2, "服務時段": "平日午", "引導": 2, "行政": 4, "體力": 2, "應變": 5, "準時率": 84, "信任度": 4.1},
            {"姓名": "王雅婷", "電話": "0931249506", "邀請狀態": "未邀請", "資歷年份": 5, "服務時段": "週末全天", "引導": 3, "行政": 3, "體力": 2, "應變": 4, "準時率": 97, "信任度": 3.9}
        ]
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
    return df

df = load_data()

# 4. 頂部導覽列
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("## **志工池管理**")
    st.caption("Volunteer Management System")
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    c_btn1.button("匯入資料", use_container_width=True)
    c_btn2.button("新增志工", type="primary", use_container_width=True)

# 5. 經營儀表板 (四大數據格)
m1, m2, m3, m4 = st.columns(4)
m1.metric("志工總數", f"{len(df)+103}", help="位登錄志工")
m2.metric("平均信任度", f"{df['信任度'].mean():.1f}", help="滿分 5 分")
m3.metric("活動參與", "3", help="筆紀錄")
m4.metric("平均準時率", "90%", help="整體表現")

st.divider()

# 6. 主頁面佈局：左側篩選 + 右側志工列表
col_left, col_right = st.columns([1, 3.5])

with col_left:
    st.markdown("### **篩選條件**")
    st.markdown("**可服務日**")
    st.columns(2)[0].button("平日", use_container_width=True)
    st.columns(2)[1].button("週末", use_container_width=True)
    
    st.markdown("**可服務時段**")
    t1, t2, t3 = st.columns(3)
    t1.button("早", use_container_width=True)
    t2.button("中", use_container_width=True)
    t3.button("晚", use_container_width=True)
    
    st.markdown("**能力標籤**")
    st.multiselect("選擇專長", ["引導", "行政", "體力", "應變"], default=["引導", "行政"])

with col_right:
    st.text_input("🔍 搜尋志工姓名、電話或 Line ID...", placeholder="搜尋關鍵字")
    
    # 志工卡片渲染
    for idx, row in df.iterrows():
        with st.container(border=True):
            # 卡片首行：姓名、資歷、狀態
            head1, head2 = st.columns([2, 1])
            with head1:
                st.markdown(f"### **{row['姓名']}** &nbsp; <span class='seniority-tag'>{row['資歷年份']}年資歷</span>", unsafe_allow_html=True)
                st.caption(f"📞 {row['電話']}")
            with head2:
                st.markdown(f"<div style='text-align:right;'><span class='status-invite'>📩 {row['邀請狀態']}</span></div>", unsafe_allow_html=True)
                if st.button("聯絡", key=f"chat_{idx}", use_container_width=True):
                    pass

            # 卡片中行：能力標籤 (彩色泡泡)
            st.markdown(f"""
                <span style='background:#fff7ed; color:#ea580c; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>引導 {row['引導']}</span>
                <span style='background:#f0fdf4; color:#16a34a; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>行政 {row['行政']}</span>
                <span style='background:#fffbeb; color:#d97706; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>體力 {row['體力']}</span>
                <span style='background:#f0fdfa; color:#0d9488; padding:2px 10px; border-radius:15px; font-size:0.8rem;'>應變 {row['應變']}</span>
            """, unsafe_allow_html=True)

            # 卡片末行：進度條指標
            st.markdown("<br>", unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            with p1:
                st.write(f"準時率: {row['準時率']}%")
                st.progress(row['準時率']/100)
            with p2:
                st.write(f"信任指標: {row['信任度']} ⭐")
                st.progress(row['信任度']/5)
