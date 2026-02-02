import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# =========================
# 0) 기본 설정
# =========================
st.set_page_config(
    page_title="AI 챗봇 데모",
    page_icon="🤖",
    layout="centered",
)

# =========================
# 1) 다크모드 CSS + 디자인 개선
# =========================
st.markdown(
    """
    <style>
      /* 전체 배경/텍스트(다크) */
      html, body, [class*="css"]  {
        color: #E5E7EB;
      }

      /* Streamlit 메인 배경 */
      .stApp {
        background: #0B1220; /* 딥 네이비 */
      }

      /* 전체 폭 + 상단 여백(타이틀 잘림 방지) */
      .block-container {
        max-width: 860px;
        padding-top: 3.2rem;   /* ✅ 타이틀 잘림 방지 */
        padding-bottom: 2rem;
      }

      /* 상단 타이틀 */
      .app-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.25;     /* ✅ 잘림 방지 */
        letter-spacing: -0.5px;
      }
      .app-subtitle {
        text-align: center;
        color: #9CA3AF;
        margin-top: 0.35rem;
        margin-bottom: 1.6rem;
        line-height: 1.35;
      }

      /* 말풍선 공통 */
      .bubble {
        padding: 11px 13px;
        border-radius: 14px;
        margin: 8px 0 14px 0;
        max-width: 78%;
        line-height: 1.5;
        box-shadow: 0 2px 14px rgba(0,0,0,0.35);
        word-wrap: break-word;
        white-space: pre-wrap;
        border: 1px solid rgba(255,255,255,0.06);
      }

      /* 사용자 말풍선(오른쪽) - 포인트 컬러 */
      .bubble-user {
        background: rgba(34, 197, 94, 0.18);  /* green */
        margin-left: auto;
        border: 1px solid rgba(34, 197, 94, 0.25);
      }

      /* 어시스턴트 말풍선(왼쪽) */
      .bubble-assistant {
        background: rgba(255, 255, 255, 0.06);
        margin-right: auto;
      }

      /* 작은 역할 라벨 */
      .role-tag {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-bottom: 6px;
      }

      /* 사이드바 다크 스타일 */
      section[data-testid="stSidebar"] {
        background: #0F172A; /* slate */
        border-right: 1px solid rgba(255,255,255,0.06);
      }

      /* 사이드바 내부 텍스트 */
      .sidebar-note {
        color: #9CA3AF;
        font-size: 0.92rem;
      }

      /* 슬라이더/버튼 여백 살짝 */
      .stButton>button {
        border-radius: 12px;
      }

      /* chat_input 위쪽 여백 */
      div[data-testid="stChatInput"] {
        margin-top: 0.5rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# 2) 헤더
# =========================
st.markdown("<div class='app-title'>🤖 AI 챗봇</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Streamlit + OpenAI API 수업용 데모</div>", unsafe_allow_html=True)

# =========================
# 3) .env 로드 + OpenAI 클라이언트 준비
# =========================
load_dotenv()
api_key = os.getenv("openai_key")

if not api_key:
    st.error("❗ .env에서 openai_key를 못 불러왔어. app.py와 .env가 같은 폴더인지 확인해줘!")
    st.stop()

client = OpenAI(api_key=api_key)

# =========================
# 4) 사이드바(설정/초기화)
# =========================
with st.sidebar:
    st.header("⚙️ 설정")
    st.markdown(
        "<div class='sidebar-note'>수업용 챗봇 데모예요.<br/>‘대화 초기화’로 기록을 지울 수 있어요.</div>",
        unsafe_allow_html=True
    )

    temperature = st.slider("temperature", 0.0, 1.2, 0.7, 0.1)

    if st.button("🧹 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =========================
# 5) 대화 기록 초기화
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# 6) 말풍선 렌더링 함수
# =========================
def render_bubble(role: str, content: str):
    role_label = "나" if role == "user" else "챗봇"
    bubble_class = "bubble-user" if role == "user" else "bubble-assistant"
    st.markdown(
        f"""
        <div class="role-tag">{role_label}</div>
        <div class="bubble {bubble_class}">{content}</div>
        """,
        unsafe_allow_html=True
    )

# =========================
# 7) 이전 대화 출력
# =========================
for msg in st.session_state.messages:
    if msg["role"] in ("user", "assistant"):
        render_bubble(msg["role"], msg["content"])

# =========================
# 8) 입력 + 응답
# =========================
user_input = st.chat_input("메시지를 입력하세요…")

if user_input:
    # (1) 사용자 메시지 저장/표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    render_bubble("user", user_input)

    # (2) 모델 호출용 messages 구성 (system은 매번 앞에 붙이기)
    messages_for_api = [
        {"role": "system", "content": "너는 친절한 한국어 챗봇이야. 핵심만 짧고 명확하게 답해줘."},
        *st.session_state.messages
    ]

    # (3) 응답 받기
    with st.spinner("생각 중..."):
        try:
            res = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages_for_api,
                temperature=temperature
            )
            answer = res.choices[0].message.content
        except Exception as e:
            st.error(f"에러가 발생했어: {e}")
            st.stop()

    # (4) 저장/표시
    st.session_state.messages.append({"role": "assistant", "content": answer})
    render_bubble("assistant", answer)
