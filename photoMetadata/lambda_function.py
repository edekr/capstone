import json
import urllib.parse
import uuid
import boto3
from exif import Image
import requests

print('Loading function')
weather_table_name = "weather"
s3 = boto3.client('s3')
weather_api_base_url = 'https://api.brightsky.dev/weather?'
dynamodb_resource = boto3.resource("dynamodb")
weather_table = dynamodb_resource.Table(weather_table_name)

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def image_coordinates(image_path):
    with open(image_path, 'rb') as src:
        img = Image(src)
    if img.has_exif:
        try:
            img.gps_longitude
            coords = (decimal_coords(img.gps_latitude,
                      img.gps_latitude_ref),
                      decimal_coords(img.gps_longitude,
                      img.gps_longitude_ref))
        except AttributeError:
            print ('No Coordinates')
    else:
        print ('The Image has no EXIF information')
    #print(f"Image {src.name}, OS Version:{img.get('software', 'Not Known')} ------")
    #print(f"dateTime: {img.datetime_original}, coordinates:{coords}")
    return img.datetime_original, coords

def load_weather_data(date, lat, long):
    date_format = date.split()[0].replace(':','-')
    timeHour_format = date.split()[1].split(":")[0]
    params = {'lat': lat, 'lon': long, 'date': date_format}
    #print(weather_api_base_url + urllib.parse.urlencode(params))
    url = (weather_api_base_url + urllib.parse.urlencode(params))

    #print("start loading weather data")
    response = requests.get(url)
    hour_weather = response.json()['weather'][int(timeHour_format)]
    station = response.json()['sources'][0]['station_name']
    return hour_weather, station

def lambda_handler(event, context):
    for record in event['Records']:
      bucket = record['s3']['bucket']['name']
      key = urllib.parse.unquote_plus(record['s3']['object']['key'])
      tmpkey = key.replace('/', '')
      download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
      #upload_path = '/tmp/resized-{}'.format(tmpkey)
      s3.download_file(bucket, key, download_path)
      image_details = image_coordinates(download_path)
      image_datetime = image_details[0]
      image_lat = image_details[1][0]
      image_long = image_details[1][1]
      image_weather = load_weather_data(image_datetime, image_lat, image_long)
      image_weather_details = image_weather[0]
      image_weather_station = image_weather[1]
      print('Image DateTime: {}'.format(image_datetime))
      print('Image Temp: {}'.format(image_weather_details['temperature']))
      print('Image Icon: {}'.format(image_weather_details['icon']))
      print('Weather Station: {}'.format(image_weather_station))
      weather_table.put_item(Item={"id":key,
        "temperature":str(image_weather_details['temperature']),
        "Icon":str(image_weather_details['icon']),
        "Weather Station":str(image_weather_station)        
        })

      #s3_client.upload_file(upload_path, '{}-resized'.format(bucket), key)