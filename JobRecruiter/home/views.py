from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
def index(request):
    template_data = {}
    template_data['title'] = 'Job Recruiter'

    return render(request, 'home/index.html', {
        'template_data': template_data
    })

def info(request):
    template_data = {}
    template_data['title'] = 'Info'
    return render(request, 'home/info.html', {
        'template_data': template_data})