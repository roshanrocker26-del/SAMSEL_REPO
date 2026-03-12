from django.db import models


class Books(models.Model):
    book_id = models.CharField(primary_key=True, max_length=50)
    series_name = models.CharField(max_length=100)
    class_field = models.CharField(db_column='class', max_length=20)
    path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'books'

    def __str__(self):
        return f"{self.series_name} - {self.class_field}"


class School(models.Model):
    school_id = models.CharField(primary_key=True, max_length=50)
    school_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=15, blank=True, null=True)
    password_hash = models.CharField(max_length=200)
    branch = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = 'school'

    def __str__(self):
        return self.school_name


class Purchase(models.Model):
    purchase_id = models.CharField(primary_key=True, max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    purchase_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'purchase'

    def __str__(self):
        return f"{self.purchase_id} - School {self.school.school_name}"


class PurchaseItems(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    valid_upto = models.DateField(blank=True, null=True)
    sent_to_school = models.BooleanField(default=False)

    class Meta:
        db_table = 'purchase_items'

    def __str__(self):
        return f"{self.book.book_id} for purchase {self.purchase.purchase_id}"