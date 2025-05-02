from .yolo_inference import Detector
import argparse
import os

def is_image_file(filename):
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))	

def main():
	parser = argparse.ArgumentParser(description="Run Yolo detection.")
	parser.add_argument("input_path", help="Path to an image file or folder of images.")
	parser.add_argument(
		"--model",
		type=str,
		choices=["v8", "v9", "v10", "v8_africa", "v9_africa", "v10_africa", "v8_asia", 
		   "v9_asia", "v10_asia", "v8_europe", "v9_europe", "v10_europe", "v8_northamerica", 
		   "v9_northamerica", "v10_northamerica", "v8_oceania", "v9_oceania", "v10_oceania", 
		   "v8_southamerica", "v9_southamerica", "v10_southamerica"],
		default="v8",
		help="Choose between multiple object detection models. Defaults to YOLOv8."
	)
	parser.add_argument(
		"--verbose",
		action="store_true",
		help="If set, outputs additional annotation information."
	)

	args = parser.parse_args()
	input_path = args.input_path

	detector = Detector(model_name=args.model)
	#detector.detect(args.image_path, verbose=args.verbose)

	base_name = os.path.splitext(os.path.basename(input_path))[0]
	annotation_dir = os.path.abspath(f"{base_name}_annotations")
	os.makedirs(annotation_dir, exist_ok=True)

	if os.path.isdir(input_path):
        # Process all image files in the folder
		for filename in sorted(os.listdir(input_path)):
			file_path = os.path.join(args.input_path, filename)
			if is_image_file(file_path):
				try:
					print(f"\nProcessing: {file_path}")
					detector.detect(file_path, save_dir = annotation_dir, verbose=args.verbose)
				except Exception as e:
					print(f"Error processing {file_path}: {e}")
	elif os.path.isfile(input_path):
		detector.detect(input_path, save_dir = annotation_dir, verbose=args.verbose)
	else:
		raise ValueError(f"Invalid path: {args.input_path}")

if __name__ == "__main__":
	main()