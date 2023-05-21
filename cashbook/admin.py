from django.contrib import admin

from .models import Category, Account, TrxType, Transaction

admin.site.register(Category)
admin.site.register(Account)
admin.site.register(TrxType)
admin.site.register(Transaction)