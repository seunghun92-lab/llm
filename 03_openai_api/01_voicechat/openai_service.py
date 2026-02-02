# SST (Speech -> Text) + GPT 응답 + TTS (Text -> Speech) 파이프라인 함수 모음
# SST : 사용자의 음성 파일을 텍스트로 변환 (Whisper 모델 등)
# LLM(GPT) : 변환된 텍스트를 이해하고 적절한 답변 생성
# TTS : 생성된 답변을 다시 음성 파일로 변환

# 필요한 라이브러리 호출
import base64                       # mp3 이진데이터를 base64 문자열로 데이터 인코딩 (생성된 음성(이진데이터)를 웹이나 앱에서 주고 받기 위해 문자열 형태로 바꾸는 기술)
from dotenv import load_dotenv      # .env 환경 변수 관리 (API키를 가져옴. os.environ)
from openai import OpenAI           # OpenAI 클라이언트 클래스
import os                           # 운영

load_dotenv()       # .env 파일을 읽어서 환경변수 등록. 
OPENAI_API_KEY = os.environ['openai_key']       # .env 에 저장된 openai_key 값을 가져옴
client = OpenAI(api_key= OPENAI_API_KEY)        # OpenAI 클라이언트 객체 생성 (키 직접 주입)


# 오디오 객체를 Whisper로 SST하여 텍스트로 반환하는 함수 (음성을 글자로 바꾸기)
def stt(audio):
    output_filepath = 'input.mp3'                  # input.mp3(임시 저장용 파일) 파일에 임시 저장함.
    audio.export(output_filepath, format = 'mp3')   # 오디오 객체를 mp3 파일로 저장


    with open(output_filepath, 'rb') as f:          # 저장된 파일을 바이너리 형식으로 연다.
        # STT 요청 (음성 -> TXT) 
        transcription = client.audio.transcriptions.create(
            model = 'whisper-1',
            file = f
        )
    
    os.remove(output_filepath)         # 임시로 만든 파일(input.mp3)을 삭제 (.mp4는 영상 등 여러가지 가능.? 뭐가 들어오든 mp3형태로)

    return transcription.text       # STT 결과 텍스트 반환

# 메세지 히스토리와 모델을 받아 해당 GPT로 응답을 생성하는 함수 (질문을 하고 답변 받기)
def ask_gpt(messages, model):
    # GPT 채팅 응답 반환
    return client.chat.completions.create(
        model = model,
        messages = messages,
        temperature= 1,                 # 창의성 (생성 다양성) : 높을 수록 랜덤성(창의성)
        top_p= 1,                       # nucleus sampling(1이면 제한 없음)
        max_completion_tokens= 4096     # 생성 토큰 최대치를 기록 : 답변 최대 길이를 제한
    ).choices[0].message.content        # 첫번째 응답 텍스트 

# 텍스트를 TTS로 mp3로 생성 후 base64 문자열로 반환하는 함수
def tts(response: str):
    filename = 'output.mp3'     # TTS 결과 mp3 파일명 지정
    # 스트리밍 방식의 TTS 요청
    with client.audio.speech.with_streaming_response.create(
        model = 'tts-1',
        voice = 'alloy',     # 음성 톤/캐릭터
        input = response     # 음성으로 변환할 텍스트
    ) as resp:
        resp.stream_to_file(filename)   # 스트리밍 결과를 mp3 파일로 저장

    with open(filename, 'rb') as f:     # rb: 리드바이너리.  생성된 mp3 파일을 바이너리로 읽기
        data = f.read()                 # mp3 이진 데이터 읽기
        b64_encoded = base64.b64encode(data).decode()     # 두가지 과정 : (1)이진 데이터 -> Base64 이진  / (2) Base64 이진 -> 문자열

    os.remove(filename)     # 생성된 출력 mp3 파일 삭제

    return b64_encoded      # base64 문자열 반환 (웹/앱에서 바로 재생용)

# ===========================================================================================================================
# 바이너리(binary)는 사람이 읽는 문자(text)가 아니라, 0과 1 (바이트)로 된 원본 데이터(컴퓨터가 이해하는 언어)
# 바이너리 모드 ('rb'): 데이터를 가공하지 않고, 0과 1로 된 있는 그대로의 이진 데이터를 바이트(bytes) 단위로 읽어옵니다.
# mp3, jpg, png, pdf 같은 파일은 대부분 바이너리 파일이다.

# - 텍스트 형식 ('r') : 사람이 읽을 수 있는 글자 데이터 (예 : "hello", JSON 문자열, CSV 내용)
# - 바이너리 형식 ('rb') : 파일 자체의 원본 바이트 (byte) 데이터 (예 : mp3, jpg, png, pdf)

# 1. 텍스트 vs 바이너리 💿
# 텍스트 모드 ('r'): 사람이 읽을 수 있는 글자(A, B, 가, 나)로 해석해서 가져옵니다. 줄바꿈 문자를 운영체제에 맞게 자동으로 바꿔주기도 하죠.
# 바이너리 모드 ('rb'): 데이터를 가공하지 않고, 0과 1로 된 있는 그대로의 이진 데이터를 바이트(bytes) 단위로 읽어옵니다.


# 업로드된 음성 파일을 텍스트로 변환(STT)해서 반환하는 함SIUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
def stt_file(uploaded_file) -> str:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=(uploaded_file.name, uploaded_file.getvalue()) # (파일명, 파일바이트) 튜플
    )
    return transcription.text                   # STT 결과 텍스트만 반환
