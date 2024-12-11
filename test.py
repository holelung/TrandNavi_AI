from app.db.task import save_message_to_db_from_redis

def test_save_message_to_db():
    """
    Redis 데이터를 MySQL로 동기화하는 Celery 작업 호출 테스트.
    """
    try:
        # 테스트로 호출할 Room ID 및 배치 크기
        room_id = 1
        batch_size = 10

        # Celery 작업 호출
        result = save_message_to_db_from_redis.delay(room_id=room_id, batch_size=batch_size)
        print(f"[INFO] Celery 작업 호출 완료. Task ID: {result.id}")
        print("[INFO] Celery 작업이 완료되기를 기다리는 중...")

        # 작업 상태 확인 (비동기 처리)
        result.get(timeout=30)  # 최대 30초 대기
        print("[SUCCESS] Redis 데이터를 MySQL로 성공적으로 동기화했습니다.")

    except Exception as e:
        print(f"[ERROR] 테스트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    test_save_message_to_db()
