import streamlit as st
import pandas as pd

# 1. 페이지 기본 설정
st.set_page_config(page_title="CS 응대 매뉴얼 검색기", page_icon="🔍", layout="wide")

# 2. 카드 형태 디자인 (CSS)
st.markdown("""
    <style>
    .cs-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0066ff;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .badge {
        background-color: #e9ecef;
        color: #333;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
        margin-right: 5px;
    }
    .q-text {
        font-size: 1.1em;
        font-weight: bold;
        color: #111;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    .a-text {
        font-size: 1.0em;
        color: #222;
        white-space: pre-wrap;
        background-color: #ffffff;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #dee2e6;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 CS 응대 매뉴얼 검색 도우미")
st.caption("구글 시트에 적은 매뉴얼이 실시간으로 반영되는 검색 시스템입니다.")

# ⚠️ 아래 큰따옴표 안에 구글 시트 CSV 주소를 넣어주세요!
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTLIy_47IhFOZPYjwTSyEBz1FzxROrC-rbo8Yx6SM_31EPynnoqL893SQbjzzAVnLGOdu28vXFDjsx2/pubhtml"

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

if not df.empty:
    # 검색창
    search_query = st.text_input("💡 키워드, 단어, 질문 내용을 입력하세요", placeholder="예: 배송, 환불, 주소변경, 스크래치").strip()

    st.markdown("---")

    # 검색 로직 (모든 칼럼에서 단어 검색)
    if search_query:
        mask = df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().str.cat(sep=' '), axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df

    st.subheader(f"📋 검색 결과 (총 {len(filtered_df)}건)")

    # 카드 형태로 검색 결과 출력
    for idx, row in filtered_df.iterrows():
        cat_main = row.get("대분류", "기타")
        cat_sub = row.get("소분류", "")
        keywords = row.get("키워드", "")
        question = row.get("고객 질문(Q)", row.get("질문", "질문 내용"))
        answer = row.get("CS 응대 답변(A)", row.get("답변", "답변 내용"))

        st.markdown(f"""
            <div class="cs-card">
                <div>
                    <span class="badge">📂 {cat_main}</span>
                    <span class="badge">🏷️ {cat_sub}</span>
                    <span style="color: #6c757d; font-size: 0.85em;">태그: {keywords}</span>
                </div>
                <div class="q-text">Q. {question}</div>
                <div class="a-text">A. {answer}</div>
            </div>
        """, unsafe_allow_html=True)
