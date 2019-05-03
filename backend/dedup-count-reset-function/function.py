import json
import boto3
import logging
import os

dedup_table_name='dedup-table'
counts_table_name='counts-table'
region = 'us-east-1'

dynamodb_resource = boto3.resource('dynamodb', region_name=region)
dedup_table = dynamodb_resource.Table(dedup_table_name)
counts_table = dynamodb_resource.Table(counts_table_name)


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
            "A": 4 * deck_count,
            "2": 4 * deck_count,
            "3": 4 * deck_count,
            "4": 4 * deck_count,
            "5": 4 * deck_count,
            "6": 4 * deck_count,
            "7": 4 * deck_count,
            "8": 4 * deck_count,
            "9": 4 * deck_count,
            "10": 4 * deck_count,
            "J": 4 * deck_count,
            "Q": 4 * deck_count,
            "K": 4 * deck_count,
            "shoe": 52 * deck_count
        },
        "tablename": "dayone"
    }
    
    body_json = json.loads(event['body'])
    if body_json['arg'] == 'shuffle':
        # reset the dynamodb table with shoe_reset_list_of_dicts
        counts_table.put_item(Item=counts_default)
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
        for item in dedup_default:
            dedup_table.put_item(Item=item)
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