import argparse
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Predict using trained YOLO model")
    parser.add_argument("--source", type=str, default="0", help="Source for inference: '0' for webcam, or path to image/video/folder. Default is '0' (webcam).")
    parser.add_argument("--weights", type=str, default="textile_defect_model.pt", help="Path to trained model weights. Default is 'textile_defect_model.pt'.")
    args = parser.parse_args()

    # Load the trained model
    model = YOLO(args.weights)
    
    # Run prediction
    # show=True will display the results in a new window
    # stream=True is memory efficient for videos/webcams
    print(f"Starting prediction with source: '{args.source}'...")
    print("If you are using a camera, a window will pop up. Press 'q' in the window to quit.")
    
    # Perform prediction (conf=0.5 ensures we only see confident detections, reducing hallucinations)
    results = model.predict(source=args.source, show=True, stream=True, conf=0.5)
    
    # Since stream=True returns a generator, we iterate through it to process the frames
    for result in results:
        # The display is handled automatically by show=True, so we just pass
        pass

if __name__ == "__main__":
    main()
