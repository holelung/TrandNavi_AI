from app import create_app
from app.redis_handler import redis_client

app = create_app()

def clear_all_sessions():
    """Redis에 저장된 모든 세션 값을 초기화"""
    keys = redis_client.keys('*')  # 모든 키 가져오기
    if keys:
        redis_client.delete(*keys)  # 모든 키 삭제
        print(f"{len(keys)}개의 세션이 초기화되었습니다.")
    else:
        print("초기화할 세션이 없습니다.")

if __name__ == '__main__':
    # 초기화 코드 실행
    clear_all_sessions()  # 앱 시작 시 Redis 세션 초기화
    app.run(debug=True)
