from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class Account(models.Model):
    name            = models.CharField(max_length=20)
    initial_balance = models.FloatField(default=0)

    def __str__(self):
        return self.name

# define Transaction Type
class TrxType(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name
    
class Transaction(models.Model):
    amount          = models.FloatField(default=0)
    account_id      = models.ForeignKey(Account, on_delete=models.CASCADE)
    category_id     = models.ForeignKey(Category, on_delete=models.CASCADE)
    trx_type_id     = models.ForeignKey(TrxType, on_delete=models.CASCADE)
    remarks         = models.CharField(max_length=100)
    create_date     = models.DateTimeField("date created")

    def __str__(self):
        return f"Amount: {self.amount}, Remarks: {self.remarks}, Date: {self.create_date},"