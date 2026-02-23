from django.db import models

class School(models.Model):
    school_id = models.CharField(max_length=50, primary_key=True)
    teacher_name = models.CharField(max_length=50) 
    school_name = models.CharField(max_length=150)

    class Meta:
        db_table = 'school'

    def __str__(self):
        return f"{self.school_name} ({self.school_id})"

class Book(models.Model):
    book_id = models.CharField(max_length=50, primary_key=True)
    series_name = models.CharField(max_length=150)
    class_name = models.CharField(max_length=50, db_column='class') 

    class Meta:
        db_table = 'books'

    def __str__(self):
        return f"{self.series_name} - {self.class_name}"

class Teacher(models.Model):
    t_id = models.CharField(max_length=50, primary_key=True)
    teacher_name = models.CharField(max_length=50)
    school_id = models.CharField(max_length=50) 
    school_name = models.CharField(max_length=150, null=True, blank=True)
    password_hash = models.CharField(max_length=50)
    contact = models.IntegerField() # User specified INTEGER
    no_of_series_purchased = models.IntegerField(default=0)
    purchase_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'teacher'

    def __str__(self):
        return self.teacher_name

class Purchase(models.Model):
    s_no = models.IntegerField(unique=True) # SERIAL in Postgres, but purchase_id is PK
    purchase_id = models.CharField(max_length=50, primary_key=True)
    t_id = models.CharField(max_length=50)
    book_id = models.CharField(max_length=50)
    purchase_date = models.DateField(auto_now_add=True)
    valid_upto = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'purchase'

    def __str__(self):
        return f"{self.purchase_id} - {self.t_id}"
