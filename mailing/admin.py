from django.contrib import admin


from .models import Mailing, Message, Client

admin.site.register(Mailing)
admin.site.register(Message)
admin.site.register(Client)
