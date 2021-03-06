import boto3
import json
import sagemaker
from sagemaker import mxnet
from sagemaker import get_execution_role
import io
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
from PIL import Image, ImageEnhance


# start AWS resources in global context
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
kinesis = boto3.client('kinesis')
role = get_execution_role()
print(role)
sess = sagemaker.Session()
iot_data = boto3.client('iot-data')

bucket_name = 'remars2019-revegas-imageslanding'

# don't touch!!! used to convert sagemaker's integer classes back to card values. 
class_map = {"AC": 0, "2C": 1, "3C": 2, "4C": 3, "5C": 4, "6C": 5, "7C": 6, "8C": 7, "9C": 8, "10C": 9, "JC": 10, "QC": 11, "KC": 12, "AD": 13, "2D": 14, "3D": 15, "4D": 16, "5D": 17, "6D": 18, "7D": 19, "8D": 20, "9D": 21, "10D": 22, "JD":23, "QD": 24, "KD": 25, "AH": 26, "2H": 27, "3H": 28, "4H": 29, "5H": 30, "6H": 31, "7H": 32, "8H": 33, "9H": 34, "10H": 35, "JH": 36, "QH": 37, "KH": 38, "AS": 39, "2S": 40, "3S": 41, "4S": 42, "5S": 43, "6S": 44, "7S": 45, "8S": 46, "9S": 47, "10S": 48, "JS": 49, "QS": 50, "KS": 51}

object_categories = list(class_map.keys())

def read_s3_contents_with_download(bucket_name, key):
    '''Download the s3 event object from s3 to an in-memory stream
    so you don't have to write to disk on lambda'''
    bytes_io = io.BytesIO()
    s3.Object(bucket_name, key).download_fileobj(bytes_io)
    return bytes_io


def visualize_detection(img, dets, dest_key, player_dealer, classes=[], thresh=0.1, bucket_name='remars2019-revegas-imageslanding'):
        '''
        visualize detections in one image, store it in s3,
        and send a message to IoT to display the image in a browser
        Parameters:
        ----------
        img : numpy.array
            image, in bgr format
        dets : numpy.array
            ssd detections, numpy.array([[id, score, x1, y1, x2, y2]...])
            each row is one object
        dest_key : string
            what object key to use to store the visualization image in S3
        player_dealer : string
            which region does the image belong to: 'pl1', 'dlr'
        height : int
            height of the bounding box, used to convert sagemaker's normalized coordinates
        width : int
            width of the bounding box, used to covnert sagemaker's normalized
            coordinates
        classes : tuple or list of str
            class names
        thresh : float
            score threshold
        bucket_name : string
            where to upload the resulting inference visualizations
        '''
        f = io.BytesIO()
        plt.clf()
        # img=mpimg.imread(img_file, 'jpg')
        plt.imshow(img)
        # height = img.shape[0]
        # width = img.shape[1]
        colors = dict()
        for det in dets:
            (klass, score, x0, y0, x1, y1) = det
            if score < thresh:
                continue
            cls_id = int(klass)
            if cls_id not in colors:
                colors[cls_id] = (random.random(), random.random(), random.random())
            xmin = int(x0)
            ymin = int(y0)
            xmax = int(x1)
            ymax = int(y1)
            rect = plt.Rectangle((xmin, ymin), xmax - xmin,
                                 ymax - ymin, fill=False,
                                 edgecolor=colors[cls_id],
                                 linewidth=3.5)
            plt.gca().add_patch(rect)
            class_name = str(cls_id)
            if classes and len(classes) > cls_id:
                class_name = classes[cls_id]
            plt.gca().text(xmin, ymin - 2,
                            '{:s} {:.3f}'.format(class_name, score),
                            bbox=dict(facecolor=colors[cls_id], alpha=0.5),
                                    fontsize=12, color='white')
        ax = plt.gca()
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        fig1 = plt.gcf()
        fig1.set_size_inches(4, 4)
        fig1.savefig(f, format='png', bbox_inches='tight',transparent=True, pad_inches=0, dpi=100)
        f.seek(0)

        s3_client.upload_fileobj(f, bucket_name, dest_key, {'ContentType': 'image/png'})
        # send IoT Message
        iot_data.publish(
            topic='newimages' + player_dealer,
            payload=json.dumps({
                's3Key': dest_key
            }))


def get_key(val): 
    '''utility to traverse class_map'''
    for key, value in class_map.items(): 
         if val == value: 
             return key 
  
    return "key doesn't exist"


def format_predictions(dets, player_dealer, thresh=0.1):
    '''takes predictions, formats them to be sent to Kinesis Data Stream'''
    data = {'playerDealer': player_dealer,'preds': []}
    for det in dets:
        (klass, score, x0, y0, x1, y1) = det
        if score < thresh:
            continue
        data['preds'].append({'cls': get_key(klass),
            'score': score,
            'xmin-ymin': [int(x0),int(y0)], # top left
            'xmax-ymax': [int(x1),int(y1)]})
    record = {
        'Data': json.dumps(data),
        'PartitionKey': str(hash(player_dealer))
    }
    return record

def read_background():
    '''Download the s3 event object from s3 to an in-memory stream
    so you don't have to write to disk on lambda'''
    bytes_io = io.BytesIO()
    s3.Object('remars2019-revegas-statichosting', 'tablebackground.jpg').download_fileobj(bytes_io)
    return bytes_io


def handler(event, context):
    global bucket_name

    # retreive a sagemaker endpoint from lambda env variable
    endpoint = str(os.environ['smendpoint'])

    # read the s3 key from the s3 event lambda trigger
    source_key = event['Records'][0]['s3']['object']['key']
    print(source_key)

    real_time_pred = mxnet.model.MXNetPredictor(
        endpoint_name=endpoint,
        sagemaker_session=sess
    )

    
    # pil_img = Image.open(img)
    # pil_img_size = pil_img.size
    # pil_img = pil_img.resize((512,512), Image.BILINEAR)

    # background_bytes = read_background()
    # new_img = Image.open(background_bytes)
    # # new_img_size = new_img.size
    # # new_img.paste(pil_img, (150,20))
    # new_img.paste(pil_img)
    # new_img_bytes = io.BytesIO()
    # pil_img.save(new_img_bytes, 'jpeg')





    # new_bytes = io.BytesIO()
    # im = Image.open(img)
    # # im = im.rotate(-45)
    # enhancer = ImageEnhance.Brightness(im)
    # # im = enhancer.enhance(0.9)
    # im = im.resize((512,512), Image.BILINEAR)
    # im.save(new_bytes, "JPEG")
    # dets = json.loads(real_time_pred.predict(new_bytes.getvalue()))
    dets = real_time_pred.predict({'s3Uri': 's3://{}/{}'.format(bucket_name, source_key)})

    dest_key_base = os.path.basename(source_key)
    dest_key_no_ext = os.path.splitext(dest_key_base)[0]
    # get playerid from sourcekey in prod
    player_dealer = dest_key_no_ext[-3:]
    dest_key = 'dest/' + dest_key_no_ext + '.png'


    
    # debugging, can comment this out
    print("Raw predictions for {}".format(source_key))
    print(dets['prediction'])
    record = format_predictions(dets['prediction'], thresh=0.2, player_dealer=player_dealer)
    # debugging, can comment this out in prod
    print(json.dumps(record))
    kinesis.put_record(
        StreamName='remars-revegas-dedup-stream',
        Data=record['Data'],
        PartitionKey=record['PartitionKey']
    )

    img = read_s3_contents_with_download(bucket_name, source_key)

    pil_img = Image.open(img)
    pil_img = pil_img.resize((416,416), Image.BILINEAR)
    new_img_bytes = io.BytesIO()
    pil_img.save(new_img_bytes, 'JPEG')
    img_file=mpimg.imread(new_img_bytes, 'jpg')
    visualize_detection(img=img_file, player_dealer=player_dealer, dets=dets['prediction'], dest_key=dest_key, classes=object_categories, thresh=0.2)
    return