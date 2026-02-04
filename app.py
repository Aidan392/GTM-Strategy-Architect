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

# --- [디자인] CSS 스타일 주입 (다크 모드 & 카드 UI) ---
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

    /* 3. 홈 화면 카드(Column) 스타일 */
    /* data-testid="column"을 타겟팅하여 카드처럼 보이게 만듦 */
    div[data-testid="column"] {
        background-color: #161B22; /* 카드 배경색 */
        border: 1px solid #30363D; /* 테두리 */
        border-radius: 15px;       /* 둥근 모서리 */
        padding: 25px;             /* 내부 여백 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); /* 그림자 */
        transition: transform 0.2s;
    }
    div[data-testid="column"]:hover {
        border-color: #58A6FF; /* 마우스 올렸을 때 테두리 색 변화 */
    }

    /* 4. 텍스트 가독성 조정 */
    h1, h2, h3, p, div, span {
        color: #E6EDF3 !important;
    }
    .stMarkdown p {
        color: #C9D1D9 !important;
    }

    /* 5. 버튼 스타일 커스터마이징 */
    
    /* 왼쪽 카드 버튼 (자동 탐지 - Light Blue) */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #4FC3F7 !important; 
        color: #000000 !important;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 8px;
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {
        background-color: #29B6F6 !important;
        box-shadow: 0 0 10px #29B6F6;
    }

    /* 오른쪽 카드 버튼 (직접 입력 - Light Yellow) */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #FFF59D !important; 
        color: #000000 !important;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 8px;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
        background-color: #FFF176 !important;
        box-shadow: 0 0 10px #FFF176;
    }

    /* 입력창 스타일 (어두운 배경에 맞게) */
    .stTextArea textarea {
        background-color: #0D1117 !important;
        color: #FFFFFF !important;
        border: 1px solid #30363D !important;
    }
    
    /* 비밀번호 입력창 */
    .stTextInput input {
        background-color: #0D1117 !important;
        color: #FFFFFF !important;
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
        st.title("🔒 Tridge Insight Portal")
        st.markdown("---")
        st.info("보안을 위해 비밀번호를 입력해주세요.")
        
        password = st.text_input("Access Code", type="password")
        
        if st.button("Log In", type="primary", use_container_width=True):
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
    st.caption("Engine: **Gemini 2.5 Pro**") 
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

# [모델명] Gemini 2.5 Pro (이름이 정확해야 합니다)
model_name = "gemini-2.5-pro"

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
        # CSS로 하늘색 버튼 적용됨
        if st.button("최신 뉴스 검색 (Auto Scan)", use_container_width=True):
            go_auto()
            st.rerun()

    with col2:
        st.markdown("### 📝 직접 입력")
        st.markdown("""
        분석하고 싶은 특정 시장 이벤트나 뉴스 기사 내용을
        직접 입력하여 전략을 수립합니다.
        <br><br>
        """, unsafe_allow_html=True)
        # CSS로 연노랑색 버튼 적용됨
        if st.button("플레이북 생성 (Manual Input)", use_container_width=True):
            go_manual()
            st.rerun()

# [MODE A] 자동 검색
elif st.session_state.view_mode == 'auto':
    st.title("🚀 최신 시장 리스크 스캔")
    st.markdown("---")

    if api_key:
        prompt = "최근 2주간 글로벌 농식품 공급망에 타격을 준 주요 이슈 3가지를 구글 검색으로 찾아서 한국어로 요약해주고, 각각 Tridge의 영업 기회인지 분석해줘."
        
        with st.spinner("Gemini 2.5 Pro가 전 세계 뉴스를 분석 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                tools = [
                    genai.protos.Tool(
                        google_search_retrieval=genai.protos.GoogleSearchRetrieval(
                            dynamic_retrieval_config=genai.protos.DynamicRetrievalConfig(
                                mode=genai.protos.DynamicRetrievalConfig.Mode.MODE_DYNAMIC
                            )
                        )
                    )
                ]
                
                tools_model = genai.GenerativeModel(model_name, tools=tools)
                response = tools_model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.info("Tip: 모델명을 'gemini-1.5-pro' 등으로 변경해보세요.")
    else:
        st.error("API Key 설정이 필요합니다.")

# [MODE B] 직접 입력
elif st.session_state.view_mode == 'manual':
    st.title("📝 뉴스 직접 분석 & 전략 수립")
    st.markdown("---")

    user_input = st.text_area("분석할 상황을 자세히 입력하세요", height=200, 
                             placeholder="기사 내용이나 시장 상황을 여기에 붙여넣으세요.")
    
    # 여기 버튼은 기본 스타일(가독성 위해)
    if st.button("📊 GTM 플레이북 생성 (Start)", type="primary", use_container_width=True):
        if user_input and api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
            prompt = f"다음 상황에 대한 4단계 GTM Playbook을 완벽한 한국어 보고서로 작성해줘:\n\n{user_input}"
            
            with st.spinner("Gemini 2.5 Pro가 심층 전략을 설계 중입니다..."):
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
        elif not api_key:
            st.error("API Key 설정이 필요합니다.")
        else:
            st.warning("내용을 입력해주세요.")

# Footer
st.markdown("---")
st.caption("Powered by Tridge Data Intelligence & Google Gemini 2.5 Pro")
