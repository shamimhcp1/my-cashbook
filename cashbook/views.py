from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import TransactionForm, CategoryForm
from django.db.models import Q, Sum
from datetime import date, timedelta
from cashbook.models import Category, Account, Transaction, TrxType
from django.core.mail import send_mail
from django.conf import settings
import datetime

def index(request):
    
    trx_types = TrxType.objects.all()
    categories = Category.objects.all()

    type_cash_in = TrxType.objects.get(name='cash_in')
    type_cash_out = TrxType.objects.get(name='cash_out')

    # Retrieve filter values
    date_filter = request.GET.get('date-filter')
    trx_type_filter = request.GET.get('trx-type')
    category_filter = request.GET.get('category')
    
    # Transaction by date
    trx_all = Transaction.objects.order_by("-create_date")
    trx_today = trx_all.filter(create_date__date=datetime.date.today())
    trx_yesterday = trx_all.filter(create_date__date=datetime.date.today() - datetime.timedelta(days=1))
    trx_this_month = trx_all.filter(create_date__month=datetime.date.today().month)
    trx_last_month = trx_all.filter(create_date__month=datetime.date.today().month - 1)

    # Calculate net balance, opening balance, total cash in, and total cash out
    acc_cash = Account.objects.get(name='cash')
    initial_balance = acc_cash.initial_balance
    opening_balance = 0
    total_cash_in = 0
    total_cash_out = 0
    net_balance = 0

    # Apply filters
    if date_filter:
        # Apply date filter based on the selected value
        
        if date_filter == 'today':
            # Filter transactions for today
            total_cash_in = trx_today.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
            total_cash_out = trx_today.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
            prev_total_cash_in = trx_all.filter(trx_type_id=type_cash_in.id, create_date__lt=datetime.date.today()).aggregate(prev_total_cash_in=Sum('amount'))['prev_total_cash_in'] or 0
            prev_total_cash_out = trx_all.filter(trx_type_id=type_cash_out.id, create_date__lt=datetime.date.today()).aggregate(prev_total_cash_out=Sum('amount'))['prev_total_cash_out'] or 0
            opening_balance = (initial_balance + prev_total_cash_in - prev_total_cash_out) or 0
            net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
            transactions = trx_today
        elif date_filter == 'all-time':
            # Filter transactions for all-time
            total_cash_in = trx_all.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
            total_cash_out = trx_all.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
            opening_balance = initial_balance or 0
            net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
            transactions = trx_all
        elif date_filter == 'yesterday':
            # Filter transactions for yesterday
            total_cash_in = trx_yesterday.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
            total_cash_out = trx_yesterday.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
            prev_total_cash_in = trx_all.filter(trx_type_id=type_cash_in.id, create_date__lt=datetime.date.today() - datetime.timedelta(days=1)).aggregate(prev_total_cash_in=Sum('amount'))['prev_total_cash_in'] or 0
            prev_total_cash_out = trx_all.filter(trx_type_id=type_cash_out.id, create_date__lt=datetime.date.today() - datetime.timedelta(days=1)).aggregate(prev_total_cash_out=Sum('amount'))['prev_total_cash_out'] or 0
            opening_balance = (initial_balance + prev_total_cash_in - prev_total_cash_out) or 0
            net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
            transactions = trx_yesterday
        elif date_filter == 'this_month':
            # Filter transactions for the current month
            total_cash_in = trx_this_month.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
            total_cash_out = trx_this_month.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
            prev_total_cash_in = trx_all.filter(trx_type_id=type_cash_in.id, create_date__lt=date.today().replace(day=1)).aggregate(prev_total_cash_in=Sum('amount'))['prev_total_cash_in'] or 0
            prev_total_cash_out = trx_all.filter(trx_type_id=type_cash_out.id, create_date__lt=date.today().replace(day=1)).aggregate(prev_total_cash_out=Sum('amount'))['prev_total_cash_out'] or 0
            opening_balance = (initial_balance + prev_total_cash_in - prev_total_cash_out) or 0
            net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
            transactions = trx_this_month
        elif date_filter == 'last_month':
            # Filter transactions for the previous month
            trx_last_month_of_last_month = trx_all.filter(create_date__month=datetime.date.today().month - 2)
            total_cash_in = trx_last_month.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
            total_cash_out = trx_last_month.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
            prev_total_cash_in = trx_last_month_of_last_month.filter(trx_type_id=type_cash_in.id).aggregate(prev_total_cash_in=Sum('amount'))['prev_total_cash_in'] or 0
            prev_total_cash_out = trx_last_month_of_last_month.filter(trx_type_id=type_cash_out.id).aggregate(prev_total_cash_out=Sum('amount'))['prev_total_cash_out'] or 0
            opening_balance = (initial_balance + prev_total_cash_in - prev_total_cash_out) or 0
            net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
            transactions = trx_last_month
        elif date_filter == 'single_day':
            # You need to implement the logic for filtering by a specific day
            pass
        elif date_filter == 'date_range':
            # You need to implement the logic for filtering by a date range
            pass
    else:
        date_filter = 'this_month'
        # Filter transactions for the current month
        total_cash_in = trx_this_month.filter(trx_type_id=type_cash_in.id).aggregate(total_cash_in=Sum('amount'))['total_cash_in'] or 0
        total_cash_out = trx_this_month.filter(trx_type_id=type_cash_out.id).aggregate(total_cash_out=Sum('amount'))['total_cash_out'] or 0
        prev_total_cash_in = trx_all.filter(trx_type_id=type_cash_in.id, create_date__lt=date.today().replace(day=1)).aggregate(prev_total_cash_in=Sum('amount'))['prev_total_cash_in'] or 0
        prev_total_cash_out = trx_all.filter(trx_type_id=type_cash_out.id, create_date__lt=date.today().replace(day=1)).aggregate(prev_total_cash_out=Sum('amount'))['prev_total_cash_out'] or 0
        opening_balance = (initial_balance + prev_total_cash_in - prev_total_cash_out) or 0
        net_balance = (opening_balance + total_cash_in - total_cash_out) or 0
        transactions = trx_this_month
    if trx_type_filter:
        # Apply transaction type filter based on the selected value
        trx_all = trx_all.filter(trx_type_id=trx_type_filter)

    if category_filter:
        # Apply category filter based on the selected value
        trx_all = trx_all.filter(category_id=category_filter)

    
    context = {
        'transactions': transactions,
        'trx_types': trx_types,
        'categories': categories,
        'type_cash_in': type_cash_in,
        'type_cash_out': type_cash_out,
        'net_balance': net_balance,
        'opening_balance': opening_balance,
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,

        'date_filter': date_filter,
        'trx_type_filter': trx_type_filter,
        'category_filter': category_filter,
    }

    return render(request, 'cashbook/index.html', context)

# cash in transaction add
def cash_in(request):
    categories = Category.objects.filter(is_active=True).order_by("name")
    type_cash_in  = TrxType.objects.get(name='cash_in')
    transaction   = Transaction()

    context = {
        'categories'    : categories
    }

    if request.method == 'POST':
        if request.POST['category'] != 'null':
            category_id = request.POST['category']
            category = get_object_or_404(Category, pk=category_id)
            transaction.category_id = category
        else:
            transaction.category_id = None

        transaction.account_id = Account.objects.get(name='cash')
        transaction.trx_type_id = type_cash_in
        transaction.amount          = request.POST['amount']
        transaction.remarks         = request.POST['remarks']
        transaction.create_date     = request.POST['create_date']
        transaction.save()

        return redirect('cashbook:index')
    else:
        return render(request, 'cashbook/cash_in.html', context)

# cash out transaction add
def cash_out(request):
    categories = Category.objects.filter(is_active=True).order_by("name")
    type_cash_out = TrxType.objects.get(name='cash_out')
    transaction   = Transaction()

    context = {
        'categories'    : categories
    }

    if request.method == 'POST':
        if request.POST['category'] != 'null':
            category_id = request.POST['category']
            category = get_object_or_404(Category, pk=category_id)
            transaction.category_id = category
        else:
            transaction.category_id = None
        
        transaction.account_id = Account.objects.get(name='cash')
        transaction.trx_type_id = type_cash_out
        
        transaction.amount          = request.POST['amount']
        transaction.remarks         = request.POST['remarks']
        transaction.create_date     = request.POST['create_date']
        transaction.save()

        return redirect('cashbook:index')
    else:
        return render(request, 'cashbook/cash_out.html', context)

def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('cashbook:index')  # Replace with the appropriate URL name for the transaction list
    else:
        form = TransactionForm(instance=transaction)

    if request.method == 'POST':
        acc_cash      = Account.objects.get(name='cash')
        transaction.account_id = acc_cash

        if request.POST['category'] != 'null':
            category_id = request.POST['category']
            category = get_object_or_404(Category, pk=category_id)
            transaction.category_id = category
        else:
            transaction.category_id = None
        
        trx_id = request.POST['trx_type']
        trx_type = get_object_or_404(TrxType, pk=trx_id)
        transaction.trx_type_id = trx_type
        
        transaction.amount          = request.POST['amount']
        transaction.remarks         = request.POST['remarks']
        transaction.create_date     = request.POST['create_date']
        transaction.save()

        return redirect('cashbook:index')  # Replace with the appropriate URL name for the transaction list
    else:

        categories    = Category.objects.filter(is_active=True).order_by('name')
        accounts      = Account.objects.all()
        trx_types     = TrxType.objects.all()
        context = {
            'form': form,
            'transaction': transaction,
            'categories'    : categories,
            'accounts'      : accounts,
            'trx_types'     : trx_types
        }
        return render(request, 'cashbook/transaction_edit.html', context)


def delete_transaction(request):
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        transaction.delete()
    
    return redirect('cashbook:index')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send email using Django's send_mail()
        send_mail(
            'Contact Form Submission',
            f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False
        )

    return render(request, 'cashbook/about.html')

def manage_category(request):
    categories = Category.objects.order_by("name")
    total_categories = categories.count()
    context = {
        'categories'    : categories,
        'total_categories' : total_categories
    }
    return render(request, 'cashbook/category/manage_category.html', context)

def add_category(request):

    category = Category()
    if request.method == 'POST':
        is_active = request.POST.get('is_active', False)
        if not is_active:
            category.is_active = is_active
        category.name = request.POST['name']
        category.save()
        return redirect('cashbook:manage_category')
    else:
        return render(request, 'cashbook/category/add_category.html')

def edit_category(request, category_id):

    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        is_active = request.POST.get('is_active', False)
        if is_active:
            category.is_active = True
        else:
            category.is_active = is_active
        category.name = request.POST['name']
        category.save()
        return redirect('cashbook:manage_category')
    else:
        form = CategoryForm(instance=category)
        return render(request, 'cashbook/category/edit_category.html', context= {
            'category' : category,
            'form'  : form
        })

def delete_category(request):
    # return HttpResponse(request.POST['category_id'])
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=request.POST['category_id'])
        category.delete()
    return redirect('cashbook:manage_category')