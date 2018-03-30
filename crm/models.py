from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.db.models import ManyToManyRel
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe


class Customer(models.Model):
    '''Customer Info Table'''
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    qq_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    id_num = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    source_choice = ((0, 'GlassDoor'),
                     (1, 'LinkedIn'),
                     (2, 'FaceBook'),
                     (3, 'Twitter'),
                     (4, 'Career Fair'),
                     (5, 'Quora'))

    source = models.SmallIntegerField(choices=source_choice)
    status_choice = ((0, 'Enrolled'),
                     (1, 'Not Enrolled'))
    status = models.SmallIntegerField(choices=status_choice)
    referral_from = models.CharField(verbose_name='Referral QQ', max_length=64, blank=True, null=True)

    consult_course = models.ForeignKey('Course', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Consult Detail')
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    memo = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s : %s" %(self.qq, self.name)

class Tag(models.Model):
    name = models.CharField(unique=True, max_length=32)

    def __str__(self):
        return self.name

class CustomerFollowUp(models.Model):
    '''Customer Follow-up Table'''
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Follow-up Content')
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)

    intention_choices = ((0, 'Enroll in two weeks'),
                         (1, 'Enroll in one month'),
                         (2, 'No enrollment plan recently'),
                         (3, 'Enrolled in other school'),
                         (4, 'Already enrolled'),
                         (5, 'Refused'),)

    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s : %s>" %(self.customer, self.intention)


class Course(models.Model):
    '''Course Table'''
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveSmallIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name='Period(Month)')
    outline = models.TextField()
    def __str__(self):
        return self.name

class Branch(models.Model):
    '''Branches'''
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class ClassList(models.Model):
    '''Class List'''
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    class_type_choices = ((0, 'Onsite(Normal)'),
                          (1, 'Onsite(Weekend)'),
                          (2, 'Online'))

    contract = models.ForeignKey('ContractTemplate', blank=True, null=True, on_delete=models.CASCADE)
    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name='Class Type')
    semester = models.PositiveSmallIntegerField(verbose_name='Semester')
    teachers = models.ManyToManyField('UserProfile')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date', blank=True, null=True)

    def __str__(self):
        return '%s %s %s' %(self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course', 'semester')


class CourseRecord(models.Model):
    '''Course Record'''
    from_class = models.ForeignKey('ClassList', on_delete=models.CASCADE, verbose_name='Class Name')
    day_num = models.PositiveSmallIntegerField(verbose_name='Day')
    teacher = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name='Course Outline')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' %(self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')


class StudyRecord(models.Model):
    '''Study Record'''
    student = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    course_record = models.ForeignKey('CourseRecord', on_delete=models.CASCADE)
    attendance_choices = ((0, 'Checked in'),
                          (1, 'Late'),
                          (2, 'Absence'),
                          (3, 'Early Leave'))
    attendance = models.SmallIntegerField(choices=attendance_choices, default=0)

    score_choices = ((100, 'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (75, 'B-'),
                     (70, 'C+'),
                     (60, 'C'),
                     (40, 'C-'),
                     (-50, 'D'),
                     (-100, 'COPY'),
                     (0, 'N/A'))

    score = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return '%s %s %s' %(self.student, self.course_record, self.score)

    class Meta:
        unique_together = ('student', 'course_record')


class Enrollment(models.Model):
    '''Enrollment Table'''
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    enrolled_class = models.ForeignKey('ClassList', on_delete=models.CASCADE, verbose_name='Enrolled Class')
    consultant = models.ForeignKey('UserProfile', verbose_name='Course Consultant', on_delete=models.CASCADE)
    contract_agreed = models.BooleanField(default=False)
    contract_approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' %(self.customer, self.enrolled_class)

    class Meta:
        unique_together = ('customer', 'enrolled_class')

class Payment(models.Model):
    '''Payment Record'''
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Amount', default=500)
    consultant = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s %s' %(self.customer, self.amount)

# class UserProfile(models.Model):
#     '''Account Table'''
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField('Role', blank=True, null=True)
#     def __str__(self):
#         return self.name

class Role(models.Model):
    '''Role Table'''
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField('Menu', blank=True)
    def __str__(self):
        return self.name


class Menu(models.Model):
    '''Menu'''
    name = models.CharField(max_length=32)
    url_type_choices = ((0, 'alias'), (1, 'absolute_url'))
    url_type = models.SmallIntegerField(choices=url_type_choices, default=0)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email_address',
        max_length=255,
        unique=True,
        null=True
    )

    password = models.CharField(('password'), max_length=128, help_text=mark_safe('''<a href='password/'>Change Password</a>'''))
    name = models.CharField(max_length=32)
    # date_of_birth = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField('Role', blank=True)

    objects = UserProfileManager()

    stu_account = models.ForeignKey("Customer", blank=True, null=True, on_delete= models.CASCADE, help_text='Create this account only after the customer has enrolled in successfully')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    # def has_perm(self, perm, obj=None):
    #     return True

    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        return self.is_active

    class Meta:
        permissions = [['permission_test', 'Hello permissions'],
                       ['can_access_my_course', 'Allowed to access course'],
                       ['can_access_customer_list', 'Allowed to access customer list'],
                       ['can_access_customer_detail', 'Allowed to access customer detailed info'],
                       ['can_access_studyrecords', 'Allowed to access study records'],
                       ['can_access_homework_detail', 'Allowed to access homework detail'],
                       ['can_upload_homework', 'Allowed to upload homework']]

class ContractTemplate(models.Model):
    name = models.CharField('Contract Name', max_length=64, unique=True)
    template = models.TextField()

    def __str__(self):
        return self.name