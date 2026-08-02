# -------------------------------------------------------------
# 頁面狀態管理 (Page Session State)
# -------------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'main'

def go_to_analysis():
    st.session_state.page = 'analysis'

def go_to_main():
    st.session_state.page = 'main'


# -------------------------------------------------------------
# 頁面 1：主要排盤結果頁 (Main Page)
# -------------------------------------------------------------
if st.session_state.page == 'main':
    st.markdown("<div class='main-title'>董大師 ‧ 數字易經排盤系統</div>", unsafe_allow_html=True)

    with st.form("birth_form"):
        col_y, col_m, col_d = st.columns([1.2, 1, 1])
        with col_y:
            year = st.number_input("國曆西元年", min_value=1900, max_value=2100, value=1982, step=1)
        with col_m:
            month = st.number_input("月", min_value=1, max_value=12, value=6, step=1)
        with col_d:
            day = st.number_input("日", min_value=1, max_value=31, value=31, step=1)
        
        submit_btn = st.form_submit_button("一 鍵 自 動 排 盤")

    # 執行計算
    solar_res = calculate_destiny_chart(year, month, day)
    st.session_state.current_res = solar_res # 暫存結果給深度分析頁面

    tab1, tab2 = st.tabs(["國曆排盤結果", "農曆排盤結果"])
    with tab1:
        render_panel(solar_res, "國曆", f"【國曆生日】: {year}年{month}月{day}日")
    with tab2:
        solar_obj = Solar.fromYmd(year, month, day)
        lunar_obj = solar_obj.getLunar()
        ly, lm, ld = lunar_obj.getYear(), lunar_obj.getMonth(), lunar_obj.getDay()
        is_leap = "閏" if lm < 0 else ""
        lunar_res = calculate_destiny_chart(ly, abs(lm), ld)
        render_panel(lunar_res, "農曆", f"【自動轉換農曆】: {ly}年{is_leap}{abs(lm)}月{ld}日")

    st.markdown("<br>", unsafe_allow_html=True)
    # 🆕 新增跳轉按鈕
    st.button("🔮 解鎖我的生命靈數 AI 深度解析報告", on_click=go_to_analysis, use_container_width=True)


# -------------------------------------------------------------
# 頁面 2：生命靈數深度分析頁 (AI Analysis Page)
# -------------------------------------------------------------
elif st.session_state.page == 'analysis':
    st.button("⬅️ 返回排盤主頁", on_click=go_to_main)
    
    res = st.session_state.get('current_res', None)
    if res:
        # 提取目標數（例如 "3號人" -> 3）
        goal_num_str = res['goal_num']
        goal_int = int(re.search(r'\d+', goal_num_str).group())
        num_info = LIFE_NUMBERS_DB.get(goal_int, {})

        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>🎯 您的目標數：{num_info.get('title', '')}</h1>", unsafe_allow_html=True)
        st.write("---")

        # 展示四維個人報告卡 (4 Cards)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🌟 先天正面特質")
            st.info(" • " + "\n • ".join(num_info.get('positive', [])))
            
            st.subheader("⚠️ 情緒與負面盲點")
            st.warning(" • " + "\n • ".join(num_info.get('negative', [])))

        with c2:
            st.subheader("🏆 落地成功鑰匙")
            st.success(" • " + "\n • ".join(num_info.get('success', [])))

            st.subheader("🧘 心智不成熟與轉化課題")
            st.error(" • " + "\n • ".join(num_info.get('immature', [])))

        st.write("---")
        
        # AI 大師客製化報告區塊
        st.subheader("🤖 AI 大師專屬天賦與突破指南")
        with st.spinner("董大師 AI 正在精算您的能量格局..."):
            # 這邊可接入 OpenAI / Gemini API
            # 以下為模擬 AI 輸出的內容範本：
            st.markdown(f"""
            > **【董大師 AI 洞察摘要】**
            > 
            > 您屬於 **{num_info.get('title', '')}**，核心命格為 **{res['pattern_name']}**（格局數：{res['pattern_num']}）。
            >
            > * **核心天賦**：你具備極強的 **{num_info.get('positive', [''])[0]}** 與 **{num_info.get('positive', [''])[1]}** 能力，若將資源集中於目標，非常容易在職場展現頭角。
            > * **成功轉化點**：關鍵在於發揮「{num_info.get('success', [''])[0]}」，這能讓你的能量真正落地。
            > * **突破盲點**：需特別留意處於壓力時容易陷入「{num_info.get('negative', [''])[0]}」的狀態，建議保持覺察，學習鬆綁控制慾。
            """)
