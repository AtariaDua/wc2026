import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 AI Mobile", 
    layout="centered", # Центрируем контент для узких экранов iPhone
    page_icon="🧠"
)

# Скрытие лишних элементов Streamlit для эффекта нативного приложения
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Стилизация кнопок под iOS */
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

st.title("🧠 WC-2026 ИИ-Комбайн")
st.caption("Версия 11.2: Мобильная архитектура под Google Chrome iOS")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}
if "history_logs" not in st.session_state:
    st.session_state.history_logs = []

# --- СТРУКТУРА ГРУПП ---
teams_dict = {
    "Группа А": ["Мексика", "Южная Корея", "ЮАР", "Чехия"],
    "Группа B": ["Канада", "Швейцария", "Катар", "Босния и Герцеговина"],
    "Группа K": ["Португалия", "Колумбия", "Узбекистан", "ДР Конго"],
    "Группа L": ["Англия", "Хорватия", "Гана", "Панама"]
}
base_team_power = {
    "Мексика": 1.7, "Южная Корея": 1.5, "ЮАР": 1.1, "Чехия": 1.4, "Канада": 1.5, "Швейцария": 1.6, "Катар": 1.1, "Босния и Герцеговина": 1.3,
    "Португалия": 2.2, "Колумбия": 1.8, "Узбекистан": 1.2, "ДР Конго": 1.1, "Англия": 2.4, "Хорватия": 1.8, "Гана": 1.3, "Панама": 1.0
}
team_tactical_matrix = {
    "Мексика": [54, 65, 12, 60, 55], "Южная Корея": [51, 48, 14, 55, 62], "ЮАР": [44, 35, 8, 45, 40], "Чехия": [48, 70, 16, 50, 68],
    "Канада": [49, 52, 11, 55, 58], "Швейцария": [53, 55, 14, 52, 48], "Катар": [42, 38, 9, 40, 45], "Босния и Герцеговина": [46, 62, 15, 48, 50],
    "Португалия": [63, 78, 10, 65, 68], "Колумбия": [53, 60, 15, 55, 62], "Узбекистан": [46, 42, 18, 50, 55], "ДР Конго": [42, 38, 14, 38, 42],
    "Англия": [65, 82, 11, 64, 62], "Хорватия": [56, 58, 13, 52, 50], "Гана": [47, 45, 11, 48, 52], "Панама": [41, 30, 9, 40, 35]
}

# --- ВЕРТИКАЛЬНЫЙ МОБИЛЬНЫЙ ИНТЕРФЕЙС (ВМЕСТО САЙДБАРА) ---
st.write("### 🎛️ Настройки")
market_mode = st.selectbox(
    "Рынок анализа",
    ["💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)", "⚖️ Бэктестинг и Верификация"]
)

selected_group = st.selectbox("Выберите группу", list(teams_dict.keys()))

if market_mode == "💰 Исходы (П1/Х/П2)":
    min_edge = st.slider("Минимальный перевес ИИ (%)", 1.0, 10.0, 3.0)
    bk_margin = 4.5
else:
    min_edge = st.slider("Минимальный перевес (тотал)", 0.2, 3.0, 0.5, step=0.1)

st.write("---")

# --- МАТЕМАТИЧЕСКИЕ ДВИЖКИ ---
def simulate_match_probs_dynamic(home, away):
    bias = st.session_state.tactical_bias["Исходы_база"]
    sim_h = np.random.poisson(base_team_power[home] * bias, 15000)
    sim_a = np.random.poisson(base_team_power[away] * bias, 15000)
    return np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)

def generate_fallback_odds(p1, x, p2, margin_pct):
    margin = 1 + (margin_pct / 100)
    return round(1 / (p1 * margin), 2), round(1 / (x * margin), 2), round(1 / (p2 * margin), 2)

def calculate_dynamic_corners(home, away):
    b = st.session_state.tactical_bias
    exp_h = b["Угловые_база"] + (team_tactical_matrix[home][0] * 0.03) + (team_tactical_matrix[home][1] * b["Коэффициент_навесов"])
    exp_a = b["Угловые_база"] + (team_tactical_matrix[away][0] * 0.03) + (team_tactical_matrix[away][1] * b["Коэффициент_навесов"])
    return round(float(np.mean(np.random.poisson(exp_h, 10000) + np.random.poisson(exp_a, 10000))), 2)

def calculate_dynamic_offsides(home, away):
    b = st.session_state.tactical_bias
    exp_h = b["Офсайды_база"] + (team_tactical_matrix[away][3] * 0.04)
    exp_a = b["Офсайды_база"] + (team_tactical_matrix[home][3] * 0.04)
    return round(float(np.mean(np.random.poisson(exp_h, 10000) + np.random.poisson(exp_a, 10000))), 2)

# --- СКРИНИНГ ДЛЯ МОБИЛЬНОГО ЭКРАНА ---
if market_mode in ["💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)"]:
    group_teams = teams_dict[selected_group]
    matchups = [(group_teams[0], group_teams[1]), (group_teams[2], group_teams[3])]
    
    for home, away in matchups:
        match_key = f"{home} - {away}"
        st.write(f"#### ⚔️ {match_key}")
        
        if market_mode == "💰 Исходы (П1/Х/П2)":
            ai_p1, ai_x, ai_p2 = simulate_match_probs_dynamic(home, away)
            bk_k1, bk_kx, bk_k2 = generate_fallback_odds(ai_p1, ai_x, ai_p2, bk_margin)
            edge_p1 = (ai_p1 - (1/bk_k1/1.045)) * 100
            
            st.code(f"1xbet -> П1: {bk_k1} | X: {bk_kx} | П2: {bk_k2}")
            st.write(f"Вероятности ИИ: П1 {ai_p1*100:.1f}% | П2 {ai_p2*100:.1f}%")
            
            if edge_p1 >= min_edge:
                st.error(f"🚨 ВАЛУЙ на П1 {home}!")
                if st.button(f"📥 В архив: {home}", key=match_key+"_m_i"):
                    st.session_state.history_logs.append({"Матч": match_key, "Рынок": "Исходы", "Прогноз ИИ": f"П1 {home}", "Линия БК": bk_k1, "Статус": "В игре", "Факт": None, "Ошибка (MAE)": None})
                    st.success("Есть!")
            else:
                st.success("🟢 Линия ровная")
                
        elif market_mode == "📐 Угловые удары":
            ai_pred = calculate_dynamic_corners(home, away)
            bk_line = 10.5 if "Португалия" in [home, away] or "Англия" in [home, away] else 9.5
            diff = ai_pred - bk_line
            
            st.write(f"Прогноз ИИ: **{ai_pred}** | БК: **{bk_line}**")
            if abs(diff) >= min_edge:
                typ = "ТБ" if diff > 0 else "ТМ"
                st.error(f"🚨 ВАЛУЙ: {typ} ({bk_line}) [Перевес: {diff:.1f}]")
                if st.button(f"📥 В архив тотал", key=match_key+"_m_c"):
                    st.session_state.history_logs.append({"Матч": match_key, "Рынок": "Угловые", "Прогноз ИИ": ai_pred, "Линия БК": bk_line, "Статус": "В игре", "Факт": None, "Ошибка (MAE)": None})
                    st.success("В архиве!")
            else:
                st.success("🟢 Валуя нет")

        elif market_mode == "🚩 Офсайды (Offside Capture)":
            ai_pred = calculate_dynamic_offsides(home, away)
            bk_line = 3.5
            diff = ai_pred - bk_line
            st.write(f"Прогноз ИИ: **{ai_pred}** | БК: **{bk_line}**")
            if abs(diff) >= min_edge:
                typ = "ТБ" if diff > 0 else "ТМ"
                st.error(f"🚨 ВАЛУЙ: {typ} ({bk_line})")
                if st.button(f"📥 В архив офсайды", key=match_key+"_m_o"):
                    st.session_state.history_logs.append({"Матч": match_key, "Рынок": "Офсайды", "Прогноз ИИ": ai_pred, "Линия БК": bk_line, "Статус": "В игре", "Факт": None, "Ошибка (MAE)": None})
                    st.success("Записано!")

        st.write("---")

# --- ЭКРАН БЭКТЕСТИНГА ДЛЯ МОБИЛКИ ---
elif market_mode == "⚖️ Бэктестинг и Верификация":
    st.subheader("⚖️ Верификация")
    if not st.session_state.history_logs:
        st.info("Архив пуст.")
    else:
        df_logs = pd.DataFrame(st.session_state.history_logs)
        if st.button("🤖 Сэмулировать результаты дня"):
            for row in st.session_state.history_logs:
                if row["Статус"] == "В игре":
                    if row["Рынок"] == "Исходы":
                        row["Факт"] = "ОК"; row["Ошибка (MAE)"] = 0.0
                    else:
                        fact_result = max(0, round(row["Прогноз ИИ"] + np.random.choice([-1, 0, 1]), 1))
                        row["Факт"] = fact_result
                        row["Ошибка (MAE)"] = round(abs(fact_result - row["Прогноз ИИ"]), 2)
                        delta = fact_result - row["Прогноз ИИ"]
                        if row["Рынок"] == "Угловые": st.session_state.tactical_bias["Угловые_база"] += delta * 0.1
                    row["Статус"] = "Рассчитан"
            st.rerun()
            
        st.dataframe(df_logs[["Матч", "Прогноз ИИ", "Факт", "Статус"]], use_container_width=True)
        st.write("⚙️ Калибровочные веса:")
        st.json(st.session_state.tactical_bias)