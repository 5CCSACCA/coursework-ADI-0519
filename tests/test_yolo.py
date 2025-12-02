import pytest

from yolo_service.model import YOLOPredictor


def test_yolo_predictor():
    predictor = YOLOPredictor()
    assert predictor.min_conf > 0


def test_model_loads():
    predictor = YOLOPredictor()
    assert predictor.model is not None


def test_missing_file():
    predictor = YOLOPredictor()
    with pytest.raises(FileNotFoundError):
        predictor.predict("nonexistent.jpg")
