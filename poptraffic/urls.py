from django.urls import path

from . import views

app_name = "pop_traffic"
urlpatterns = [
    path('', views.PopTrafficModelDesView.as_view(), name='main'),
    path('model_des/', views.PopTrafficModelDesView.as_view(), name='model_des'),
    path('data_des/', views.PopTrafficDataDesView.as_view(), name='data_des'),
    path('input_model/',views.PopTrafficInputModelView.as_view(), name='input_model'),
    path('upload_data/', views.PopTrafficUploadData.as_view(), name='upload_data'),
    path('train/', views.PopTrafficTrain.as_view(), name='train')
]