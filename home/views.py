import os
from datetime import timezone

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login

from django.shortcuts import render, redirect
from .models import UserDetails
from django.contrib.auth.hashers import make_password

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if username or email already exists
        if UserDetails.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})

        if UserDetails.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already exists'})

        if request.POST['Password'] != request.POST['RepeatPassword']:
            return render(request, 'register.html', {'error': 'Passwords do not match'})

        # Proceed with user creation
        user = UserDetails(
            username=request.POST['Username'],
            first_name=request.POST['Firstname'],
            last_name=request.POST['Lastname'],
            email=request.POST['Email'],
            password=make_password(request.POST['Password']),
            is_active=True,
            is_staff=False,
            is_superuser=False,
            last_login=None,
            date_joined=timezone.now()
        )
        user.save()

        return redirect('login')  # Redirect to login after successful registration

    return render(request, 'register.html')


def home(request):
    return render(request, 'home/welcome.html')


def login(request):
    return render(request, 'login.html')


def register(request):
    return render(request, 'register.html')


def cards(request):
    return render(request, 'cards.html')


def charts(request):
    return render(request, 'charts.html')

def favicon(request):
    return render(request, '/static/img/favicon.ico')

def resetpwd(request):
    return render(request, 'forgot-password.html')


def tables(request):
    return render(request, 'tables.html')


# views.py

from django.shortcuts import render
import pandas as pd


def upload_data(request):
    if request.method == 'POST':
        datafile = request.FILES.get('datafile')
        if datafile:
            df = pd.read_csv(datafile)
            # Convert the DataFrame to HTML table
            data_html = df.to_html(classes='table table-bordered', index=False)
            context = {'data_table': data_html}
            return render(request, 'tables.html', context)
    return render(request, 'tables.html')

def serve_audio(request, filename):
    file_path = os.path.join('/path/to/audio/', filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="audio/mpeg")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404