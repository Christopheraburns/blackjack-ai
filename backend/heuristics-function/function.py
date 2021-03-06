import boto3
import json
from base64 import b64decode
from dynamodb_json import json_util
import numpy as np
from decimal import *
from collections import OrderedDict
from time import sleep

iot_data = boto3.client('iot-data')
lambda_client = boto3.client('lambda')

dealer_hand_table='dealer-hand'
counts_table_name='counts-table'
region = 'us-east-1'
dynamodb_resource = boto3.resource('dynamodb', region_name=region)

dealer_table = dynamodb_resource.Table(dealer_hand_table)
counts_table = dynamodb_resource.Table(counts_table_name)

# use this map to convert the hand ranks (sent as strings) to generate a sum worth for a hand
rank_map = {
    'A' : 11, # rank_map['A'][0] soft ace or rank_map['A'][1] hard depending on the values of the rest of the hand
    'K': 10,
    'Q': 10,
    'J': 10,
    '10': 10,
    '9': 9,
    '8': 8,
    '7': 7,
    '6': 6,
    '5': 5,
    '4': 4,
    '3': 3,
    '2': 2
}

def sum_dealer_hand_worth(hand):
    '''
    hand = object, {'A': 1, 'J': 1, '4': 1}
    '''
    worth = 0
    for k,v in hand.items():
        card_val = rank_map[k]
        worth = worth + int(card_val * v) # hand's worth pre-aces

    return worth
        
def sum_player_hand_worth(hand):
    '''
    hand = object, {'A': 1, 'J': 1, '4': 1}
    '''
    payload = {}
    worth = 0
    count_of_aces = 0
    for k,v in hand.items():
        if k == 'A':
            count_of_aces = v
            continue
        card_val = rank_map[k]
        worth = worth + int(card_val * v) # hand's worth pre-aces
    if count_of_aces > 0:
        if worth + count_of_aces + 10 <= 21:
            payload['ace'] = 1
            payload['psum'] = worth + count_of_aces + 10
            return payload
        else:
            payload['ace'] = 0
            payload['psum'] = worth + count_of_aces
            return payload
    else:
        payload = {'ace': 0,'psum': worth}
        return payload


def handler(event, context):
    # back off to wait for the dealer hand to be in dynamodb
    backoff_ms=1 # start at 1 ms
    while 'hand' not in dealer_table.get_item(Key={'dlr': 'dlr'}, ConsistentRead=True)['Item']:
        # backing off for a few milliseconds until the dealer hand shows up in the dynamo table
        print('Waiting for the dealer hand to arrive')
        print(backoff_ms)
        # stop the backoff_ms after 64 ms
        if backoff_ms > 64:
            backoff_ms = 64
        sleep(backoff_ms/1000)
        backoff_ms = backoff_ms*2
    # dealer hand arrived, read it in a variable
    print('The dealer hand arrived!')
    dealer_hand = json_util.loads(dealer_table.get_item(Key={'dlr': 'dlr'}, ConsistentRead=True)['Item'])
    # print('Dealers hand:')
    # print(dealer_hand)
    # print(event)
    player = list(event.keys())[0]
    player_hand = event[player]

    
    rl_payload = sum_player_hand_worth(player_hand)
    # TODO: Implement below!
    dealer_hand_numeric = sum_dealer_hand_worth(dealer_hand['hand'])
    rl_payload['dcard'] = dealer_hand_numeric


    # dealer_hand_worth = sum_dealer_hand_worth(dealer_hand['hand'])

    # sleep(1)
    # deck_counts = json_util.loads(counts_table.get_item(Key={'tablename': 'dayone'})['Item'])

    # bunch of print statements for logging
    print("Player hand I received in the payload:")
    print(player)
    print(player_hand)
    print("RL Payload:")
    print(rl_payload)
    print("Dealer hand from dynamo:")
    print(dealer_hand['hand'])
    # print("Dealer hand worth:")
    # print(dealer_hand_worth)
    # print("Deck counts:")
    # print(deck_counts)


    '''
    Do heuristics or RL here (set an env variable) or do both
    '''
    guidance = {
        'guidance': 'Stand'
    }
    if rl_payload['psum'] == 0 or rl_payload['dcard'] == 0:
        guidance['guidance'] = 'Feed me hands!'
    elif rl_payload['psum'] == 21:
        guidance['guidance'] = 'Twenty One!'
    elif rl_payload['psum'] > 21:
        guidance['guidance'] = 'Bust!'
    elif len(dealer_hand['hand'].keys()) > 1:
        return
    else:
        print("doing fancy heuristic/RL stuff now")
        response = lambda_client.invoke(
                FunctionName='rl-agent',
                InvocationType='RequestResponse',
                Payload=json.dumps(rl_payload)
            )
        body =  json.loads(response['Payload'].read().decode("utf-8").replace('\\', '').replace('\"\"', '\"'))
        guidance['guidance'] = body['body']


    # publish the guidance (hit or stand) to an IoT topic that corresponds to the player
    iot_data.publish(
        topic='guidance' + player,
        payload=json.dumps(guidance))