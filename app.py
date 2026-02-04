import streamlit as st
import google.generativeai as genai
from google.ai.generativelanguage import Content, Part

# --- 1. 페이지 설정 (깔끔한 화이트 모드) ---
st.set_page_config(
    page_title="Tridge GTM Insight Portal",
    page_icon="🌍",
    layout="wide"
)

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
    sidebar_msg = "✅ Connected"
else:
    api_key = "" 
    sidebar_msg = "⚠️ No API Key"

with st.sidebar:
    st.image("https://cdn.tridge.com/assets/images/logo-dark.svg", width=150)
    st.caption(sidebar_msg)
    # [수정] 목록에 있던 것 중 가장 확실한 모델 사용
    st.caption("Engine: **gemini-flash-latest**") 
    st.markdown("---")
    if st.session_state.view_mode != 'home':
        st.button("🏠 홈으로 이동", on_click=go_home, use_container_width=True)

# --- 4. 모델 설정 ---
# 목록에서 확인된, 무료 할당량이 보장되는 모델 이름
model_name = "gemini-flash-latest"

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

# --- 5. 화면 로직 구현 ---

# [HOME] 메인 화면
if st.session_state.view_mode == 'home':
    st.title("🌍 Tridge Global Market Strategist")
    st.markdown("### 시장의 위기를 기회로 전환하는 GTM 전략 설계 도구")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🤖 **AI 자동 탐지 모드**")
        st.markdown("""
        구글 검색을 통해 최근 2주간의  
        **글로벌 농식품 공급망 이슈**를  
        자동으로 찾아냅니다.
        """)
        if st.button("🚀 최신 시장 리스크 스캔하기", use_container_width=True):
            go_auto()
            st.rerun()

    with col2:
        st.warning("📝 **전문가 분석 모드**")
        st.markdown("""
        이미 알고 있는 특정 이슈나  
        **뉴스를 직접 입력**하여  
        심층 전략을 수립합니다.
        """)
        if st.button("✍️ 뉴스 직접 입력해서 분석하기", use_container_width=True):
            go_manual()
            st.rerun()

# [MODE A] 자동 검색
elif st.session_state.view_mode == 'auto':
    st.title("🚀 최신 시장 리스크 스캔")
    st.markdown("---")

    if api_key:
        prompt = "최근 2주간 글로벌 농식품 공급망에 타격을 준 주요 이슈 3가지를 구글 검색으로 찾아서 한국어로 요약해주고, 각각 Tridge의 영업 기회인지 분석해줘."
        
        with st.spinner("Gemini Flash가 전 세계 뉴스를 스캔 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                # 검색 도구 설정
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
                st.info("여전히 오류가 난다면, Google Search 도구 없이 텍스트 분석 모드로 전환해야 합니다.")
    else:
        st.error("API Key 설정이 필요합니다.")

# [MODE B] 직접 입력
elif st.session_state.view_mode == 'manual':
    st.title("📝 뉴스 직접 분석 & 전략 수립")
    st.markdown("---")

    user_input = st.text_area("분석할 상황을 자세히 입력하세요", height=200, 
                             placeholder="기사 내용을 붙여넣으세요.")
    
    if st.button("📊 GTM 플레이북 생성 (Start)", type="primary", use_container_width=True):
        if user_input and api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
            prompt = f"다음 상황에 대한 4단계 GTM Playbook을 완벽한 한국어 보고서로 작성해줘:\n\n{user_input}"
            
            with st.spinner("Gemini Flash가 심층 전략을 설계 중입니다..."):
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
st.caption("Powered by Tridge Data Intelligence & Google Gemini Flash")
