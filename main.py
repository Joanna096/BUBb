import streamlit as st
import pandas as pd
import os

# 1. 頁面配置
st.set_page_config(page_title="志工池經營看板", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 優化 (美化儀表板卡片)
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    [data-testid="stMetricValue"] { color: #6366f1; }
    </style>
    """, unsafe_allow_html=True)

# 3. 登入邏輯
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🛡️ 志工池管理系統")
    pwd = st.text_input("管理員密碼", type="password")
    if st.button("登入系統", use_container_width=True):
        if pwd == "volunteer2025":
            st.session_state.authenticated = True
            st.rerun()
    st.stop()

# 4. 資料載入與欄位自動對齊 (核心修復邏輯)
DB_FILE = "volunteer_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            temp_df = pd.read_csv(DB_FILE)
            # 修復欄位名稱可能的空格問題
            temp_df.columns = [c.strip() for c in temp_df.columns]
            
            # 檢查並補全缺失欄位，防止 KeyError
            required_cols = ["姓名", "電話", "Line ID", "服務時段", "引導", "行政", "體力", "應變", "準時率", "信任度", "評價備註"]
            for col in required_cols:
                if col not in temp_df.columns:
                    # 數字型欄位補 0，文字型補 "未提供"
                    temp_df[col] = 0 if col in ["引導", "行政", "體力", "應變", "信任度"] else "未提供"
            return temp_df
        except Exception as e:
            st.error(f"資料讀取錯誤: {e}")
            
    # 若檔案不存在，生成 100 筆模擬資料供測試
    import random
    data = []
    names = ["張", "林", "王", "李", "陳", "黃", "周", "吳"]
    last_names = ["大明", "小花", "志強", "美玲", "阿和", "淑芬"]
    for i in range(100):
        data.append({
            "姓名": random.choice(names) + random.choice(last_names),
            "電話": f"0912-{random.randint(100,999)}-{random.randint(100,999)}",
            "Line ID": f"id_{random.randint(1000,9999)}",
            "服務時段": random.choice(["平日", "週末", "全天"]),
            "引導": random.randint(1,5), "行政": random.randint(1,5), 
            "體力": random.randint(1,5), "應變": random.randint(1,5),
            "準時率": f"{random.randint(80,100)}%", "信任度": round(random.uniform(3.0, 5.0), 1),
            "評價備註": "系統自動生成"
        })
    df_init = pd.DataFrame(data)
    df_init.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
    return df_init

df = load_data()

# 5. 側邊欄與導覽
st.sidebar.title("💜 志工池管理")
menu = st.sidebar.radio("功能選單", ["📊 經營儀表板", "👥 志工搜尋器", "📥 批次匯入"])

if st.sidebar.button("安全登出"):
    st.session_state.authenticated = False
    st.rerun()

# --- 分頁：經營儀表板 ---
if menu == "📊 經營儀表板":
    st.title("📊 經營儀表板")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("總志工人數", len(df))
    # 安全計算平均信任度
    avg_trust = pd.to_numeric(df["信任度"], errors='coerce').mean()
    m2.metric("平均信任度", f"{avg_trust:.1f} ⭐")
    m3.metric("高信任比例", "75%", "維持高標")
    m4.metric("本月服務人次", "128 次")
    
    st.divider()
    st.subheader("核心能力分佈")
    skills = ["引導", "行政", "體力", "應變"]
    avg_skills = [pd.to_numeric(df[s], errors='coerce').mean() for s in skills]
    st.bar_chart(pd.DataFrame({"能力": skills, "平均等級": avg_skills}), x="能力", y="平均等級", color="#6366f1")

# --- 分頁：志工搜尋器 ---
elif menu == "👥 志工搜尋器":
    st.title("👥 志工搜尋器")
    search_q = st.text_input("🔍 搜尋姓名或電話")
    f_df = df[df["姓名"].str.contains(search_q) | df["電話"].str.contains(search_q)] if search_q else df
    
    for i in range(0, len(f_df), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(f_df):
                row = f_df.iloc[i + j]
                with cols[j]:
                    with st.container(border=True):
                        st.subheader(f"{row['姓名']} ⭐")
                        st.write(f"📞 {row['電話']} | 💬 Line ID: {row['Line ID']}")
                        st.write(f"**能力：** 引導 Lv.{row['引導']} | 體力 Lv.{row['體力']}")
                        st.link_button(f"🟢 聯絡 {row['姓名']}", f"https://line.me/R/ti/p/~{row['Line ID']}", use_container_width=True)

# --- 分頁：資料匯入 ---
elif menu == "📥 批次匯入":
    st.title("📥 批次匯入")
    up_file = st.file_uploader("上傳 CSV 檔案", type="csv")
    if up_file:
        new_df = pd.read_csv(up_file)
        new_df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")
        st.success("匯入成功！請點擊儀表板查看更新。")
     
