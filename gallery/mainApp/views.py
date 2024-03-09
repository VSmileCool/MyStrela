from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404

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
                    title = file.name
                    Files.objects.create(user=request.user, file=file, title=title)
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
            album_form = CreateAlbum(request.POST)
            if album_form.is_valid():
                album = Album.objects.create(user=request.user, title=album_form.cleaned_data['title'])
                album.allowed_users.add(request.user)
                return redirect('photo_add', album_id=album.id)
        else:
            form = MultiFileForm()
            album_form = CreateAlbum()
            albums = Album.objects.filter(user=request.user)
            return render(request, 'Albums.html', {'albums': albums, 'form': form, 'album_form': album_form})
    except ValueError:
        return redirect('albums')


@login_required
def album_view(request, album_id):
    photos = []
    videos = []

    album = get_object_or_404(Album, pk=album_id, user=request.user)
    files = album.files.all()
    for file in files:
        file_name = file.file.name.lower()

        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            photos.append(file)
        elif file_name.endswith(('.mp4', '.avi', '.mov')):
            videos.append(file)

    return render(request, 'SomeAlbum.html', {'album': album, 'photos': photos, 'videos': videos})


@login_required
def add_files_to_album(request, album_id):
    try:
        album = get_object_or_404(Album, id=album_id, user=request.user)
        if request.method == 'POST':
            selected_photos_ids = request.POST.getlist('selected_photos')
            selected_videos_ids = request.POST.getlist('selected_videos')
            for video_id in selected_videos_ids:
                video = get_object_or_404(Files, id=video_id, user=request.user)
                print(video)
                new_video = album.files.add(video)
                print(new_video)
            for photo_id in selected_photos_ids:
                photo = get_object_or_404(Files, id=photo_id, user=request.user)
                album.files.add(photo)
            return redirect('album_files', album_id=album.id)
        else:
            photos = Files.objects.filter(
                Q(user=request.user, file__endswith='.jpg') |
                Q(user=request.user, file__endswith='.jpeg') |
                Q(user=request.user, file__endswith='.png') |
                Q(user=request.user, file__endswith='.gif')
            )
            videos = Files.objects.filter(
                Q(user=request.user, file__endswith='.mp4') |
                Q(user=request.user, file__endswith='.avi') |
                Q(user=request.user, file__endswith='.mov')
            )
            return render(request, 'ChooseFilesToAdd.html', {'photos': photos, 'videos': videos})
    except Exception as e:
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


@login_required
def delete_file(request, file_id):
    file_to_delete = get_object_or_404(Files, id=file_id, user=request.user)
    # Проверка, принадлежит ли файл пользователю для безопасности
    if file_to_delete.user != request.user:
        raise Http404("File not found")

    try:
        file_to_delete.file.delete()
        return JsonResponse({'message': 'File successfully deleted'})
    except Exception as e:
        print(f"Error deleting file: {e}")
        return JsonResponse({'error': 'Failed to delete file'}, status=500)


def download_file_view(request, file_id):

    # Получаем объект файла по его идентификатору
    file_object = get_object_or_404(Files, id=file_id)
    # Открываем файл на сервере и создаем FileResponse
    response = FileResponse(open(file_object.file.path, 'rb'))

    # Устанавливаем заголовки для скачивания файла
    response['Content-Disposition'] = f'attachment; filename="{file_object.file.name}"'
    return response
