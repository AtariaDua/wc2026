import streamlit as st
import pandas as pd
import numpy as np
import requests

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 LIVE 12.0", 
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
st.caption("Версия 12.0: Прямая интеграция с реальной линией 1xbet через API")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}

# Твой персональный ключ интеграции
API_KEY = "cdb08ac6f34a7ce6e66a67a3887016d0"

# Базовая сила команд для симулятора (дополняется динамически)
base_team_power = {
    "Mexico": 1.7, "South Korea": 1.5, "South Africa": 1.1, "Czech Republic": 1.4, "Canada": 1.5, "Switzerland": 1.6, "Qatar": 1.1,
    "Brazil": 2.3, "Morocco": 1.8, "Scotland": 1.3, "USA": 1.7, "Germany": 2.1, "Netherlands": 2.0, "Japan": 1.7, "Argentina": 2.4,
    "Spain": 2.3, "France": 2.4, "England": 2.4, "Portugal": 2.2, "Croatia": 1.8, "Italy": 1.9, "Belgium": 2.0, "Uruguay": 1.9
}

# --- ФУНКЦИЯ ЗАГРУЗКИ РЕАЛЬНОЙ ЛИНИИ 1XBET (Кэш на 1 час) ---
@st.cache_data(ttl=3600)
def fetch_live_1xbet_odds():
    # Запрос к спортивному шлюзу (Регион: Европа, Рынки: исходы h2h)
    url = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cleaned_matches = []
            
            for match in data:
                home_team = match.get("home_team")
                away_team = match.get("away_team")
                
                # Ищем конкретно контору 1xbet в массиве европейских букмекеров
                onexbet_odds = None
                for bookmaker in match.get("bookmakers", []):
                    if bookmaker.get("key") == "onexbet":
                        market = bookmaker.get("markets", [])[0]
                        outcomes = market.get("outcomes", [])
                        
                        # Вытаскиваем коэффициенты П1, Х, П2
                        k1, kx, k2 = 2.0, 3.2, 2.0 # дефолт, если смазано
                        for out in outcomes:
                            if out.get("name") == home_team: k1 = out.get("price")
                            elif out.get("name") == away_team: k2 = out.get("price")
                            elif out.get("name") == "Draw": kx = out.get("price")
                        onexbet_odds = (k1, kx, k2)
                        break
                
                # Если 1xbet выставил линию на этот матч, забираем его в обработку ИИ
                if onexbet_odds:
                    cleaned_matches.append({
                        "home": home_team,
                        "away": away_team,
                        "k1": onexbet_odds[0],
                        "kx": onexbet_odds[1],
                        "k2": onexbet_odds[2]
                    })
            return cleaned_matches
        else:
            return []
    except:
        return []

# --- МАТЕМАТИЧЕСКИЙ ДВИЖОК СИМУЛЯЦИЙ ---
def core_calc(home, away):
    b = st.session_state.tactical_bias
    # 15 000 симуляций по распределению Пуассона
    sim_h = np.random.poisson(base_team_power.get(home, 1.5) * b["Исходы_база"], 15000)
    sim_a = np.random.poisson(base_team_power.get(away, 1.5) * b["Исходы_база"], 15000)
    
    p1 = np.mean(sim_h > sim_a)
    x = np.mean(sim_h == sim_a)
    p2 = np.mean(sim_h < sim_a)
    return p1, x, p2

# --- ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
market_mode = st.selectbox("Выберите рабочую область", ["🔥 Сливки Дня (LIVE 1xbet)", "📊 Полный скрининг линии"])

live_data = fetch_live_1xbet_odds()

if not live_data:
    st.warning("⚠️ Не удалось загрузить линию 1xbet. Возможно, официальная линия на ближайший тур ЧМ еще не сформирована букмекером или превышен лимит API.")
    st.info("Приложение перешло в режим ожидания генерации котировок.")
else:
    if market_mode == "🔥 Сливки Дня (LIVE 1xbet)":
        st.subheader("🚀 Анализ реальной линии матчей")
        
        all_signals = []
        for m in live_data:
            p1, x, p2 = core_calc(m["home"], m["away"])
            
            # Расчет чистого математического перевеса над текущей линией 1xbet
            edge_1 = (p1 - (1 / m["k1"] / 1.045)) * 100
            edge_2 = (p2 - (1 / m["k2"] / 1.045)) * 100
            
            all_signals.append({"match": f"{m['home']} - {m['away']}", "type": f"Поб. {m['home']}", "prob": p1, "odds": m["k1"], "edge": edge_1})
            all_signals.append({"match": f"{m['home']} - {m['away']}", "type": f"Поб. {m['away']}", "prob": p2, "odds": m["k2"], "edge": edge_2})
            
        df_all = pd.DataFrame(all_signals)
        
        # 🚂 ЖИВОЙ ЭКСПРЕСС ДНЯ
        st.write("### 🚂 ИИ-Экспресс Дня (Прямо из 1xbet)")
        express_pool = df_all[(df_all["prob"] >= 0.55) & (df_all["odds"] >= 1.45) & (df_all["odds"] <= 1.85)].sort_values(by="prob", ascending=False)
        
        if len(express_pool) >= 2:
            leg1 = express_pool.iloc[0]
            leg2 = express_pool.iloc[1]
            total_odds = round(leg1["odds"] * leg2["odds"], 2)
            
            st.success(f"""
            **🔥 Живой экспресс сформирован! Итоговый коэффициент в 1xbet: {total_odds}**
            
            1. ⚽ **{leg1['match']}** -> Ставка: **{leg1['type']}** за **{leg1['odds']}** (ИИ: {leg1['prob']*100:.1f}%)
            2. ⚽ **{leg2['match']}** -> Ставка: **{leg2['type']}** за **{leg2['odds']}** (ИИ: {leg2['prob']*100:.1f}%)
            """)
        else:
            st.info("🟢 Букмекер выставил слишком плотную линию. Надежных двойников для экспресса прямо сейчас нет.")
            
        st.write("---")
        
        # 🎯 ТОП-5 ВАЛУЕВ
        st.write("### 🎯 Топ-5 Одиночных ставок (Ошибки линии 1xbet)")
        profitable_ordinars = df_all[df_all["edge"] >= 3.0].sort_values(by="edge", ascending=False).head(5)
        
        if not profitable_ordinars.empty:
            for idx, row in profitable_ordinars.iterrows():
                with st.container():
                    st.error(f"🔥 **{row['match']}** -> **{row['type']}** за **{row['odds']}**")
                    st.write(f"Чистый перевес над 1xbet: **+{row['edge']:.1f}%** | Вероятность по ИИ: {row['prob']*100:.1f}%")
        else:
            st.info("🟢 Крупных ошибок в линии 1xbet (перекосов от +3%) на данные матчи не обнаружено.")

    elif market_mode == "📊 Полный скрининг линии":
        st.subheader("📊 Текущие котировки и симуляции")
        for m in live_data:
            st.write(f"#### ⚔️ {m['home']} vs {m['away']}")
            p1, x, p2 = core_calc(m["home"], m["away"])
            st.code(f"Линия 1xbet -> П1: {m['k1']} | X: {m['kx']} | П2: {m['k2']}")
            st.write(f"Расчет ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
            st.write("---")
