from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.views import APIView
from rest_framework.response import Response

from api.servicies import *
from api import serializers as api_serializers

import os

# Create your views here.
# api/
def root(request):
    try:
        file_path = os.path.join(settings.STATIC_DIR, 'root.txt')

        with open(file_path, 'r') as f:
            file_content = f.read()
        return HttpResponse(file_content, content_type='text/plain')

    except Exception as e:
        print("UNKNOWN SERVER ERROR", e)
        return HttpResponseServerError()

# api/auth/authenticate



class Coughs(APIView):
    def get(self, request):
        current_site = get_current_site(request)
        hostname = current_site.domain # get hostname

        coughs_dir = os.path.join(settings.MEDIA_ROOT, "audios/coughs") # get coughs directory

        file_list = [file for file in os.listdir(coughs_dir) if os.path.isfile(os.path.join(coughs_dir, file))] # get all files in coughs_dir
        link_list = [f'http://{hostname}/audios/coughs/{file}' for file in file_list] # create links for each file
        coughlist = [{'name': file, 'link': link} for file, link in zip(file_list, link_list)] # create a list of dictionaries with name and link for each file

        serializer = api_serializers.CoughListSerializer(data=coughlist, many=True) # type: ignore # serialize coughlist
        if not serializer.is_valid():
            raise Exception("Invalid data")

        response_data = serializer.validated_data


        return Response(response_data)

class Cough(APIView):
    def post(self, request):
        try:
            serializer = api_serializers.AudioSerializer(data=request.data)

            if not serializer.is_valid():
                raise Exception("Invalid data")

            file = serializer.save()
            UploadCoughFile().call(file)

            return HttpResponse('Cough file uploaded successfully', content_type='text/plain')

        except UploadCoughFile().UploadFileError:
            return HttpResponseServerError()
        except Exception as e:
            print("UNKNOWN SERVER ERROR", e)
            return HttpResponseServerError()

class MusicGenerate(APIView):
    def put(self, request):
        try:
            GenerateMusic().call()

            return HttpResponse('Music generated successfully', content_type='text/plain')

        except GenerateMusic().GenerateMusicError:
            return HttpResponseServerError()
        except Exception as e:
            print("UNKNOWN SERVER ERROR", e)
            return HttpResponseServerError()

class Musics(APIView):
    def get(self, request):
        current_site = get_current_site(request)
        hostname = current_site.domain # get hostname

        musics_dir = os.path.join(settings.MEDIA_ROOT, "audios") # get musics directory

        file_list = [file for file in os.listdir(musics_dir) if os.path.isfile(os.path.join(musics_dir, file))] # get all files in musics_dir
        link_list = [f'http://{hostname}/audios/{file}' for file in file_list] # create links for each file
        musiclist = [{'name': file, 'link': link} for file, link in zip(file_list, link_list)] # create a list of dictionaries with name and link for each file

        serializer = api_serializers.MusicListSerializer(data=musiclist, many=True) # type: ignore # serialize musiclist
        if not serializer.is_valid():
            raise Exception("Invalid data")

        response_data = serializer.validated_data


        return Response(response_data)
