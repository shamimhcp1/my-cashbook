from django.db import models
import datetime

class Category(models.Model):
    name = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Account(models.Model):
    name            = models.CharField(max_length=20)
    initial_balance = models.FloatField(default=0)
    net_balance  = models.FloatField(default=0)
    last_updated = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.name

# define Transaction Type
class TrxType(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    amount          = models.FloatField(blank=False, null=False)
    account_id      = models.ForeignKey(Account, on_delete=models.CASCADE)
    category_id     = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    trx_type_id     = models.ForeignKey(TrxType, on_delete=models.CASCADE)
    remarks         = models.TextField(blank=True)
    create_date     = models.DateTimeField("date created")

    def __str__(self):
        return f"Amount: {self.amount}, Remarks: {self.remarks}, Date: {self.create_date},"