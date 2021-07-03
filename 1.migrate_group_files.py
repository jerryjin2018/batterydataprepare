import boto3
import re
import botocore
from botocore.exceptions import ClientError

# Notice
# Should configure your environment correctly, such as AWS AKSK or Role.

def main():
# "bucket_name" should be your bucket name
    bucket_name = "*****2020temp"

    try:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)

        for obj in bucket.objects.filter(Delimiter='/'):
            try:
                items = re.split('_+', obj.key)
                s3.Object(bucket_name, items[0]).load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    # The folder does not exist.
                    print("folder s://", bucket_name, "/", items[0], "is not existed.")

                    folder_name = items[0]
                    # Create a folder within this bucket, then move the object into this folder
                    # Copy object A as object B
                    s3.Object(bucket_name, folder_name+'/'+obj.key).copy_from(CopySource = bucket_name+'/'+obj.key)
                    # Delete the former object A
                    s3.Object(bucket_name, obj.key).delete()
                else:
                    # Something else has gone wrong.
                    raise
            else:
                # The folder exists.
                print("folder s://", bucket_name, "/", items[0], "is existed.")
                folder_name = items[0]

                # move the object into this folder directly
                s3.Object(bucket_name, folder_name+'/'+obj.key).copy_from(CopySource = bucket_name+'/'+obj.key)
                s3.Object(bucket_name, obj.key).delete()

    except ClientError as e:
        print(e)

if __name__ == '__main__':
    main()   
