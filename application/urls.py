from django.urls import path
from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="index"),
    path('signup', views.signup, name="signup"),
    path('login', views.login, name="login"),
    path('logout', views.logout, name="logout"),
    path('doctors', views.all_doctors, name="doctors"),
    path('departments', views.all_departments, name="departments"),
    path('department/<name>', views.per_department, name="department"),
    path('doctor/<id>', views.per_doct, name="doctor"),
    path('myProfile', views.myProfile, name="myProfile"),
    path('profile/<id>', views.profile, name="profile"),
    path('send_request', views.send_request, name="send_request"),
    path('reject/<id>', views.reject, name="reject"),
    path('completed/<id>', views.completed, name="completed"),
    path('check_password', views.check_password, name="check_password"),
    path('emergency', views.emergency, name="emergency"),
    path('chat',views.chat, name='chat'),
    path('chat/<str:pk>',views.chat_pk, name='chat_pk'),
    path('edit/', views.update , name="eprofil"),
    path('covid/', views.home_form , name="covid"),
    url(r'^result$', views.home_view, name="home_view"),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_sent.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='password_reset_form.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_done.html'
         ),
         name='password_reset_complete'),
]

urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
