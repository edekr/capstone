mkdir ../infrastructure/build

cd fetch_image_data_lambda

pip install -r requirements.txt -t .
zip -r ../../infrastructure/build/fetch_image_data_lambda.zip .