# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Books(models.Model):
    book_id = models.CharField(primary_key=True, max_length=50)
    series_name = models.CharField(max_length=100)
    class_field = models.CharField(db_column='class', max_length=20)  # Field renamed because it was a Python reserved word.
    path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'books'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Purchase(models.Model):
    purchase_id = models.CharField(primary_key=True, max_length=50)
    t = models.ForeignKey('Teacher', models.DO_NOTHING)
    purchase_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase'


class PurchaseItems(models.Model):
    purchase = models.ForeignKey(Purchase, models.DO_NOTHING, blank=True, null=True)
    book = models.ForeignKey(Books, models.DO_NOTHING, blank=True, null=True)
    valid_upto = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'purchase_items'


class SamselWebsiteBook(models.Model):
    book_id = models.CharField(primary_key=True, max_length=50)
    series_name = models.CharField(max_length=150)
    class_field = models.CharField(db_column='class', max_length=50)  # Field renamed because it was a Python reserved word.

    class Meta:
        managed = False
        db_table = 'samsel_website_book'


class SamselWebsitePurchase(models.Model):
    s_no = models.AutoField(primary_key=True)
    purchase_id = models.CharField(max_length=50)
    t_id = models.CharField(max_length=50)
    book_id = models.CharField(max_length=50)
    purchase_date = models.DateField()
    valid_upto = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'samsel_website_purchase'


class SamselWebsiteSchool(models.Model):
    school_id = models.CharField(primary_key=True, max_length=50)
    teacher_name = models.CharField(max_length=50)
    school_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'samsel_website_school'


class SamselWebsiteTeacher(models.Model):
    t_id = models.CharField(primary_key=True, max_length=50)
    teacher_name = models.CharField(max_length=50)
    school_id = models.CharField(max_length=50)
    school_name = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    no_of_series_purchased = models.IntegerField()
    purchase_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'samsel_website_teacher'


class School(models.Model):
    school_id = models.CharField(primary_key=True, max_length=50)
    school_name = models.CharField(max_length=150)
    contact = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'school'


class Teacher(models.Model):
    t_id = models.CharField(primary_key=True, max_length=50)
    teacher_name = models.CharField(max_length=100)
    school = models.ForeignKey(School, models.DO_NOTHING)
    password_hash = models.CharField(max_length=200)
    contact = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teacher'
