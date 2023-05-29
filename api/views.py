from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings
import markdown
from django.contrib.sites.shortcuts import get_current_site
import os


# Create your views here.
def root(request):
    file_path = os.path.join(settings.STATIC_DIR, 'root.txt')

    with open(file_path, 'r') as f:
        file_content = f.read()

    return HttpResponse(file_content, content_type='text/plain')

def coughs(request):
    current_site = get_current_site(request)
    hostname = current_site.domain # get hostname

    coughs_dir = os.path.join(settings.MEDIA_ROOT, "audios/coughs") # get coughs directory

    file_list = [file for file in os.listdir(coughs_dir) if os.path.isfile(os.path.join(coughs_dir, file))] # get all files in coughs_dir
    link_list = [f'<a href="http://{hostname}/audios/coughs/{file}">{file}</a>' for file in file_list] # create links for each file

    response_content = '\n'.join(file_list) # serialize links into a string

    return HttpResponse(response_content, content_type='text/plain')
