from __future__ import annotations

from app.models.sensor_autoencoder import (
    SensorAutoEncoder,
    calculate_reconstruction_error,
)


MODEL = SensorAutoEncoder()

# 포트폴리오용 기본 임계값입니다.
# 실제 서비스에서는 검증 데이터 기반으로 threshold를 산정해야 합니다.
ANOMALY_SCORE_THRESHOLD = 1000.0


def predict_sensor_anomaly(
    temperature: float,
    vibration: float,
    pressure: float,
) -> dict:
    """
    PyTorch AutoEncoder를 사용해 센서 입력값의 anomaly score를 계산합니다.
    """
    sensor_values = [temperature, vibration, pressure]
    anomaly_score = calculate_reconstruction_error(MODEL, sensor_values)

    is_anomaly = anomaly_score >= ANOMALY_SCORE_THRESHOLD

    return {
        "temperature": temperature,
        "vibration": vibration,
        "pressure": pressure,
        "anomaly_score": anomaly_score,
        "threshold": ANOMALY_SCORE_THRESHOLD,
        "is_anomaly": is_anomaly,
        "model": "SensorAutoEncoder",
        "note": (
            "현재 모델은 포트폴리오용 기본 AutoEncoder 구조입니다. "
            "실제 운영에서는 정상 센서 데이터로 학습한 weight와 검증 기반 threshold가 필요합니다."
        ),
    }