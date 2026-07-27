import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="CS 응대 매뉴얼 검색기", page_icon="🔍", layout="wide")

# 2. 커스텀 스타일 (제목 가독성 조정 & 답변 글자 확대 및 볼드체)
st.markdown("""
    <style>
    /* 접이식 항목(Expander) 제목 스타일: 적당하고 보기에 편한 크기 */
    div[data-testid="stExpander"] details summary p {
        font-size: 1.02rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
    }
    
    /* 답변 상자 디자인: 글자 크기 1~2pt 확대 및 볼드체 적용 */
    .answer-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 16px;
        border-radius: 6px;
        font-size: 1.18rem; /* 답변 글자 크기 확대 */
        font-weight: 700;  /* 굵은 볼드체 */
        line-height: 1.6;
        color: #0f172a;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 CS 응대 매뉴얼 검색 도우미")
st.caption("검색어를 입력하면 관련 항목이 표시됩니다. 항목을 **클릭**하면 상세 답변이 펼쳐집니다.")

# ⚠️ 구글 시트 CSV 주소 (채영님의 진짜 CSV 링크를 넣어주세요!)
GOOGLE_SHEET_CSV_URL = "여기에_구글시트_CSV_링크를_넣어주세요"

# 데이터 불러오기 함수 (10초마다 자동 최신화)
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
    # 상단 검색창
    search_query = st.text_input(
        "💡 키워드, 태그, 질문 단어를 입력하세요 (띄어쓰기나 쉼표로 여러 키워드 검색 가능)", 
        placeholder="예: 네모 정산구조, 환불 배송"
    ).strip()

    st.markdown("---")

    # 스마트 다중 키워드 검색 로직
    if search_query:
        keywords = [k.strip().lower() for k in search_query.replace(',', ' ').split() if k.strip()]

        def calc_score(row):
            row_str = row.astype(str).str.lower().str.cat(sep=' ')
            return sum(1 for k in keywords if k in row_str)

        scores = df.apply(calc_score, axis=1)
        filtered_df = df[scores > 0].copy()
        filtered_df['match_score'] = scores[scores > 0]
        filtered_df = filtered_df.sort_values(by='match_score', ascending=False)
    else:
        filtered_df = df

    st.subheader(f"📋 검색 결과 (총 {len(filtered_df)}건)")

    # 접이식 카드로 검색 결과 출력
    for idx, row in filtered_df.iterrows():
        cat_main = get_col_val(row, ["대분류", "카테고리"], "일반")
        cat_sub = get_col_val(row, ["소분류", "중분류"], "")
        keywords_text = get_col_val(row, ["키워드", "태그", "tag"], "")
        question = get_col_val(row, ["고객질문", "질문", "q"], "질문 내용")
        answer = get_col_val(row, ["응대답변", "답변", "a"], "답변 내용")

        header_title = f"📌 [{cat_main}" + (f" > {cat_sub}] " if cat_sub else "] ") + f"Q. {question}"

        with st.expander(header_title, expanded=False):
            if keywords_text:
                st.caption(f"🏷️ **연관 태그:** {keywords_text}")
            st.markdown("**💬 CS 응대 답변:**")
            st.markdown(f"<div class='answer-box'>{answer}</div>", unsafe_allow_html=True)
