from app.services.torch_anomaly_service import predict_sensor_anomaly


def test_predict_sensor_anomaly_returns_score():
    result = predict_sensor_anomaly(
        temperature=95.7,
        vibration=5.6,
        pressure=2.4,
    )

    assert result["model"] == "SensorAutoEncoder"
    assert "anomaly_score" in result
    assert "is_anomaly" in result
    assert isinstance(result["anomaly_score"], float)
    assert isinstance(result["is_anomaly"], bool)