#!/usr/bin/python3
# coding=utf-8
import sys
import requests
import time
import datetime
import imageio as iio
from requests.auth import HTTPBasicAuth
import traceback
from tomato_analyzer import TomatoAnalyzer
import cv2
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
def load_env():
    """Load environment variables from different possible locations"""
    env_paths = [
        '/etc/tedge/.env',  # System-wide configuration
        '/bin/.env',        # Binary directory
        '.env'              # Current directory
    ]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            return True
    
    raise Exception("No .env file found in any of the expected locations")

# Load environment variables
load_env()

# Get environment variables with error handling
def get_env_variable(var_name):
    """Get environment variable with error handling"""
    value = os.getenv(var_name)
    if value is None:
        raise Exception(f"Environment variable {var_name} not found")
    return value

# Get configuration from environment variables
try:
    C8Y_BASEURL = get_env_variable('C8Y_BASEURL')
    TENANT_ID = get_env_variable('C8Y_TENANT_ID')
    USERNAME = get_env_variable('C8Y_USERNAME')
    PASSWORD = get_env_variable('C8Y_PASSWORD')
    WORKDIR = get_env_variable('WORKDIR')
except Exception as e:
    print(f"Configuration error: {str(e)}")
    sys.exit(1)

USER = f"{TENANT_ID}/{USERNAME}"
auth = HTTPBasicAuth(USERNAME, PASSWORD)

IMAGE_NAME = "webcam_image_analyzed.jpg"
IMAGE_PATH = f"{WORKDIR}/{IMAGE_NAME}"
TYPE = "image/jpeg"

# Initialize tomato analyzer
analyzer = TomatoAnalyzer()

def get_image_id() -> str:
    url = f"{C8Y_BASEURL}/inventory/binaries"
    params = {"pageSize": 2000, "type": TYPE}
    response = requests.get(url, params=params, auth=auth)
    for item in response.json()["managedObjects"]:
        if item["name"] == IMAGE_NAME:
            return item["id"]

def stream(minutes: int):
    timeout_timestamp = datetime.datetime.now() + datetime.timedelta(minutes=minutes)

    while datetime.datetime.now() < timeout_timestamp:
        startframetime = datetime.datetime.now()

        id = get_image_id()
        print(f"binary id read: {id}")

        if not id:
            raise Exception(
                f"No file of type {TYPE} and name {IMAGE_NAME} that can be updated"
            )

        # Capture image
        camera = iio.get_reader("<video0>")
        image = camera.get_data(0)
        camera.close()

        # Convert image from RGB to BGR (OpenCV format)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Analyze image
        analyzed_image, results = analyzer.analyze_image(image_bgr)
        
        # Save analyzed image
        cv2.imwrite(IMAGE_PATH, analyzed_image)

        # Upload to Cumulocity
        url = f"{C8Y_BASEURL}/inventory/binaries/{id}"
        headers = {"Content-Type": TYPE}
        payload = open(IMAGE_PATH, "rb")

        response = requests.request(
            "PUT", url, headers=headers, data=payload, auth=(USERNAME, PASSWORD)
        )

        time.sleep(10 - ((datetime.datetime.now() - startframetime).seconds))

    del camera

if __name__ == "__main__":
    try:
        device_id = sys.argv[1].split(",")[2]
        timeout_minutes = int(sys.argv[1].split(",")[3])
        stream(timeout_minutes)
    except Exception as e:
        print(e)
        traceback.print_exc()