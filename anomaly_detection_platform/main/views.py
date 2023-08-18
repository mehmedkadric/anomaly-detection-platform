import pickle
import random

import numpy as np
import pandas as pd
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.core.paginator import Paginator
from django.db.models import Count
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from .models import *


def index(request):
    score = 0
    if request.method == 'POST':
        form = PredictionDataForm(request.POST)
        if form.is_valid():
            # Process the form data and save it if needed
            # For example, you can access the data as follows:
            time_slot = form.cleaned_data['time']
            genre = form.cleaned_data['genre']
            price = form.cleaned_data['price']
            pages = form.cleaned_data['pages']

            data_dict = {
                "time": time_slot,
                "genre": genre,
                "price": int(price),
                "pages": pages,
            }

            fake_data = [data_dict]
            # Load the OneClassSVM model from the pickle file
            with open('/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/oneclasssvm_model.pkl', 'rb') as file:
                loaded_model = pickle.load(file)

            # Load the encoders from the pickle files
            with open('/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/time_encoder.pkl', 'rb') as file:
                time_encoder = pickle.load(file)

            with open('/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/genre_encoder.pkl', 'rb') as file:
                genre_encoder = pickle.load(file)

            # Apply the encoders to the 'X' data
            time_encoded = time_encoder.transform([[d['time']] for d in fake_data])
            genre_encoded = genre_encoder.transform([d['genre'] for d in fake_data])

            X = [[d['price'], d['pages']] + list(time_encoded[i]) + [genre_encoded[i]] for i, d in enumerate(fake_data)]

            score = loaded_model.predict(X)[0]
    else:
        form = PredictionDataForm()

    return render(request, 'home.html', {'form': form, "score": score})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            django_login(request, user)
            messages.info(request, f"You are now logged in as {username}")
            return redirect("main:index")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = UserRegistrationForm

    context = {
        "form": form,
    }

    return render(request, "register.html", context=context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                django_login(request, user)
                messages.info(request, f"Welcome {username}!")
                return redirect("main:index")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    if request.user.is_authenticated:
        messages.info(request, "Already logged in")
        return redirect("main:index")
    form = AuthenticationForm()

    context = {
        "form": form,
    }

    return render(request, "login.html", context=context)


def about_us(request):
    return render(request, 'about_us.html')


def logout(request):
    django_logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:index")


@login_required(login_url='/login')
def profile(request):
    return render(request=request, template_name="profile.html")


@login_required(login_url='/login')
def playground(request):
    score = 0
    if request.method == 'POST':
        form = PredictionDataForm(request.POST)
        if form.is_valid():
            # Process the form data and save it if needed
            # For example, you can access the data as follows:
            time_slot = form.cleaned_data['time']
            genre = form.cleaned_data['genre']
            price = form.cleaned_data['price']
            pages = form.cleaned_data['pages']

            data_dict = {
                "time": time_slot,
                "genre": genre,
                "price": int(price),
                "pages": pages,
            }

            fake_data = [data_dict]
            # Load the OneClassSVM model from the pickle file
            with open(
                    '/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/oneclasssvm_model.pkl',
                    'rb') as file:
                loaded_model = pickle.load(file)

            # Load the encoders from the pickle files
            with open(
                    '/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/time_encoder.pkl',
                    'rb') as file:
                time_encoder = pickle.load(file)

            with open(
                    '/Users/mehmed/Documents/projects/anomaly-detection-platform/anomaly_detection_platform/main/static/models/genre_encoder.pkl',
                    'rb') as file:
                genre_encoder = pickle.load(file)

            # Apply the encoders to the 'X' data
            time_encoded = time_encoder.transform([[d['time']] for d in fake_data])
            genre_encoded = genre_encoder.transform([d['genre'] for d in fake_data])

            X = [[d['price'], d['pages']] + list(time_encoded[i]) + [genre_encoded[i]] for i, d in enumerate(fake_data)]

            score = loaded_model.predict(X)[0]
            if score == -1:
                messages.error(request, f"Anomalous transaction!")
            elif score == 1:
                messages.success(request, f"Normal transaction.")
    else:
        form = PredictionDataForm()

    return render(request, 'playground.html', {'form': form, "score": score})


@login_required(login_url='/login')
def generate_fake_data(request):
    user = request.user
    data_params, created = DataGenerationParams.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = DataGenerationParamsForm(request.POST, instance=data_params)
        if form.is_valid():
            form.save()

            # Generate fake data
            num_data_points = data_params.num_records
            # Generate time_data following a normal distribution

            time_mean = form.cleaned_data.get('time_mean')
            time_std = form.cleaned_data.get('time_std')
            time_data = np.random.normal(loc=time_mean, scale=time_std, size=num_data_points)
            time_data = np.clip(time_data, 0, 24)

            # Generate price_data following a normal distribution
            price_mean = form.cleaned_data.get('price_mean')
            price_std = form.cleaned_data.get('price_std')
            price_data = np.random.normal(loc=price_mean, scale=price_std, size=num_data_points)
            price_data = np.clip(price_data, 0, None).astype(int)

            # Generate pages_data following a normal distribution
            pages_mean = form.cleaned_data.get('pages_std')
            pages_std = form.cleaned_data.get('pages_std')
            pages_data = np.random.normal(loc=pages_mean, scale=pages_std, size=num_data_points)
            pages_data = np.clip(pages_data, 0, None)
            pages_data = np.round(pages_data).astype(int)

            # Define genre options
            genre_options = ['fiction', 'non-fiction', 'mystery', 'romance']

            # Generate fake data
            fake_data = []

            # Save or update individual records in DataSet model
            DataSet.objects.filter(user=user).delete()  # Clear existing records for the user
            for i in range(num_data_points):
                time = f"{int(time_data[i]):02d}:00-{int(time_data[i]) + 1:02d}:00"
                genre = random.choice(genre_options)
                price = price_data[i]
                pages = pages_data[i]

                data_point = DataSet(
                    user=user,
                    time_data=time,
                    genre_data=genre,
                    price_data=price,
                    pages_data=pages,
                    params=data_params,
                )
                fake_data.append(data_point)
            DataSet.objects.bulk_create(fake_data)
            messages.success(request, "Dataset created successfully!")
            return redirect('main:generate-fake-data')  # Redirect to the home page after data generation and save

    else:
        form = DataGenerationParamsForm(instance=data_params)

    # Pagination
    data_sets = DataSet.objects.filter(user=user).order_by('-id')  # Order by id to get the latest records first
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data_sets, 10)  # Show 10 records per page
    page_obj = paginator.get_page(page_number)
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'generate_fake_data.html', context)


@login_required(login_url='/login')
def learning_corner_view(request):
    return render(request, 'learning_corner.html')


@login_required(login_url='/login')
def analysis(request):
    data_sets = DataSet.objects.filter(user=request.user).order_by('-id')  # Order by id to get the latest records first
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data_sets, 10)  # Show 10 records per page
    page_obj = paginator.get_page(page_number)
    time_data_values = list(DataSet.objects
                            .filter(user=request.user)
                            .values('time_data'))

    time_data_grouped_values = list(DataSet.objects
                                    .filter(user=request.user)
                                    .values('time_data')
                                    .annotate(count=Count('time_data'))
                                    .order_by('-count'))
    time_frame = {
        "morning": 0,
        "noon": 0,
        "afternoon": 0,
    }
    for time_interval in time_data_values:
        if time_interval['time_data'] in ["11:00-12:00", "12:00-13:00", "13:00-14:00"]:
            time_frame['noon'] += 1
        elif time_interval['time_data'] in ["08:00-09:00", "09:00-10:00", "10:00-11:00"]:
            time_frame['morning'] += 1
        else:
            time_frame["afternoon"] += 1

    time_analysis = {
        "field": "Time",
        "most_common": time_data_grouped_values[0],
        "least_common": time_data_grouped_values[-1],
        "time_frame": time_frame,
    }

    genre_analysis = {
        "field": "Genre",
        "value_counts": list(DataSet.objects
                             .filter(user=request.user)
                             .values('genre_data')
                             .annotate(count=Count('genre_data'))
                             .order_by('-count'))
    }
    price_data_grouped_values = list(DataSet.objects
                                     .filter(user=request.user)
                                     .values('price_data')
                                     .annotate(count=Count('price_data'))
                                     .order_by('-count'))

    price_data_values = list(DataSet.objects
                             .filter(user=request.user)
                             .values('price_data'))

    price_distribution = {
        "$0-$4": 0,
        "$5-$14": 0,
        "$15-$24": 0,
        "$25-$34": 0,
        "$35-$44": 0,
        "$45-$54": 0,
        "$55-$64": 0,
        "$64+": 0,
    }

    for price_data in price_data_values:
        if int(price_data['price_data']) < 5:
            price_distribution["$0-$4"] += 1
        elif int(price_data['price_data']) < 15:
            price_distribution["$5-$14"] += 1
        elif int(price_data['price_data']) < 25:
            price_distribution["$15-$24"] += 1
        elif int(price_data['price_data']) < 35:
            price_distribution["$25-$34"] += 1
        elif int(price_data['price_data']) < 45:
            price_distribution["$35-$44"] += 1
        elif int(price_data['price_data']) < 55:
            price_distribution["$45-$54"] += 1
        elif int(price_data['price_data']) < 65:
            price_distribution["$55-$64"] += 1
        else:
            price_distribution["$64+"] += 1
    price_analysis = {
        "field": "price_data",
        "most_common": price_data_grouped_values[0],
        "least_common": price_data_grouped_values[-1],
        "price_distribution": price_distribution,
    }

    pages_data_grouped_values = list(DataSet.objects
                                     .filter(user=request.user)
                                     .values('pages_data')
                                     .annotate(count=Count('pages_data'))
                                     .order_by('-count'))

    pages_data_values = list(DataSet.objects
                             .filter(user=request.user)
                             .values('pages_data'))

    pages_distribution = {
        "0-49": 0,
        "50-99": 0,
        "100-199": 0,
        "200-299": 0,
        "300-399": 0,
        "400+": 0,
    }

    for page_data in pages_data_values:
        if int(page_data['pages_data']) < 50:
            pages_distribution["0-49"] += 1
        elif int(page_data['pages_data']) < 100:
            pages_distribution["50-99"] += 1
        elif int(page_data['pages_data']) < 200:
            pages_distribution["100-199"] += 1
        elif int(page_data['pages_data']) < 300:
            pages_distribution["200-299"] += 1
        elif int(page_data['pages_data']) < 400:
            pages_distribution["300-399"] += 1
        else:
            pages_distribution["400+"] += 1

    pages_analysis = {
        "field": "price_data",
        "most_common": pages_data_grouped_values[0],
        "least_common": pages_data_grouped_values[-1],
        "pages_distribution": pages_distribution,
    }

    context = {
        'page_obj': page_obj,
        'time_analysis': time_analysis,
        'genre_analysis': genre_analysis,
        'price_analysis': price_analysis,
        'pages_analysis': pages_analysis,
        'record_count': DataSet.objects.filter(user=request.user).count()
    }

    return render(request, 'analysis.html', context=context)
