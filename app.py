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

# 2. 페이지 기본 설정 (브라우저 탭에 BTX 블루 로고 적용)
st.set_page_config(
    page_title="BTX CS 응대 매뉴얼 검색", 
    page_icon=logo_img if logo_img else "🚕", 
    layout="wide"
)

# 3. 고도화된 커스텀 스타일 (Pretendard 폰트 전면 적용 + 아이콘 폰트 깨짐 방지)
st.markdown("""
    <style>
    /* Pretendard 폰트 불러오기 및 전체 적용 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');

    html, body, .stApp {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
    }

    /* 📌 스트림릿 내장 아이콘 폰트 보호 (접기 버튼 <<, 돋보기, 태그 등 텍스트 깨짐 완벽 방지) */
    [data-testid="stIconMaterial"], 
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stBaseButton-headerNoPadding"] *,
    [data-testid="stFileUploaderDropzone"] i,
    .material-symbols-outlined,
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'StreamlitIcons' !important;
    }

    /* 상단 여백 축소 */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }
    
    /* 설명글 스타일 */
    .sub-description {
        font-size: 1.05rem !important;
        color: #475569;
        margin-top: -10px;
        margin-bottom: 15px;
    }

    /* 검색창 및 카테고리 라벨(제목) 스타일 - 진한 파란색 볼드체 */
    .stTextInput label p, .cat-label {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #003399 !important;
        margin-bottom: 8px;
    }

    /* 카테고리 버튼 내부 글자: Pretendard 굵은 볼드체 */
    div[data-testid="stButton"] button p {
        font-size: 1.08rem !important;
        font-weight: 700 !important;
    }

    /* 대분류/키워드 그룹 구분 헤더 (테두리 및 그림자 강조) */
    .category-header {
        background-color: #eff6ff;
        border-left: 5px solid #003399;
        padding: 10px 16px;
        font-size: 1.15rem;
        font-weight: 700;
        color: #003399;
        border-radius: 6px;
        margin-top: 25px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }

    /* 접이식 항목(Expander) 제목 스타일 */
    div[data-testid="stExpander"] details summary p {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    /* 📌 답변 상자 디자인 (줄간격 및 카드 형태 개선) */
    .answer-box {
        background-color: #f8fafc;
        border-left: 4px solid #003399;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        padding: 18px;
        border-radius: 8px;
        font-size: 1.18rem;
        font-weight: 700;
        line-height: 1.8;
        color: #0f172a;
        margin-top: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    /* 표준 원형 스피너 로딩 UI */
    .stSpinner > div {
        border-top-color: #003399 !important;
        border-width: 3px !important;
        width: 36px !important;
        height: 36px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚕 BTX CS 응대 매뉴얼 검색")
st.markdown("<p class='sub-description'>검색어를 입력하거나 카테고리를 선택하면 관련 항목이 정리되어 표시됩니다.</p>", unsafe_allow_html=True)

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

# 구글 시트 열 이름을 알아서 찾아주는 함수
def get_col_val(row, possible_names, default_val=""):
    for col in row.index:
        for name in possible_names:
            if name.lower() in str(col).lower().replace(" ", ""):
                return str(row[col])
    return default_val

# 📌 문장별 줄바꿈 자동 처리 함수
def format_answer_sentences(text):
    if not text:
        return ""
    text = str(text)
    # 구글 시트 기존 줄바꿈(\n) 보존
    text = text.replace('\n', '<br>')
    # 마침표(.), 물음표(?), 느낌표(!), 닫는 괄호 마침표().) 뒤 띄어쓰기를 자동으로 줄바꿈(<br>) 처리
    text = re.sub(r'([.?!]|\)\.)\s+', r'\1<br>', text)
    return text

if not df.empty:
    # 📌 1. 키워드 검색창
    search_query = st.text_input(
        "🔎 키워드, 태그, 질문 단어를 입력하세요", 
        placeholder="예: 헤이나우, 네모택시, 가맹조건, 위약금"
    ).strip()

    # 카테고리 세션 상태 초기화
    if "selected_cat" not in st.session_state:
        st.session_state.selected_cat = "전체 카테고리"

    # 카테고리 목록 추출
    main_cat_col = None
    for col in df.columns:
        if any(k in str(col).lower() for k in ["대분류", "카테고리"]):
            main_cat_col = col
            break

    categories = ["전체 카테고리"]
    if main_cat_col:
        unique_cats = [c for c in df[main_cat_col].unique() if str(c).strip()]
        categories.extend(unique_cats)

    # 📌 2. 카테고리 선택 버튼 그룹
    st.markdown("<div class='cat-label'>🚕 카테고리 선택</div>", unsafe_allow_html=True)
    
    cols = st.columns(len(categories))
    for idx, cat in enumerate(categories):
        is_selected = (st.session_state.selected_cat == cat)
        btn_type = "primary" if is_selected else "secondary"
        
        if cols[idx].button(cat, key=f"cat_btn_{idx}", type=btn_type, use_container_width=True):
            st.session_state.selected_cat = cat
            st.rerun()

    st.markdown("---")

    # 1단계: 카테고리 필터링
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

    st.subheader(f"📋 검색 결과 (총 {len(filtered_df)}건)")

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
                    # 📌 문장별 줄바꿈 자동 적용
                    formatted_answer = format_answer_sentences(answer)
                    st.markdown(f"<div class='answer-box'>{formatted_answer}</div>", unsafe_allow_html=True)
    else:
        st.warning("검색 결과가 없습니다. 다른 키워드나 카테고리를 선택해 보세요.")
