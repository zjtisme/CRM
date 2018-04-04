# CRM
<p>Start this project by typing "python3 manage.py runserver 127.0.0.1:8080" if you don't have the virtual env for python</p>
<p>If you are the first time to use this app, please be sure to create a admin user by typing "python3 manage.py createsuperuser" and 
follow the instructions.</p>
<p>You can manage your account by typing "localhost:8080/admin" or you can choose my customized admin version just by replacing
"admin" in the previous url with "king_admin"</p>
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^crm/', include("crm.urls")),
    url(r'^account/login/$', views.acc_login),
    url(r'^$', views.index),
    url(r'^account/logout/$', views.acc_logout, name='acc_logout'),
    url(r'^student/', include("student.urls")),
    url(r'^king_admin/', include("king_admin.urls")),
]
