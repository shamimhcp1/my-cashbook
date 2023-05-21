from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .forms import TransactionForm
from django.db.models import Q

from cashbook.models import Category, Account, Transaction, TrxType

def index(request):
    acc_cash        = Account.objects.get(name='Cash')
    trx_all         = Transaction.objects.order_by("-create_date")
    type_cash_in    = TrxType.objects.get(name='cash_in')
    type_cash_out   = TrxType.objects.get(name='cash_out')

    total_cash_in = 0
    for trx in trx_all:
        if trx.trx_type_id == type_cash_in:
            total_cash_in += trx.amount
            
    total_cash_out = 0
    for trx in trx_all:
        if trx.trx_type_id == type_cash_out:
            total_cash_out += trx.amount

    net_balance = 0
    net_balance = acc_cash.initial_balance + total_cash_in - total_cash_out

    context = {
        'trx_all'       : trx_all,
        'type_cash_in'  : type_cash_in,
        'type_cash_out' : type_cash_out,
        'total_cash_in' : total_cash_in,
        'total_cash_out': total_cash_out,
        'acc_cash'      : acc_cash,
        'net_balance'   : net_balance,
        'categories'    : Category.objects.all(),
        'trx_types'     : TrxType.objects.all()
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