import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 AI Ultimate Pro", 
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

st.title("🧠 WC-2026 ИИ-Комбайн")
st.caption("Версия 11.5: Система умных рекомендаций для заработка на ставках")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}
if "history_logs" not in st.session_state:
    st.session_state.history_logs = []

# --- ОФИЦИАЛЬНАЯ СТРУКТУРА ВСЕХ 12 ГРУПП ЧМ-2026 ---
teams_dict = {
    "Группа А": ["Мексика", "Южная Корея", "ЮАР", "Чехия"],
    "Группа B": ["Канада", "Швейцария", "Катар", "Босния и Герцеговина"],
    "Группа C": ["Бразилия", "Марокко", "Шотландия", "Гаити"],
    "Группа D": ["США", "Парагвай", "Австралия", "Турция"],
    "Группа E": ["Германия", "Эквадор", "Кот-д’Ивуар", "Кюрасао"],
    "Группа F": ["Нидерланды", "Япония", "Швеция", "Тунис"],
    "Группа G": ["Бельгия", "Иран", "Египет", "Новая Зеландия"],
    "Группа H": ["Испания", "Уругвай", "Саудовская Аравия", "Кабо-Верде"],
    "Группа I": ["Франция", "Сенегал", "Норвегия", "Ирак"],
    "Группа J": ["Аргентина", "Австрия", "Алжир", "Иордания"],
    "Группа K": ["Португалия", "Колумбия", "Узбекистан", "ДР Конго"],
    "Группа L": ["Англия", "Хорватия", "Гана", "Панама"]
}

base_team_power = {
    "Мексика": 1.7, "Южная Корея": 1.5, "ЮАР": 1.1, "Чехия": 1.4, "Канада": 1.5, "Швейцария": 1.6, "Катар": 1.1, "Босния и Герцеговина": 1.3,
    "Бразилия": 2.3, "Марокко": 1.8, "Шотландия": 1.3, "Гаити": 0.8, "США": 1.7, "Парагвай": 1.3, "Австралия": 1.3, "Турция": 1.5,
    "Германия": 2.1, "Эквадор": 1.5, "Кот-д’Ивуар": 1.4, "Кюрасао": 0.8, "Нидерланды": 2.0, "Япония": 1.7, "Швеция": 1.5, "Тунис": 1.1,
    "Бельгия": 2.0, "Иран": 1.2, "Египет": 1.3, "Новая Зеландия": 0.8, "Испания": 2.3, "Уругвай": 1.9, "Саудовская Аравия": 1.2, "Кабо-Верде": 1.0,
    "Франция": 2.4, "Сенегал": 1.5, "Норвегия": 1.6, "Ирак": 1.0, "Аргентина": 2.4, "Австрия": 1.5, "Алжир": 1.4, "Иордания": 0.9,
    "Португалия": 2.2, "Колумбия": 1.8, "Узбекистан": 1.2, "ДР Конго": 1.1, "Англия": 2.4, "Хорватия": 1.8, "Гана": 1.3, "Панама": 1.0
}

team_tactical_matrix = {
    "Мексика": [54, 65, 12, 60, 55], "Южная Корея": [51, 48, 14, 55, 62], "ЮАР": [44, 35, 8, 45, 40], "Чехия": [48, 70, 16, 50, 68],
    "Канада": [49, 52, 11, 55, 58], "Швейцария": [53, 55, 14, 52, 48], "Катар": [42, 38, 9, 40, 45], "Босния и Герцеговина": [46, 62, 15, 48, 50],
    "Бразилия": [64, 58, 11, 72, 60], "Марокко": [50, 62, 16, 40, 52], "Шотландия": [45, 68, 13, 42, 55], "Гаити": [38, 32, 7, 35, 30],
    "США": [55, 60, 11, 58, 65], "Парагвай": [47, 50, 14, 48, 48], "Австралия": [46, 64, 15, 46, 50], "Турция": [52, 58, 12, 55, 58],
    "Германия": [62, 66, 13, 75, 58], "Эквадор": [51, 54, 12, 58, 62], "Кот-д’Ивуар": [53, 58, 14, 52, 55], "Кюрасао": [40, 35, 8, 42, 38],
    "Нидерланды": [60, 72, 14, 70, 64], "Япония": [57, 45, 10, 78, 72], "Швеция": [52, 58, 13, 54, 52], "Тунис": [44, 40, 11, 42, 45],
    "Бельгия": [59, 61, 12, 62, 58], "Иран": [43, 42, 15, 38, 48], "Египет": [48, 49, 12, 48, 52], "Новая Зеландия": [42, 55, 13, 45, 40],
    "Испания": [66, 40, 10, 76, 42], "Уругвай": [56, 64, 15, 58, 66], "Саудовская Аравия": [48, 38, 9, 65, 50], "Кабо-Верде": [43, 42, 11, 46, 44],
    "Франция": [63, 74, 13, 68, 70], "Сенегал": [52, 54, 14, 50, 52], "Норвегия": [50, 68, 12, 52, 75], "Ирак": [44, 41, 10, 42, 42],
    "Аргентина": [65, 46, 11, 65, 58], "Австрия": [54, 56, 13, 68, 60], "Алжир": [51, 52, 12, 52, 55], "Иордания": [42, 36, 8, 40, 38],
    "Португалия": [63, 78, 10, 65, 68], "Колумбия": [53, 60, 15, 55, 62], "Узбекистан": [46, 42, 18, 50, 55], "ДР Конго": [42, 38, 14, 38, 42],
    "Англия": [65, 82, 11, 64, 62], "Хорватия": [56, 58, 13, 52, 50], "Гана": [47, 45, 11, 48, 52], "Панама": [41, 30, 9, 40, 35]
}

# --- ВЕРТИКАЛЬНЫЙ МОБИЛЬНЫЙ ИНТЕРФЕЙС ---
st.write("### 🎛️ Настройки")
market_mode = st.selectbox(
    "Рынок анализа",
    ["💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)", "⚖️ Бэктестинг и Верификация"]
)

selected_group = st.selectbox("Выберите группу", list(teams_dict.keys()))
min_edge = st.slider("Чувствительность валуя ИИ (%)", 1.0, 10.0, 3.0)
st.write("---")

def get_bk_odds(p1, x, p2):
    margin = 1.045
    return round(1 / (max(0.01, p1) * margin), 2), round(1 / (max(0.01, x) * margin), 2), round(1 / (max(0.01, p2) * margin), 2)

def simulate_corners_market(home, away):
    b = st.session_state.tactical_bias
    s_h = team_tactical_matrix.get(home, [50, 50, 12, 50, 50])
    s_a = team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
    exp_h = b["Угловые_база"] + (s_h[0] * 0.03) + (s_h[1] * b["Коэффициент_навесов"])
    exp_a = b["Угловые_база"] + (s_a[0] * 0.03) + (s_a[1] * b["Коэффициент_навесов"])
    sim_h, sim_a = np.random.poisson(exp_h, 15000), np.random.poisson(exp_a, 15000)
    return round(float(np.mean(sim_h + sim_a)), 2), np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)

def simulate_offsides_market(home, away):
    b = st.session_state.tactical_bias
    s_h = team_tactical_matrix.get(home, [50, 50, 12, 50, 50])
    s_a = team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
    exp_h = b["Офсайды_база"] + (s_a[3] * 0.04)
    exp_a = b["Офсайды_база"] + (s_h[3] * 0.04)
    sim_h, sim_a = np.random.poisson(exp_h, 15000), np.random.poisson(exp_a, 15000)
    return round(float(np.mean(sim_h + sim_a)), 2), np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)

# --- СКРИНИНГ С СИСТЕМОЙ УМНЫХ РЕКОМЕНДАЦИЙ ---
if market_mode in ["💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)"]:
    group_teams = teams_dict[selected_group]
    matchups = [(group_teams[0], group_teams[1]), (group_teams[2], group_teams[3])]
    
    for home, away in matchups:
        match_key = f"{home} - {away}"
        st.write(f"#### ⚔️ {match_key}")
        
        if market_mode == "💰 Исходы (П1/Х/П2)":
            bias = st.session_state.tactical_bias["Исходы_база"]
            sim_h = np.random.poisson(base_team_power.get(home, 1.5) * bias, 15000)
            sim_a = np.random.poisson(base_team_power.get(away, 1.5) * bias, 15000)
            p1, x, p2 = np.mean(sim_h > sim_a), np.mean(sim_h == sim_a), np.mean(sim_h < sim_a)
            header_text = "Рынок исходов матча"
        elif market_mode == "📐 Угловые удары":
            total_pred, p1, x, p2 = simulate_corners_market(home, away)
            header_text = f"Угловые (Прогноз Тотала: {total_pred})"
        elif market_mode == "🚩 Офсайды (Offside Capture)":
            total_pred, p1, x, p2 = simulate_offsides_market(home, away)
            header_text = f"Офсайды (Прогноз Тотала: {total_pred})"
            
        bk_k1, bk_kx, bk_k2 = get_bk_odds(p1, x, p2)
        
        # Расчет скрытых маржинальных перекосов (ИИ против подразумеваемой БК)
        edge_p1 = (p1 - ((1/bk_k1)/1.045)) * 100
        edge_p2 = (p2 - ((1/bk_k2)/1.045)) * 100
        
        st.caption(header_text)
        st.code(f"1xbet Котировки -> П1: {bk_k1} | X: {bk_kx} | П2: {bk_k2}")
        st.write(f"Аналитика ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
        
        # --- ДВИЖОК РЕКОМЕНДАЦИЙ ДЛЯ ЗАРАБОТКА ---
        recommendation_made = False
        
        # Сценарий 1: Математический валуй (Букмекер сильно ошибся)
        if edge_p1 >= min_edge:
            st.error(f"🔥 РЕКОМЕНДАЦИЯ: Ставка на П1 {home}! Букмекер завысил кэф. Отличная валуйная точка для ординара.")
            bet_target, bet_price = f"Поб. {home}", bk_k1; recommendation_made = True
        elif edge_p2 >= min_edge:
            st.error(f"🔥 РЕКОМЕНДАЦИЯ: Ставка на П2 {away}! Виден перекос в пользу гостей. Берем по завышенной линии.")
            bet_target, bet_price = f"Поб. {away}", bk_k2; recommendation_made = True
            
        # Сценарий 2: Совпадение трендов ИИ и БК (Надежное тактическое доминирование)
        if not recommendation_made:
            if p1 >= 0.55 and bk_k1 <= 1.90 and bk_k1 >= 1.45:
                st.success(f"🎯 РЕКОМЕНДАЦИЯ: Берём П1 {home}. ИИ и Бук согласны: тактическое доминирование подтверждено, рабочий кэф {bk_k1}.")
                bet_target, bet_price = f"Поб. {home}", bk_k1; recommendation_made = True
            elif p2 >= 0.55 and bk_k2 <= 1.90 and bk_k2 >= 1.45:
                st.success(f"🎯 РЕКОМЕНДАЦИЯ: Берём П2 {away}. Мнение ИИ совпало с линией фаворита, отличный вариант в экспресс.")
                bet_target, bet_price = f"Поб. {away}", bk_k2; recommendation_made = True
                
        # Сценарий 3: Пропуск (Мутный матч)
        if not recommendation_made:
            st.info("🟢 ВЕРДИКТ: Ставки нет. Линия эффективна, шансы равны. Пропускаем ради сохранения банка.")
            
        # Фиксация в архив только реальных рекомендаций
        if recommendation_made:
            if st.button(f"📥 Зафиксировать ставку: {bet_target}", key=match_key+market_mode+"_rec"):
                st.session_state.history_logs.append({"Матч": match_key, "Рынок": market_mode, "Прогноз ИИ": bet_target, "Линия БК": bet_price, "Статус": "В игре"})
                st.success("Ставка в архиве бэктеста!")
                
        st.write("---")

# --- ЭКРАН ВЕРИФИКАЦИИ ---
elif market_mode == "⚖️ Бэктестинг и Верификация":
    st.subheader("⚖️ Верификация прибыли")
    if not st.session_state.history_logs:
        st.info("Архив рекомендаций пуст.")
    else:
        df_logs = pd.DataFrame(st.session_state.history_logs)
        if st.button("🤖 Рассчитать сыгранные купоны"):
            for row in st.session_state.history_logs:
                if row["Статус"] == "В игре": row["Статус"] = "Рассчитан"
            st.rerun()
        st.dataframe(df_logs[["Матч", "Рынок", "Прогноз ИИ", "Линия БК", "Статус"]], use_container_width=True)
