resource "aws_lambda_function" "fetch_image_data_lambda" {

  filename      = "build/fetch_image_data_lambda.zip"
  function_name = "fetch_image_data_lambda"
  role          = "arn:aws:iam::018572766339:role/LabRole"
  handler       = "lambda_function.lambda_handler"


  source_code_hash = filebase64sha256("build/fetch_image_data_lambda.zip")

  runtime = "python3.9"
  timeout = 600
  #layers = [ aws_lambda_layer_version.requests_layer.arn ]

#   environment {
#     variables = {
#       WEATHER_TABLE_NAME = var.weather_table_name
#     }
#   }
}