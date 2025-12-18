import streamlit as st
import pandas as pd
import os

# 頁面配置
st.set_page_config(page_title="志工池經營看板", layout="wide", initial_sidebar_state="expanded")

# --- 自定義 CSS 讓介面更像 Replit 版 ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .volunteer-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_stdio=True)

# --- 登入邏輯 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🛡️ 志工池管理系統")
    pwd = st.text_input("請輸入管理員密碼", type="password")
    if st.button("登入系統", use_container_width=True):
        if pwd == "volunteer2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# --- 資料載入 ---
DB_FILE = "volunteer_data.csv"
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # 預設範例資料，確保初次開啟不空白
    data = {
        "姓名": ["陳小明", "林雅婷"],
        "電話": ["0912-345-678", "0922-444-555"],
        "Line ID": ["ming_chen", "yating_lin"],
        "服務時段": ["週末早、週末中", "平日晚、週末晚"],
        "引導": [5, 3], "行政": [3, 5], "體力": [3, 2], "應變": [2, 4],
        "準時率": ["95%", "98%"], "信任度": [4.5, 4.8], "評價備註": ["穩定可靠", "溝通強"]
    }
    return pd.DataFrame(data)

df = load_data()

# --- 側邊欄導覽 ---
st.sidebar.title("💜 志工池管理")
menu = st.sidebar.radio("選單", ["📊 經營儀表板", "👥 志工搜尋", "📥 資料匯入"])

if st.sidebar.button("登出"):
    st.session_state.authenticated = False
    st.rerun()

# --- 分頁 1：經營儀表板 ---
if menu == "📊 經營儀表板":
    st.title("📊 經營儀表板")
    st.caption("即時掌握志工池健康度與人力分佈")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("總志工人數", len(df), "+2% 本月")
    m2.metric("平均準時率", "92.5%", "維持高標")
    m3.metric("活躍參與者", int(len(df)*0.8), "80% 活躍率")
    m4.metric("總評價數", len(df)*15, "+5 新增")
    
    st.divider()
    st.subheader("能力分佈概況")
    # 模擬圓柱圖效果
    skills = ["引導", "行政", "體力", "應變"]
    avg_skills = [df[s].mean() for s in skills]
    chart_data = pd.DataFrame({"能力": skills, "平均等級": avg_skills})
    st.bar_chart(chart_data, x="能力", y="平均等級", color="#6366f1")

# --- 分頁 2：志工搜尋 ---
elif menu == "👥 志工搜尋":
    st.title("👥 志工搜尋器")
    st.caption("根據能力與時間篩選適合的人選")
    
    # 搜尋列
    search_q = st.text_input("🔍 搜尋姓名或電話...", placeholder="輸入關鍵字")
    
    # 過濾資料
    f_df = df[df["姓名"].str.contains(search_q)] if search_q else df
    
    st.write(f"總計：{len(f_df)} 人")
    
    # 志工卡片顯示 (一排兩格)
    for i in range(0, len(f_df), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(f_df):
                row = f_df.iloc[i + j]
                with cols[j]:
                    with st.container(border=True):
                        c1, c2 = st.columns([1, 3])
                        c1.write("👤") # 可換成頭像圖片
                        with c2:
                            st.subheader(f"{row['姓名']} ⭐")
                            st.caption(f"📞 {row['電話']} | 💬 {row['Line ID']}")
                        
                        st.divider()
                        st.write(f"**能力標籤**")
                        st.write(f"引導 Lv.{row['引導']} | 體力 Lv.{row['體力']}")
                        st.write(f"**可服務時段**")
                        st.write(row['服務時段'])
                        
                        l_col, r_col = st.columns(2)
                        l_col.link_button("💬 聯絡志工", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)
                        r_col.button(f"➕ 新增紀錄", key=f"btn_{i+j}", use_container_width=True)

# --- 分頁 3：資料匯入 ---
elif menu == "📥 資料匯入":
    st.title("📥 資料匯入")
    up_file = st.file_uploader("拖拽 CSV 檔案至此", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("資料匯入成功！請切換至搜尋分頁查看。")
