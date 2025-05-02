import unittest
from yolo10_package.yolo_inference import YOLOv10Detector

class TestYOLOv10(unittest.TestCase):
    def test_model_init(self):
        detector = YOLOv10Detector()
        self.assertIsNotNone(detector.model)

if __name__ == "__main__":
    unittest.main()
