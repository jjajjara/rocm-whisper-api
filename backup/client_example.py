import requests
import os
import argparse
import mimetypes

# API 서버의 주소입니다.
API_URL = "http://localhost:8080/transcribe"

def get_mime_type(file_path):
    """파일 경로를 기반으로 MIME 타입을 추측합니다."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type
    
    # 추측에 실패할 경우, 확장자를 기반으로 일반적인 타입을 반환합니다.
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.m4a':
        return 'audio/mp4'
    if ext == '.mp3':
        return 'audio/mpeg'
    if ext == '.wav':
        return 'audio/wav'
    # 기본값
    return 'application/octet-stream'

def test_transcribe_api(file_path):
    """
    지정된 오디오 파일을 Whisper API 서버로 보내고 결과를 출력하는 함수입니다.
    """
    # 1. 파일이 존재하는지 확인합니다.
    if not os.path.exists(file_path):
        print(f"오류: 테스트 파일을 찾을 수 없습니다. '{file_path}'")
        return

    # 2. 파일의 MIME 타입을 동적으로 결정합니다.
    mime_type = get_mime_type(file_path)
    print(f"파일: '{os.path.basename(file_path)}', MIME 타입: '{mime_type}'")

    # 3. 파일을 바이너리 읽기 모드('rb')로 엽니다.
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, mime_type)}
        
        print(f"파일을 API 서버({API_URL})로 전송합니다...")
        
        try:
            # 4. requests 라이브러리를 사용하여 POST 요청을 보냅니다.
            response = requests.post(API_URL, files=files, timeout=300)

            # 5. 응답을 처리합니다.
            if response.status_code == 200:
                result = response.json()
                print("\n--- 변환 성공 ---")
                print(f"파일명: {result.get('filename')}")
                print(f"감지된 언어: {result.get('language')}")
                print(f"변환된 텍스트: {result.get('text')}")
            else:
                print(f"\n--- 오류 발생 ---")
                print(f"상태 코드: {response.status_code}")
                print(f"에러 내용: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"\n--- API 요청 중 오류 발생 ---")
            print(f"서버에 연결할 수 없거나 요청에 실패했습니다: {e}")

if __name__ == "__main__":
    # 명령줄에서 인수를 받기 위한 파서를 설정합니다.
    parser = argparse.ArgumentParser(
        description="오디오 파일을 Whisper API로 보내 텍스트로 변환합니다.",
        epilog="사용 예: python client_example.py ./audio/my_recording.mp3"
    )
    # 'filepath'라는 이름의 필수 인수를 추가합니다.
    parser.add_argument("filepath", help="변환할 오디오 파일의 경로")
    
    args = parser.parse_args()
    
    # 인수로 받은 파일 경로를 사용하여 API 함수를 호출합니다.
    test_transcribe_api(args.filepath)

