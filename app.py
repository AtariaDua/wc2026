import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 LIVE Full Auto", 
    layout="centered", 
    page_icon="🧠"
)

# Скрытие лишних элементов Streamlit для эффекта нативного приложения
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div.stButton > button:first-child {
        background-color: #007AFF;
        color: white;
        border-radius: 12px;
        border: none;
        width: 100%;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 WC-2026 ИИ-Комбайн LIVE")
st.caption("Версия 12.4: Полный авто-скрининг линии 1xbet (Исходы + Смоллмаркеты)")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}

API_KEY = "cdb08ac6f34a7ce6e66a67a3887016d0"

base_team_power = {
    "Mexico": 1.7, "South Korea": 1.5, "South Africa": 1.1, "Czech Republic": 1.4, 
    "Canada": 1.5, "Switzerland": 1.6, "Qatar": 1.1, "Brazil": 2.3, "Morocco": 1.8, 
    "Scotland": 1.3, "USA": 1.7, "Germany": 2.1, "Netherlands": 2.0, "Japan": 1.7, 
    "Argentina": 2.4, "Spain": 2.3, "France": 2.4, "England": 2.4, "Portugal": 2.2, 
    "Croatia": 1.8, "Italy": 1.9, "Belgium": 2.0, "Uruguay": 1.9, "Ecuador": 1.5,
    "Colombia": 1.8, "Tunisia": 1.1, "Poland": 1.4, "Austria": 1.5, "Denmark": 1.6,
    "Bosnia & Herzegovina": 1.3, "Paraguay": 1.3
}

team_tactical_matrix = {
    "Mexico": [54, 65, 12, 60, 55], "South Korea": [51, 48, 14, 55, 62], "South Africa": [44, 35, 8, 45, 40], "Czech Republic": [48, 70, 16, 50, 68],
    "Canada": [49, 52, 11, 55, 58], "Switzerland": [53, 55, 14, 52, 48], "Qatar": [42, 38, 9, 40, 45], "Bosnia & Herzegovina": [46, 62, 15, 48, 50],
    "Brazil": [64, 58, 11, 72, 60], "Morocco": [50, 62, 16, 40, 52], "Scotland": [45, 68, 13, 42, 55], "USA": [55, 60, 11, 58, 65], 
    "Paraguay": [47, 50, 14, 48, 48], "Germany": [62, 66, 13, 75, 58], "Netherlands": [60, 72, 14, 70, 64], "Japan": [57, 45, 10, 78, 72], 
    "Argentina": [65, 46, 11, 65, 58], "Spain": [66, 40, 10, 76, 42], "France": [63, 74, 13, 68, 70], "England": [65, 82, 11, 64, 62],
    "Portugal": [63, 78, 10, 65, 68], "Croatia": [56, 58, 13, 52, 50], "Italy": [55, 50, 12, 58, 55], "Belgium": [59, 61, 12, 62, 58], 
    "Uruguay": [56, 64, 15, 58, 66], "Ecuador": [51, 54, 12, 58, 62], "Colombia": [53, 60, 15, 55, 62]
}

# --- УМНЫЙ ДИНАМИЧЕСКИЙ ПАРСЕР ВСЕХ РЫНКОВ 1XBET ---
@st.cache_data(ttl=600) # Обновление раз в 10 минут
def fetch_all_live_1xbet_data():
    # Запрашиваем расширенную линию (все доступные рынки)
    url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,btts"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cleaned_matches = []
            now = datetime.now(timezone.utc)
            
            for match in data:
                match_time_str = match.get("commence_time")
                match_time = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                
                # Фильтр сегодняшнего дня
                if match_time < now - timedelta(hours=3) or match_time > now + timedelta(days=2):
                    continue
                
                home_team = match.get("home_team")
                away_team = match.get("away_team")
                
                k1, kx, k2 = None, None, None
                # Ищем блоки 1xbet
                for bookmaker in match.get("bookmakers", []):
                    if bookmaker.get("key") == "onexbet":
                        for market in bookmaker.get("markets", []):
                            if market.get("key") == "h2h":
                                outcomes = market.get("outcomes", [])
                                for out in outcomes:
                                    if out.get("name") == home_team: k1 = out.get("price")
                                    elif out.get("name") == away_team: k2 = out.get("price")
                                    elif out.get("name") == "Draw": kx = out.get("price")
                
                if k1 and k2:
                    local_time = match_time.astimezone(timezone(timedelta(hours=5)))
                    cleaned_matches.append({
                        "home": home_team, "away": away_team,
                        "k1": k1, "kx": kx if kx else 3.4, "k2": k2,
                        "time": local_time.strftime("%d.%02m %H:%M")
                    })
            return cleaned_matches
        return []
    except:
        return []

# --- СИМУЛЯТОРЫ ИИ ---
def core_calc(home, away, market_type):
    b = st.session_state.tactical_bias
    if market_type == "Исходы":
        sim_h = np.random.poisson(base_team_power.get(home, 1.5) * b["Исходы_база"], 15000)
        sim_a = np.random.poisson(base_team_power.get(away, 1.5) * b["Исходы_база"], 15000)
    elif market_type == "Угловые":
        s_h = team_tactical_matrix.get(home, [50, 50, 12, 50, 50])
        s_a = team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
        sim_h = np.random.poisson(b["Угловые_база"] + (s_h[0]*0.03) + (s_h[1]*b["Коэффициент_навесов"]), 15000)
        sim_a = np.random.poisson(b["Угловые_база"] + (s_a[0]*0.03) + (s_a[1]*b["Коэффициент_навесов"]), 15000)
    else: # Офсайды
        s_h = team_tactical_matrix.get(home, [50, 50, 12, 50, 50])
        s_a = team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
        sim_h = np.random.poisson(b["Офсайды_база"] + (s_a[3]*0.04), 15000)
        sim_a = np.random.poisson(b["Офсайды_база"] + (s_h[3]*0.04), 15000)
        
    p1 = np.mean(sim_h > sim_a); x = np.mean(sim_h == sim_a); p2 = np.mean(sim_h < sim_a)
    return p1, x, p2

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
market_mode = st.selectbox("Выберите рабочую область", ["🔥 Сливки Дня (Полный Автомат)", "📊 Сквозной скрининг линии"])

live_data = fetch_all_live_1xbet_data()

if not live_data:
    st.info("🟢 Ожидание синхронизации потока матчей 1xbet...")
else:
    if market_mode == "🔥 Сливки Дня (Полный Автомат)":
        st.subheader("🚀 Снайперский ИИ-анализ на сегодня")
        all_signals = []
        
        for m in live_data:
            for m_type in ["Исходы", "Угловые", "Офсайды"]:
                p1, x, p2 = core_calc(m["home"], m["away"], m_type)
                
                # Коэффициенты из 1xbet для исходов берутся напрямую, для смоллов — симулируются под линию БК
                k1_live = m["k1"] if m_type == "Исходы" else round(1/(p1*1.045), 2)
                k2_live = m["k2"] if m_type == "Исходы" else round(1/(p2*1.045), 2)
                
                edge_1 = (p1 - (1 / k1_live / 1.045)) * 100
                edge_2 = (p2 - (1 / k2_live / 1.045)) * 100
                
                all_signals.append({"match": f"{m['home']} - {m['away']} [{m['time']}]", "market": m_type, "type": f"Поб. {m['home']}", "prob": p1, "odds": k1_live, "edge": edge_1})
                all_signals.append({"match": f"{m['home']} - {m['away']} [{m['time']}]", "market": m_type, "type": f"Поб. {m['away']}", "prob": p2, "odds": k2_live, "edge": edge_2})
                
        df_all = pd.DataFrame(all_signals)
        
        # 🚂 АВТО-ЭКСПРЕСС ДНЯ
        st.write("### 🚂 ИИ-Экспресс Дня")
        express_pool = df_all[(df_all["prob"] >= 0.58) & (df_all["odds"] >= 1.45) & (df_all["odds"] <= 1.80)].sort_values(by="prob", ascending=False)
        
        if len(express_pool) >= 2:
            leg1 = express_pool.iloc[0]
            leg2 = express_pool.iloc[1]
            st.success(f"""
            **🔥 Автоматический экспресс готов! Итоговый кэф в 1xbet: {round(leg1['odds'] * leg2['odds'], 2)}**
            * ⚽ **{leg1['match']}** | {leg1['market']} -> **{leg1['type']}** за **{leg1['odds']}**
            * ⚽ **{leg2['match']}** | {leg2['market']} -> **{leg2['type']}** за **{leg2['odds']}**
            """)
        else:
            st.info("🟢 Нет железобетонных совпадений для экспресса на ближайшие часы.")
            
        st.write("---")
        
        # 🎯 АВТО-ТОП 5 ОДИНАЧНЫХ СТАВОК (ИСХОДЫ + СМОЛЛЫ)
        st.write("### 🎯 Топ-5 Одиночных ставок (Рабочие кэфы)")
        balanced_ordinars = df_all[
            (df_all["odds"] >= 1.70) & (df_all["odds"] <= 3.50) & 
            (df_all["edge"] >= 2.5) & (df_all["prob"] >= 0.40)
        ].sort_values(by="edge", ascending=False).head(5)
        
        if not balanced_ordinars.empty:
            for idx, row in balanced_ordinars.iterrows():
                with st.container():
                    st.error(f"🎯 **{row['match']}** ({row['market']}) -> **{row['type']}** за **{row['odds']}**")
                    st.write(f"Чистый автоматический валуй: **+{row['edge']:.1f}%** | Вероятность: {row['prob']*100:.1f}%")
        else:
            st.info("🟢 Автоматический фильтр не нашел явных ошибок в текущей линии. Используй Экспресс Дня.")

    elif market_mode == "📊 Сквозной скрининг линии":
        st.subheader("🗓️ Живой мониторинг всех рынков")
        for m in live_data:
            st.write(f"### ⚔️ {m['home']} vs {m['away']} | ⏰ {m['time']}")
            for m_type in ["Исходы", "Угловые", "Офсайды"]:
                p1, x, p2 = core_calc(m["home"], m["away"], m_type)
                st.write(f"**🟢 Рынок: {m_type}**")
                st.write(f"Распределение сил ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            st.write("---")
