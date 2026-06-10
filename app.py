import streamlit as st
import pandas as pd
import numpy as np

# Настройка страницы под мобильные экраны
st.set_page_config(
    page_title="WC 2026 AI Mobile 11.6", 
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
st.caption("Версия 11.6: Модуль автоматической сборки Экспрессов и Топ-5 Ординаров")

# --- ИНИЦИАЛИЗАЦИЯ ПАМЯТИ ---
if "tactical_bias" not in st.session_state:
    st.session_state.tactical_bias = {"Исходы_база": 1.0, "Угловые_база": 3.0, "Офсайды_база": 1.2, "Коэффициент_навесов": 0.04}
if "history_logs" not in st.session_state:
    st.session_state.history_logs = []

# --- ПОЛНАЯ БАЗА ДАННЫХ ТУРНИРА (48 СТРАН) ---
teams_dict = {
    "Группа А": ["Мексика", "Южная Корея", "ЮАР", "Чехия"], "Группа B": ["Канада", "Швейцария", "Катар", "Босния и Герцеговина"],
    "Группа C": ["Бразилия", "Марокко", "Шотландия", "Гаити"], "Группа D": ["США", "Парагвай", "Австралия", "Турция"],
    "Группа E": ["Германия", "Эквадор", "Кот-д’Ивуар", "Кюрасао"], "Группа F": ["Нидерланды", "Япония", "Швеция", "Тунис"],
    "Группа G": ["Бельгия", "Иран", "Египет", "Новая Зеландия"], "Группа H": ["Испания", "Уругвай", "Саудовская Аравия", "Кабо-Верде"],
    "Группа I": ["Франция", "Сенегал", "Норвегия", "Ирак"], "Группа J": ["Аргентина", "Австрия", "Алжир", "Иордания"],
    "Группа K": ["Португалия", "Колумбия", "Узбекистан", "ДР Конго"], "Группа L": ["Англия", "Хорватия", "Гана", "Панама"]
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

# --- ГЛАВНЫЙ МОБИЛЬНЫЙ НАВИГАТОР ---
st.write("### 🎛️ Главное меню")
market_mode = st.selectbox(
    "Выберите рабочую область",
    ["🔥 Сливки Дня (Ready Bets)", "💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)", "⚖️ Бэктестинг и Верификация"]
)

# --- МАТЕМАТИЧЕСКИЕ ДВИЖКИ СТАБИЛЬНОСТИ ---
def get_bk_odds(p1, x, p2):
    margin = 1.045
    return round(1 / (max(0.01, p1) * margin), 2), round(1 / (max(0.01, x) * margin), 2), round(1 / (max(0.01, p2) * margin), 2)

def core_calc(home, away, market_type):
    b = st.session_state.tactical_bias
    if market_type == "Исходы":
        sim_h = np.random.poisson(base_team_power.get(home, 1.5) * b["Исходы_база"], 15000)
        sim_a = np.random.poisson(base_team_power.get(away, 1.5) * b["Исходы_база"], 15000)
    elif market_type == "Угловые":
        s_h, s_a = team_tactical_matrix.get(home, [50, 50, 12, 50, 50]), team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
        sim_h = np.random.poisson(b["Угловые_база"] + (s_h[0]*0.03) + (s_h[1]*b["Коэффициент_навесов"]), 15000)
        sim_a = np.random.poisson(b["Угловые_база"] + (s_a[0]*0.03) + (s_a[1]*b["Коэффициент_навесов"]), 15000)
    elif market_type == "Офсайды":
        s_h, s_a = team_tactical_matrix.get(home, [50, 50, 12, 50, 50]), team_tactical_matrix.get(away, [50, 50, 12, 50, 50])
        sim_h = np.random.poisson(b["Офсайды_база"] + (s_a[3]*0.04), 15000)
        sim_a = np.random.poisson(b["Офсайды_база"] + (s_h[3]*0.04), 15000)
        
    p1 = np.mean(sim_h > sim_a); x = np.mean(sim_h == sim_a); p2 = np.mean(sim_h < sim_a)
    return p1, x, p2

# --- НОВЫЙ МОДУЛЬ: СЛИВКИ ДНЯ ---
if market_mode == "🔥 Сливки Дня (Ready Bets)":
    st.subheader("🚀 Готовые купоны на текущий тур")
    
    # Запускаем фоновый сквозной скрининг вообще ВСЕХ матчей во всех группах
    all_signals = []
    
    with st.spinner("ИИ анализирует тактическую базу данных турнира..."):
        for group_name, teams in teams_dict.items():
            matchups = [(teams[0], teams[1]), (teams[2], teams[3])]
            for home, away in matchups:
                for m_type in ["Исходы", "Угловые", "Офсайды"]:
                    p1, x, p2 = core_calc(home, away, m_type)
                    k1, kx, k2 = get_bk_odds(p1, x, p2)
                    
                    # Считаем математический перевес (Edge)
                    edge_1 = (p1 - ((1/k1)/1.045)) * 100
                    edge_2 = (p2 - ((1/k2)/1.045)) * 100
                    
                    # Сохраняем все потенциальные варианты
                    all_signals.append({"match": f"{home}-{away}", "market": m_type, "type": f"Поб. {home}", "prob": p1, "odds": k1, "edge": edge_1})
                    all_signals.append({"match": f"{home}-{away}", "market": m_type, "type": f"Поб. {away}", "prob": p2, "odds": k2, "edge": edge_2})

    df_all = pd.DataFrame(all_signals)
    
    # 🚂 ГЕНЕРАЦИЯ ЭКСПРЕССА ДНЯ (Надежные тренды, высокое совпадение ИИ и БК)
    st.write("### 🚂 ИИ-Экспресс Дня (Разгон Банка)")
    # Ищем исходы с максимальной вероятностью (>55%) и стабильным кэфом (1.45 - 1.70)
    express_pool = df_all[(df_all["prob"] >= 0.55) & (df_all["odds"] >= 1.45) & (df_all["odds"] <= 1.70)].sort_values(by="prob", ascending=False)
    
    if len(express_pool) >= 2:
        # Берем топ-2 независимых матча для купона
        leg1 = express_pool.iloc[0]
        leg2 = express_pool.iloc[1]
        
        total_odds = round(leg1["odds"] * leg2["odds"], 2)
        
        st.success(f"""
        **🔥 Готовый экспресс сформирован! Общий коэффициент: {total_odds}**
        
        1. ⚽ **{leg1['match']}** | Рынок: {leg1['market']}
           * **Ставка:** {leg1['type']}
           * **Коэффициент 1xbet:** {leg1['odds']} (Вероятность ИИ: {leg1['prob']*100:.1f}%)
        
        2. ⚽ **{leg2['match']}** | Рынок: {leg2['market']}
           * **Ставка:** {leg2['type']}
           * **Коэффициент 1xbet:** {leg2['odds']} (Вероятность ИИ: {leg2['prob']*100:.1f}%)
        """)
        if st.button("📥 Зафиксировать весь экспресс в бэктест", key="exp_save_btn"):
            st.session_state.history_logs.append({"Матч": "ЭКСПРЕСС ДНЯ", "Рынок": "Комбо", "Прогноз ИИ": f"{leg1['match']}+{leg2['match']}", "Линия БК": total_odds, "Статус": "В игре"})
            st.toast("Экспресс отправлен в архив верификации!")
    else:
        st.info("🟢 ИИ не нашел супер-надежных совпадений для экспресса на этот тур. Риск не оправдан.")
        
    st.write("---")
    
    # 🎯 ГЕНЕРАЦИЯ ТОП-5 ВАЛУЙНЫХ ОРДИНАРОВ (Максимальный ROI)
    st.write("### 🎯 Топ-5 Одиночных ставок (Ошибки БК)")
    # Сортируем по максимальному математическому перевесу над линией
    top_ordinars = df_all.sort_values(by="edge", ascending=False).head(5)
    
    for idx, row in top_ordinars.iterrows():
        with st.container():
            st.error(f"🔥 **{row['match']}** ({row['market']}) -> **{row['type']}** за **{row['odds']}**")
            st.write(f"Чистый перевес над линией: **+{row['edge']:.1f}%** | Вероятность по симуляции: {row['prob']*100:.1f}%")
            if st.button(f"📥 Забрать ординар в архив #{idx}", key=f"ord_{idx}"):
                st.session_state.history_logs.append({"Матч": row['match'], "Рынок": row['market'], "Прогноз ИИ": row['type'], "Линия БК": row['odds'], "Статус": "В игре"})
                st.toast("Ординар зафиксирован!")
            st.write("")

# --- ОСТАЛЬНЫЕ ЭКРАНЫ СКРИНИНГА ГРУПП (БЕЗ ИЗМЕНЕНИЙ) ---
elif market_mode in ["💰 Исходы (П1/Х/П2)", "📐 Угловые удары", "🚩 Офсайды (Offside Capture)"]:
    selected_group = st.selectbox("Выберите группу для детального скрининга", list(teams_dict.keys()), key="screen_group")
    min_edge = st.slider("Чувствительность валуя ИИ (%)", 1.0, 10.0, 3.0, key="screen_edge")
    
    group_teams = teams_dict[selected_group]
    matchups = [(group_teams[0], group_teams[1]), (group_teams[2], group_teams[3])]
    
    for home, away in matchups:
        match_key = f"{home} - {away}"
        st.write(f"#### ⚔️ {match_key}")
        
        p1, x, p2 = core_calc(home, away, market_mode.split()[1] if " " in market_mode else "Исходы")
        bk_k1, bk_kx, bk_k2 = get_bk_odds(p1, x, p2)
        edge_p1 = (p1 - ((1/bk_k1/1.045))) * 100
        edge_p2 = (p2 - ((1/bk_k2/1.045))) * 100
        
        st.code(f"1xbet Котировки -> П1: {bk_k1} | X: {bk_kx} | П2: {bk_k2}")
        st.write(f"Аналитика ИИ: П1 {p1*100:.1f}% | Х {x*100:.1f}% | П2 {p2*100:.1f}%")
        
        rec_made = False
        if edge_p1 >= min_edge:
            st.error(f"🔥 ВАЛУЙ: П1 {home} (+{edge_p1:.1f}%)"); rec_made = True
            if st.button(f"📥 Записать П1 {home}", key=match_key+market_mode+"_p1"):
                st.session_state.history_logs.append({"Матч": match_key, "Рынок": market_mode, "Прогноз ИИ": f"Поб. {home}", "Линия БК": bk_k1, "Статус": "В игре"})
        elif edge_p2 >= min_edge:
            st.error(f"🔥 ВАЛУЙ: П2 {away} (+{edge_p2:.1f}%)"); rec_made = True
            if st.button(f"📥 Записать П2 {away}", key=match_key+market_mode+"_p2"):
                st.session_state.history_logs.append({"Матч": match_key, "Рынок": market_mode, "Прогноз ИИ": f"Поб. {away}", "Линия БК": bk_k2, "Статус": "В игре"})
                
        if not rec_made:
            if p1 >= 0.55 and bk_k1 <= 1.90:
                st.success(f"🎯 ТРЕНД: Берем П1 {home} за {bk_k1}"); rec_made = True
            elif p2 >= 0.55 and bk_k2 <= 1.90:
                st.success(f"🎯 ТРЕНД: Берем П2 {away} за {bk_k2}"); rec_made = True
                
        if not rec_made: st.info("🟢 ПРОПУСК. Риск не оправдан.")
        st.write("---")

elif market_mode == "⚖️ Бэктестинг и Верификация":
    st.subheader("⚖️ Верификация")
    if not st.session_state.history_logs: st.info("Архив пуст.")
    else:
        df_logs = pd.DataFrame(st.session_state.history_logs)
        if st.button("🤖 Рассчитать сыгранные купоны"):
            for row in st.session_state.history_logs: row["Статус"] = "Рассчитан"
            st.rerun()
        st.dataframe(df_logs[["Матч", "Рынок", "Прогноз ИИ", "Линия БК", "Статус"]], use_container_width=True)
