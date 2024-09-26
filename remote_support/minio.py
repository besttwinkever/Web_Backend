from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import *

def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object('images', image_name, file_object, file_object.size)
        return f"http://localhost:9000/images/{image_name}"
    except Exception as e:
        return {"error": str(e)}

def add_pic(issue, pic):
    client = Minio(           
            endpoint=settings.AWS_S3_ENDPOINT_URL,
           access_key=settings.AWS_ACCESS_KEY_ID,
           secret_key=settings.AWS_SECRET_ACCESS_KEY,
           secure=settings.MINIO_USE_SSL
    )
    i = issue.id
    img_obj_name = f"{i}.jpg"

    if pic == None:
        return Response({"error": "Нет файла для изображения."})
    result = process_file_upload(pic, client, img_obj_name)

    if 'error' in result:
        return Response(result)

    issue.image = result
    issue.save()

    return Response({"message": "success"})

def delete_pic(issue):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    i = issue.id
    img_obj_name = f"{i}.jpg"

    client.remove_object('images', img_obj_name)
    issue.image = "http://localhost:9000/images/default.jpg"
    issue.save()

    return Response({"message": "success"})