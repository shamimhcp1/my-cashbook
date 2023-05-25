# forms.py

from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'account_id', 'category_id', 'trx_type_id', 'remarks', 'create_date']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
