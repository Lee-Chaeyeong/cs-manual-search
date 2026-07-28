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

# 3. 레이아웃 고도화 CSS (사이드바 팝오버 메뉴 & 메인 화면 완전 고정 디자인)
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

    /* 메인 화면 여백 정돈 */
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        max-width: 96% !important;
    }

    /* 📌 1. 슬림 좌측 사이드바 */
    [data-testid="stSidebar"] {
        min-width: 170px !important;
        max-width: 180px !important;
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        color: #003399 !important;
        text-align: center !important;
        padding-bottom: 8px;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 12px !important;
    }

    /* 📌 사이드바 대분류 일반 버튼 스타일 (강력한 볼드체 적용) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        padding: 10px 8px !important;
        margin-bottom: 4px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
        font-size: 1.02rem !important;
        font-weight: 800 !important; /* 확 띄는 볼드체 */
        color: #0F172A !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* 📌 2. 사이드바 팝오버(Popover) 버튼 커스텀 (그룹웨어 플로팅 메뉴 디자인) */
    div[data-testid="stPopover"] {
        width: 100% !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stPopover"] > button {
        width: 100% !important;
        padding: 10px 8px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background-color: #EFF6FF !important;
        border-color: #93C5FD !important;
    }

    div[data-testid="stPopover"] > button p {
        font-size: 1.02rem !important;
        font-weight: 800 !important; /* 확 띄는 볼드체 */
        color: #0F172A !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* 대분류 버튼 활성화(Primary) 상태 - 버튼, 팝오버 모두 적용 */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"],
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="baseButton-primary"],
    div[data-testid="stPopover"] > button[kind="primary"],
    div[data-testid="stPopover"] > button[data-testid="baseButton-primary"] {
        background-color: #003399 !important;
        border-color: #003399 !important;
    }
    
    /* 활성화 상태의 텍스트 색상을 강제로 하얀색으로 변경 */
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[data-testid="baseButton-primary"] p,
    div[data-testid="stPopover"] > button[kind="primary"] p,
    div[data-testid="stPopover"] > button[data-testid="baseButton-primary"] p {
        color: #FFFFFF !important;
    }

    /* 📌 팝오버 창 스타일링 (버튼 클릭 시 메인 화면 위로 뜨는 둥근 팝업) */
    div[data-testid="stPopoverBody"] {
        border-radius: 14px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
        padding: 12px !important;
        min-width: 190px !important;
        background-color: #FFFFFF !important;
    }

    /* 📌 팝오버 내부 소분류 세로 버튼 디자인 */
    div[data-testid="stPopoverBody"] div[data-testid="stButton"] button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
        color: #334155 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }

    /* 🔥 마우스 오버 시 확 눈에 띄는 진한 하늘색 하이라이트 */
    div[data-testid="stPopoverBody"] div[data-testid="stButton"] button:hover {
        background-color: #BFDBFE !important; /* 진한 하늘색 */
        color: #003399 !important; /* 텍스트는 찐파랑 */
        font-weight: 800 !important;
    }

    div[data-testid="stPopoverBody"] div[data-testid="stButton"] button p {
        text-align: left !important;
        color: inherit !important;
    }

    /* 📌 3. 검색창 & 검색 버튼 스타일 */
    .stTextInput > div > div {
        border-radius: 10px !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
    }

    .main div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button {
        height: 44px !important;
        border-radius: 10px !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        background-color: #003399 !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(0, 51, 153, 0.2) !important;
        transition: all 0.2s ease !important;
    }

    .main div[data-testid="stColumn"]:nth-child(2) div[data-testid="stButton"] button:hover {
        background-color: #002266 !important;
    }

    .sub-description {
        font-size: 1.05rem !important;
        color: #475569;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    /* 대분류 그룹 카테고리 헤더 */
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
    
    /* E열 CS 답변 상자 */
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

    /* F열 이관 양식 상자 */
    .form-box {
        background-color: #FEF3C7;
        border-left: 4px solid #D97706;
        border-top: 1px solid #FDE68A;
        border-right: 1px solid #FDE68A;
        border-bottom: 1px solid #FDE68A;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.7;
        color: #78350F;
        margin-top: 12px;
    }

    /* G열 관련 링크 상자 */
    .link-box {
        background-color: #F0F9FF;
        border-left: 4px solid #0284C7;
        border-top: 1px solid #BAE6FD;
        border-right: 1px solid #BAE6FD;
        border-bottom: 1px solid #BAE6FD;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 1.05rem;
        font-weight: 700;
        color: #0369A1;
        margin-top: 12px;
    }

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
st.markdown("<p class='sub-description'>왼쪽 메뉴에서 대분류를 클릭하면 하위 소분류 목록이 팝업으로 나타납니다.</p>", unsafe_allow_html=True)

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

# 구글 시트 열 이름 파싱 함수
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
    # 📌 1. 세션 상태 초기화
    if "selected_main_cat" not in st.session_state:
        st.session_state.selected_main_cat = "전체 카테고리"
    if "selected_sub_cat" not in st.session_state:
        st.session_state.selected_sub_cat = None

    # 대분류/소분류 열 찾기
    main_cat_col = None
    sub_cat_col = None
    for col in df.columns:
        col_clean = str(col).lower().replace(" ", "")
        if any(k in col_clean for k in ["대분류", "카테고리"]):
            main_cat_col = col
        elif any(k in col_clean for k in ["소분류", "중분류"]):
            sub_cat_col = col

    categories = ["전체 카테고리"]
    if main_cat_col:
        unique_mains = [str(c).strip() for c in df[main_cat_col].unique() if str(c).strip()]
        categories.extend(unique_mains)

    # 📌 2. 사이드바 (팝오버 레이어 메뉴 적용)
    st.sidebar.markdown("<p style='text-align: center; font-weight: 800; color: #003399; margin-bottom: 8px;'>카테고리</p>", unsafe_allow_html=True)

    for idx, main_cat in enumerate(categories):
        # '전체 카테고리' 선택 시
        if main_cat == "전체 카테고리":
            is_main_selected = (st.session_state.selected_main_cat == "전체 카테고리")
            btn_type = "primary" if is_main_selected else "secondary"
            if st.sidebar.button("전체 카테고리", key="main_all", type=btn_type, use_container_width=True):
                st.session_state.selected_main_cat = "전체 카테고리"
                st.session_state.selected_sub_cat = None
                st.rerun()
        else:
            # 대분류별 소분류 목록 가져오기
            sub_df = df[df[main_cat_col] == main_cat] if main_cat_col else pd.DataFrame()
            sub_categories = [str(s).strip() for s in sub_df[sub_cat_col].unique() if str(s).strip()] if sub_cat_col and not sub_df.empty else []

            # 소분류가 있는 대분류는 클릭 시 오른쪽으로 플로팅 팝업창이 떠오름
            if sub_categories:
                # 팝오버 창 생성 (메인 화면 레이아웃 밀림 방지)
                popover = st.sidebar.popover(main_cat, use_container_width=True)
                
                with popover:
                    # 🔥 폴더 아이콘 대신 택시 아이콘(🚕) 적용
                    st.markdown(f"<p style='font-size:1.05rem; font-weight:800; color:#003399; border-bottom:1px solid #E2E8F0; padding-bottom:6px; margin-bottom:8px;'>🚕 {main_cat}</p>", unsafe_allow_html=True)
                    
                    # '대분류 전체 보기' 버튼
                    if st.button(f"전체 {main_cat} 보기", key=f"pop_all_{idx}"):
                        st.session_state.selected_main_cat = main_cat
                        st.session_state.selected_sub_cat = None
                        st.rerun()
                        
                    st.markdown("<hr style='margin:4px 0 8px 0; border:none; border-top:1px dashed #CBD5E1;'>", unsafe_allow_html=True)
                    
                    # 하위 소분류 세로 목록
                    for s_idx, sub_cat in enumerate(sub_categories):
                        if st.button(sub_cat, key=f"pop_sub_{idx}_{s_idx}"):
                            st.session_state.selected_main_cat = main_cat
                            st.session_state.selected_sub_cat = sub_cat
                            st.rerun()
            else:
                # 하위 소분류가 없는 경우 일반 버튼
                is_main_selected = (st.session_state.selected_main_cat == main_cat)
                btn_type = "primary" if is_main_selected else "secondary"
                if st.sidebar.button(main_cat, key=f"main_single_{idx}", type=btn_type, use_container_width=True):
                    st.session_state.selected_main_cat = main_cat
                    st.session_state.selected_sub_cat = None
                    st.rerun()

    # 📌 3. 메인 화면 - 키워드 검색 영역 (완전 고정 위치)
    st.markdown("<p style='font-size: 1.15rem; font-weight: 800; color: #003399; margin-bottom: 6px;'>🔎 키워드, 태그, 질문 단어를 입력하세요</p>", unsafe_allow_html=True)
    
    col_search_input, col_search_btn = st.columns([5.5, 1])
    
    with col_search_input:
        search_query = st.text_input(
            "검색어 입력창", 
            placeholder="예: 헤이나우, 네모택시, 가맹조건, 위약금",
            label_visibility="collapsed"
        ).strip()
        
    with col_search_btn:
        search_clicked = st.button("🔍 검색", use_container_width=True)

    st.markdown("---")

    # 📌 4. 데이터 필터링
    filtered_df = df.copy()
    
    # 1단계: 대분류 필터링
    if st.session_state.selected_main_cat != "전체 카테고리" and main_cat_col:
        filtered_df = filtered_df[filtered_df[main_cat_col] == st.session_state.selected_main_cat]
        
        # 2단계: 소분류 필터링
        if st.session_state.selected_sub_cat and sub_cat_col:
            filtered_df = filtered_df[filtered_df[sub_cat_col] == st.session_state.selected_sub_cat]

    # 3단계: 키워드 검색 필터링
    if search_query:
        keywords = [k.strip().lower() for k in search_query.replace(',', ' ').split() if k.strip()]

        def calc_score(row):
            row_str = row.astype(str).str.lower().str.cat(sep=' ')
            return sum(1 for k in keywords if k in row_str)

        scores = filtered_df.apply(calc_score, axis=1)
        filtered_df = filtered_df[scores > 0].copy()
        filtered_df['match_score'] = scores[scores > 0]
        filtered_df = filtered_df.sort_values(by='match_score', ascending=False)

    # 결과 타이틀 경로 표시
    main_title = st.session_state.selected_main_cat
    sub_title = st.session_state.selected_sub_cat
    
    path_str = main_title
    if main_title != "전체 카테고리" and sub_title:
        path_str += f" > {sub_title}"

    if search_query:
        st.subheader(f"📋 [{path_str}] '{search_query}' 검색 결과 (총 {len(filtered_df)}건)")
    else:
        st.subheader(f"📋 [{path_str}] 매뉴얼 목록 (총 {len(filtered_df)}건)")

    # 그룹별 Q&A 카드 출력
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
                transfer_form = get_col_val(row, ["이관양식", "이관 양식", "이관"], "")
                related_link = get_col_val(row, ["관련링크", "관련 링크", "링크", "link"], "")

                sub_tag = f"[{cat_sub}] " if cat_sub else ""
                header_title = f"💬 {sub_tag}Q. {question}"

                with st.expander(header_title, expanded=False):
                    if keywords_text:
                        st.caption(f"🏷️ **연관 태그:** {keywords_text}")
                    
                    # E열 CS 응대 답변
                    st.markdown("**💡 CS 응대 답변:**")
                    formatted_answer = format_answer_sentences(answer)
                    st.markdown(f"<div class='answer-box'>{formatted_answer}</div>", unsafe_allow_html=True)

                    # F열 이관 양식
                    if transfer_form and str(transfer_form).strip():
                        formatted_form = format_answer_sentences(transfer_form)
                        st.markdown(f"<div class='form-box'><b>📋 이관 양식:</b><br>{formatted_form}</div>", unsafe_allow_html=True)

                    # G열 관련 링크
                    if related_link and str(related_link).strip():
                        raw_link = str(related_link).strip()
                        full_url = raw_link if raw_link.startswith(("http://", "https://")) else f"https://{raw_link}"
                        st.markdown(f"<div class='link-box'>🔗 <b>관련 링크:</b> <a href='{full_url}' target='_blank' style='color: #0284C7; font-weight: 800; text-decoration: underline;'>{raw_link} 바로가기</a></div>", unsafe_allow_html=True)
    else:
        st.warning("선택하신 카테고리 또는 검색어에 대한 결과가 없습니다.")
