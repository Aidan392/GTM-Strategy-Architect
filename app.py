import streamlit as st
import google.generativeai as genai

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="Tridge GTM Insight Portal",
    page_icon="🌍",
    layout="wide"
)

# --- 2. 사이드바: API Key 입력창 ---
with st.sidebar:
    st.image("https://cdn.tridge.com/assets/images/logo-dark.svg", width=150)
    st.title("⚙️ 설정")
    
    # 비밀번호 형태로 입력받아 화면에 노출되지 않음
    api_key = st.text_input("Google API Key를 입력하세요", type="password")
    
    st.markdown("---")
    st.caption("API Key는 저장되지 않으며, 일회성으로만 사용됩니다.")
    st.markdown("[🔑 API Key 발급받기](https://aistudio.google.com/)")

# --- 3. 메인 화면 ---
st.title("🌍 Tridge Global Market Strategist")
st.markdown("### 시장의 위기를 기회로 전환하는 GTM 전략 설계 도구")

# --- 4. AI 모델 구동 로직 ---
if api_key:
    try:
        # 1) API 설정
        genai.configure(api_key=api_key)
        
        # 2) 시스템 프롬프트 (뇌 이식)
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
        - 이벤트 심층 분석 (수치 포함)
        - 나비 효과 분석 (산지 -> 바이어 영향)
        - 타겟 기업 분석 (Tier 1 기업 실명 거론)
        
        2단계: 제품 및 가격 전략 (Product & Pricing)
        - 솔루션 패키지명
        - 핵심 기능 매핑 (Tridge Eye, Suppliers)
        - 가격 제안
        
        3단계: 마케팅 및 수요 창출 (Marketing)
        - 콘텐츠 제목 (웨비나/백서)
        - SNS 훅
        
        4단계: 세일즈 실행 (Sales Execution)
        - 콜드 이메일 (제목, 본문)
        - 거절 대응 스크립트
        """

        # 3) 모델 초기화
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            system_instruction=system_instruction
        )
        
        # --- 5. 기능 구현 (탭) ---
        tab1, tab2 = st.tabs(["🔍 시장 이슈 자동 검색", "📝 뉴스 직접 분석"])

        with tab1:
            st.write("구글 검색을 통해 최근 2주간의 주요 농식품 공급망 이슈를 찾습니다.")
            if st.button("🚀 최신 시장 리스크 스캔하기"):
                prompt = "최근 2주간 글로벌 농식품 공급망에 타격을 준 주요 이슈 3가지를 구글 검색으로 찾아서 한국어로 요약해주고, 각각 Tridge의 영업 기회인지 분석해줘."
                
                with st.spinner("최신 뉴스를 분석 중입니다..."):
                    try:
                        # 검색 도구 활성화된 모델 별도 호출
                        tools_model = genai.GenerativeModel('gemini-1.5-pro', tools='google_search-retrieval')
                        response = tools_model.generate_content(prompt)
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"검색 오류 발생: {e}")

        with tab2:
            st.write("분석하고 싶은 특정 뉴스나 상황을 입력하세요.")
            user_input = st.text_area("예: 캐나다-미국 관세 전쟁으로 커피 가격 상승 예상", height=100)
            
            if st.button("📊 GTM 플레이북 생성"):
                if user_input:
                    prompt = f"다음 상황에 대한 4단계 GTM Playbook을 완벽한 한국어 보고서로 작성해줘:\n\n{user_input}"
                    
                    with st.spinner("전략 보고서를 설계 중입니다..."):
                        try:
                            response = model.generate_content(prompt)
                            st.markdown(response.text)
                        except Exception as e:
                            st.error(f"생성 오류 발생: {e}")
                else:
                    st.warning("분석할 내용을 입력해주세요.")

    except Exception as e:
        st.error(f"API Key가 올바르지 않습니다: {e}")

else:
    # 키가 없을 때 안내 문구
    st.warning("👈 왼쪽 사이드바에 Google API Key를 입력해주세요.")
    st.info("팀원들은 각자의 API Key를 입력하여 사용할 수 있습니다.")

# --- Footer ---
st.markdown("---")
st.caption("Powered by Tridge Data Intelligence & Google Gemini 1.5 Pro")
