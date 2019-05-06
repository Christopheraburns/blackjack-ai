import boto3
import json
from base64 import b64decode
from dynamodb_json import json_util
import numpy as np
from decimal import *
from collections import OrderedDict

iot_data = boto3.client('iot-data')

dedup_table_name='dedup-table'
counts_table_name='counts-table'
region = 'us-east-1'

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
dedup_table = dynamodb_resource.Table(dedup_table_name)
counts_table = dynamodb_resource.Table(counts_table_name)


def decode_kinesis(records):
    '''convert b64 encoded kinesis data records to list of json objects'''
    kinesis_json=[]
    for record in records:
        line = json.loads(b64decode(record['kinesis']['data']))
        kinesis_json.append(line)
    return kinesis_json

def get_hands(deduped_records_dict):
    hands = {}
    for x in deduped_records_dict:
        player_dealer = x['playerDealer']
        hands[player_dealer] = []
        '''
        {
            'pl4': ['2','2','K'],

        }
        '''
        for pred in x['preds']:
            cards = pred['cls']
            hands[player_dealer].append(cards)
        remove_duplicates = list(dict.fromkeys(hands[player_dealer]))
        hands[player_dealer] = remove_duplicates
    return hands



def deduped_records(new_preds):
    '''where the magic happens'''
    pl_existing_cards_list = []
    new_preds_deduped_list = []
    for new_pred in new_preds:
        # read ddb for existing preds in this player/dealer region
        pl_existing_cards = json_util.loads(
            dedup_table.get_item(
                Key={'tablename': 'dayone','playerDealer': new_pred['playerDealer']}
            )['Item']
        )
        # debugging, comment out later
        print("Dynamo response")
        print(pl_existing_cards)
        if 'preds' in pl_existing_cards:
            # if we already saw predictions for a player/dealer region
            new_preds_deduped=[]
            old_preds = pl_existing_cards['preds']
            for pred in new_pred['preds']:
                for old_pred in old_preds:
                    # for a detection, calculate its bounding box euclidean distance from the previous detected bboxes within the player/dealer region
                    new_top_left = np.array((pred['xmin-ymin'][0], pred['xmin-ymin'][1]))
                    old_top_left = np.array((old_pred['xmin-ymin'][0], old_pred['xmin-ymin'][1]))
                    top_left_distance = np.linalg.norm(new_top_left-old_top_left)

                    new_bottom_right = np.array((pred['xmax-ymax'][0], pred['xmax-ymax'][1]))
                    old_bottom_right = np.array((old_pred['xmax-ymax'][0], old_pred['xmax-ymax'][1]))
                    bottom_right_distance = np.linalg.norm(new_bottom_right-old_bottom_right)
                    # ASSUMPTION! May need to modify these distances and include a condition on matching suit/rank
                    if top_left_distance < 20 and bottom_right_distance < 20:
                        # if the distance is pretty short, discard the prediction. print statements below for debugging
                        print("card too similar")
                        print("New preds deduped before:")
                        print(new_preds_deduped)

                        # all we need to do is "match" a detection with an old detection once. if we do, we should discard it.
                        while pred in new_preds_deduped:
                            new_preds_deduped.remove(pred)

                        print("New preds deduped after:")
                        print(new_preds_deduped)
                        # never run this loop again for the new detection since it "matched" a card in the given player/dealer region. start the loop for a new detection:
                        break
                    new_preds_deduped.append(pred)
            pl_existing_cards['preds'].extend(new_preds_deduped)
        else:
            # if the dedup table is cleared via the browser button, that means there were no cards on the table and this is a brand new hand, so we skip the dedup logic:
            pl_existing_cards['preds'] = new_pred['preds']
            new_preds_deduped=new_pred['preds']
        pl_existing_cards_list.append(pl_existing_cards)
        new_preds_deduped_list.extend(new_preds_deduped)
    return pl_existing_cards_list, new_preds_deduped_list


def remove_second_ranksuit(new_preds_deduped):
    '''We store the count of ranks and count of cards from the deduped detections
    and then divide in half. 

    ASSUMPTION 1: dealer must place cards
    with both values on a card uncovered. otherwise, this will
    completely break. 

    ASSUMPTION 2: this also assumes our ML Model 
    accurately detects both values on a card.'''
    classes = {
            "01-A": 0,
            "02-K": 0,
            "03-Q": 0,
            "04-J": 0,
            "05-10": 0,
            "06-9": 0,
            "07-8": 0,
            "08-7": 0,
            "09-6": 0,
            "10-5": 0,
            "11-4": 0,
            "12-3": 0,
            "13-2": 0,
            "14-shoe": 0
    }
    for preds in new_preds_deduped:
        classes['14-shoe'] = classes['14-shoe'] + 1
        if preds['cls'][:-1] == 'A':
            classes['01-A'] = classes['01-A'] + 1
        elif preds['cls'][:-1] == 'K':
            classes['02-K'] = classes['02-K'] + 1
        elif preds['cls'][:-1] == 'Q':
            classes['03-Q'] = classes['03-Q'] + 1
        elif preds['cls'][:-1] == 'J':
            classes['04-J'] = classes['04-J'] + 1
        elif preds['cls'][:-1] == '10':
            classes['05-10'] = classes['05-10'] + 1
        elif preds['cls'][:-1] == '9':
            classes['06-9'] = classes['06-9'] + 1
        elif preds['cls'][:-1] == '8':
            classes['07-8'] = classes['07-8'] + 1
        elif preds['cls'][:-1] == '7':
            classes['08-7'] = classes['08-7'] + 1
        elif preds['cls'][:-1] == '6':
            classes['09-6'] = classes['09-6'] + 1
        elif preds['cls'][:-1] == '5':
            classes['10-5'] = classes['10-5'] + 1
        elif preds['cls'][:-1] == '4':
            classes['11-4'] = classes['11-4'] + 1
        elif preds['cls'][:-1] == '3':
            classes['12-3'] = classes['12-3'] + 1
        elif preds['cls'][:-1] == '2':
            classes['13-2'] = classes['13-2'] + 1
    for k, v in classes.items():
        classes[k] = int(v * 0.5)
    return classes

def handler(event, context):
    '''this lambda function is designed to run with a concurrency of 1 to prevent race conditions on the dynamodb table!!! therefore the unit of scale
    is per table since dedup is stored at the tablename level'''

    # read the kinesis record from the kinesis lambda trigger
    kinesis_records=event['Records']
    # list of objects
    new_preds = decode_kinesis(kinesis_records)
    # debugging
    print("New preds before dedup:")
    print(new_preds)

    deduped_records_dict, new_preds_deduped = deduped_records(new_preds=new_preds)
    print("Deduped preds:")
    print(deduped_records_dict)
    print(new_preds_deduped)

    hands = get_hands(deduped_records_dict)
    print("Player/Dealer Hands:")
    print(hands)

    for item in deduped_records_dict:
        deduped_records_dump = json.dumps(item)
        deduped_records_dec = json.loads(deduped_records_dump, parse_float=Decimal)
        # store deduped results to DynamoDB for next trigger
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
    print("Counts after using the json utils:")
    print(counts_dec)
    counts_table.put_item(Item=counts_dec)


    

    # generate probabilities:
    ordered_dict = OrderedDict(sorted(counts_dec['counts'].items(), key=lambda t: t[0]))
    counts_list = []
    probabilities = []
    cards_left_in_shoe = counts_dec['counts']['14-shoe']
    for k,v in ordered_dict.items():
        if k == '14-shoe':
            continue
        counts_list.append(v)
        probability = (v/cards_left_in_shoe) * 100
        probabilities.append(probability)
    print("Just a count list")
    print(counts_list)
    print("Just a probabilities list")
    print(probabilities)

    probabilities_clean = list(np.around(np.array(probabilities), 2))
    print("Just a probabilities list rounded")
    print(probabilities_clean)
    iot_data.publish(
        topic='probabilities',
        payload=json.dumps(probabilities_clean))
    iot_data.publish(
        topic='counts',
        payload=json.dumps(counts_list))
    
    return