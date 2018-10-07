from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf.urls.static import static
from HotelApp import views
#from django_registration.views import RegistrationView
from django_registration.backends.one_step.views import RegistrationView
from HotelProject import settings
from django.conf.urls import include, url
from django.contrib.auth.views import LoginView, LogoutView


class MyRegistrationView(RegistrationView):
    def get_sucess_url(self,user):
        return '/HotelApp/user/'

urlpatterns = [
    url(r'^$', views.home , name = 'home'),
    url(r'^register/completed$', views.regcomplete , name = 'registration_complete'),
    url(r'^HotelApp/', include('HotelApp.urls')),
    url(r'^ManageHotels/', include('ManageHotels.urls')),
    url(r'^Authorize/', include('Authorize.urls')),
    url(r'^Reservations/', include('Reservations.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
    url(r'^social/', include('allauth.urls')),
    url(r'^accounts/', include('django_registration.backends.activation.urls')),
    url(r'^accounts/login/$', LoginView.as_view(), name ='auth_login'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name ='auth_logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
