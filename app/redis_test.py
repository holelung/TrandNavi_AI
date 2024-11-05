import redis

# Redis 서버 URL 설정
REDIS_URL = "redis://localhost:6379/0"

try:
    # Redis 클라이언트 생성
    client = redis.from_url(REDIS_URL)
    client.ping()
    print("Redis 서버에 성공적으로 연결되었습니다!")

    # 데이터 추가 예제
    client.set("test_key", "Hello, Redis! yo")
    value = client.get("test_key")
    print("Redis에서 가져온 값:", value.decode("utf-8"))
except redis.ConnectionError as e:
    print("Redis 서버에 연결할 수 없습니다:", e)