from django.db import models
from django.utils import timezone

class Book(models.Model):
    title = models.CharField(max_length=255,default="Unknown")
    authors = models.CharField(max_length=255,default="Unknown")
    isbn = models.CharField(max_length=13, unique=True,default="0000000000")  # Assuming ISBN is unique
    publisher = models.CharField(max_length=255,default="Unknown")
    page = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    def decrease_stock(self, quantity=1):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()

    def increase_stock(self, quantity=1):
        self.stock += quantity
        self.save()

    def is_available(self):
        return self.stock > 0



class Member(models.Model):
    name = models.CharField(max_length=100,null=True)
    outstanding_debt = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # Add more member-related fields as needed
    def calculate_total_debt(self):
        return Transaction.objects.filter(member=self).aggregate(total_debt=models.Sum('rent_fee'))['total_debt']

    def has_exceeded_debt_limit(self):
        return self.calculate_total_debt() > 500


class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    rent_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def calculate_rent_fee(self):
        # Add logic to calculate rent fee based on issue and return date
        return self.rent_fee

    def is_overdue(self):
        if self.return_date and self.return_date > timezone.now().date():
            return True
        return False

