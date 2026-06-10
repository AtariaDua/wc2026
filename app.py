# 🎯 ГЕНЕРАЦИЯ ТОП-5 ВАЛУЙНЫХ ОРДИНАРОВ (Максимальный ROI с фильтром >= 3%)
    st.write("### 🎯 Топ-5 Одиночных ставок (Ошибки БК)")
    
    # Отфильтровываем только реальные перекосы от +3% и выше
    profitable_ordinars = df_all[df_all["edge"] >= 3.0].sort_values(by="edge", ascending=False).head(5)
    
    if not profitable_ordinars.empty:
        for idx, row in profitable_ordinars.iterrows():
            with st.container():
                st.error(f"🔥 **{row['match']}** ({row['market']}) -> **{row['type']}** за **{row['odds']}**")
                st.write(f"Чистый перевес над линией: **+{row['edge']:.1f}%** | Вероятность по симуляции: {row['prob']*100:.1f}%")
                if st.button(f"📥 Забрать ординар в архив #{idx}", key=f"ord_{idx}"):
                    st.session_state.history_logs.append({"Матч": row['match'], "Рынок": row['market'], "Прогноз ИИ": row['type'], "Линия БК": row['odds'], "Статус": "В игре"})
                    st.toast("Ординар зафиксирован!")
                st.write("")
    else:
        st.info("🟢 Крупных ошибок букмекера (валуев от +3%) в этом туре не найдено. Линия БК слишком эффективна. Для ставок используйте надежный 'ИИ-Экспресс Дня'.")
