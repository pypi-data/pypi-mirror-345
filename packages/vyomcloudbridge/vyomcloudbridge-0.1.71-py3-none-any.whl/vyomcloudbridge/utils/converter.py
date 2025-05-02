import sensor_msgs.msg 
import cv2
from cv_bridge import CvBridge
import base64
import numpy as np
import json
from rosidl_runtime_py.convert import message_to_ordereddict

def compress_and_encode_image(msg, quality=100, max_width=800):
    """
    Compress an image message and encode it as base64 string
    
    Args:
        msg: ROS image message
        quality: JPEG quality (0-100), lower means more compression
        max_width: Maximum width to resize to (keeps aspect ratio)
        
    Returns:
        dict: Dictionary with base64 encoded image and metadata
    """
    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    
    # Resize the image if needed while maintaining aspect ratio
    height, width = cv_image.shape[:2]
    if width > max_width:
        scale_factor = max_width / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        cv_image = cv2.resize(cv_image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Encode the image as JPEG with compression
    encode_params = [cv2.IMWRITE_JPEG_PROGRESSIVE, 1, cv2.IMWRITE_JPEG_QUALITY, quality]
    success, encoded_image = cv2.imencode('.jpg', cv_image, encode_params)
    
    if not success:
        raise ValueError("Image encoding failed")
    
    # Convert to base64
    base64_encoded = base64.b64encode(encoded_image).decode('utf-8')
    
    # Create response dictionary with image data and metadata
    result = {
        "image_base64": base64_encoded,
        "format": "jpeg",
    }

    json_string = json.dumps(result)
    
    # print(f"Compressed image size: {len(encoded_image)} bytes")
    # print(f"Base64 string size: {len(base64_encoded)} characters")
    # print(f"Json_string: {json_string}")
    return json_string

def convert(msg_type, format, msg):
    if msg_type == sensor_msgs.msg.Image:

        return compress_and_encode_image(msg)
    else:
        return message_to_ordereddict(msg)