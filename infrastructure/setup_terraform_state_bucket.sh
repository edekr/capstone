TERRAFORM_S3_BUCKET_NAME=myterraformstatebucket-1234567
if aws s3 ls "s3://$TERRAFORM_S3_BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'
then
    aws s3api create-bucket --bucket $TERRAFORM_S3_BUCKET_NAME --region eu-central-1 --create-bucket-configuration LocationConstraint=eu-central-1
else
    echo "terraform bucket already exist"
fi