import streamlit as st
import re
from lunar_python import Solar, Lunar

# -------------------------------------------------------------
# 1. 頁面配置
# -------------------------------------------------------------
st.set_page_config(
    page_title="董大師 數字易經排盤系統",
    page_icon="🔮",
    layout="wide"
)

# -------------------------------------------------------------
# 2. 自訂 CSS 樣式：極致玄青金箔 ‧ 現代暗夜琉璃
# -------------------------------------------------------------
st.markdown("""
<style>
    /* 全局背景：極致玄青暗夜 */
    .stApp, body {
        background: radial-gradient(circle at 50% 0%, #1E2638 0%, #0B0E14 70%) !important;
        color: #E2E8F0 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang TC", "Microsoft JhengHei", sans-serif;
    }
    
    /* 限制整體寬度與邊距 */
    .block-container {
        max-width: 820px !important;
        padding-top: 2.5rem !important;
        padding-bottom: 3rem !important;
    }

    /* 主標題：鍍金漸層字體 */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #FFF0D0 0%, #D4AF37 50%, #AA771C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px !important;
        font-weight: 800;
        letter-spacing: 3px;
        margin-bottom: 24px;
        filter: drop-shadow(0 2px 8px rgba(212, 175, 55, 0.25));
    }

    /* ----------------------------------------------------
       暗琉璃浮雕卡片 (Form 面板)
       ---------------------------------------------------- */
    [data-testid="stForm"] {
        background: rgba(22, 28, 40, 0.65) !important;
        backdrop-filter: blur(16px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        padding: 24px !important;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }

    /* 隱藏輸入框提示 */
    [data-testid="stInputInstruction"],
    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* 輸入框 Label 統一對齊與高度 */
    label, [data-testid="stWidgetLabel"] p {
        color: #CBD5E1 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        margin-bottom: 8px !important;
        min-height: 22px !important;
        display: flex !important;
        align-items: center !important;
    }

    /* 精準修正數字輸入框 (stNumberInput) 的外框與對齊 */
    div[data-testid="stNumberInput"] > div {
        background-color: rgba(15, 20, 30, 0.85) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stNumberInput"] > div:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.3) !important;
    }

    /* 清除內部子層 div 的重複背景與邊框 */
    div[data-testid="stNumberInput"] div {
        border: none !important;
        background-color: transparent !important;
    }

    /* 調大輸入日期的數字字體 */
    .stNumberInput input {
        background-color: transparent !important;
        color: #FFF0D0 !important;
        font-weight: 800 !important;
        font-size: 22px !important;
        text-align: center !important;
        padding: 4px 0 !important;
    }

    /* 加減按鈕優化 */
    .stNumberInput button {
        background-color: rgba(255, 255, 255, 0.04) !important;
        color: #D4AF37 !important;
        border: none !important;
        transition: background 0.2s ease !important;
    }

    .stNumberInput button:hover {
        background-color: rgba(212, 175, 55, 0.2) !important;
        color: #FFF0D0 !important;
    }

    /* 金箔流光主按鈕 */
    .stButton > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #EAB308 0%, #D4AF37 50%, #A16207 100%) !important;
        color: #0F172A !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 20px !important;
        width: 100% !important;
        margin-top: 14px !important;
        letter-spacing: 2px !important;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.45) !important;
    }

    /* ----------------------------------------------------
       Tabs 頁籤 (曜石黑 + 香檳金邊框)
       ---------------------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        background-color: transparent !important;
        margin-top: 15px !important;
        margin-bottom: 20px !important;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px !important;
        background-color: rgba(15, 20, 30, 0.6) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        flex: 1 !important;
        text-align: center !important;
    }

    /* 未選中的 Tab */
    .stTabs [data-baseweb="tab"] *,
    .stTabs button *,
    .stTabs p {
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }

    /* 選中的 Tab */
    .stTabs [aria-selected="true"] {
        background: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid #D4AF37 !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.25) !important;
    }

    .stTabs [aria-selected="true"] * {
        color: #FFF0D0 !important;
        font-weight: 700 !important;
    }

    /* ----------------------------------------------------
       排盤結果卡片區
       ---------------------------------------------------- */
    .panel-header {
        color: #D4AF37 !important;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 15px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .section-subcaption {
        color: #94A3B8 !important;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    /* 同一格整合容器 (左右併排) */
    .combined-box {
        background: rgba(15, 23, 42, 0.6) !important;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        align-items: stretch;
    }

    .combined-left {
        flex: 1.2;
        min-width: 200px;
        display: flex;
        flex-direction: column;
    }

    .combined-right {
        flex: 1;
        min-width: 140px;
        display: flex;
        flex-direction: column;
        border-left: 1px solid rgba(212, 175, 55, 0.2);
        padding-left: 16px;
    }

    .matrix-divider {
        border: none;
        border-top: 1px dashed rgba(255, 255, 255, 0.1);
        margin: 8px 0;
        width: 100%;
    }

    @media (max-width: 480px) {
        .combined-right {
            border-left: none;
            border-top: 1px dashed rgba(212, 175, 55, 0.2);
            padding-left: 0;
            padding-top: 12px;
        }
    }

    .matrix-row {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin: 4px 0;
    }
    
   /* 普通星宿方格 */
    .star-box {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(30, 41, 59, 0.5) !important;
        border-radius: 10px;
        width: 60px;
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        flex-shrink: 0;
    }
    
    /* 核心格局星 (黃金高光) */
    .star-box-core {
        border: 2px solid #D4AF37 !important;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.2) 0%, rgba(30, 41, 59, 0.8) 100%) !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.35) !important;
        border-radius: 10px;
        width: 60px;
        height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        flex-shrink: 0;
    }
    
    .star-top, .star-bottom { 
        font-size: 15px; 
        font-weight: 700; 
        color: #F8FAFC !important; 
        line-height: 1.15;
    }
    
    /* 右上角標記 */
    .star-mark { 
        position: absolute;
        top: 2px;
        right: 4px;
        font-size: 13px !important; 
        font-weight: 800 !important; 
        color: #FFD700 !important; 
        text-shadow: 0 0 4px rgba(212, 175, 55, 0.6);
    }

    /* 詳細計算過程 Fieldset */
    .tk-fieldset {
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        padding: 14px 16px;
        margin-top: 18px;
        border-radius: 12px;
        background: rgba(11, 15, 20, 0.5) !important; 
    }
    .tk-legend {
        font-size: 13px;
        font-weight: 700;
        color: #D4AF37 !important;
        padding: 0 8px;
    }
    .tk-text-area {
        background-color: rgba(5, 8, 12, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important; 
        border-radius: 8px;
        padding: 12px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 13px;
        color: #CBD5E1 !important;
        white-space: pre-wrap;
        word-break: break-word;
        height: auto !important;
        overflow: visible !important;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. 八星對照表與算盤邏輯
# -------------------------------------------------------------
STAR_MAP = {
    '11': ('比肩', '最強'), '22': ('比肩', '最強'),
    '88': ('比肩', '強'),   '99': ('比肩', '強'),
    '66': ('比肩', '次強'), '77': ('比肩', '次強'),
    '33': ('比肩', '弱'),   '44': ('比肩', '弱'),
    
    '14': ('正印', '最強'), '41': ('正印', '最強'),
    '67': ('正印', '強'),   '76': ('正印', '強'),
    '39': ('正印', '次強'), '93': ('正印', '次強'),
    '28': ('正印', '弱'),   '82': ('正印', '弱'),

    '13': ('食神', '最強'), '31': ('食神', '最強'),
    '68': ('食神', '強'),   '86': ('食神', '強'),
    '49': ('食神', '次強'), '94': ('食神', '次強'),
    '27': ('食神', '弱'),   '72': ('食神', '弱'),

    '19': ('正官', '最強'), '91': ('正官', '最強'),
    '78': ('正官', '強'),   '87': ('正官', '強'),
    '34': ('正官', '次強'), '43': ('正官', '次強'),
    '26': ('正官', '弱'),   '62': ('正官', '弱'),

    '17': ('七煞', '最強'), '71': ('七煞', '最強'),
    '89': ('七煞', '強'),   '98': ('七煞', '強'),
    '46': ('七煞', '次強'), '64': ('七煞', '次強'),
    '23': ('七煞', '弱'),   '32': ('七煞', '弱'),

    '16': ('偏印', '最強'), '61': ('偏印', '最強'),
    '47': ('偏印', '強'),   '74': ('偏印', '強'),
    '38': ('偏印', '次強'), '83': ('偏印', '次強'),
    '29': ('偏印', '弱'),   '92': ('偏印', '弱'),

    '12': ('傷官', '最強'), '21': ('傷官', '最強'),
    '69': ('傷官', '強'),   '96': ('傷官', '強'),
    '48': ('傷官', '次強'), '84': ('傷官', '次強'),
    '37': ('傷官', '弱'),   '73': ('傷官', '弱'),

    '18': ('劫財', '最強'), '81': ('劫財', '最強'),
    '97': ('劫財', '強'),   '79': ('劫財', '強'),
    '36': ('劫財', '次強'), '63': ('劫財', '次強'),
    '24': ('劫財', '弱'),   '42': ('劫財', '弱'),
}

COMPOUND_PATTERN_MAP = {
    19: "正官格", 28: "比肩格", 29: "比肩格",
    37: "傷官格", 38: "比肩格", 39: "傷官格",
    46: "七煞格", 47: "比肩格", 48: "傷官格"
}

TOP_ROW_STARS = {"比肩", "正印", "食神", "正官"}
BOTTOM_ROW_STARS = {"七煞", "偏印", "傷官", "劫財"}

HIDDEN_ENERGY_MAP = {
    "正官": "七煞", "正印": "偏印", "比肩": "劫財", "食神": "劫財",
    "七煞": "正官", "偏印": "正印", "劫財": "食神", "傷官": "食神"
}

def process_digits_and_pairs(year: int, month: int, day: int):
    year_s, month_s, day_s = str(abs(year)), str(abs(month)), str(abs(day))
    raw_seq = f"{year_s}{month_s}{day_s}"
    pairs_info = []

    n = len(raw_seq)
    i = 0
    
    while i < n - 1:
        current_char = raw_seq[i]
        
        # 情況 1：當前字是 '5'，與下一個數字組成兩位數（如 50、53 等）
        if current_char == '5':
            pair = f"5{raw_seq[i+1]}"
            pairs_info.append({
                "pair": pair,
                "star": "比肩",
                "strength": "強",
                "is_infinite": False
            })
            i += 1
            continue

        # 情況 2：下一個數字是 '5'
        if raw_seq[i+1] == '5':
            j = i + 1
            while j < n and raw_seq[j] == '5':
                j += 1
            
            prev_d = current_char
            
            # 只有當「5 前面不是 0」且「5 後面還有數字且後面也不是 0」時，才允許搭橋！
            if prev_d != '0' and j < n and raw_seq[j] != '0':
                next_d = raw_seq[j]
                target_pair = prev_d + next_d
                star_name, strength = STAR_MAP.get(target_pair, (None, None))
                fives_str = raw_seq[i+1:j]
                if star_name:
                    pairs_info.append({
                        "pair": f"{prev_d}{fives_str}{next_d}➔{target_pair}", 
                        "star": star_name, 
                        "strength": strength, 
                        "is_infinite": True
                    })
                i = j  # 搭橋成功，指標跳過 5
                continue
            else:
                # 拒絕搭橋，形成前數字與 5 的兩位數組合 (如 85)
                pair = f"{current_char}5"
                pairs_info.append({
                    "pair": pair, 
                    "star": "比肩", 
                    "strength": "強", 
                    "is_infinite": False
                })
                i += 1
                continue

        # 情況 3：一般相鄰兩位數字組合
        pair = raw_seq[i:i+2]
        star_name, strength = ("比肩", "強") if '0' in pair else STAR_MAP.get(pair, (None, None))
        if star_name:
            pairs_info.append({
                "pair": pair, 
                "star": star_name, 
                "strength": strength, 
                "is_infinite": False
            })
        i += 1

    return raw_seq, pairs_info

def calculate_destiny_chart(year: int, month: int, day: int):
    raw_seq, pairs_info = process_digits_and_pairs(year, month, day)
    
    full_digits = [int(ch) for ch in raw_seq if ch.isdigit()]
    pattern_num = sum(full_digits)
    
    goal_num = pattern_num
    while goal_num >= 10:
        goal_num = sum(int(c) for c in str(goal_num))
        
    if pattern_num in COMPOUND_PATTERN_MAP:
        pattern_name = COMPOUND_PATTERN_MAP[pattern_num]
    else:
        p_pair = str(pattern_num)
        star = STAR_MAP.get(p_pair, ("比肩", "普通"))[0]
        pattern_name = f"{star}格"

    core_pattern_star = pattern_name.replace("格", "")

    star_counts = {}
    star_has_infinite = {}
    for p in pairs_info:
        s_name = p['star']
        star_counts[s_name] = star_counts.get(s_name, 0) + 1
        if p['is_infinite']:
            star_has_infinite[s_name] = True

    processed_stars = []
    visited = set()
    for p in pairs_info:
        s_name = p['star']
        if s_name in visited: continue
        visited.add(s_name)
        count = star_counts[s_name]
        mark = "∞" if star_has_infinite.get(s_name, False) else (str(count) if count > 1 else "")
        processed_stars.append({
            "name": s_name,
            "top_char": s_name[0] if len(s_name) > 0 else "",
            "bottom_char": s_name[1] if len(s_name) > 1 else "",
            "mark": mark,
            "is_hidden": False
        })

    top_stars = [s for s in processed_stars if s['name'] in TOP_ROW_STARS]
    bottom_stars = [s for s in processed_stars if s['name'] in BOTTOM_ROW_STARS]
    
    num_cols = max(len(top_stars), len(bottom_stars))
    if num_cols == 0: num_cols = 1
    
    matrix_top = [None] * num_cols
    matrix_bottom = [None] * num_cols

    for t_idx, star in enumerate(top_stars):
        if t_idx < num_cols: matrix_top[t_idx] = star
    for b_idx, star in enumerate(bottom_stars):
        if b_idx < num_cols: matrix_bottom[b_idx] = star

    for c in range(num_cols):
        if matrix_top[c] is not None and matrix_bottom[c] is None:
            hidden_name = HIDDEN_ENERGY_MAP.get(matrix_top[c]['name'], "")
            if hidden_name:
                matrix_bottom[c] = {"name": hidden_name, "top_char": hidden_name[0], "bottom_char": hidden_name[1], "mark": "x", "is_hidden": True}
        elif matrix_bottom[c] is not None and matrix_top[c] is None:
            hidden_name = HIDDEN_ENERGY_MAP.get(matrix_bottom[c]['name'], "")
            if hidden_name:
                matrix_top[c] = {"name": hidden_name, "top_char": hidden_name[0], "bottom_char": hidden_name[1], "mark": "x", "is_hidden": True}

    grid_2d = [matrix_top, matrix_bottom]
    core_r, core_c = -1, -1
    core_item = None
    has_exact_pattern_star = False

    for r in range(2):
        for c in range(num_cols):
            item = grid_2d[r][c]
            if item and item['name'] == core_pattern_star and not item.get('is_hidden', False):
                core_r, core_c, core_item, has_exact_pattern_star = r, c, item, True
                break
        if core_r != -1: break

    # 未入格修正：取末位星做為中心
    if not has_exact_pattern_star:
        pattern_name = f"{pattern_name}-未入格"
        fallback_star_name = None
        for p in reversed(pairs_info):
            if p.get('star'):
                fallback_star_name = p['star']
                break
        
        if fallback_star_name:
            for r in range(2):
                for c in range(num_cols):
                    item = grid_2d[r][c]
                    if item and item['name'] == fallback_star_name and not item.get('is_hidden', False):
                        core_r, core_c, core_item = r, c, item
                        break
                if core_r != -1: break

    pattern_layout_tuples = []
    if core_item:
        opp_r = 1 if core_r == 0 else 0
        pattern_layout_tuples.append(("+", f"{core_item['name']}{core_item['mark']}"))

        opp_side_items = [grid_2d[opp_r][c]['name'] + grid_2d[opp_r][c]['mark'] for c in (core_c - 1, core_c + 1) if 0 <= c < num_cols and grid_2d[opp_r][c]]
        if opp_side_items: pattern_layout_tuples.append(("-", " ".join(opp_side_items)))

        opp_item = grid_2d[opp_r][core_c]
        if opp_item: pattern_layout_tuples.append(("+", f"{opp_item['name']}{opp_item['mark']}"))

        same_side_items = [grid_2d[core_r][c]['name'] + grid_2d[core_r][c]['mark'] for c in (core_c - 1, core_c + 1) if 0 <= c < num_cols and grid_2d[core_r][c]]
        if same_side_items: pattern_layout_tuples.append(("-", " ".join(same_side_items)))

    clean_top = [item for item in matrix_top if item is not None]
    clean_bottom = [item for item in matrix_bottom if item is not None]

    return {
        "raw_seq": raw_seq,
        "pattern_num": pattern_num,
        "goal_num": f"{goal_num}號人",
        "pattern_name": pattern_name,
        "core_item": core_item,
        "matrix_top": clean_top,
        "matrix_bottom": clean_bottom,
        "pairs_info": pairs_info,
        "pattern_layout_tuples": pattern_layout_tuples
    }

# -------------------------------------------------------------
# 4. Web UI 渲染模組
# -------------------------------------------------------------
def build_star_box_html(item, core_item):
    if not item: return ''
    is_core = (core_item is not None and item == core_item)
    box_class = "star-box-core" if is_core else "star-box"
    mark_html = f'<div class="star-mark">{item["mark"]}</div>' if item["mark"] else ''
    return f'<div class="{box_class}">{mark_html}<div class="star-top">{item["top_char"]}</div><div class="star-bottom">{item["bottom_char"]}</div></div>'

def render_panel(res, title_prefix, date_desc):
    core_item = res['core_item']
    top_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_top']])
    bottom_boxes_html = "".join([build_star_box_html(item, core_item) for item in res['matrix_bottom']])

    st.markdown(f"<div class='panel-header'>〔 {title_prefix}排盤結果 〕</div>", unsafe_allow_html=True)
    
    layout_content = ""
    if res['pattern_layout_tuples']:
        for sign, content in res['pattern_layout_tuples']:
            layout_content += f"<div style='margin: 6px 0;'><span style='color:#D4AF37; font-size: 16px; font-weight:800;'>{sign} &nbsp; {content}</span></div>"
    else:
        layout_content = "<div style='color:#64748B; font-size:14px;'>無能量排列組合</div>"

    st.markdown(f"""
    <div class="combined-box">
        <div class="combined-left">
            <div class="section-subcaption">{title_prefix} ‧ 神煞排盤矩陣</div>
            <div class="matrix-row">{top_boxes_html}</div>
            <hr class="matrix-divider">
            <div class="matrix-row">{bottom_boxes_html}</div>
        </div>
        <div class="combined-right">
            <div class="section-subcaption">{title_prefix} ‧ 格局能量排列</div>
            <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; min-height: 80px;">
                {layout_content}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    detail_text = f"{date_desc}\n"
    detail_text += f"【處理後數字串】: {res['raw_seq']}\n"
    detail_text += f"【格局數】: {res['pattern_num']}  ｜  【目標數】: {res['goal_num']}  ｜  【格局】: {res['pattern_name']}\n"
    detail_text += "────────────────────────────────────────\n"
    detail_text += "【兩兩拆解與歸類詳情】:\n"
    for p in res['pairs_info']:
        inf_tag = " [無限大 ∞]" if p['is_infinite'] else ""
        detail_text += f"  • 組合 [{p['pair']}] ➔ {p['star']} ({p['strength']}){inf_tag}\n"
    
    st.markdown(f"""
    <fieldset class="tk-fieldset">
        <legend class="tk-legend">{title_prefix} - 詳細計算過程</legend>
        <div class="tk-text-area">{detail_text}</div>
    </fieldset>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. 主畫面介面
# -------------------------------------------------------------
st.markdown("<div class='main-title'>董大師 ‧ 數字易經排盤系統</div>", unsafe_allow_html=True)

# 輸入表單卡片
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
solar_obj = Solar.fromYmd(year, month, day)
lunar_obj = solar_obj.getLunar()
ly, lm, ld = lunar_obj.getYear(), lunar_obj.getMonth(), lunar_obj.getDay()

is_leap = "閏" if lm < 0 else ""
lunar_res = calculate_destiny_chart(ly, abs(lm), ld)

# 切換頁籤
tab1, tab2 = st.tabs(["國曆排盤結果", "農曆排盤結果"])

with tab1:
    render_panel(solar_res, "國曆", f"【國曆生日】: {year}年{month}月{day}日")

with tab2:
    render_panel(lunar_res, "農曆", f"【自動轉換農曆】: {ly}年{is_leap}{abs(lm)}月{ld}日 (對應國曆 {year}/{month}/{day})")
