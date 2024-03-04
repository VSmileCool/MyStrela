from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

from mainApp.forms import CustomUserCreationForm, MultiFileForm, CustomUserAuthForm, CreateAlbum
from mainApp.models import Files, Album


def home_view(request):
    register_form = CustomUserCreationForm()
    login_form = CustomUserAuthForm()
    show_registration_form = False
    show_login_form = False
    if request.method == 'POST':
        print("GOT POST AUTH")
        print(request.POST)
        if 'register_form' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('gallery')  # Укажите свое представление для переадресации после регистрации
            else:
                show_registration_form = True

        elif 'login_form' in request.POST:
            login_form = CustomUserAuthForm(request, request.POST)
            if login_form.is_valid():
                # user = login_form.get_user()
                user = authenticate(request, email=login_form.cleaned_data['email'],
                                    password=login_form.cleaned_data['password'])
                if user is not None:
                    # Пользователь успешно аутентифицирован
                    login(request, user)
                    return redirect('gallery')  # Укажите свое представление для переадресации после входа
                else:
                    # Аутентификация не удалась
                    show_login_form = True
            else:
                show_login_form = True

    return render(request, 'Home.html', {'registration_form': register_form, 'login_form': login_form,
                                         'show_registration_form': show_registration_form,
                                         'show_login_form': show_login_form})


@login_required
def gallery_view(request):
    try:
        if request.method == 'POST':
            print(request.POST)
            form = MultiFileForm(request.POST, request.FILES)
            if form.is_valid():
                for file in request.FILES.getlist('files'):
                    Files.objects.create(user=request.user, file=file)
            return redirect('gallery')
        else:
            form = MultiFileForm()
            photos = Files.objects.filter(
                Q(user=request.user, file__endswith='.jpg') |
                Q(user=request.user, file__endswith='.jpeg') |
                Q(user=request.user, file__endswith='.png')
            )
            return render(request, 'Gallery.html', {'photos': photos, 'form': form})
    except ValueError:
        return redirect('gallery')


@login_required
def albums_view(request):
    try:
        if request.method == 'POST':
            print(request.POST)
            album_form = CreateAlbum(request.POST, request.TITLE)
            if album_form.is_valid():
                print("HUISHE")
                Album.objects.create(user=request.user, title=album_form.cleaned_data['title'])
            return redirect('albums')
        else:
            form = MultiFileForm()
            album_form = CreateAlbum()
            albums = Album.objects.filter(user=request.user)
            return render(request, 'Albums.html', {'albums': albums, 'form': form, 'album_form': album_form})
    except ValueError:
        return redirect('albums')


@login_required
def videos_view(request):
    try:
        if request.method == 'POST':
            print(request.POST)
            form = MultiFileForm(request.POST, request.FILES)
            if form.is_valid():
                for file in request.FILES.getlist('files'):
                    Files.objects.create(user=request.user, file=file)
            return redirect('videos')
        else:
            form = MultiFileForm()
            videos = Files.objects.filter(
                Q(user=request.user, file__endswith='.mp4') |
                Q(user=request.user, file__endswith='.avi') |
                Q(user=request.user, file__endswith='.mov')
            )
            return render(request, 'Videos.html', {'videos': videos, 'form': form})
    except ValueError:
        return redirect('videos')


@login_required
def bin_view(request):
    pass
    # try:
    #     if request.method == 'POST':
    #         print(request.POST)
    #         form = MultiFileForm(request.POST, request.FILES)
    #         if form.is_valid():
    #             for file in request.FILES.getlist('files'):
    #                 Files.objects.create(user=request.user, image=file)
    #         return redirect('gallery')
    #     else:
    #         form = MultiFileForm()
    #         photos = Files.objects.filter(user=request.user)
    #         return render(request, 'Albums.html', {'photos': photos, 'form': form})
    # except ValueError:
    #     return redirect('gallery')
