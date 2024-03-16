from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.home_view, name="home"),

    path('gallery/', views.gallery_view, name="gallery"),
    path('albums/', views.albums_view, name="albums"),
    path('videos/', views.videos_view, name="videos"),
    path('albums/<int:album_id>/', views.album_view, name='album_files'),

    re_path(r'^gallery/changeimage/$', views.change_image_view, name='user_change_image'),
    path('gallery/changeimage/save_image/', views.save_image),
    path('gallery/changeimage/crop_image/save_cropped_image/', views.save_cropped_image),
    re_path(r'^gallery/changeimage/crop_image/$', views.crop_image),

    path('delete/<int:file_id>/', views.delete_file, name="deleting"),
    path('download/<int:file_id>/', views.download_file_view, name="saving"),

    re_path(r'^add-user-to-album/$', views.add_user_to_album, name="adding_user"),
    re_path(r'^delete-user-from-album/$', views.delete_user_from_album, name="deleting_user"),
    path('albums/add-photos/<int:album_id>/', views.add_files_to_album, name='photo_add'),
    re_path(r'tags/add-tag/$', views.add_tag, name='tag_add'),
]
