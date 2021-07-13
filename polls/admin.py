from django.contrib import admin

from polls.models import *

admin.site.register(Poll)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Result)
