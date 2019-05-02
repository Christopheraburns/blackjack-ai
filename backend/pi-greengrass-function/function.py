import greengrasssdk
import logging
import json
import picamera
import boto3
from botocore.config import Config
import io
import numpy as np
from PIL import Image
import uuid
from datetime import datetime
from threading import Timer

s3_config = Config(s3={"use_accelerate_endpoint": True})
bucket = 'remars2019-revegas-imageslanding'

s3_resource = boto3.resource('s3', region_name='us-east-1', config=s3_config
)

s3 = s3_resource.meta.client
client = greengrasssdk.client('iot-data')

def crop_image(img, crop_area, new_bytesio):
    cropped_image = img.crop(crop_area)
    cropped_image.save(new_bytesio)
    

def take_pics(bucket):
    # camera start
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
    #     'pl1': (400, 400, 800, 800),
    #     'pl2': (400, 400, 800, 800),
    #     'pl3': (400, 400, 800, 800),
    #     'pl4': (400, 400, 800, 800),
    #     'pl5': (400, 400, 800, 800),
    #     'dlr': (400, 400, 800, 800)
    # }
    
    img_whole = Image.open(stream)
    
    for k, v in crop_areas.items():
        crop_img_bytes = io.BytesIO()
        crop_image(img_whole, v, crop_img_bytes)
        img_name = 'images/' + str(uuid.uuid4()) + k + ".jpg"
        s3.upload_fileobj(crop_img_bytes, bucket, img_name, ExtraArgs={'ContentType': 'image/jpeg'})
        payload = {'s3Key': img_name}
        client.publish(topic="newimages" + k, payload=json.dumps(payload))
    
    # comment this out in prod
    s3.upload_fileobj(stream, bucket, 'raw/' + str(uuid.uuid4()) + ".jpg", ExtraArgs={'ContentType': 'image/jpeg'})
    
    Timer(2, take_pics(bucket=bucket)).start()
        
take_pics(bucket=bucket)

def function_handler(event, context):
    return