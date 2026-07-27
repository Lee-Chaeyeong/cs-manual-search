import streamlit as st
import pandas as pd
import re
import os
from PIL import Image

# 1. 브라우저 탭 파비콘용 블루 로고 로딩
logo_img = None
logo_filename = "20251218 PNG 축약형 로고_블루.png"

if os.path.exists(logo_filename):
    try:
        logo_img = Image.open(logo_filename)
    except Exception:
        logo_img = None
else:
    for f in os.listdir('.'):
        if f.lower().endswith('.png'):
            try:
                logo_img = Image.open(f)
                break
            except Exception:
                pass

# 2. 페이지 기본 설정
st.set_page_config(
    page_title="BTX CS 응대 매뉴얼 검색", 
    page_icon=logo_img if logo_img else "🚕", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. 레이아웃 고도화 커스텀 CSS (사이드바 폭 축소 + 가운데 정렬 + 라인/그림자 강화)
st.markdown("""
    <style>
    /* Pretendard 폰트 전면 적용 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

    html, body, .stApp {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    /* 스트림릿 내장 아이콘 폰트 보호 */
    [data-testid="stIconMaterial"], 
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stBaseButton-headerNoPadding"] *,
    [data-testid="stFileUploaderDropzone"] i,
    .material-symbols-outlined,
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'StreamlitIcons' !important;
    }

    /* 메인 화면 여백 및 배경 정돈 */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }

    /* 📌 1. 왼쪽 사이드바 폭 축소 및 디자인 정돈 */
    [data-testid="stSidebar"] {
        min-width: 230px !important;
        max-width: 240px !important;
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }

    /* 사이드바 제목 디자인 */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #003399 !important;
        text-align: center !important;
        padding-bottom: 8px;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 12px !important;
    }

    /* 📌 2. 사이드바 버튼: 아이콘 없이 순수 글자만 '가운데 정렬' */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        padding: 9px 10px !important;
        margin-bottom: 5px !important;
        border-radius: 8px !important;
        text-align: center !important;
        justify-content: center !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
        font-size: 1rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* 📌 3. 메인 영역 검색창 & 입력 상자 카드화 (라인 + 은은한 그림자) */
    .stTextInput > div > div {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
    }

    .stTextInput label p {
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: #003399 !important;
        margin-bottom: 6px;
    }

    /* 서브 설명글 */
    .sub-description {
        font-size: 1.05rem !important;
        color: #475569;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    /* 대분류 그룹 카드 헤더 (선명한 블루 테두리 + 그림자) */
    .category-header {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-left: 5px solid #003399;
        padding: 10px 16px;
        font-size: 1.15rem;
        font-weight: 800;
        color: #003399;
        border-radius: 8px;
        margin-top: 25px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 51, 153, 0.05);
    }

    /* Q&A 아코디언 카드 (명확한 라인 + 그림자) */
    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        background-color: #FFFFFF !important;
        margin-bottom: 10px !important;
    }

    div[data-testid="stExpander"] details summary p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    
    /* 📌 4. CS 답변 상자 입체적 카드 레이아웃 */
    .answer-box {
        background-color: #F8FAFC;
        border-left: 4px solid #003399;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        padding: 18px 20px;
        border-radius: 8px;
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.8;
        color: #0F172A;
        margin-top: 10px;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.03);
    }

    /* 로딩 스피너 UI */
    .stSpinner > div {
        border-top-color: #003399 !important;
        border-width: 3px !important;
        width: 36px !important;
        height: 36px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. 헤더 타이틀
st.title("🚕 BTX CS 응대 매뉴얼 검색")
st.markdown("<p class='sub-description'>왼쪽 메뉴에서 카테고리를 선택하거나, 키워드를 검색하면 관련 매뉴얼이 정돈되어 표시됩니다.</p>", unsafe_allow_html=True)

# ⚠️ 구글 시트 CSV 주소 (채영님의 진짜 CSV 링크를 넣어주세요!)
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLIy_47IhFOZPYjwTSyEBz1FzxROrC-rbo8Yx6SM_31EPynnoqL893SQbjzzAVnLGOdu28vXFDjsx2/pub?output=csv"

@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        return df.fillna("")
    except Exception as e:
        st.error("구글 시트를 불러오는 중 오류가 발생했습니다. CSV 링크를 확인해 주세요.")
        return pd.DataFrame()

with st.spinner("매뉴얼 데이터를 불러오는 중입니다..."):
    df = load_data()

# 구글 시트 열 이름 검색 함수
def get_col_val(row, possible_names, default_val=""):
    for col in row.index:
        for name in possible_names:
            if name.lower() in str(col).lower().replace(" ", ""):
                return str(row[col])
    return default_val

# 문장별 자동 줄바꿈 함수
def format_answer_sentences(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace('\n', '<br>')
    text = re.sub(r'([.?!]|\)\.)\s+', r'\1<br>', text)
    return text

if not df.empty:
    # 📌 1. 왼쪽 사이드바 (세로 카테고리 메뉴 - 순수 글자 & 가운데 정렬)
    st.sidebar.header("카테고리 선택")

    if "selected_cat" not in st.session_state:
        st.session_state.selected_cat = "전체 카테고리"

    main_cat_col = None
    for col in df.columns:
        if any(k in str(col).lower() for k in ["대분류", "카테고리"]):
            main_cat_col = col
            break

    categories = ["전체 카테고리"]
    if main_cat_col:
        unique_cats = [c for c in df[main_cat_col].unique() if str(c).strip()]
        categories.extend(unique_cats)

    # 사이드바 세로 버튼 목록 생성 (아이콘 제외, 순수 카테고리 이름만 사용)
    for idx, cat in enumerate(categories):
        is_selected = (st.session_state.selected_cat == cat)
        btn_type = "primary" if is_selected else "secondary"
        
        if st.sidebar.button(cat, key=f"side_cat_{idx}", type=btn_type, use_container_width=True):
            st.session_state.selected_cat = cat
            st.rerun()

    # 📌 2. 메인 화면 - 키워드 검색창
    search_query = st.text_input(
        "🔎 키워드, 태그, 질문 단어를 입력하세요", 
        placeholder="예: 헤이나우, 네모택시, 가맹조건, 위약금"
    ).strip()

    st.markdown("---")

    # 1단계: 사이드바 카테고리 필터링
    filtered_df = df.copy()
    if st.session_state.selected_cat != "전체 카테고리" and main_cat_col:
        filtered_df = filtered_df[filtered_df[main_cat_col] == st.session_state.selected_cat]

    # 2단계: 키워드 검색 필터링
    if search_query:
        keywords = [k.strip().lower() for k in search_query.replace(',', ' ').split() if k.strip()]

        def calc_score(row):
            row_str = row.astype(str).str.lower().str.cat(sep=' ')
            return sum(1 for k in keywords if k in row_str)

        scores = filtered_df.apply(calc_score, axis=1)
        filtered_df = filtered_df[scores > 0].copy()
        filtered_df['match_score'] = scores[scores > 0]
        filtered_df = filtered_df.sort_values(by='match_score', ascending=False)

    # 결과 제목 안내
    selected_cat_name = st.session_state.selected_cat
    st.subheader(f"📋 [{selected_cat_name}] 검색 결과 (총 {len(filtered_df)}건)")

    # 그룹별 노출
    if not filtered_df.empty:
        grouped = {}
        for idx, row in filtered_df.iterrows():
            cat_main = get_col_val(row, ["대분류", "카테고리"], "일반")
            if cat_main not in grouped:
                grouped[cat_main] = []
            grouped[cat_main].append(row)

        for cat_name, rows in grouped.items():
            st.markdown(f"<div class='category-header'>🚕 {cat_name} ({len(rows)}건)</div>", unsafe_allow_html=True)
            
            for row in rows:
                cat_sub = get_col_val(row, ["소분류", "중분류"], "")
                keywords_text = get_col_val(row, ["키워드", "태그", "tag"], "")
                question = get_col_val(row, ["고객질문", "질문", "q"], "질문 내용")
                answer = get_col_val(row, ["응대답변", "답변", "a"], "답변 내용")

                sub_tag = f"[{cat_sub}] " if cat_sub else ""
                header_title = f"💬 {sub_tag}Q. {question}"

                with st.expander(header_title, expanded=False):
                    if keywords_text:
                        st.caption(f"🏷️ **연관 태그:** {keywords_text}")
                    st.markdown("**💡 CS 응대 답변:**")
                    formatted_answer = format_answer_sentences(answer)
                    st.markdown(f"<div class='answer-box'>{formatted_answer}</div>", unsafe_allow_html=True)
    else:
        st.warning("선택하신 카테고리 또는 검색어에 대한 결과가 없습니다.")
