from ultralytics import YOLO
from importlib import resources
import cv2
import os
from datetime import datetime
import json
import uuid
import requests
from tqdm import tqdm

MODEL_MAP = {
    "v8": "yv8_all_best.pt",
    "v9": "yv9_all_best.pt",
    "v10": "yv10_all_best.pt",
    "v8_africa": "yv8_africa_30e_best.pt",
    "v9_africa": "yv9_africa_30e_best.pt",
    "v10_africa": "yv10_africa_25e_best.pt",
    "v8_asia": "yv8_asia_30e_best.pt",
    "v9_asia": "yv9_asia_30e_best.pt",
    "v10_asia": "",
    "v8_europe": "",
    "v9_europe": "yv9_europe_40e_best.pt",
    "v10_europe": "yv10_europe_30e_best.pt",
    "v8_northamerica": "yv8_northamerica_30e_best.pt",
    "v9_northamerica": "yv9_northamerica_30e_best.pt",
    "v10_northamerica": "yv10_northamerica_25e_best.pt",
    "v8_oceania": "yv8_oceania_30e_best.pt",
    "v9_oceania": "yv9_oceania_30e_best.pt",
    "v10_oceania": "",
    "v8_southamerica": "yv8_southamerica_30e_best.pt",
    "v9_southamerica": "yv9_southamerica_30e_best.pt",
    "v10_southamerica": "yv10_southamerica_25e_best.pt"
}

# for usage from hugging face
MODEL_URL_BASE = "https://huggingface.co/tiloftus/flagsense_models/resolve/main"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".flagsense_models")

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PACKAGE_DIR, "models")
#YV8_ALL_PATH = os.path.join(PACKAGE_DIR, "models", "yv8_all_best.pt")

class Detector:
    def __init__(self, model_name: str = "v8"):
        """Initialize the model- defaults to YOLOv8 all country model."""
        if model_name not in MODEL_MAP:
            raise ValueError(f"Unknown model name '{model_name}'. Available options: {list(MODEL_MAP.keys())}")
        
        #with resources.path("flagsense.models", MODEL_MAP[model_name]) as model_path:
        #    self.model = YOLO(str(model_path))
        print(model_name)
        model_path = download_model_if_needed(model_name)
        print(model_path)
        self.model = YOLO(model_path)

    def detect(self, image_path: str, save_dir: str = None, verbose: bool = False):
        """Run model on an image, return detections, and optionally save results."""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        results = self.model(img)

        img_h, img_w = img.shape[:2]
        base_filename = os.path.splitext(os.path.basename(image_path))[0]

        # Save the image with bounding boxes overlaid - only do if --verbose flag
        if verbose:
            annotated_img = results[0].plot()
            overlay_dir = os.path.join(save_dir, "image_overlay")
            os.makedirs(overlay_dir, exist_ok=True)
            annot_overlay_path = os.path.join(overlay_dir, f"{base_filename}_annotated.jpg")
            #print(annot_overlay_path)
            cv2.imwrite(annot_overlay_path, annotated_img)
            print(f"Annotated image saved at {annot_overlay_path}")

        # Create YOLO format annotations
        yolo_dir = os.path.join(save_dir, "yolo")
        os.makedirs(yolo_dir, exist_ok=True)
        annot_yolo_path = os.path.join(yolo_dir, f"{base_filename}.txt")
        with open(annot_yolo_path, "w") as f:
            for box in results[0].boxes:
                cls_id = int(box.cls[0].item())  # class id
                xywh = box.xywh[0].cpu().tolist()  # x_center, y_center, width, height (in pixels)
                img_h, img_w = img.shape[:2]

                # Normalize values
                x_c = xywh[0] / img_w
                y_c = xywh[1] / img_h
                w = xywh[2] / img_w
                h = xywh[3] / img_h

                f.write(f"{cls_id} {x_c:.6f} {y_c:.6f} {w:.6f} {h:.6f}\n")        

        print(f"YOLO-format annotation saved at {annot_yolo_path}")

        # Create COCO JSON format annotations
        coco_dir = os.path.join(save_dir, "coco")
        os.makedirs(coco_dir, exist_ok=True)
        annot_coco_path = os.path.join(coco_dir, f"{base_filename}_coco.json")
        coco_dict = {
            "info": {
                "description": "Single image COCO-style annotations",
                "version": "1.0",
                "date_created": datetime.utcnow().isoformat()
            },
            "images": [{
                "id": image_path,
                "width": img_w,
                "height": img_h,
                "file_name": image_path
            }],
            "annotations": [],
            "categories": []  # Optional unless using class names
        }

        for idx, box in enumerate(results[0].boxes):
            cls_id = int(box.cls[0].item())
            xywh = box.xywh[0].cpu().tolist()  # center_x, center_y, width, height
            x_c, y_c, w, h = xywh
            x_min = x_c - w / 2
            y_min = y_c - h / 2

            annotation = {
                "id": idx,
                "image_id": image_path,
                "category_id": cls_id,
                "bbox": [x_min, y_min, w, h],  # COCO uses absolute pixel coordinates
                "area": w * h,
                "iscrowd": 0
            }
            coco_dict["annotations"].append(annotation)

        with open(annot_coco_path, "w") as f:
            json.dump(coco_dict, f, indent=4)
        print(f"COCO-format annotation saved at {annot_coco_path}")

        return results  # Returns "results" data type
    
def download_model_if_needed(model_name: str):
    """Download model from Hugging Face if not already cached."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    filename = MODEL_MAP[model_name]
    local_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(local_path):
        return local_path
        
    url = f"{MODEL_URL_BASE}/{filename}"
    print(f"Downloading model '{model_name}' from {url}...")
        
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))

    with open(local_path, 'wb') as f, tqdm(
        total=total,
        unit='iB',
        unit_scale=True,
        desc=filename
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)
            bar.update(len(chunk))

    print(f"Model downloaded and cached at: {local_path}")
    return local_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run model detection.")
    parser.add_argument("image_path", help="Path to the image file.")

    args = parser.parse_args()

    detector = Detector()
    detector.detect(args.image_path)