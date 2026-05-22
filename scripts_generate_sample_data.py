from __future__ import annotations # 미래 기능 활성화 : Python 3.7 이상에서 타입 힌트에 forward reference (아직 정의되지 않은 클래스 이름)를 문자열 대신 직접 쓸 수 있도록 해줌

import csv # csv 파일 읽기 / 쓰기
import random # 난수 생성
from pathlib import Path # 파일 경로 관리
from datetime import datetime, timedelta # 날짜와 시간 계산

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
# 현재 파일 위치 기준으로 data 폴더를 생성. 없으면 새로 만듦

random.seed(42)
# 난수 생성 시 항상 같은 결과가 나오도록 시드 고정.(재현성 확보)

LINES = ["LINE_A", "LINE_B", "LINE_C", "LINE_D"]
PRODUCTS = ["PANEL_X", "MOTOR_Y", "SENSOR_Z"]
DEFECT_TYPES = ["scratch", "dimension_error", "assembly_error", "contamination"]
# 생산 라인, 제품, 불량 유형 리스트 정의

def generate_production_logs(days: int = 14) -> None:
    today = datetime(2026, 5, 22)

    with open(DATA_DIR / "production_logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "line_id",
                "product_code",
                "output_qty",
                "operating_hours",
            ],
        )
        writer.writeheader()
        # CSV 파일 생성, 헤더 작성

        for d in range(days):
            date = today - timedelta(days=days - d - 1)
            # 날짜를 하루씩 거슬러 올라가며 기록

            for line in LINES:
                base_output = 900 + LINES.index(line) * 80
                output_qty = int(random.gauss(base_output, 70))
                # 라인별 기본 생산량 설정 후 정규분호로 변동치 추가

                writer.writerow(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "line_id": line,
                        "product_code": random.choice(PRODUCTS),
                        "output_qty": max(output_qty, 500),
                        "operating_hours": round(random.uniform(7.2, 8.5), 2),
                    }
                )


def generate_quality_logs(days: int = 14) -> None:
    today = datetime(2026, 5, 22)

    with open(DATA_DIR / "quality_inspection.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "line_id",
                "inspected_qty",
                "defect_qty",
                "defect_type",
            ],
        )
        writer.writeheader()

        for d in range(days):
            date = today - timedelta(days=days - d - 1)

            for line in LINES:
                inspected_qty = random.randint(760, 1150)

                base_rate = 0.018

                # LINE_C는 의도적으로 불량률이 높게 설계
                if line == "LINE_C":
                    base_rate = 0.045

                # 최근 며칠간 LINE_B도 약간 악화
                if line == "LINE_B" and d > days - 5:
                    base_rate = 0.038

                defect_qty = int(
                    inspected_qty * random.uniform(base_rate * 0.7, base_rate * 1.4)
                )

                writer.writerow(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "line_id": line,
                        "inspected_qty": inspected_qty,
                        "defect_qty": defect_qty,
                        "defect_type": random.choice(DEFECT_TYPES),
                    }
                )


def generate_sensor_logs(days: int = 14) -> None:
    start = datetime(2026, 5, 22) - timedelta(days=days - 1)

    with open(DATA_DIR / "machine_sensor_logs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp",
                "line_id",
                "machine_id",
                "temperature",
                "vibration",
                "pressure",
            ],
        )
        writer.writeheader()

        for d in range(days):
            day = start + timedelta(days=d)

            for hour in [0, 4, 8, 12, 16, 20]:
                timestamp = day + timedelta(hours=hour)

                for line in LINES:
                    temperature = random.gauss(76, 4)
                    vibration = random.gauss(3.2, 0.5)
                    pressure = random.gauss(2.2, 0.25)

                    # LINE_C는 최근 구간에서 설비 이상이 발생하도록 설계
                    if line == "LINE_C" and d >= days - 6 and hour in [12, 16]:
                        temperature += random.uniform(9, 14)
                        vibration += random.uniform(1.1, 1.8)

                    writer.writerow(
                        {
                            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            "line_id": line,
                            "machine_id": f"{line}_M01",
                            "temperature": round(temperature, 2),
                            "vibration": round(vibration, 2),
                            "pressure": round(pressure, 2),
                        }
                    )


if __name__ == "__main__":
    generate_production_logs()
    generate_quality_logs()
    generate_sensor_logs()
    print(f"Sample data generated in {DATA_DIR}")