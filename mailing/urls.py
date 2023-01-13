from django.urls import path
from mailing.views import *
from rest_framework import routers

router = routers.SimpleRouter()
router.register('client', ClientViewSet)
router.register('mailing', MailingViewSet)
urlpatterns = router.urls
