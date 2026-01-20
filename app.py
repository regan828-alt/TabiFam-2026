import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- APP 設定 ---
st.set_page_config(page_title="TabiFam 東京親子遊 2026", page_icon="🇯🇵", layout="wide")

# --- 自定義 CSS (美化介面) ---
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .food-card { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #ff4b4b; }
    .nav-btn { background-color: #4285F4; color: white; padding: 5px 10px; border-radius: 5px; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# --- 側邊導航欄 ---
with st.sidebar:
    st.title("📱 TabiFam")
    st.caption("2026/2/28 - 3/5 東京親子行")
    menu = st.radio("功能選單", ["📅 每日行程", "💰 預算記帳", "🗺️ 景點地圖", "🎒 必備清單"])
    
    st.divider()
    st.info("💡 距離出發還有：399 天 (假設今日為 2025/1)")

# --- 資料數據 (模擬資料庫) ---
itinerary_data = {
    "Day 1 (2/28 五)": {
        "title": "抵達與台場散策",
        "stay": "MIMARU 東京 八丁堀",
        "events": [
            {"time": "12:00", "event": "抵達成田機場 (BR184)", "icon": "🛬"},
            {"time": "14:00", "event": "專車接送至飯店 Check-in", "icon": "🏨"},
            {"time": "15:00", "event": "爸爸：東京國際展示場報到", "icon": "👨"},
            {"time": "15:30", "event": "媽媽+小孩：台場散步、鋼彈拍照", "icon": "👩‍👦"},
        ],
        "food": [
            {"name": "Bills 台場", "desc": "世界第一早餐，鬆餅必吃", "price": "¥2,500"},
            {"name": "Kua'Aina 漢堡", "desc": "夏威夷酪梨漢堡，小孩最愛", "price": "¥1,800"},
            {"name": "麵屋 翠悅", "desc": "八丁堀濃郁雞白湯拉麵", "price": "¥1,200"}
        ],
        "loc": [35.6277, 139.7732] # 台場座標
    },
    "Day 2 (3/1 六)": {
        "title": "東京馬拉松 & 寶可夢",
        "stay": "MIMARU 東京 八丁堀",
        "events": [
            {"time": "08:00", "event": "爸爸：東京馬拉松起跑", "icon": "🏃"},
            {"time": "11:00", "event": "媽媽+小孩：日本橋寶可夢咖啡", "icon": "☕"},
            {"time": "15:00", "event": "全家會合 (日本橋/飯店)", "icon": "🤝"},
            {"time": "18:00", "event": "秋葉原逛街 (Yodobashi)", "icon": "🛍️"},
        ],
        "food": [
            {"name": "Pokemon Cafe", "desc": "需預約，皮卡丘造型餐", "price": "¥3,500"},
            {"name": "金子半之助", "desc": "日本橋超豪華天丼", "price": "¥1,500"},
            {"name": "炸牛排 壹貳參", "desc": "秋葉原名店，石板現煎", "price": "¥1,800"}
        ],
        "loc": [35.6812, 139.7671] # 東京車站/日本橋
    },
    "Day 3 (3/2 日)": {
        "title": "富士山一日遊",
        "stay": "MIMARU 東京 八丁堀",
        "events": [
            {"time": "07:45", "event": "KKDAY 巴士團集合", "icon": "🚌"},
            {"time": "10:30", "event": "河口湖、忍野八海", "icon": "🗻"},
            {"time": "18:00", "event": "返回東京", "icon": "🏙️"},
        ],
        "food": [
            {"name": "ほうとう不動", "desc": "河口湖名物蔬菜烏龍麵", "price": "¥1,100"},
            {"name": "富士天婦羅", "desc": "現炸天婦羅，CP值高", "price": "¥1,500"},
            {"name": "Cheese Cake Garden", "desc": "湖畔起司蛋糕", "price": "¥600"}
        ],
        "loc": [35.4925, 138.7490] # 河口湖
    },
    "Day 4 (3/3 一)": {
        "title": "移動日 & 東京巨蛋城",
        "stay": "東京巨蛋飯店",
        "events": [
            {"time": "10:00", "event": "退房 & 移動至巨蛋飯店", "icon": "🧳"},
            {"time": "13:00", "event": "東京巨蛋城遊樂設施", "icon": "🎡"},
            {"time": "18:00", "event": "飯店附近晚餐", "icon": "🍽️"},
        ],
        "food": [
            {"name": "Moomin Cafe", "desc": "嚕嚕米陪吃，麵包吃到飽", "price": "¥1,800"},
            {"name": "敘敘苑 巨蛋店", "desc": "高檔燒肉午間套餐", "price": "¥3,500"},
            {"name": "Shake Shack", "desc": "紐約漢堡，戶外座位", "price": "¥1,600"}
        ],
        "loc": [35.7056, 139.7519] # 東京巨蛋
    },
    "Day 5 (3/4 二)": {
        "title": "明治神宮 & 澀谷夜景",
        "stay": "東京巨蛋飯店",
        "events": [
            {"time": "10:00", "event": "明治神宮參拜", "icon": "⛩️"},
            {"time": "12:30", "event": "原宿/表參道午餐", "icon": "🛍️"},
            {"time": "19:00", "event": "SHIBUYA SKY 夜景", "icon": "🌃"},
        ],
        "food": [
            {"name": "AFURI 原宿", "desc": "柚子鹽拉麵，清爽不膩", "price": "¥1,200"},
            {"name": "Luke's Lobster", "desc": "表參道龍蝦堡", "price": "¥2,000"},
            {"name": "挽肉與米", "desc": "炭烤漢堡排 (需搶票)", "price": "¥1,800"}
        ],
        "loc": [35.6580, 139.7016] # 澀谷
    },
    "Day 6 (3/5 四)": {
        "title": "WBC 熱血賽事 & 返台",
        "stay": "溫暖的家",
        "events": [
            {"time": "10:00", "event": "退房 & 寄放行李", "icon": "🧳"},
            {"time": "12:00", "event": "WBC 台灣 vs 澳洲", "icon": "⚾"},
            {"time": "17:30", "event": "前往成田機場", "icon": "🚆"},
            {"time": "20:20", "event": "BR195 起飛", "icon": "🛫"},
        ],
        "food": [
            {"name": "Taco Bell", "desc": "方便外帶進球場", "price": "¥900"},
            {"name": "巨蛋美食街", "desc": "各式日式料理", "price": "¥1,200"},
            {"name": "壽司三崎港", "desc": "成田機場最後一吃", "price": "¥2,000"}
        ],
        "loc": [35.7056, 139.7519] # 東京巨蛋
    }
}

# --- 頁面邏輯 ---

if menu == "📅 每日行程":
    st.header("📅 您的專屬行程表")
    
    selected_day = st.selectbox("選擇日期", list(itinerary_data.keys()))
    day_data = itinerary_data[selected_day]
    
    st.subheader(f"{selected_day} | {day_data['title']}")
    st.info(f"🛌 住宿：{day_data['stay']}")
    
    # 行程時間軸
    st.markdown("### 🕒 時間軸")
    for item in day_data['events']:
        with st.expander(f"{item['icon']} {item['time']} - {item['event']}"):
            st.write("點擊這裡可以查看詳細備註與導航按鈕...")
            st.markdown(f"[📍 開啟 Google Maps 導航](https://www.google.com/maps/search/?api=1&query={item['event']})")

    # 美食推薦卡片 (3欄)
    st.markdown("### 🍱 今日周邊美食推薦")
    cols = st.columns(3)
    for i, food in enumerate(day_data['food']):
        with cols[i]:
            st.markdown(f"""
            <div class="food-card">
                <h4>{food['name']}</h4>
                <p>{food['desc']}</p>
                <p><b>預算：{food['price']}</b></p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "💰 預算記帳":
    st.header("💰 旅費管家")
    
    col1, col2 = st.columns(2)
    with col1:
        total_budget = st.number_input("總預算 (TWD)", value=100000, step=1000)
    with col2:
        current_rate = st.number_input("今日匯率 (JPY/TWD)", value=0.22, format="%.3f")

    st.divider()
    
    # 模擬記帳輸入
    st.subheader("📝 快速記帳")
    with st.form("expense_form"):
        c1, c2, c3 = st.columns(3)
        item = c1.text_input("項目 (如: 晚餐)")
        amount_jpy = c2.number_input("金額 (JPY)", min_value=0)
        category = c3.selectbox("類別", ["餐飲", "交通", "購物", "住宿", "娛樂"])
        submit = st.form_submit_button("新增支出")
    
    if submit:
        st.success(f"已記錄：{item} ¥{amount_jpy}")

    # 模擬數據視覺化
    st.subheader("📊 消費分析")
    # 這裡建立假數據來展示圖表
    df = pd.DataFrame({
        "Category": ["住宿", "機票", "餐飲", "交通", "購物"],
        "Amount": [35000, 42000, 15000, 5000, 20000]
    })
    fig = px.pie(df, values='Amount', names='Category', title='預算分配預覽 (TWD)')
    st.plotly_chart(fig)

elif menu == "🗺️ 景點地圖":
    st.header("🗺️ 行程地圖總覽")
    
    # 建立地圖
    m = folium.Map(location=[35.6895, 139.6917], zoom_start=11)
    
    # 將所有行程點標註上去
    for day, data in itinerary_data.items():
        folium.Marker(
            data['loc'], 
            popup=day, 
            tooltip=data['title'],
            icon=folium.Icon(color="red" if "WBC" in data['title'] else "blue", icon="info-sign")
        ).add_to(m)

    st_folium(m, width=700, height=500)

elif menu == "🎒 必備清單":
    st.header("🎒 智慧檢查清單")
    
    tab1, tab2 = st.tabs(["⚾ WBC 觀賽包", "🏃 馬拉松應援包"])
    
    with tab1:
        st.markdown("### 3/5 東京巨蛋入場檢查")
        st.warning("⚠️ 注意：東京巨蛋全場無現金交易 (Cashless Only)！")
        st.checkbox("Suica/Pasmo 餘額充足")
        st.checkbox("台灣隊球衣 / 國旗")
        st.checkbox("護照 (免稅/身分查驗)")
        st.checkbox("未開封寶特瓶 (500ml以下)")
        st.checkbox("行動電源 (充飽)")
    
    with tab2:
        st.markdown("### 3/1 爸爸加油團")
        st.checkbox("野餐墊")
        st.checkbox("爸爸的保暖外套 (完賽用)")
        st.checkbox("能量果凍飲")
        st.checkbox("行動電源")
        st.checkbox("下載 R-navi 追蹤 App")

# --- 底部 ---
st.divider()
st.caption("Designed for You by Gemini AI | Ver 1.0 Alpha")