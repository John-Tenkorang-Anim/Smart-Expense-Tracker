import boto3
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_BUCKET_NAME, AWS_REGION

def upload_to_s3(file_path, file_name):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )
    
    try:
        s3.upload_file(file_path, AWS_BUCKET_NAME, file_name)
        return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None
