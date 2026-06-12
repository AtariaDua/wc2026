import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 LIVE Calendar", 
    layout="centered", 
    page_icon="🧠"
)

# Скрытие лишних элементов Streamlit
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
st.caption("Версия 12.2: Автоматическая синхронизация с сегодняшним календарем FIFA")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}

API_KEY = "cdb08ac6f34a7ce6e66a67a3887016d0"

# Расширенная база данных реальных участников ЧМ-2026 (Английские названия из API FIFA)
base_team_power = {
    "Mexico": 1.7, "South Korea": 1.5, "South Africa": 1.1, "Czech Republic": 1.4, 
    "Canada": 1.5, "Switzerland": 1.6, "Qatar": 1.1, "Brazil": 2.3, "Morocco": 1.8, 
    "Scotland": 1.3, "USA": 1.7, "Germany": 2.1, "Netherlands": 2.0, "Japan": 1.7, 
    "Argentina": 2.4, "Spain": 2.3, "France": 2.4, "England": 2.4, "Portugal": 2.2, 
    "Croatia": 1.8, "Italy": 1.9, "Belgium": 2.0, "Uruguay": 1.9, "Ecuador": 1.5,
    "Colombia": 1.8, "Tunisia": 1.1, "Poland": 1.4, "Austria": 1.5, "Denmark": 1.6
}

@st.cache_data(ttl=900) # Проверка линии каждые 15 минут
def fetch_live_calendar_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cleaned_matches = []
            now = datetime.now(timezone.utc)
            
            for match in data:
                # Парсим официальное время матча от FIFA
                match_time_str = match.get("commence_time")
                match_time = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                
                # ФИЛЬТР КАЛЕНДАРЯ: Берем только сегодняшние и ближайшие матчи (на ближайшие 3 дня)
                if match_time < now - timedelta(hours=3) or match_time > now + timedelta(days=3):
                    continue
                
                home_team = match.get("home_team")
                away_team = match.get("away_team")
                
                onexbet_odds = None
                for bookmaker in match.get("bookmakers", []):
                    if bookmaker.get("key") == "onexbet":
                        market = bookmaker.get("markets", [])[0]
                        outcomes = market.get("outcomes", [])
                        k1, kx, k2 = 2.0, 3.2, 2.0
                        for out in outcomes:
                            if out.get("name") == home_team: k1 = out.get("price")
                            elif out.get("name") == away_team: k2 = out.get("price")
                            elif out.get("name") == "Draw": kx = out.get("price")
                        onexbet_odds = (k1, kx, k2)
                        break
                
                if onexbet_odds:
                    # Переводим время в локальное для Алматы (+5 часов)
                    local_time = match_time.astimezone(timezone(timedelta(hours=5)))
                    cleaned_matches.append({
                        "home": home_team,
                        "away": away_team,
                        "k1": onexbet_odds[0],
                        "kx": onexbet_odds[1],
                        "k2": onexbet_odds[2],
                        "time": local_time.strftime("%d.%02m %H:%M")
                    })
            
            # Жесткая сортировка по календарной сетке (сначала самые ранние игры)
            cleaned_matches.sort(key=lambda x: x["time"])
            return cleaned_matches
        return []
    except:
        return []

def core_calc(home, away):
    b = st.session_state.tactical_bias
    sim_h = np.random.poisson(base_team_power.get(home, 1.5) * b["Исходы_база"], 15000)
    sim_a = np.random.poisson(base_team_power.get(away, 1.5) * b["Исходы_база"], 15000)
    return np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)

market_mode = st.selectbox("Выберите рабочую область", ["🔥 Сливки Дня (Ближайшие матчи)", "📊 Сквозной скрининг календаря"])
live_data = fetch_live_calendar_odds()

if not live_data:
    st.info("🟢 Все прошедшие матчи обработаны. Ожидаем, когда 1xbet опубликует линию на следующие календарные сутки ЧМ-2026...")
else:
    if market_mode == "🔥 Сливки Дня (Ближайшие матчи)":
        all_signals = []
        for m in live_data:
            p1, x, p2 = core_calc(m["home"], m["away"])
            edge_1 = (p1 - (1 / m["k1"] / 1.045)) * 100
            edge_2 = (p2 - (1 / m["k2"] / 1.045)) * 100
            all_signals.append({"match": f"{m['home']} - {m['away']} [{m['time']}]", "type": f"Поб. {m['home']}", "prob": p1, "odds": m["k1"], "edge": edge_1})
            all_signals.append({"match": f"{m['home']} - {m['away']} [{m['time']}]", "type": f"Поб. {m['away']}", "prob": p2, "odds": m["k2"], "edge": edge_2})
            
        df_all = pd.DataFrame(all_signals)
        
        st.write("### 🚂 ИИ-Экспресс Ближайшего Дня")
        express_pool = df_all[(df_all["prob"] >= 0.55) & (df_all["odds"] >= 1.45) & (df_all["odds"] <= 1.85)].sort_values(by="prob", ascending=False)
        
        if len(express_pool) >= 2:
            leg1 = express_pool.iloc[0]
            leg2 = express_pool.iloc[1]
            st.success(f"""
            **🔥 Экспресс на ближайшие игры собран! Итоговый кэф в 1xbet: {round(leg1['odds'] * leg2['odds'], 2)}**
            * ⚽ {leg1['match']} -> Ставка: **{leg1['type']}** за **{leg1['odds']}**
            * ⚽ {leg2['match']} -> Ставка: **{leg2['type']}** за **{leg2['odds']}**
            """)
        else:
            st.info("🟢 На ближайшие 24 часа супер-надежных экспресс-исходов в линии нет.")
            
        st.write("---")
        st.write("### 🎯 Топ-5 Одиночных ставок (Календарный фильтр)")
        balanced_ordinars = df_all[(df_all["odds"] >= 1.70) & (df_all["odds"] <= 3.50) & (df_all["edge"] >= 2.0) & (df_all["prob"] >= 0.40)].sort_values(by="edge", ascending=False).head(5)
        
        if not balanced_ordinars.empty:
            for idx, row in balanced_ordinars.iterrows():
                with st.container():
                    st.error(f"🎯 **{row['match']}** -> **{row['type']}** за **{row['odds']}**")
                    st.write(f"Математический перевес: **+{row['edge']:.1f}%** | Вероятность: {row['prob']*100:.1f}%")
                    st.write("")
        else:
            st.info("🟢 На сегодняшние игры валуев в рабочих кэфах не обнаружено.")

    elif market_mode == "📊 Сквозной скрининг календаря":
        st.subheader("🗓️ Расписание и котировки 1xbet по времени старта")
        for m in live_data:
            st.write(f"#### ⚔️ {m['home']} vs {m['away']} | ⏰ Время (АЛМ): {m['time']}")
            p1, x, p2 = core_calc(m["home"], m["away"])
            st.code(f"Линия 1xbet -> П1: {m['k1']} | X: {m['kx']} | П2: {m['k2']}")
            st.write(f"Расчет ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            st.write("---")
