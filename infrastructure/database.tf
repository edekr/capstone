resource "aws_dynamodb_table" "weather_table_name" {
  name           = "weather"
  billing_mode   = "PROVISIONED"
  read_capacity  = 20
  write_capacity = 20
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }


}