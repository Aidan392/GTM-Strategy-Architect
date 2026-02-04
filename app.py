import streamlit as st
import google.generativeai as genai
from google.ai.generativelanguage import Content, Part

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="Tridge GTM Insight Portal",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- [디자인] CSS 스타일 주입 (다크 모드 & 가독성 개선) ---
st.markdown("""
<style>
    /* 1. 전체 배경색 (Deep Dark Blue/Black) */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }

    /* 2. 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    /* 사이드바 안의 버튼 텍스트 색상 */
    section[data-testid="stSidebar"] button {
        color: #FAFAFA !important; 
    }

    /* 3. 홈 화면 카드(Column) 박스 디자인 - 확실한 구분감 */
    div[data-testid="column"] {
        background-color: #161B22; /* 카드 배경색 (메인보다 약간 밝음) */
        border: 1px solid #30363D; /* 테두리 */
        border-radius: 15px;       /* 둥근 모서리 */
        padding: 30px;             /* 내부 여백 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5); /* 그림자 */
        height: 100%;
    }
    /* 마우스 올렸을 때 효과 */
    div[data-testid="column"]:hover {
        border-color: #58A6FF; 
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    /* 4. 텍스트 가독성 조정 */
    h1, h2, h3, h4, p, div, span, label {
        color: #E6EDF3 !important;
    }

    /* 5. 버튼 스타일 커스터마이징 (글씨 잘 보이게 수정) */
    
    /* [왼쪽] 자동 탐지 버튼 (하늘색 배경 + 검은 글씨) */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #4FC3F7 !important; 
        color: #000000 !important; /* 검은색 글씨 강제 적용 */
        border: none;
        font-weight: 800; /* 폰트 굵게 */
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 16px;
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {
        background-color: #29B6F6 !important;
        box-shadow: 0 0 15px #29B6F6;
        color: #000000 !important;
    }

    /* [오른쪽] 직접 입력 버튼 (연노랑 배경 + 검은 글씨) */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #FFF59D !important; 
        color: #000000 !important; /* 검은색 글씨 강제 적용 */
        border: none;
        font-weight: 800;
        padding: 15px 20px;
        border-radius: 8px;
        font-size: 16px;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
        background-color: #FFF176 !important;
        box-shadow: 0 0 15px #FFF176;
        color: #000000 !important;
    }

    /* 6. 입력창 스타일 (흰색 글씨 나오게) */
    .stTextArea textarea {
        background-color: #0D1117 !important;
        color: #FFFFFF !important; /* 입력 글씨 흰색 */
        border: 1px solid #30363D !important;
        font-size: 15px;
    }
    /* placeholder 색상 조정 */
    .stTextArea textarea::placeholder {
        color: #8B949E !important;
    }
    
    /* 비밀번호 입력창 */
    .stTextInput input {
        background-color: #0D1117 !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D !important;
    }
</style>
""", unsafe_allow_html=True)


# --- [보안] 0. 비밀번호 잠금 장치 ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # 로그인 화면 디자인
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🔒 Tridge Insight Portal")
        st.markdown("---")
        st.info("보안을 위해 비밀번호를 입력해주세요.")
        
        password = st.text_input("Access Code", type="password")
        
        # 로그인 버튼도 잘 보이게 Primary 스타일 적용
        if st.button("Log In ➜", type="primary", use_container_width=True):
            if password == "66745500": 
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
    st.stop() 


# ---------------------------------------------------------
# 로그인 성공 후 메인 로직
# ---------------------------------------------------------

# --- 2. 화면 상태 관리 ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'home'

def go_home():
    st.session_state.view_mode = 'home'
def go_auto():
    st.session_state.view_mode = 'auto'
def go_manual():
    st.session_state.view_mode = 'manual'

# --- 3. API Key 처리 ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    sidebar_msg = "✅ Connected (Secure)"
else:
    api_key = "" 
    sidebar_msg = "⚠️ No API Key Found"

with st.sidebar:
    st.image("https://cdn.tridge.com/assets/images/logo-dark.svg", width=150)
    st.markdown("### System Status")
    st.caption(sidebar_msg)
    st.caption("Engine: **Gemini 1.5 Pro**") 
    st.markdown("---")
    if st.session_state.view_mode != 'home':
        st.button("🏠 홈으로 이동", on_click=go_home, use_container_width=True)

# --- 4. 모델 설정 ---
system_instruction = """
### ROLE
You are the "Tridge GTM Strategy Architect."
Your mission is to architect comprehensive Go-to-Market plays that convert global market disruptions into immediate revenue opportunities for Tridge.

### LANGUAGE RULES (MANDATORY)
1. OUTPUT LANGUAGE: KOREAN (한국어) ONLY.
2. Terminology: Use professional Korean terms (e.g., 공급망, 대체 산지, 도착 원가).

### OUTPUT SCHEMA: TRIDGE GTM PLAYBOOK
Structure the response into 4 Phases using horizontal dividers (---).
1단계: 시장 인텔리전스 (Market Intelligence)
2단계: 제품 및 가격 전략 (Product & Pricing)
3단계: 마케팅 및 수요 창출 (Marketing)
4단계: 세일즈 실행 (Sales Execution)
"""

# [중요 변경] 429 오류 해결을 위해 가장 안정적인 Pro 모델 사용
# 1.5 Pro는 무료 티어 할당량이 넉넉하여 에러가 나지 않습니다.
model_name = "gemini-1.5-pro"

# --- 6. 화면 로직 구현 ---

# [HOME] 메인 대시보드 (다크 카드 UI)
if st.session_state.view_mode == 'home':
    st.title("Tridge GTM Strategy Architect")
    st.markdown("#### GTM 전략 수립 시작하기")
    st.markdown("") # 여백
    st.markdown("") 

    # 2개의 카드 레이아웃
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 자동 탐색")
        st.markdown("""
        최신 글로벌 농식품 공급망 이슈를 자동으로 검색하여
        GTM 전략 수립 대상을 찾습니다.
        <br><br>
        """, unsafe_allow_html=True)
        # CSS로 하늘색 버튼 + 검은 글씨 적용됨
        if st.button("최신 뉴스 검색 (Auto Scan)", use_container_width=True):
            go_auto()
            st.rerun()

    with col2:
        st.markdown("### 📝 직접 입력")
        st.markdown("""
        분석하고 싶은 특정 시장 이벤트나 뉴스 기사 내용을
        직접 입력하여 전략을 수립합니다.
