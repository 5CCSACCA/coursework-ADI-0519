from yolo_service.model import YOLOPredictor


def test_yolo_predictor():
    predictor = YOLOPredictor()
    assert predictor.min_conf > 0
