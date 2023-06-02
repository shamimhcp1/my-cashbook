from django.urls import path
from . import views

app_name = "cashbook"
urlpatterns = [
    path("", views.index, name="index"),
    path('accounts/<str:acc_name>/', views.accounts_view, name='accounts_view'),

    path("transaction/cash_in", views.cash_in, name="cash_in"),
    path("transaction/cash_out", views.cash_out, name="cash_out"),
    path('transaction/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transaction/delete/', views.delete_transaction, name='delete_transaction'),
    
    path('contact/', views.contact_view, name='contact'),
    
    path('category/', views.manage_category, name='manage_category'),
    path('category/add', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>', views.edit_category, name='edit_category'),
    path('category/delete/', views.delete_category, name='delete_category'),
]