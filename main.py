import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池經營看板", layout="wide", initial_sidebar_state="expanded")

# 2. 修正後的 CSS (修復 unsafe_allow_html 報錯)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .volunteer-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# 3. 登入邏輯
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

# 4. 資料載入 (確保初次開啟就有資料)
DB_FILE = "volunteer_data.csv"
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # 建立預設模擬資料
    data = {
        "姓名": ["陳小明", "林雅婷", "王大衛", "李美美"],
        "電話": ["0912-345-678", "0922-111-222", "0933-888-999", "0955-666-777"],
        "Line ID": ["ming_chen", "yating_lin", "david_w", "meimei_lee"],
        "服務時段": ["週末早", "平日晚", "週末全天", "平日午"],
        "引導": [5, 3, 4, 2], "行政": [3, 5, 2, 4], "體力": [4, 2, 5, 1], "應變": [2, 4, 3, 5],
        "準時率": ["95%", "98%", "90%", "100%"], "信任度": [4.5, 4.8, 3.9, 4.9], 
        "評價備註": ["表現優異", "細心負責", "體力好", "應變快"]
    }
    df_init = pd.DataFrame(data)
    df_init.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
    return df_init

df = load_data()

# 5. 側邊欄導覽
st.sidebar.title(" 志工池管理")
menu = st.sidebar.radio("功能選單", ["📊 經營儀表板", "👥 志工搜尋", "📥 資料匯入"])

if st.sidebar.button("安全登出"):
    st.session_state.authenticated = False
    st.rerun()

# --- 分頁 1：經營儀表板 ---
if menu == "📊 經營儀表板":
    st.title("📊 經營儀表板")
    st.caption("即時掌握志工池健康度與人力分佈")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("總志工人數", len(df))
    m2.metric("平均信任度", f"{df['信任度'].mean():.1f} ⭐")
    m3.metric("高信任比例", "75%", "優質池")
    m4.metric("本月服務人次", "128 次", "+12")
    
    st.divider()
    st.subheader("能力分佈概況")
    skills = ["引導", "行政", "體力", "應變"]
    avg_skills = [df[s].mean() for s in skills]
    chart_data = pd.DataFrame({"能力專長": skills, "平均等級": avg_skills})
    st.bar_chart(chart_data, x="能力專長", y="平均等級", color="#6366f1")

# --- 分頁 2：志工搜尋 ---
elif menu == "👥 志工搜尋":
    st.title("👥 志工搜尋器")
    
    search_q = st.text_input("🔍 搜尋姓名或電話...", placeholder="例如：陳小明")
    f_df = df[df["姓名"].str.contains(search_q) | df["電話"].str.contains(search_q)] if search_q else df
    
    st.write(f"目前名單：{len(f_df)} 人")
    
    # 志工卡片 (雙欄顯示)
    for i in range(0, len(f_df), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(f_df):
                row = f_df.iloc[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(f"{row['姓名']} ⭐")
                        st.write(f"📞 {row['電話']} | 💬 ID: {row['Line ID']}")
                        st.write(f"**能力：** 引導 Lv.{row['引導']} | 體力 Lv.{row['體力']}")
                        st.write(f"**時段：** {row['服務時段']}")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        btn_col1.link_button("🟢 聯絡志工", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)
                        btn_col2.button("➕ 新增紀錄", key=f"rec_{i+j}", use_container_width=True)

# --- 分頁 3：資料匯入 ---
elif menu == "📥 資料匯入":
    st.title("📥 批次匯入志工")
    up_file = st.file_uploader("請上傳 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("🎉 資料匯入成功！請前往搜尋分頁查看結果。")
