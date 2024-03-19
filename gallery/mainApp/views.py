import json
from io import BytesIO

from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import Http404, JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from mainApp.forms import CustomUserCreationForm, MultiFileForm, CustomUserAuthForm, CreateAlbum
from mainApp.models import Files, Album, CustomUser, Tag


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
                print("form is valid")
                user = register_form.save()
                login(request, user)
                return redirect('gallery')
            else:
                print("form isn't valid")
                show_registration_form = True

        elif 'login_form' in request.POST:
            login_form = CustomUserAuthForm(request, request.POST)
            if login_form.is_valid():
                user = authenticate(request, email=login_form.cleaned_data['email'],
                                    password=login_form.cleaned_data['password'])
                if user is not None:
                    login(request, user)
                    return redirect('gallery')
                else:
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
                Q(user=request.user, file__endswith='.png') |
                Q(user=request.user, file__endswith='.row') |
                Q(user=request.user, file__endswith='.dng')
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
                return redirect('photo_add', album_id=album.id)
        else:
            form = MultiFileForm()
            album_form = CreateAlbum()
            shared_albums = Album.objects.filter(allowed_users__id=request.user.id)
            albums = Album.objects.filter(user_id=request.user.id)
            return render(request, 'Albums.html', {'shared_albums': shared_albums, 'albums': albums, 'form': form, 'album_form': album_form})
    except ValueError:
        return redirect('albums')


@login_required
def album_view(request, album_id):
    photos = []
    videos = []
    all_user_emails = CustomUser.objects.values_list('email', flat=True)
    user = request.user

    album = get_object_or_404(Album, pk=album_id)
    allowed_users = album.allowed_users.all()

    files = album.files.all()
    for file in files:
        file_name = file.file.name.lower()
        if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.dng', '.row')):
            photos.append(file)
        elif file_name.endswith(('.mp4', '.avi', '.mov')):
            videos.append(file)
    if request.user == album.user:
        if allowed_users:
            return render(request, 'SomeAlbum.html',
                          {'allowed_users': allowed_users, 'user': user, 'album': album, 'photos': photos,
                           'videos': videos,
                           'emails': all_user_emails})
        else:
            return render(request, 'SomeAlbum.html',
                          {'allowed_users': False, 'user': user, 'album': album, 'photos': photos, 'videos': videos,
                           'emails': all_user_emails})
    elif request.user in allowed_users:
        return render(request, 'SomeAlbum.html',
                      {'member': True, 'user': user, 'album': album, 'photos': photos, 'videos': videos})
    else:
        raise Http404("File not found")


@login_required
def add_files_to_album(request, album_id):
    try:
        album = get_object_or_404(Album, id=album_id)
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
                Q(user=request.user, file__endswith='.row') |
                Q(user=request.user, file__endswith='.dng')
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


@login_required
def download_file_view(request, file_id):
    file_object = get_object_or_404(Files, id=file_id)
    response = FileResponse(open(file_object.file.path, 'rb'))

    # Устанавливаем заголовки для скачивания файла
    response['Content-Disposition'] = f'attachment; filename="{file_object.file.name}"'
    return response


@login_required
def add_user_to_album(request):
    user_email = request.GET.get('user_email')
    album_id = request.GET.get('album_id')

    album = get_object_or_404(Album, pk=album_id)
    if request.user == album.user:
        user_to_add = get_object_or_404(CustomUser, email=user_email)
        album.allowed_users.add(user_to_add)
        print('added')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('albums')
    else:
        raise Http404("Auth error")


@login_required
def delete_user_from_album(request):
    user_email = request.GET.get('user_email')
    album_id = request.GET.get('album_id')

    album = get_object_or_404(Album, pk=album_id)
    if request.user == album.user:
        user_to_remove = get_object_or_404(CustomUser, email=user_email)
        album.allowed_users.remove(user_to_remove)
        print('deleted')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('albums')
    else:
        raise Http404("Auth error")


@login_required
# @csrf_exempt
def add_tag(request):
    print("WE ARE ADDING NOW")
    new_tag = request.GET.get('tag')
    file_id = request.GET.get('file_id')
    print(new_tag, file_id)

    file = get_object_or_404(Files, pk=file_id)
    if True:
        tag = Tag.objects.create(name=new_tag)
        file.tags.add(tag)
        print('added')
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        else:
            return redirect('gallery')
    else:
        raise Http404("Auth error")


# ТАМАРЕН КОД СНИЗУ
@login_required
def change_image_view(request):
    if request.method == 'GET':
        photo_url = request.GET.get('photo')
        photo_id = request.GET.get('id')
        if photo_url:
            return render(request, 'ChangeImage.html', {'photourl': photo_url, 'photoid': photo_id})


@login_required
def crop_image(request):
    if request.method == 'GET':
        photo_url = request.GET.get('photo')
        photo_id = request.GET.get('id')

        return render(request, 'CropImage.html', {'photourl': photo_url, 'photoid': photo_id})


def save_cropped_image(request):
    print("WE ARE IN SAVING CROPPED IMAGE")
    x = int(request.GET.get('x'))
    y = int(request.GET.get('y'))
    height = int(request.GET.get('height'))
    width = int(request.GET.get('width'))
    id = request.GET.get('id')

    myModel = Files.objects.get(pk=id)

    original_photo = BytesIO(myModel.file.read())
    output_photo = BytesIO()

    image = Image.open(original_photo)
    # print(x,y,height,width)
    image = image.crop((x, y, x + width, y + height))
    # image = image.crop((190,40,340+190,380))

    # image = image.rotate(-int(rValue))
    # image = enhBrightness.enhance(int(bValue) / 100)
    # enhContrast = ImageEnhance.Contrast(image)
    # image = enhContrast.enhance(int(cValue) / 100 )

    image.save(output_photo, 'JPEG')

    myModel.file.save(f"{id}_cropped.jpg", ContentFile(output_photo.getvalue()))
    myModel.save()

    path = myModel.file.path
    # return HttpResponse(json.dumps({'filepath': path[path.index("\media")::]}),content_type="application/json")


def save_image(request):
    if request.method == 'GET':
        bValue = request.GET.get('brightness')
        cValue = request.GET.get('contrast')
        rValue = request.GET.get('rotation')
        photo = request.GET.get('photo')
        id = request.GET.get('id')
        textX = request.GET.get('textX')
        textY = request.GET.get('textY')
        textValue = request.GET.get('textValue')

        myModel = Files.objects.get(pk=id)

        original_photo = BytesIO(myModel.file.read())
        rotated_photo = BytesIO()

        image = Image.open(original_photo)

        enhBrightness = ImageEnhance.Brightness(image)

        image = image.rotate(-int(rValue))
        image = enhBrightness.enhance(int(bValue) / 100)
        enhContrast = ImageEnhance.Contrast(image)
        image = enhContrast.enhance(int(cValue) / 100)

        print(textY, textX, textValue)

        if textValue:
            font = ImageFont.load_default(size=16 * 3)
            width, height = image.size
            draw_text = ImageDraw.Draw(image)
            draw_text.text(((width * int(textX)) / 100, (height * int(textY)) / 100), textValue, fill='#1C0606',
                           font=font)

        image.save(rotated_photo, 'JPEG')

        myModel.file.save(f"{photo[photo.rindex('/') + 1:photo.rindex('.'):]}.jpg", ContentFile(rotated_photo.getvalue()))
        myModel.save()

        print("1!!!!", myModel.file.path)

        # with open ("D:/Programming/TexStrela2024/gallery/media/user_1/ocr.jpg", 'rb') as f:
        # Files.objects.create(user=request.user, file=file_object, title="tututu")
        print(bValue, cValue, rValue, photo, id)
        path = myModel.file.path
        return HttpResponse(json.dumps({'filepath': path[path.index("media") - 1::]}), content_type="application/json")
