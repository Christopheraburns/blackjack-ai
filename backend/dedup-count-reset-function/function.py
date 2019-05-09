import json
import boto3
import logging
import os

dedup_table_name='dedup-table'
counts_table_name='counts-table'
dealer_hand_table='dealer-hand'
region = 'us-east-1'

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
dedup_table = dynamodb_resource.Table(dedup_table_name)
counts_table = dynamodb_resource.Table(counts_table_name)
dealer_table = dynamodb_resource.Table(dealer_hand_table)


'''
1. Invoked via AWS Amplify JS REST Lambda Invocation POST (tdb)

2. Read an arg (new hand / deck shuffle)

3. Clear the Dynamodb dedup table for new hand,
   clear the Dynamodb counts table for deck shuffle

'''

def lambda_handler(event, context):
    print(json.loads(event['body']))
    # put this in handler in case of container reuse and we need to update the
    # env variable
    deck_count = int(os.environ['num_decks'])
    
    dedup_default = [
        {
            'tablename': 'dayone',
            'playerDealer': 'pl1'
        },
        {
            'tablename': 'dayone',
            'playerDealer': 'pl2'
        },
        {
            'tablename': 'dayone',
            'playerDealer': 'pl3'
        },
        {
            'tablename': 'dayone',
            'playerDealer': 'pl4'
        },
        {
            'tablename': 'dayone',
            'playerDealer': 'pl5'
        },
        {
            'tablename': 'dayone',
            'playerDealer': 'dlr'
        }
    ]

    counts_default = {
        "counts": {
            "01-A": 4 * deck_count,
            "02-K": 4 * deck_count,
            "03-Q": 4 * deck_count,
            "04-J": 4 * deck_count,
            "05-10": 4 * deck_count,
            "06-9": 4 * deck_count,
            "07-8": 4 * deck_count,
            "08-7": 4 * deck_count,
            "09-6": 4 * deck_count,
            "10-5": 4 * deck_count,
            "11-4": 4 * deck_count,
            "12-3": 4 * deck_count,
            "13-2": 4 * deck_count,
            "14-shoe": 52 * deck_count
        },
        "tablename": "dayone"
    }
    
    dealer_default = {
        'dlr': 'dlr'
    }

    body_json = json.loads(event['body'])
    if body_json['arg'] == 'shuffle':
        # in the case of shuffle, reset the count, and clear the dudup
        # table for a new hand
        counts_table.put_item(Item=counts_default)
        dealer_table.put_item(Item=dealer_default)
        for item in dedup_default:
            dedup_table.put_item(Item=item)
        return {
            'statusCode': 200,
            'body': json.dumps('Counts are reset!'),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Credentials' : True
            }
        }
                
    elif body_json['arg'] == 'new_round':
        # in the case of new round, just reset the dedup table,
        # don't reset the shoe counts
        for item in dedup_default:
            dedup_table.put_item(Item=item)
        dealer_table.put_item(Item=dealer_default)
        return {
            'statusCode': 200,
            'body': json.dumps('Dedup table is reset!'),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Credentials' : True
            }
        }
                
    else:
        print('unrecognized arg')
        return {
            'statusCode': 200,
            'body': json.dumps('Unrecognized arg!'),
            'headers': {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Credentials' : True
            }
        }