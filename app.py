import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="CS 응대 매뉴얼 검색기", page_icon="🔍", layout="wide")

st.title("🔍 CS 응대 매뉴얼 검색 도우미")
st.caption("검색어를 입력하면 관련 항목이 표시됩니다. 항목을 **클릭**하면 상세 답변이 펼쳐집니다.")

# ⚠️ 구글 시트 CSV 주소 (아까 넣으셨던 진짜 CSV 링크를 여기에 넣으세요!)
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLIy_47IhFOZPYjwTSyEBz1FzxROrC-rbo8Yx6SM_31EPynnoqL893SQbjzzAVnLGOdu28vXFDjsx2/pub?output=csv"

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

# 구글 시트 제목이 조금 달라도 알아서 질문/답변 열을 찾아주는 스마트 함수
def get_col_val(row, possible_names, default_val=""):
    for col in row.index:
        for name in possible_names:
            if name.lower() in str(col).lower().replace(" ", ""):
                return str(row[col])
    return default_val

if not df.empty:
    # 상단 검색창
    search_query = st.text_input("💡 키워드, 태그, 질문 단어를 입력하세요", placeholder="예: 정산구조, 수수료, 환불, 배송").strip()

    st.markdown("---")

    # 검색 필터링 로직
    if search_query:
        mask = df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().str.cat(sep=' '), axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    st.subheader(f"📋 검색 결과 (총 {len(filtered_df)}건)")

    # 📌 핵심: 클릭해서 펼쳐보는 리스트 형태로 출력
    for idx, row in filtered_df.iterrows():
        cat_main = get_col_val(row, ["대분류", "카테고리"], "일반")
        cat_sub = get_col_val(row, ["소분류", "중분류"], "")
        keywords = get_col_val(row, ["키워드", "태그", "tag"], "")
        question = get_col_val(row, ["고객질문", "질문", "q"], "질문 내용")
        answer = get_col_val(row, ["응대답변", "답변", "a"], "답변 내용")

        # 클릭하기 전 보이는 제목 헤더
        header_title = f"📂 [{cat_main}" + (f" > {cat_sub}] " if cat_sub else "] ") + f"Q. {question}"

        # 클릭하면 펼쳐지는 박스 (st.expander)
        with st.expander(header_title, expanded=False):
            if keywords:
                st.caption(f"🏷️ **연관 태그:** {keywords}")
            st.markdown("---")
            st.markdown("**💬 CS 응대 답변:**")
            st.info(answer)
