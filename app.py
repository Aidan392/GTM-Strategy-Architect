import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="Tridge GTM Insight Portal",
    page_icon="🌍",
    layout="wide"
)

# --- 2. API Key 및 모델 확인 기능 ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    connection_status = "✅ Connected"
    
    # [핵심 기능] 내 API 키로 쓸 수 있는 모델 목록 가져오기
    try:
        my_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                my_models.append(m.name)
    except:
        my_models = ["목록 로딩 실패"]
else:
    api_key = ""
    connection_status = "⚠️ No API Key"
    my_models = []

# --- 3. 사이드바 (모델 리스트 확인용) ---
with st.sidebar:
    st.image("https://cdn.tridge.com/assets/images/logo-dark.svg", width=150)
    st.caption(connection_status)
    st.divider()
    
    st.markdown("### 📋 사용 가능한 모델 목록")
    st.caption("아래 목록에 있는 이름만 사용 가능합니다.")
    
    # 모델 목록 보여주기
    if my_models:
        for model in my_models:
            # 보기 좋게 'models/' 부분 제외하고 출력
            clean_name = model.replace("models/", "")
            st.code(clean_name, language=None)
    else:
        st.write("확인된 모델이 없습니다.")

    st.divider()
    
    # 화면 전환 버튼
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'home'
    
    def go_home(): st.session_state.view_mode = 'home'
    def go_auto(): st.session_state.view_mode = 'auto'
    def go_manual(): st.session_state.view_mode = 'manual'
    
    if st.session_state.view_mode != 'home':
        st.button("🏠 홈으로 이동", on_click=go_home, use_container_width=True)

# --- 4. 모델 설정 (2026년 기준 무료 표준 모델 추정) ---
# 1.5는 404(없음), 2.5는 429(유료)이므로 2.0 Flash 시도
model_name = "gemini-2.0-flash" 

system_instruction = """
### ROLE
You are the "Tridge GTM Strategy Architect."
### LANGUAGE
KOREAN ONLY.
### OUTPUT
1. Market Intelligence
2. Product & Pricing
3. Marketing
4. Sales Execution
"""

# --- 5. 메인 화면 로직 ---

if st.session_state.view_mode == 'home':
    st.title("🌍 Tridge Global Market Strategist")
    st.write("2026 GTM Strategy Tool")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.info("🤖 AI 자동 탐지")
        if st.button("🚀 스캔 시작", use_container_width=True):
            go_auto()
            st.rerun()
    with col2:
        st.warning("📝 전문가 분석")
        if st.button("✍️ 직접 입력", use_container_width=True):
            go_manual()
            st.rerun()

elif st.session_state.view_mode == 'auto':
    st.title("🚀 시장 리스크 스캔")
    st.info(f"현재 적용된 모델: {model_name}")
    
    if st.button("스캔 실행"):
        # 검색 기능은 복잡하니 일단 텍스트 생성만 테스트하여 모델 확인
        prompt = "최근 글로벌 농식품 이슈 3가지를 요약해줘."
        with st.spinner("분석 중..."):
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.warning("👈 왼쪽 사이드바의 '사용 가능한 모델 목록'을 확인하고, app.py의 model_name을 그 중 하나로 바꿔주세요.")

elif st.session_state.view_mode == 'manual':
    st.title("📝 뉴스 직접 분석")
    st.info(f"현재 적용된 모델: {model_name}")
    
    user_input = st.text_area("내용 입력", height=150)
    if st.button("분석 실행"):
        if user_input:
            prompt = f"다음 내용 분석해줘:\n{user_input}"
            with st.spinner("분석 중..."):
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    st.warning("👈 왼쪽 사이드바의 모델 목록에 있는 이름으로 model_name을 수정해야 합니다.")
