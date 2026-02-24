from django.db import models

class Teacher(models.Model):
    t_id = models.CharField(primary_key=True, max_length=50)
    teacher_name = models.CharField(max_length=50)
    school_id = models.CharField(max_length=50)
    school_name = models.CharField(max_length=150, blank=True, null=True)
    password_hash = models.CharField(max_length=50)
    contact = models.IntegerField()
    no_of_series_purchased = models.IntegerField(default=0)
    purchase_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teacher'

    def __str__(self):
        return self.teacher_name

class Books(models.Model):
    book_id = models.CharField(primary_key=True, max_length=50)
    series_name = models.CharField(max_length=150)
    class_num = models.CharField(db_column='class', max_length=50)  # 'class' is a reserved keyword in Python

    class Meta:
        managed = False
        db_table = 'books'

    def __str__(self):
        return f"{self.series_name} - {self.class_num}"

class Purchase(models.Model):
    s_no = models.AutoField(primary_key=True)
    purchase_id = models.CharField(max_length=50)
    t_id = models.ForeignKey(Teacher, db_column='t_id', on_delete=models.CASCADE)
    book_id = models.ForeignKey(Books, db_column='book_id', on_delete=models.CASCADE)
    purchase_date = models.DateField(auto_now_add=True)
    valid_upto = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase'

    def __str__(self):
        return f"{self.t_id.teacher_name} -> {self.book_id.book_id}"
