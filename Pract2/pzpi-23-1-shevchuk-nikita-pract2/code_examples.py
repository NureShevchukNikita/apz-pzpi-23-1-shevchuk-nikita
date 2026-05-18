import time
from typing import Optional

class SpotifyCdnEdgeCache:
    def __init__(self) -> None:
        self._cached_chunks: dict[str, bytes] = {}

    def get_audio_chunk(self, track_id: str) -> Optional[bytes]:
        return self._cached_chunks.get(track_id)

    def cache_track(self, track_id: str, data: bytes) -> None:
        self._cached_chunks[track_id] = data

class ApolloApiGateway:
    def __init__(self, cdn_node: SpotifyCdnEdgeCache) -> None:
        self._cdn = cdn_node
        self._central_storage: dict[str, bytes] = {
            "track_404": b"[BinaryAudioData_Track404]",
            "track_777": b"[BinaryAudioData_Track777]"
        }

    def route_stream_request(self, user_id: str, track_id: str) -> bytes:
        cached_data = self._cdn.get_audio_chunk(track_id)
        if cached_data:
            return b"CDN_EDGE_SUCCESS: " + cached_data

        raw_data = self._central_storage.get(track_id, b"")
        if raw_data:
            self._cdn.cache_track(track_id, raw_data)
            return b"CENTRAL_CLOUD_FETCH_SUCCESS: " + raw_data
        return b"ERROR: TRACK_NOT_FOUND"


class KafkaAnalyticsEventBus:
    def __init__(self) -> None:
        self._topic_telemetry: list[dict] = []

    def publish_listen_event(self, user_id: str, track_id: str) -> None:
        event = {
            "timestamp": time.time(),
            "user_id": user_id,
            "track_id": track_id,
            "action": "play_completed"
        }
        self._topic_telemetry.append(event)

    def get_logged_events(self) -> list[dict]:
        return self._topic_telemetry


if __name__ == "__main__":
    cdn = SpotifyCdnEdgeCache()
    gateway = ApolloApiGateway(cdn)
    kafka = KafkaAnalyticsEventBus()

    print("--- Сценарій 1: Запит треку користувачем (Кеш пустий) ---")
    response1 = gateway.route_stream_request("user_nikita", "track_777")
    print(response1.decode('utf-8'))

    print("\n--- Сценарій 2: Повторний запит (Отримання через CDN Edge) ---")
    response2 = gateway.route_stream_request("user_anton", "track_777")
    print(response2.decode('utf-8'))

    print("\n--- Сценарій 3: Асинхронне відправлення події в Kafka Bus ---")
    kafka.publish_listen_event("user_nikita", "track_777")
    print("Зафіксовані події для аналітики Wrapped:", kafka.get_logged_events())
