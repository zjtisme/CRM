from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Sum
register = template.Library()



@register.simple_tag
def get_score(enroll_obj, customer_obj):
    study_records = enroll_obj.studyrecord_set.\
        filter(course_record__from_class_id = enroll_obj.enrolled_class.id)
    print(study_records)
    return study_records.aggregate(Sum('score'))