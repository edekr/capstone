mkdir ../infrastructure/build

cd fetch_image_data_lambda
pip install exif
pip install -r requirements.txt -t python/lib/python3.9/site-packages
zip -r ../../infrastructure/build/fetch_image_data_lambda.zip .
