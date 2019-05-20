import greengrasssdk
import logging
import json
import picamera
import boto3
import os
from botocore.config import Config
import io
import numpy as np
from PIL import Image
import uuid
from datetime import datetime
from threading import Timer
from time import sleep
from goprocam import GoProCamera, constants


'''Upload to S3 using Transfer Accelerate from the local
pi device'''
s3_config = Config(s3={"use_accelerate_endpoint": True})
bucket = 'remars2019-revegas-imageslanding'

s3_resource = boto3.resource('s3', region_name='us-east-1', config=s3_config
)

s3 = s3_resource.meta.client
client = greengrasssdk.client('iot-data')


def crop_image(img, crop_area, crop_img_bytes):
    cropped_image = img.crop(crop_area)
    cropped_image.save(crop_img_bytes, 'jpeg')
    

# TODO this function is a clone of take_pics.  crop_areas should be moved to global to avoid making multiple changes

def take_gopro_pics(bucket):
    '''
        Calls GoPro (Hero 7 Black) RESTFul API to take and download a picture from the camera
        * Requires this python library: https://github.com/KonradIT/gopro-py-api (pip install goprocam)
        * Camera must be powered on
        * The device running this code must be connected to the camera's wifi network
        * SSID is GP26185174 (Password is available to view on the GoPro camera connections - settings
        * Must be a 2.6GHZ NIC

    :param bucket:
    :return: void
    '''
    gpCam = GoProCamera.GoPro()
    gpCam.downloadLastMedia(gpCam.take_photo(0.1), "allhands.jpg")

    while True:
        exists = os.path.isfile("allhands.jpg")
        if exists:
            break

    img_whole = Image.open("allhands.jpg")

    crop_areas = {
        'pl1': (404, 157, 828, 682),
        'pl2': (846, 68, 1280, 566)
    }

    for k, v in crop_areas.items():
        '''Loop through the player regions, crop them, and upload them
        to s3 with the suffix on the key name. then send a message to IoT'''
        crop_img_bytes = io.BytesIO()
        crop_image(img_whole, v, crop_img_bytes)
        crop_img_bytes.seek(0)
        img_name = 'images/' + str(uuid.uuid4()) + k + ".jpg"
        s3.upload_fileobj(crop_img_bytes, bucket, img_name, ExtraArgs={'ContentType': 'image/jpeg'})
        payload = {'s3Key': img_name}
        client.publish(topic="newimages" + k, payload=json.dumps(payload))






def take_pics(bucket):
    # camera start (benchmark time it takes to take a pic)
    # cam_start = datetime.now()
    camera = picamera.PiCamera()
    stream = io.BytesIO()
    camera.start_preview()
    camera.capture(stream, use_video_port=True, format='jpeg', quality=100)
    stream.seek(0)
    camera.close()
    # camera end
    # cam_end = datetime.now() - cam_start
    # print("Time to take image: " + str(cam_end.total_seconds()))
    
    # initial test
    crop_areas = {
        'pl1': (404, 157, 828, 682),
        'pl2': (846, 68, 1280, 566)
    }
    
    # prod
    # update these with measurements from the raw/ dir above
    # crop_areas = {
    #     'pl1': (400, 400, 800, 800), # top-left (x,y), bottom-right (x,y)
    #     'pl2': (400, 400, 800, 800),
    #     'pl3': (400, 400, 800, 800),
    #     'pl4': (400, 400, 800, 800),
    #     'pl5': (400, 400, 800, 800),
    #     'dlr': (400, 400, 800, 800)
    # }
    
    img_whole = Image.open(stream)
    
    
    for k, v in crop_areas.items():
        '''Loop through the player regions, crop them, and upload them
        to s3 with the suffix on the key name. then send a message to IoT'''
        crop_img_bytes = io.BytesIO()
        crop_image(img_whole, v, crop_img_bytes)
        crop_img_bytes.seek(0)
        img_name = 'images/' + str(uuid.uuid4()) + k + ".jpg"
        s3.upload_fileobj(crop_img_bytes, bucket, img_name, ExtraArgs={'ContentType': 'image/jpeg'})
        payload = {'s3Key': img_name}
        client.publish(topic="newimages" + k, payload=json.dumps(payload))
    
    '''Use this to upload the whole image and measure the 6 regions, then
    comment it out to speed things up'''
    # s3.upload_fileobj(stream, bucket, 'raw/' + str(uuid.uuid4()) + ".jpg", ExtraArgs={'ContentType': 'image/jpeg'})

        

while 1:
    take_pics(bucket=bucket)
    sleep(5)


def function_handler(event, context):
    return