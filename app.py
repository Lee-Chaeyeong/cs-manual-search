import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="BTX CS 응대 매뉴얼 검색", page_icon="🚕", layout="wide")

# 2. 커스텀 스타일
st.markdown("""
    <style>
    /* 상단 여백 축소 */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* 설명글 스타일 */
    .sub-description {
        font-size: 1.05rem !important;
        color: #475569;
        margin-top: -10px;
        margin-bottom: 15px;
    }

    /* 검색창 및 필터 라벨(제목) 스타일 */
    .stTextInput label p, .stSelectbox label p {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }

    /* 📌 [신규 추가] 카테고리 필터 클릭 시 펼쳐지는 하위 항목(드롭다운 리스트) 글자 크기, 볼드체, 색상 상향 */
    div[data-baseweb="select"] div {
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }

    ul[data-testid="stSelectboxVirtualDropdown"] li, li[role="option"] {
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
        padding-top: 8px !important;
        padding-bottom: 8px !important;
    }

    /* 대분류/키워드 그룹 구분 헤더 */
    .category-header {
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
        padding: 10px 16px;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e3a8a;
        border-radius: 6px;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    /* 접이식 항목(Expander) 제목 스타일 */
    div[data-testid="stExpander"] details summary p {
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    /* 답변 상자 디자인 */
    .answer-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 16px;
        border-radius: 6px;
        font-size: 1.18rem;
        font-weight: 700;
        line-height: 1.6;
        color: #0f172a;
        margin-top: 8px;
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

df = load_data()

# 구글 시트 열 이름을 알아서 찾아주는 함수
def get_col_val(row, possible_names, default_val=""):
    for col in row.index:
        for name in possible_names:
            if name.lower() in str(col).lower().replace(" ", ""):
                return str(row[col])
    return default_val

if not df.empty:
    col_search, col_filter = st.columns([3, 1])
    
    main_cat_col = None
    for col in df.columns:
        if any(k in str(col).lower() for k in ["대분류", "카테고리"]):
            main_cat_col = col
            break

    categories = ["전체 카테고리"]
    if main_cat_col:
        unique_cats = [c for c in df[main_cat_col].unique() if str(c).strip()]
        categories.extend(unique_cats)

    with col_search:
        search_query = st.text_input(
            "🔎 키워드, 태그, 질문 단어를 입력하세요", 
            placeholder="예: 헤이나우, 네모택시, 가맹조건, 위약금"
        ).strip()
        
    with col_filter:
        selected_cat = st.selectbox("🚕 카테고리 필터", categories)

    st.markdown("---")

    # 1단계: 카테고리 필터링
    filtered_df = df.copy()
    if selected_cat != "전체 카테고리" and main_cat_col:
        filtered_df = filtered_df[filtered_df[main_cat_col] == selected_cat]

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
                    st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
    else:
        st.warning("검색 결과가 없습니다. 다른 키워드나 카테고리를 선택해 보세요.")
