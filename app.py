import streamlit as st
import google.generativeai as genai
from google.ai.generativelanguage import Content, Part

# --- 1. 페이지 설정 (심플 화이트) ---
st.set_page_config(
    page_title="Tridge GTM Insight Portal",
    page_icon="🌍",
    layout="wide"
)

# --- 2. 화면 상태 관리 ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'home'

def go_home(): st.session_state.view_mode = 'home'
def go_auto(): st.session_state.view_mode = 'auto'
def go_manual(): st.session_state.view_mode = 'manual'

# --- 3. API Key ---
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    sidebar_msg = "✅ System Ready"
else:
    api_key = "" 
    sidebar_msg = "⚠️ No API Key"

with st.sidebar:
    st.image("https://cdn.tridge.com/assets/images/logo-dark.svg", width=150)
    st.caption(sidebar_msg)
    st.caption("Engine: **Gemini 1.5 Pro (Optimized)**") 
    st.markdown("---")
    if st.session_state.view_mode != 'home':
        st.button("🏠 홈으로 이동", on_click=go_home, use_container_width=True)

# --- 4. 모델 설정 (품질의 핵심) ---
model_name = "gemini-1.5-pro"

# [핵심] AI를 강제로 똑똑하게 만드는 설정
generation_config = {
    "temperature": 0.3,  # 낮을수록 분석적이고 사실적인 답변 (0.0 ~ 1.0)
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192, # 긴 보고서를 쓰도록 허용
}

# [핵심] "대충 쓰면 해고" 수준의 강력한 페르소나 주입
system_instruction = """
### ROLE DEFINITION
You are the **Chief Strategy Officer (CSO) at Tridge**, the world's leading agricultural data & trading platform.
Your audience is the Executive Board. They do not want summaries. They want **Money-Making Intelligence**.

### YOUR OBJECTIVE
Analyze the input news/event and construct a "Tridge GTM Playbook" that converts market disruptions into revenue.

### ANALYSIS GUIDELINES (Must Follow)
1.  **NO GENERIC ADVICE:** Do not say "Monitor the market" or "Strengthen relationships." Say "Secure 500 tons of Brazilian Soybeans immediately" or "Target Vietnamese cashew buyers."
2.  **DATA-DRIVEN INFERENCE:** If specific numbers are missing, use your knowledge to estimate logic (e.g., "Expected price hike: 15-20% based on historical drought data").
3.  **TRIDGE ANGLE:** Always connect the strategy to Tridge's specific assets:
    - *Tridge Fulfillment Solution* (Logistics)
    - *Global Sourcing Hubs* (Alternative origins)
    - *Data Intelligence* (Price forecasting)

### OUTPUT FORMAT (Strictly Korean)
Report must be professional, concise, and structured as follows:

---
# 🌍 Tridge GTM Strategic Report

## 🚨 Executive Summary (3줄 요약)
- [핵심 이슈]
- [Tridge에 미치는 영향]
- [즉시 실행해야 할 한 가지 Action]

## 1단계: Market Intelligence (심층 분석)
- **공급망 타격 분석:** 구체적으로 어떤 품목, 어떤 국가의 물량이 얼마나 감소/지연되는가?
- **가격 변동 시나리오:** 단기(2주) 및 중기(3개월) 가격 예측. (상승/하락/보합)
- **숨겨진 기회:** 경쟁사가 보지 못하는 이면의 기회 (예: 환율 차익, 대체재 수요 급증).

## 2단계: Product & Sourcing (제품 및 소싱)
- **Target Products:** 지금 당장 확보해야 할 핵심 품목 3가지.
- **Origin Switch (산지 전환):** 위기 발생 국가를 대체할 구체적인 국가와 이유.
- **Inventory Strategy:** Long(매수) 포지션인가, Short(매도) 포지션인가?

## 3단계: Marketing & Demand (마케팅)
- **Target Buyer Persona:** 이 물건을 가장 급하게 찾는 사람은 누구인가? (국가/업종 구체적 명시)
- **Killer Message:** 바이어에게 보낼 제안서의 '제목(Subject Line)'과 '핵심 문구'.

## 4단계: Sales Execution (세일즈 액션)
- **Priority Leads:** 접촉 1순위 국가 및 기업 리스트.
- **Objection Handling:** 바이어가 "비싸다"고 할 때 대응할 논리.
- **KPI Goal:** 이 전략으로 달성할 예상 매출 목표 (가상의 수치라도 논리적으로 제시).
---
"""

# --- 5. 화면 로직 ---

# [HOME]
if st.session_state.view_mode == 'home':
    st.title("🌍 Tridge Global Market Strategist")
    st.markdown("### 시장의 위기를 기회로 전환하는 GTM 전략 설계 도구")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("🤖 **AI 자동 탐지 모드**")
        st.markdown("최근 글로벌 이슈를 자동으로 검색하여 분석합니다.")
        if st.button("🚀 최신 시장 리스크 스캔하기", use_container_width=True):
            go_auto()
            st.rerun()

    with col2:
        st.warning("📝 **전문가 분석 모드**")
        st.markdown("특정 기사나 이슈를 깊이 있게 해부합니다.")
        if st.button("✍️ 뉴스 직접 입력해서 분석하기", use_container_width=True):
            go_manual()
            st.rerun()

# [MODE A] 자동 검색
elif st.session_state.view_mode == 'auto':
    st.title("🚀 최신 시장 리스크 스캔 (High-Intel)")
    st.markdown("---")

    if api_key:
        # 검색 쿼리도 구체적으로 변경
        prompt = "Find 3 critical supply chain disruptions in the global agricultural market from the last 2 weeks. Summarize them in Korean and provide a Tridge GTM opportunity analysis for each."
        
        with st.spinner("Gemini 1.5 Pro가 전 세계 데이터를 정밀 분석 중입니다..."):
            try:
                genai.configure(api_key=api_key)
                
                # [Search Tool] 최신 문법 적용
                tools = [
                    genai.protos.Tool(
                        google_search=genai.protos.GoogleSearch()
                    )
                ]
                
                # Config 적용하여 모델 로드
                tools_model = genai.GenerativeModel(
                    model_name, 
                    tools=tools,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
                
                response = tools_model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.warning("검색 도구 오류 시, '직접 입력' 모드를 사용해주세요.")
    else:
        st.error("API Key 설정이 필요합니다.")

# [MODE B] 직접 입력
elif st.session_state.view_mode == 'manual':
    st.title("📝 뉴스 직접 분석 & 전략 수립 (Deep Dive)")
    st.markdown("---")

    user_input = st.text_area("분석할 기사 전문을 입력하세요 (길수록 좋습니다)", height=300, 
                             placeholder="기사 내용을 통째로 붙여넣으세요. AI가 문맥을 파악합니다.")
    
    if st.button("📊 GTM 플레이북 생성 (Start)", type="primary", use_container_width=True):
        if user_input and api_key:
            genai.configure(api_key=api_key)
            
            # Config 적용하여 모델 로드
            model = genai.GenerativeModel(
                model_name=model_name, 
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            
            prompt = f"""
            Analyze the following news and create the Tridge GTM Playbook.
            Input News:
            {user_input}
            """
            
            with st.spinner("Gemini 1.5 Pro가 CSO 관점에서 전략을 수립 중입니다..."):
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
st.caption("Powered by Tridge Data Intelligence & Google Gemini 1.5 Pro (Optimized)")
