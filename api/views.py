from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings
from api.servicies import *
from django.contrib.sites.shortcuts import get_current_site
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
# def authenticate(request):
#     if request.method == 'POST':
#         try:
#             username = request.POST['username']
#             password = request.POST['password']

#             AuthenticateAccount.call(username, password)

#             return HttpResponse('User authenticated successfully', content_type='text/plain')

#         except AuthenticateAccount.AuthenticationError:
#             print("ERROR AUTHENTICATING USER")
#             return HttpResponseServerError()
#         except Exception as e:
#             print("UNKNOWN SERVER ERROR", e)
#             return HttpResponseServerError()


# api/coughs
def coughs(request):
    current_site = get_current_site(request)
    hostname = current_site.domain # get hostname

    coughs_dir = os.path.join(settings.MEDIA_ROOT, "audios/coughs") # get coughs directory

    file_list = [file for file in os.listdir(coughs_dir) if os.path.isfile(os.path.join(coughs_dir, file))] # get all files in coughs_dir
    link_list = [f'<a href="http://{hostname}/audios/coughs/{file}">{file}</a>' for file in file_list] # create links for each file

    response_content = '\n'.join(file_list) # serialize links into a string

    return HttpResponse(response_content, content_type='text/plain')

# api/coughs
@csrf_exempt
def cough(request):
    try:
        if request.method == 'POST':
            file = request.FILES['file']
            UploadCoughFile().call(file)

            return HttpResponse('Cough file uploaded successfully', content_type='text/plain')

    except UploadCoughFile().UploadFileError:
        print("ERROR UPLOADING COUGH FILE")
        return HttpResponseServerError()
    except Exception as e:
        print("UNKNOWN SERVER ERROR", e)
        return HttpResponseServerError()
    print("Uploading cough file")
    response = HttpResponse('Uploading cough file', content_type='text/plain')
    return response

