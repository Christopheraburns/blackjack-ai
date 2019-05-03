import boto3
import json
from base64 import b64decode
from dynamodb_json import json_util
import numpy as np
from decimal import Decimal

iot_data = boto3.client('iot-data')

dedup_table_name='dedup-table'
counts_table_name='counts-table'
region = 'us-east-1'

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
dedup_table = dynamodb_resource.Table(dedup_table_name)
counts_table = dynamodb_resource.Table(counts_table_name)


def decode_kinesis(records):
    kinesis_json=[]
    for record in records:
        line = json.loads(b64decode(record['kinesis']['data']))
        kinesis_json.append(line)
    return kinesis_json


def deduped_records(new_preds):
    pl_existing_cards_list = []
    new_preds_deduped_list = []
    for new_pred in new_preds:
        pl_existing_cards = json_util.loads(
            dedup_table.get_item(
                Key={'tablename': 'dayone','playerDealer': new_pred['playerDealer']}
            )['Item']
        )
        print("Dynamo response")
        print(pl_existing_cards)
        if 'preds' in pl_existing_cards:
            new_preds_deduped=[]
            old_preds = pl_existing_cards['preds']
            for pred in new_pred['preds']:
                for old_pred in old_preds:
                    new_top_left = np.array((pred['xmin-ymin'][0], pred['xmin-ymin'][1]))
                    old_top_left = np.array((old_pred['xmin-ymin'][0], old_pred['xmin-ymin'][1]))
                    top_left_distance = np.linalg.norm(new_top_left-old_top_left)

                    new_bottom_right = np.array((pred['xmax-ymax'][0], pred['xmax-ymax'][1]))
                    old_bottom_right = np.array((old_pred['xmax-ymax'][0], old_pred['xmax-ymax'][1]))
                    bottom_right_distance = np.linalg.norm(new_bottom_right-old_bottom_right)
                    if top_left_distance < 20 and bottom_right_distance < 20:
                        print("card too similar")
                        print("New preds deduped before:")
                        print(new_preds_deduped)

                        while pred in new_preds_deduped:
                            new_preds_deduped.remove(pred)

                        print("New preds deduped after:")
                        print(new_preds_deduped)
                        break
                    new_preds_deduped.append(pred)
            pl_existing_cards['preds'].extend(new_preds_deduped)
        else:
            pl_existing_cards['preds'] = new_pred['preds']
            new_preds_deduped=new_pred['preds']
        pl_existing_cards_list.append(pl_existing_cards)
        new_preds_deduped_list.extend(new_preds_deduped)
    return pl_existing_cards_list, new_preds_deduped_list


def remove_second_ranksuit(new_preds):
    classes = {
            'A': 0,
            '2': 0,
            '3': 0,
            '4': 0,
            '5': 0,
            '6': 0,
            '7': 0,
            '8': 0,
            '9': 0,
            '10': 0,
            'J': 0,
            'Q': 0,
            'K': 0,
            'shoe': 0
    }
    for preds in new_preds:
        classes[preds['cls'][:-1]] = classes[preds['cls'][:-1]] + 1
        classes['shoe'] = classes['shoe'] + 1
    for k, v in classes.items():
        classes[k] = int(v * 0.5)
    return classes

def handler(event, context):
    
    kinesis_records=event['Records']
    # list of objects
    new_preds = decode_kinesis(kinesis_records)
    print("New preds before dedup:")
    print(new_preds)

    deduped_records_dict, new_preds_deduped = deduped_records(new_preds=new_preds)
    print("Deduped preds:")
    print(deduped_records_dict)
    print(new_preds_deduped)

    for item in deduped_records_dict:
        deduped_records_dump = json.dumps(item)
        deduped_records_dec = json.loads(deduped_records_dump, parse_float=Decimal)
        dedup_table.put_item(Item=deduped_records_dec)
    
    klasses = remove_second_ranksuit(new_preds_deduped)
    print("Dedup-ed classes from the stream:")
    print(klasses)
    '''
    klasses = {
        'A':16,
        'K':16,
        ...
        '2':16
    }
    '''

    counts = counts_table.get_item(Key={'tablename': 'dayone'})['Item']
    print("Counts read from DDB:")
    print(counts)
    '''
    counts = {
        'tablename': 'dayone',
        'counts': {
            'A':16,
            'K':16,
            ...
            '2':16
        }
    }
    '''

    for k,v in klasses.items():
        counts['counts'][k] = counts['counts'][k] - v
    print("Counts after subtracting:")
    print(counts)
    counts_dec = json_util.loads(counts)
    counts_table.put_item(Item=counts_dec)

    iot_data.publish(
        topic='counts',
        payload=json.dumps(json_util.loads(counts['counts'])))
    
    return