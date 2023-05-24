from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import TransactionForm
from django.db.models import Q, Sum
from datetime import date, timedelta
from cashbook.models import Category, Account, Transaction, TrxType
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    
    trx_types = TrxType.objects.all()
    categories = Category.objects.all()

    # Retrieve filter values from request
    date_filter = request.GET.get('date-filter', '')
    trx_type_filter = request.GET.get('trx-type', '')
    category_filter = request.GET.get('category', '')

    # Filter transactions based on filter values
    trx_all = Transaction.objects.order_by("-create_date")
    if date_filter:
        if date_filter == 'today':
            trx_all = trx_all.filter(create_date__date=date.today())
        elif date_filter == 'all-time':
            trx_all = Transaction.objects.order_by("-create_date")
        elif date_filter == 'yesterday':
            trx_all = trx_all.filter(create_date__date=date.today() - timedelta(days=1))
        elif date_filter == 'this_month':
            trx_all = trx_all.filter(create_date__month=date.today().month)
        elif date_filter == 'last_month':
            trx_all = trx_all.filter(create_date__month=date.today().month - 1)
        elif date_filter == 'single_day':
            # You'll need to add logic to handle single-day filtering
            pass
        elif date_filter == 'date_range':
            # You'll need to add logic to handle date range filtering
            pass
    else:
        date_filter = 'this_month'
        trx_all = trx_all.filter(create_date__month=date.today().month)

    if trx_type_filter:
        trx_all = trx_all.filter(trx_type_id=trx_type_filter)

    if category_filter:
        trx_all = trx_all.filter(category_id=category_filter)

    # Calculate totals and net balance
    type_cash_in = TrxType.objects.get(name='cash_in')
    type_cash_out = TrxType.objects.get(name='cash_out')

    total_cash_in = trx_all.filter(trx_type_id=type_cash_in).aggregate(Sum('amount'))['amount__sum'] or 0
    total_cash_out = trx_all.filter(trx_type_id=type_cash_out).aggregate(Sum('amount'))['amount__sum'] or 0

    acc_cash = Account.objects.get(name='Cash')
    net_balance = acc_cash.initial_balance + total_cash_in - total_cash_out

    context = {
        'trx_all': trx_all,
        'trx_types': trx_types,
        'categories': categories,
        'net_balance': net_balance,
        'acc_cash': acc_cash,
        'total_cash_in': total_cash_in,
        'total_cash_out': total_cash_out,

        'type_cash_in': type_cash_in,
        'type_cash_out': type_cash_out,
        
        'date_filter': date_filter,
        'trx_type_filter': trx_type_filter,
        'category_filter': category_filter,
    }

    return render(request, 'cashbook/index.html', context)

def cash_in(request):
    categories    = Category.objects.all()
    accounts      = Account.objects.all()
    type_cash_in  = TrxType.objects.get(name='cash_in')
    transaction   = Transaction()

    context = {
        'categories'    : categories,
        'accounts'      : accounts
    }

    if request.method == 'POST':
        account_id = request.POST['account']
        account = get_object_or_404(Account, pk=account_id)
        transaction.account_id = account

        category_id = request.POST['category']
        category = get_object_or_404(Category, pk=category_id)
        transaction.category_id = category
        
        transaction.trx_type_id = type_cash_in
        
        transaction.amount          = request.POST['amount']
        transaction.remarks         = request.POST['remarks']
        transaction.create_date     = request.POST['create_date']
        transaction.save()

        return redirect('cashbook:index')
    else:
        return render(request, 'cashbook/cash_in.html', context)

def cash_out(request):
    categories    = Category.objects.all()
    accounts      = Account.objects.all()
    type_cash_out = TrxType.objects.get(name='cash_out')
    transaction   = Transaction()

    context = {
        'categories'    : categories,
        'accounts'      : accounts
    }

    if request.method == 'POST':
        account_id = request.POST['account']
        account = get_object_or_404(Account, pk=account_id)
        transaction.account_id = account

        category_id = request.POST['category']
        category = get_object_or_404(Category, pk=category_id)
        transaction.category_id = category
        
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
        account_id = request.POST['account']
        account = get_object_or_404(Account, pk=account_id)
        transaction.account_id = account

        category_id = request.POST['category']
        category = get_object_or_404(Category, pk=category_id)
        transaction.category_id = category
        
        trx_id = request.POST['trx_type']
        trx_type = get_object_or_404(TrxType, pk=trx_id)
        transaction.trx_type_id = trx_type
        
        transaction.amount          = request.POST['amount']
        transaction.remarks         = request.POST['remarks']
        transaction.create_date     = request.POST['create_date']
        transaction.save()

        return redirect('cashbook:index')  # Replace with the appropriate URL name for the transaction list
    else:
        categories    = Category.objects.all()
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