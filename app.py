def render_panel(res, title_prefix, date_desc):
    core_item = res['core_item']
    top_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_top']])
    bottom_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_bottom']])

    st.markdown(f"<div class='panel-header'>〔 {title_prefix}排盤結果 〕</div>", unsafe_allow_html=True)
    
    # 拆解命格名稱與未入格標籤
    pattern_str = res['pattern_name']
    if "-未入格" in pattern_str:
        pattern_main = pattern_str.replace("-未入格", "")
        badge_html = '<span class="status-badge status-unbound">未入格</span>'
    else:
        pattern_main = pattern_str
        badge_html = '<span class="status-badge status-bound">已入格</span>'

    layout_content = ""
    if res['pattern_layout_tuples']:
        for sign, content in res['pattern_layout_tuples']:
            layout_content += f"<div style='margin: 4px 0;'><span style='color:#D4AF37; font-size: 15px; font-weight:800;'>{sign} &nbsp; {content}</span></div>"
    else:
        layout_content = "<div style='color:#64748B; font-size:14px;'>無能量排列組合</div>"

    # 💡 移除 HTML 縮排與空行，避免觸發 Streamlit 的 Code Block 判定
    panel_html = f"""<div class="combined-box">
<div class="combined-col combined-core">
<div class="section-subcaption">{title_prefix} ‧ 核心指標</div>
<div class="core-metrics-wrapper">
<div class="metric-item">
<span class="metric-label">🎯 目標數</span>
<span class="metric-value-gold">{res['goal_num']}</span>
</div>
<div class="metric-item">
<span class="metric-label">🔢 格局數</span>
<span class="metric-value-gold">{res['pattern_num']}</span>
</div>
<div class="metric-item">
<span class="metric-label">☯️ 命格屬性</span>
<div style="display:flex; align-items:center;">
<span class="metric-value-text">{pattern_main}</span>
{badge_html}
</div>
</div>
</div>
</div>
<div class="combined-col combined-matrix">
<div class="section-subcaption">{title_prefix} ‧ 神煞排盤矩陣</div>
<div class="matrix-wrapper">
<div class="matrix-row">{top_boxes_html}</div>
<hr class="matrix-divider">
<div class="matrix-row">{bottom_boxes_html}</div>
</div>
</div>
<div class="combined-col combined-energy">
<div class="section-subcaption">{title_prefix} ‧ 格局能量排列</div>
<div class="energy-wrapper">
{layout_content}
</div>
</div>
</div>"""

    st.markdown(panel_html, unsafe_allow_html=True)

    detail_text = f"{date_desc}\n"
    detail_text += f"【處理後數字串】: {res['raw_seq']}\n"
    detail_text += f"【格局數】: {res['pattern_num']}  ｜  【目標數】: {res['goal_num']}  ｜  【格局】: {res['pattern_name']}\n"
    detail_text += "────────────────────────────────────────\n"
    detail_text += "【兩兩拆解與歸類詳情】:\n"
    for p in res['pairs_info']:
        inf_tag = " [無限大 ∞]" if p['is_infinite'] else ""
        detail_text += f"  • 組合 [{p['pair']}] ➔ {p['star']} ({p['strength']}){inf_tag}\n"
    
    st.markdown(f"""<fieldset class="tk-fieldset">
<legend class="tk-legend">{title_prefix} - 詳細計算過程</legend>
<div class="tk-text-area">{detail_text}</div>
</fieldset>""", unsafe_allow_html=True)
