import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. APP 設定與 Session State 初始化 ---
st.set_page_config(page_title="TabiFam 東京親子遊", page_icon="🇯🇵", layout="wide")

# 初始化記帳暫存區 (Session State)
if 'expenses' not in st.session_state:
    st.session_state['expenses'] = []

# --- 2. 自定義 CSS (手機版優化) ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .food-card { 
        background-color: #fff3e0; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        border-left: 5px solid #ff9800; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心數據 (含美食座標) ---
# 注意：為了演示，美食座標是基於主地點做的微調模擬
itinerary_data = {
    "Day 1 (2/28 五)": {
        "title": "抵達與台場散策",
        "stay": "MIMARU 東京 八丁堀",
        "loc": [35.6748, 139.7803], # 飯店位置
        "food": [
            {"name": "Bills 台場", "desc": "世界第一早餐", "price": 2500, "lat": 35.6290, "lon": 139.7735},
            {"name": "Kua'Aina 漢堡", "desc": "夏威夷酪梨漢堡", "price": 1800, "lat": 35.6275, "lon": 139.7710},
            {"name": "麵屋 翠悅", "desc": "飯店旁雞白湯", "price": 1200, "lat": 35.6750, "lon": 139.7805}
        ],
        "events": [
            {"time": "12:00", "event": "抵達成田機場", "icon": "🛬"},
            {"time": "15:30", "event": "台場鋼彈", "icon": "🤖"}
        ]
    },
    "Day 2 (3/1 六)": {
        "title": "東京馬拉松 & 寶可夢",
        "stay": "MIMARU 東京 八丁堀",
        "loc": [35.6812, 139.7671], # 東京車站
        "food": [
            {"name": "Pokemon Cafe", "desc": "皮卡丘造型餐", "price": 3500, "lat": 35.6805, "lon": 139.7740},
            {"name": "金子半之助", "desc": "豪華天丼", "price": 1500, "lat": 35.6850, "lon": 139.7750},
            {"name": "炸牛排 壹貳參", "desc": "秋葉原炸牛排", "price": 1800, "lat": 35.7020, "lon": 139.7715}
        ],
        "events": [
            {"time": "08:00", "event": "爸爸馬拉松起跑", "icon": "🏃"},
            {"time": "11:00", "event": "寶可夢咖啡", "icon": "☕"}
        ]
    },
    "Day 3 (3/2 日)": {
        "title": "富士山一日遊",
        "stay": "MIMARU 東京 八丁堀",
        "loc": [35.4925, 138.7490], # 河口湖
        "food": [
            {"name": "ほうとう不動", "desc": "蔬菜烏龍麵", "price": 1100, "lat": 35.5015, "lon": 138.7660},
            {"name": "富士天婦羅", "desc": "現炸天婦羅", "price": 1500, "lat": 35.4980, "lon": 138.7500}
        ],
        "events": [
            {"time": "10:30", "event": "河口湖/忍野八海", "icon": "🗻"}
        ]
    },
    "Day 4 (3/3 一)": {
        "title": "移動日 & 東京巨蛋",
        "stay": "東京巨蛋飯店",
        "loc": [35.7056, 139.7519], # 巨蛋
        "food": [
            {"name": "Moomin Cafe", "desc": "嚕嚕米陪吃", "price": 1800, "lat": 35.7060, "lon": 139.7530},
            {"name": "敘敘苑 巨蛋店", "desc": "高檔燒肉午餐", "price": 3500, "lat": 35.7050, "lon": 139.7510}
        ],
        "events": [
            {"time": "13:00", "event": "巨蛋城遊樂設施", "icon": "🎡"}
        ]
    },
    "Day 5 (3/4 二)": {
        "title": "明治神宮 & 澀谷",
        "stay": "東京巨蛋飯店",
        "loc": [35.6580, 139.7016], # 澀谷
        "food": [
            {"name": "AFURI 原宿", "desc": "柚子鹽拉麵", "price": 1200, "lat": 35.6715, "lon": 139.7030},
            {"name": "Luke's Lobster", "desc": "龍蝦堡", "price": 2000, "lat": 35.6670, "lon": 139.7060},
            {"name": "挽肉與米", "desc": "炭烤漢堡排", "price": 1800, "lat": 35.6590, "lon": 139.6980}
        ],
        "events": [
            {"time": "10:00", "event": "明治神宮", "icon": "⛩️"},
            {"time": "19:00", "event": "SHIBUYA SKY", "icon": "🌃"}
        ]
    },
    "Day 6 (3/5 四)": {
        "title": "WBC 賽事 & 返台",
        "stay": "溫暖的家",
        "loc": [35.7056, 139.7519], # 巨蛋
        "food": [
            {"name": "Taco Bell", "desc": "方便外帶", "price": 900, "lat": 35.7065, "lon": 139.7525},
            {"name": "壽司三崎港", "desc": "機場美食", "price": 2000, "lat": 35.7719, "lon": 140.3928}
        ],
        "events": [
            {"time": "12:00", "event": "WBC 台灣vs澳洲", "icon": "⚾"}
        ]
    }
}

# --- 4. 側邊選單 ---
with st.sidebar:
    st.title("📱 TabiFam App")
    menu = st.radio("功能導航", ["📅 行程總覽", "🗺️ 美食地圖", "💰 記帳管家", "🎒 檢查清單"])
    st.divider()
    st.info("💡 貼心提醒：地圖上的「橘色叉子」圖示就是美食推薦喔！")

# --- 5. 頁面邏輯 ---

# === 📅 行程總覽 ===
if menu == "📅 行程總覽":
    st.header("📅 每日行程")
    selected_day = st.selectbox("選擇日期", list(itinerary_data.keys()))
    day_data = itinerary_data[selected_day]
    
    st.subheader(f"{day_data['title']}")
    
    # 時間軸
    for item in day_data['events']:
        with st.expander(f"{item['icon']} {item['time']} {item['event']}"):
            st.write(f"行程重點：{item['event']}")
            st.markdown(f"[📍 開啟 Google Maps 導航](https://www.google.com/maps/search/?api=1&query={item['event']})")

    st.markdown("---")
    st.markdown("### 🍴 推薦美食")
    for food in day_data['food']:
        st.markdown(f"""
        <div class="food-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{food['name']}</b>
                <span style="color:#ff9800;">¥{food['price']}</span>
            </div>
            <small>{food['desc']}</small>
        </div>
        """, unsafe_allow_html=True)

# === 🗺️ 美食地圖 (新功能) ===
elif menu == "🗺️ 美食地圖":
    st.header("🗺️ 景點與美食攻略圖")
    
    # 建立地圖
    m = folium.Map(location=[35.6895, 139.6917], zoom_start=11)
    
    # 迴圈加入所有標記
    for day, data in itinerary_data.items():
        # 1. 每日主要景點 (藍色)
        folium.Marker(
            data['loc'], 
            popup=f"<b>{day}</b><br>{data['title']}", 
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        # 2. 美食餐廳 (橘色 + 刀叉圖示)
        for food in data['food']:
            folium.Marker(
                [food['lat'], food['lon']],
                popup=f"<b>{food['name']}</b><br>預算: ¥{food['price']}",
                tooltip=food['name'],
                icon=folium.Icon(color="orange", icon="cutlery")
            ).add_to(m)

    st_folium(m, width=700, height=500)
    st.caption("🔵 藍色：每日主要景點 / 住宿點 | 🟠 橘色：推薦美食餐廳")

# === 💰 記帳管家 (新功能) ===
elif menu == "💰 記帳管家":
    st.header("💰 旅費記帳本")
    
    # 設定預算
    c1, c2 = st.columns(2)
    total_budget = c1.number_input("總預算 (TWD)", value=100000)
    rate = c2.number_input("匯率 (JPY->TWD)", value=0.22)
    
    st.divider()

    # 輸入表單
    st.subheader("📝 新增一筆消費")
    with st.form("add_expense"):
        col_a, col_b, col_c = st.columns([2, 1, 1])
        item_name = col_a.text_input("品項 (如: 拉麵)")
        amount = col_b.number_input("日幣金額", min_value=0)
        category = col_c.selectbox("類別", ["餐飲", "交通", "購物", "住宿"])
        
        submitted = st.form_submit_button("➕ 加入清單")
        
        if submitted and amount > 0:
            st.session_state['expenses'].append({
                "品項": item_name,
                "日幣": amount,
                "台幣(約)": int(amount * rate),
                "類別": category
            })
            st.success("已儲存！")

    # 顯示統計與列表
    if st.session_state['expenses']:
        df = pd.DataFrame(st.session_state['expenses'])
        
        # 計算總額
        total_spent_twd = df["台幣(約)"].sum()
        remain = total_budget - total_spent_twd
        
        # 儀表板
        m1, m2, m3 = st.columns(3)
        m1.metric("已花費 (TWD)", f"${total_spent_twd:,}")
        m2.metric("剩餘預算", f"${remain:,}", delta_color="normal" if remain > 0 else "inverse")
        m3.metric("消費筆數", len(df))
        
        st.markdown("### 🧾 消費明細")
        st.dataframe(df, use_container_width=True)
        
        # 簡單圖表
        st.markdown("### 📊 花費分佈")
        fig = px.pie(df, values='台幣(約)', names='類別', hole=0.4)
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("目前還沒有消費紀錄，試著輸入第一筆吧！")

# === 🎒 檢查清單 ===
elif menu == "🎒 檢查清單":
    st.header("🎒 出發前確認")
    st.markdown("### 3/5 WBC 特別檢查")
    st.checkbox("Suica/Pasmo (巨蛋全場無現金!)")
    st.checkbox("台灣球衣 / 國旗")
    st.checkbox("行動電源")
    
    st.markdown("### 隨身攜帶")
    st.checkbox("護照")
    st.checkbox("網卡 /漫遊已開通")
    st.checkbox("常備藥品 (小孩用)")