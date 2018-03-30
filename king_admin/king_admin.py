from crm import models
from django.shortcuts import render, redirect, HttpResponse

class BaseAdmin(object):
    list_display = []
    list_filters = ['id']
    search_fields = []
    list_per_page = 10
    ordering = None
    filter_horizontal = []
    actions = ['delete_selected_objs', ]
    readonly_fields = []
    readonly_table = False
    modelform_exclude_fields = []

    def delete_selected_objs(self, request, querysets):
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        if self.readonly_table:
            errors = {"readonly_table": "This table is readonly, cannot be deleted"}
        else:
            errors = {}
        if request.POST.get('delete_confirm') == 'yes':
            if not self.readonly_table:
                querysets.delete()
                return redirect('/king_admin/%s/%s/' %(app_name, table_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        return render(request, 'king_admin/table_obj_delete.html', {'obj':querysets, 'admin_class':self, 'app_name':app_name, 'table_name':table_name,
                                                                    'selected_ids':selected_ids, 'action': request._admin_action,
                                                                    'errors': errors})

    def default_form_validation(self):
        '''Like the form method of django form'''
        pass

class CustomerAdmin(BaseAdmin):
    list_display = ['id', 'qq', 'name', 'source', 'consultant', 'consult_course', 'date', 'status', 'enroll']
    list_filters = ['source', 'consultant', 'consult_course', 'status', 'date']
    search_fields =  ['qq', 'name', 'consultant__name']
    list_per_page = 2
    filter_horizontal = ['tags']
    # readonly_fields = ['qq', 'consultant',]
    actions = ['delete_selected_objs', ]
    # readonly_table = True

    def enroll(self):

        if self.instance.status == 0:
            link_name = 'Enroll in a new course'
        else:
            link_name = 'Enroll'

        return '''<a href="/crm/customer/%s/enrollment/"> %s </a>''' %(self.instance.id, link_name)


    def default_form_validation(self):
        '''Like the form method of django form'''
        print('ok',self.instance)

        consult_content = self.cleaned_data.get("content",'')
        if len(consult_content) < 15:
            return self.ValidationError(
                ('Field %(field)s must have at least 15 characters.'),
                code='invalid',
                params={'field': 'content'},
            )

    # should return the cleaned name, otherwise the name will become null
    def clean_name(self):
        if not self.cleaned_data['name']:
            self.add_error('name', 'cannot be null')

        return self.cleaned_data['name']


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ['id', 'customer', 'consultant', 'date']

class UserProfileAdmin(BaseAdmin):
    list_display = ['email', 'name']
    readonly_fields = ['password']
    filter_horizontal = ['groups', 'user_permissions','roles']
    modelform_exclude_fields = ['last_login']

class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class', 'day_num', 'teacher', 'has_homework', 'homework_title', 'date']


    def initialize_studyrecords(modeladmin, request, queryset):
        print("Hello action", request, queryset)
        if len(queryset) > 1:
            return HttpResponse('Only one course record can be selected!')

        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            #models.StudyRecord.objects.get_or_create(
            #     student=enroll_obj,
            #     course_record=queryset[0],
            #     attendance=0,
            #     score=0,
            #
            # )

            new_obj_list.append(models.StudyRecord(
                    student=enroll_obj,
                    course_record=queryset[0],
                    attendance=0,
                    score=0))

        models.StudyRecord.objects.bulk_create(new_obj_list)

        return redirect('/king_admin/crm/studyrecord/?course_record=%s'%queryset[0].id)

    initialize_studyrecords.short_description = 'initialize this course record.'
    actions = ['initialize_studyrecords',]

class StudyRecordAdmin(BaseAdmin):
    list_display = ['student', 'course_record', 'attendance', 'score', 'date']
    list_filters = ['course_record', 'score', 'attendance']

enabled_admins = {}
def register(model_class, admin_class = None):
    if model_class._meta.app_label not in enabled_admins:
        enabled_admins[model_class._meta.app_label] = {}

    #admin_obj = admin_class()
    admin_class.model = model_class
    enabled_admins[model_class._meta.app_label][model_class._meta.model_name] = admin_class


register(models.Customer, CustomerAdmin)
register(models.CustomerFollowUp, CustomerFollowUpAdmin)
register(models.UserProfile, UserProfileAdmin)
register(models.CourseRecord, CourseRecordAdmin)
register(models.StudyRecord, StudyRecordAdmin)