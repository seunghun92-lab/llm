import streamlit as st
from openai_service import ask_gpt, tts  # stt_file은 아래에서 안내

try:
    from openai_service import stt_file  # openai_service.py에 추가한 경우
except ImportError:
    stt_file = None  # 없으면 텍스트 입력만 사용

def main():
    st.set_page_config(
        page_title='😎Voice Chatbot😎',
        page_icon="🎤",
        layout='wide'
    )
    st.header('🎤Voice Chatbot🎤')
    st.markdown('---')

    with st.expander('Voice Chatbot 프로그램 처리절차', expanded=False):
        st.write(
            """
            1. 음성 파일(wav/mp3/m4a)을 업로드하거나, 텍스트로 질문을 입력합니다.
            2. 음성 파일 업로드 시 Whisper로 STT(음성→텍스트)를 수행합니다.
            3. 변환된 텍스트(또는 입력 텍스트)로 LLM에 질의 후 응답을 받습니다.
            4. LLM의 응답을 TTS로 음성으로 변환하여 자동 재생합니다.
            5. 모든 질문/답변은 채팅 형식으로 화면에 표시합니다.
            """
        )

    system_prompt = '당신은 친절한 챗봇입니다. 사용자의 질문에 50단어 이내로 간결하게 답변해주세요.'

    # session_state 초기화
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{'role': 'system', 'content': system_prompt}]
    if 'check_reset' not in st.session_state:
        st.session_state['check_reset'] = False

    with st.sidebar:
        model = st.radio(label='GPT 모델', options=['gpt-4.1-mini', 'gpt-5-nano', 'gpt-5.2'], index=0)

        if st.button(label='초기화'):
            st.session_state['messages'] = [{'role': 'system', 'content': system_prompt}]
            st.session_state['check_reset'] = True

        st.markdown('---')
        st.caption("🎙️ 강의실 PC 일부에서 ffmpeg(Device Guard) 차단 이슈가 있어, 녹음 위젯 대신 업로드/텍스트 입력으로 구성했습니다.")

    col1, col2 = st.columns(2)

    # =======================
    # (1) 입력 영역
    # =======================
    with col1:
        st.subheader('입력하기')

        # 1) 음성 업로드
        st.markdown("### 🎧 음성 파일 업로드")
        uploaded = st.file_uploader(
            "wav/mp3/m4a 파일을 올려주세요",
            type=["wav", "mp3", "m4a"],
            accept_multiple_files=False
        )

        # 2) 텍스트 입력 (업로드가 없거나 STT 함수가 없을 때 대비)
        st.markdown("### ⌨️ 텍스트로 질문")
        typed_text = st.text_input("질문을 입력하세요", value="", placeholder="예) 점심 뭐 먹을까?")

        # 실행 버튼 (업로드 또는 텍스트 둘 중 하나라도 있으면 활성)
        can_run = (uploaded is not None and stt_file is not None) or (typed_text.strip() != "")
        run_clicked = st.button("질문 보내기", disabled=not can_run)

        # 리셋 직후 1회 처리 방지 플래그 해제
        if st.session_state['check_reset']:
            st.session_state['check_reset'] = False

        if run_clicked:
            # 1) 음성 업로드가 있고 stt_file이 있으면 STT 수행
            if uploaded is not None and stt_file is not None:
                st.audio(uploaded.getvalue())  # 업로드한 파일 미리 듣기
                query = stt_file(uploaded)
            else:
                # 2) 그 외에는 텍스트 입력 사용
                query = typed_text.strip()

            if not query:
                st.warning("질문이 비어 있습니다.")
                return

            # GPT 질의
            st.session_state['messages'].append({'role': 'user', 'content': query})
            response = ask_gpt(st.session_state['messages'], model)
            st.session_state['messages'].append({'role': 'assistant', 'content': response})

            # TTS 재생
            base64_encoded_audio = tts(response)
            st.html(f"""
            <audio autoplay="true">
                <source src="data:audio/mp3;base64,{base64_encoded_audio}">
            </audio>
            """)

    # =======================
    # (2) 채팅 로그
    # =======================
    with col2:
        st.subheader('질문/답변')

        for message in st.session_state['messages']:
            role = message['role']
            content = message['content']

            if role == 'system':
                continue

            with st.chat_message(role):
                st.markdown(content)

        if stt_file is None:
            st.info("ℹ️ openai_service.py에 stt_file()이 없어서, 현재는 '텍스트 질문'만 가능합니다. (아래 안내 참고)")

if __name__ == '__main__':
    main()