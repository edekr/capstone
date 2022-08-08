import json
import urllib.parse
import boto3
import requests
from datetime import date, datetime
import os
import time

print('Loading function')

s3 = boto3.client('s3')
#weather_table_name = os.environ["WEATHER_DATA"]


#dynamodb_resource = boto3.resource("dynamodb")
#weather_table = dynamodb_resource.Table(weather_table_name)
weather_api_base_url = 'https://api.brightsky.dev/weather?'

def lambda_handler(event):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    evTime = urllib.parse.unquote_plus(event['Records'][0]['eventTime'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        print(key)
        print(evTime)
        #weather_data = load_weather_data(evTime)
        #print(weather_data)
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

now = datetime.now()



def handle(event, context):
    weather_api_data = load_weather_data()
    mapped_data = map_weather_data(weather_api_data)
    save_weather_data(mapped_data)

if __name__ == "__main__":
    lambda_handler({})