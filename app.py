import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 LIVE 12.8", 
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
st.caption("Версия 12.8: Автоматические пороги окупаемости для Угловых и Офсайдов")

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

@st.cache_data(ttl=600)
def fetch_live_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cleaned_matches = []
            now = datetime.now(timezone.utc)
            for match in data:
                match_time_str = match.get("commence_time")
                match_time = datetime.strptime(match_time_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
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
                    local_time = match_time.astimezone(timezone(timedelta(hours=5)))
                    cleaned_matches.append({"home": home_team, "away": away_team, "k1": onexbet_odds[0], "kx": onexbet_odds[1], "k2": onexbet_odds[2], "time": local_time.strftime("%d.%02m %H:%M")})
            return cleaned_matches
        return []
    except:
        return []

def simulate_smalls(home, away, market_type):
    b = st.session_state.tactical_bias
    s_h = team_tactical_matrix.get(home, [50, 50, 12, 50, 50])
    s_a = team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
    if market_type == "Угловые":
        exp_h = b["Угловые_база"] + (s_h[0]*0.03) + (s_h[1]*b["Коэффициент_навесов"])
        exp_a = b["Угловые_база"] + (s_a[0]*0.03) + (s_a[1]*b["Коэффициент_навесов"])
    else:
        exp_h = b["Офсайды_база"] + (s_a[3]*0.04)
        exp_a = b["Офсайды_база"] + (s_h[3]*0.04)
    sim_h = np.random.poisson(exp_h, 15000)
    sim_a = np.random.poisson(exp_a, 15000)
    return np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a), round(float(np.mean(sim_h + sim_a)), 1)

# --- НАВИГАЦИЯ ---
market_mode = st.selectbox(
    "Выберите рабочую область",
    ["🔥 Сливки Дня", "💰 Победы и ничьи матчей (1xbet)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)"]
)

live_data = fetch_live_matches()

if not live_data:
    st.info("🟢 Ожидание публикации котировок 1xbet на текущий игровой день...")
else:
    if market_mode == "🔥 Сливки Дня":
        st.subheader("🚀 Готовые решения на ближайшие игры")
        all_signals = []
        for m in live_data:
            sim_h = np.random.poisson(base_team_power.get(m["home"], 1.5), 15000)
            sim_a = np.random.poisson(base_team_power.get(m["away"], 1.5), 15000)
            p1, p2 = np.mean(sim_h > sim_a), np.mean(sim_h < sim_a)
            all_signals.append({"match": f"{m['home']}-{m['away']}", "type": f"Поб. {m['home']}", "prob": p1, "odds": m["k1"]})
            all_signals.append({"match": f"{m['home']}-{m['away']}", "type": f"Поб. {m['away']}", "prob": p2, "odds": m["k2"]})
        df_all = pd.DataFrame(all_signals)
        
        st.write("### 🚂 ИИ-Экспресс Дня")
        ep = df_all[(df_all["prob"]>=0.55) & (df_all["odds"]>=1.45) & (df_all["odds"]<=1.85)]
        if len(ep) >= 2:
            st.success(f"🔥 Итоговый кэф купона: {round(ep.iloc[0]['odds']*ep.iloc[1]['odds'], 2)}\n* ⚽ {ep.iloc[0]['match']} -> {ep.iloc[0]['type']} ({ep.iloc[0]['odds']})\n* ⚽ {ep.iloc[1]['match']} -> {ep.iloc[1]['type']} ({ep.iloc[1]['odds']})")
        else: st.info("🟢 Нет подходящих матчей для экспресса.")

    elif market_mode == "💰 Победы и ничьи матчей (1xbet)":
        st.subheader("💰 Мониторинг рынка чистых исходов")
        for m in live_data:
            st.write(f"#### ⚔️ {m['home']} vs {m['away']} | ⏰ {m['time']}")
            sim_h = np.random.poisson(base_team_power.get(m['home'], 1.5), 15000)
            sim_a = np.random.poisson(base_team_power.get(m['away'], 1.5), 15000)
            p1, x, p2 = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
            st.code(f"Линия 1xbet -> П1: {m['k1']} | X: {m['kx']} | П2: {m['k2']}")
            st.write(f"ИИ Прогноз: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            
            req_k1 = round(1 / (p1 * 1.045), 2) if p1 > 0 else 99.0
            req_k2 = round(1 / (p2 * 1.045), 2) if p2 > 0 else 99.0
            if m["k1"] < req_k1: st.write(f"🛑 **П1 ({m['home']}):** Не ставить. Кэф занижен БК. (Порог ИИ: >= **{req_k1}**)")
            else: st.write(f"🔥 **П1 ({m['home']}):** ВАЛУЙНЫЙ КЭФ. Можно ставить (Порог ИИ: >= {req_k1})")
            if m["k2"] < req_k2: st.write(f"🛑 **П2 ({m['away']}):** Не ставить. Кэф занижен БК. (Порог ИИ: >= **{req_k2}**)")
            else: st.write(f"🔥 **П2 ({m['away']}):** ВАЛУЙНЫЙ КЭФ. Можно ставить (Порог ИИ: >= {req_k2})")
            st.write("---")

    elif market_mode == "📐 Угловые удары":
        st.subheader("📐 Анализ угловых по календарю FIFA")
        for m in live_data:
            st.write(f"#### ⚔️ {m['home']} vs {m['away']} | ⏰ {m['time']}")
            p1, x, p2, total_pred = simulate_smalls(m["home"], m["away"], "Угловые")
            
            # Расчет минимальных пороговых кэфов окупаемости
            req_k1 = round(1 / (p1 * 1.045), 2) if p1 > 0 else 99.0
            req_k2 = round(1 / (p2 * 1.045), 2) if p2 > 0 else 99.0
            
            st.caption(f"📈 Ожидаемый общий Тотал матча: **{total_pred}** угловых")
            st.write(f"Вероятности ИИ: П1 (Канада) {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            
            st.error(f"📋 **ПРАВИЛО СТАВКИ В 1XBET ДЛЯ УГЛОВЫХ:**")
            st.write(f"👉 Ставь на **П1 ({m['home']})**, только если оригинальный кэф в 1xbet **>= {req_k1}**")
            st.write(f"👉 Ставь на **П2 ({m['away']})**, только если оригинальный кэф в 1xbet **>= {req_k2}**")
            st.write("---")

    elif market_mode == "🚩 Офсайды (Offside Capture)":
        st.subheader("🚩 Анализ офсайдов по календарю FIFA")
        for m in live_data:
            st.write(f"#### ⚔️ {m['home']} vs {m['away']} | ⏰ {m['time']}")
            p1, x, p2, total_pred = simulate_smalls(m["home"], m["away"], "Офсайды")
            
            # Расчет минимальных пороговых кэфов окупаемости
            req_k1 = round(1 / (p1 * 1.045), 2) if p1 > 0 else 99.0
            req_k2 = round(1 / (p2 * 1.045), 2) if p2 > 0 else 99.0
            
            st.caption(f"📈 Ожидаемый общий Тотал матча: **{total_pred}** офсайдов")
            st.write(f"Вероятности ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            
            st.error(f"📋 **ПРАВИЛО СТАВКИ В 1XBET ДЛЯ ОФСАЙДОВ:**")
            st.write(f"👉 Ставь на **П1 ({m['home']})**, только если оригинальный кэф в 1xbet **>= {req_k1}**")
            st.write(f"👉 Ставь на **П2 ({m['away']})**, только если оригинальный кэф в 1xbet **>= {req_k2}**")
            st.write("---")
