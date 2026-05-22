from __future__ import annotations

import torch
from torch import nn


class SensorAutoEncoder(nn.Module):
    """
    제조 설비 센서 값 temperature, vibration, pressure를 입력으로 받는
    간단한 AutoEncoder 모델입니다.

    현재 프로젝트에서는 포트폴리오용 최소 모델 서빙 구조를 보여주기 위해
    학습된 weight 파일 없이 기본 초기화 모델을 사용합니다.
    """

    def __init__(self, input_dim: int = 3, hidden_dim: int = 2) -> None:
        super().__init__()

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
        )

        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim, input_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        encoded = self.encoder(x)
        reconstructed = self.decoder(encoded)
        return reconstructed


def calculate_reconstruction_error(
    model: SensorAutoEncoder,
    sensor_values: list[float],
) -> float:
    """
    입력 센서값과 AutoEncoder 복원값의 평균 제곱 오차를 계산합니다.
    """
    model.eval()

    with torch.no_grad():
        x = torch.tensor([sensor_values], dtype=torch.float32)
        reconstructed = model(x)
        error = torch.mean((x - reconstructed) ** 2).item()

    return float(error)