import os

import cv2

from mycobot_mcp.robot_operator import RobotOperator
from mycobot_mcp.settings import MyCobotMCPSettings


if __name__ == "__main__":
    os.environ["DDS_API_TOKEN"] = "aecc0c90cfd8eb105c84047712e4406f"
    settings = MyCobotMCPSettings()
    operator = RobotOperator(settings)
    result = operator.capture_and_detect(["apple", "banana", "orange"])
    cv2.imwrite("result.png", result.annotated_image)
