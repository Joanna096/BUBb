import pandas as pd
import random

# 定義隨機資料範圍
names = ["張", "林", "王", "李", "陳", "趙", "黃", "周", "吳", "徐"]
given_names = ["大明", "小花", "志強", "美玲", "阿和", "淑芬", "俊傑", "雅婷", "家豪", "怡君"]
periods = ["平日", "週末", "平日/週末"]
times = ["早", "中", "晚", "早/中", "中/晚", "全天"]

data = []
for i in range(100):
    name = random.choice(names) + random.choice(given_names)
    phone = f"09{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(100, 999)}"
    line_id = f"user_{random.randint(1000, 9999)}"
    service_time = f"{random.choice(periods)}({random.choice(times)})"
    
    # 能力標籤與指標 (1-5分)
    guidance = random.randint(1, 5)
    admin = random.randint(1, 5)
    strength = random.randint(1, 5)
    reaction = random.randint(1, 5)
    
    on_time_rate = f"{random.randint(70, 100)}%"
    trust_score = round(random.uniform(3.0, 5.0), 1)
    
    data.append([
        name, phone, line_id, service_time, 
        guidance, admin, strength, reaction, 
        on_time_rate, trust_score, "模擬測試資料", "活動A/角色B/2024-01-01"
    ])

# 轉換為 DataFrame 並儲存
df = pd.DataFrame(data, columns=[
    "姓名", "電話", "Line ID", "服務時段", 
    "引導", "行政", "體力", "應變", 
    "準時率", "信任度", "評價備註", "參與歷程"
])

df.to_csv("volunteer_100.csv", index=False, encoding="utf-8-sig")
print("成功生成 100 筆資料：volunteer_100.csv")
