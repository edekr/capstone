from copyreg import pickle
import json
import urllib.parse
import boto3
import requests
#from decimal import Decimal
#print('Loading function')



weather_api_base_url = 'https://api.brightsky.dev/weather?'
weather_table_name = "weather"
s3 = boto3.client('s3')
dynamodb_resource = boto3.resource("dynamodb")
weather_table = dynamodb_resource.Table(weather_table_name)

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    evTime = urllib.parse.unquote_plus(event['Records'][0]['eventTime'], encoding='utf-8')
   # response = s3.get_object(Bucket=bucket, Key=key)
    print(key)
    print(evTime)
    picweather = load_weather_data(evTime)
    print(picweather)
    weather_table.put_item(Item={"id":key,
     "temperature":str(picweather[0]["temperature"]),
     "sunshine":str(picweather[0]["sunshine"])})

def load_weather_data(date):
    params = {'lat': 53.55, 'lon': 9.99, 'date': date}
    print(weather_api_base_url + urllib.parse.urlencode(params))
    url = (weather_api_base_url + urllib.parse.urlencode(params))

    print("start loading weather data")
    response = requests.get(url)
    return response.json()["weather"]




if __name__ == "__main__":
    lambda_handler({
  "Records": [
    {
      "eventVersion": "2.0",
      "eventSource": "aws:s3",
      "awsRegion": "eu-central-1",
      "eventTime": "2022-01-01T00:00:00.000Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "EXAMPLE"
      },
      "requestParameters": {
        "sourceIPAddress": "127.0.0.1"
      },
      "responseElements": {
        "x-amz-request-id": "EXAMPLE123456789",
        "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "testConfigRule",
        "bucket": {
          "name": "myimageuploadbucket-1234567",
          "ownerIdentity": {
            "principalId": "EXAMPLE"
          },
          "arn": "arn:aws:s3:::example-bucket"
        },
        "object": {
          "key": "IMG_4138.JPG",
          "size": 1024,
          "eTag": "0123456789abcdef0123456789abcdef",
          "sequencer": "0A1B2C3D4E5F678901"
        }
      }
    }
  ]
},{})