import argparse
import os

import cv2

from mycobot_mcp.object_detection import ObjectDetection


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", type=str)
    args = parser.parse_args()
    os.environ["DDS_API_TOKEN"] = "aecc0c90cfd8eb105c84047712e4406f"

    object_detection = ObjectDetection(["apple", "banana", "orange"])
    image_path = args.image_path
    objects = object_detection.detect(image_path)
    annotated_frame = object_detection.visualize(image_path, objects, with_mask=False)
    print(objects)
    cv2.imwrite(os.path.splitext(image_path)[0] + "_annotated.png", annotated_frame)
