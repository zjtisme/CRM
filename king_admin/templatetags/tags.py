
from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime, timedelta
from django.core.exceptions import FieldDoesNotExist

register = template.Library()


@register.simple_tag
def render_app_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

@register.simple_tag
def build_table_row(request, obj, admin_class):
    row_ele = ''
    for index, column in enumerate(admin_class.list_display):
        try:
            field_obj = obj._meta.get_field(column)
            if field_obj.choices:
                column_data = getattr(obj, 'get_%s_display' % column)()
            else:
                column_data = getattr(obj, column)

            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime('%Y-%m-%d %H:%M:%S')

            if index == 0:
                column_data = "<a href='{request_path}{obj_id}/change/'>{data}</a>".format(request_path=request.path,
                                                                                   obj_id=obj.id, data=column_data)
        except FieldDoesNotExist as e:
            if hasattr(admin_class, column):
                column_func = getattr(admin_class, column)
                admin_class.instance = obj
                admin_class.request = request
                column_data = column_func()

        if column_data:
            row_ele += '<td>%s</td>' % column_data
        else:
            row_ele += '<td></td>'
        # row_ele += '<td>%s</td>' % column_data

    return mark_safe(row_ele)

@register.simple_tag
def render_page_ele(loop_counter,query_sets, filter_condition):
    filters = ''
    for k, v in filter_condition.items():
        filters += '&%s=%s' %(k, v)

    if loop_counter < 3 or loop_counter > query_sets.paginator.num_pages - 2:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' % (ele_class, loop_counter, filters, loop_counter)

        return mark_safe(ele)

    if abs(query_sets.number - loop_counter) <= 1:
        ele_class = ""
        if query_sets.number == loop_counter:
            ele_class = "active"
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>''' %(ele_class,loop_counter,filters, loop_counter)

        return mark_safe(ele)

    return ''

@register.simple_tag
def render_filter_ele(condition, admin_class, filter_condition):
    # select_ele = '''<select name='%s'><option value=''>-----</option>''' % condition
    select_ele = '''<select name='{filter_field}'><option value=''>-----</option>'''
    field_obj = admin_class.model._meta.get_field(condition)
    if field_obj.choices:
        selected = ''
        for choice_item in field_obj.choices:
            if filter_condition.get(condition) == str(choice_item[0]):
                selected = 'selected'
            select_ele += '''<option value='%s' %s> %s</option>''' %(choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ == 'ForeignKey':
        selected = ''
        for choice_item in field_obj.get_choices()[1:]:
            if filter_condition.get(condition) == str(choice_item[0]):
                selected = 'selected'
            select_ele += '''<option value='%s' %s> %s</option>''' % (choice_item[0], selected, choice_item[1])
            selected = ''

    if type(field_obj).__name__ in ('DateTimeField', 'DateField'):
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(['Yesterday', today_ele - timedelta(days=1)])
        date_els.append(['Last 7 Days', today_ele - timedelta(days=7)])
        date_els.append(['This Month', today_ele.replace(day=1)])
        date_els.append(['Last 30 Days', today_ele - timedelta(days=30)])
        date_els.append(['Last 90 Days', today_ele - timedelta(days=90)])
        date_els.append(['Last 180 Days', today_ele - timedelta(days=180)])
        date_els.append(['This Year', today_ele.replace(month=1, day=1)])
        date_els.append(['Last Year', today_ele - timedelta(days=365)])
        selected = ''
        for item in date_els:
            select_ele += '''<option value='%s' %s> %s</option>''' % (item[1], selected, item[0])

        filter_field_name = '%s__gte' % condition
    else:
        filter_field_name = condition

    select_ele += "</select>"
    select_ele = select_ele.format(filter_field=filter_field_name)
    return mark_safe(select_ele)


@register.simple_tag
def build_paginators(query_sets, filter_condition, previous_orderby, search_text):
    filters = ''
    for k, v in filter_condition.items():
        filters += '&%s=%s' % (k, v)
    page_btns = ''
    added_dot_ele = False
    for page_num in query_sets.paginator.page_range:
        if page_num < 3 or page_num > query_sets.paginator.num_pages - 2:
            ele_class = ""
            if query_sets.number == page_num:
                ele_class = "active"
            page_btns += '''<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>''' % (
            ele_class, page_num, filters, previous_orderby, search_text, page_num)
        elif abs(query_sets.number - page_num) <= 1:
            ele_class = ""
            if query_sets.number == page_num:
                ele_class = "active"
            page_btns += '''<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>''' % (
                ele_class, page_num, filters, previous_orderby, search_text, page_num)
            added_dot_ele = False
        else:
            if added_dot_ele == False:
                page_btns += '<li><a>...</a></li>'
                added_dot_ele = True

    return mark_safe(page_btns)

@register.simple_tag
def build_table_header_column(column, orderby_key, filter_condition, admin_class):
    filters = ''
    for k, v in filter_condition.items():
        filters += '&%s=%s' % (k, v)
    ele = '''<th><a href="?{filters}&o={orderby_key}">{column}</a></th>'''
    if orderby_key:
        if orderby_key.strip('-') == column:
            orderby_key = orderby_key
        else:
            orderby_key = column
    else:
        orderby_key = column

    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist as e:
        column_verbose_name = column
        ele = '''<th><a href="javascript:void(0)">{column}</a></th>'''.format(column=column_verbose_name)
        return mark_safe(ele)
    return mark_safe(ele.format(orderby_key=orderby_key, column=column_verbose_name, filters=filters))

@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_m2m_obj_list(admin_class, field, form_obj):
    field_obj = getattr(admin_class.model, field.name)
    all_obj_list = field_obj.rel.model.objects.all()

    if form_obj.instance.id:
        obj_instance_field = getattr(form_obj.instance, field.name)
        selected_obj_list = obj_instance_field.all()
    else:
        return all_obj_list

    standby_obj_list = []
    for obj in all_obj_list:
        if obj not in selected_obj_list:
            standby_obj_list.append(obj)

    return standby_obj_list


@register.simple_tag
def get_m2m_selected_obj_list(form_obj, field):
    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field.name)
        return field_obj.all()

@register.simple_tag
def print_obj_methods(obj):
    print('----------debug %s---------' % obj)
    print(dir(obj))

@register.simple_tag
def display_all_related_objs(objs):

    if objs:
        model_class = objs[0]._meta.model
        model_name = objs[0]._meta.model_name
        return mark_safe(recursive_related_objs_lookup(objs))

def recursive_related_objs_lookup(objs):
    ul_ele = "<ul>"
    for obj in objs:
        li_ele = '''<li>%s: %s</li>'''%(obj._meta.verbose_name, obj.__str__().strip('<>'))
        ul_ele += li_ele
        for m2m_field in obj._meta.local_many_to_many:
            sub_ul_ele = "<ul>"
            m2m_field_obj = getattr(obj, m2m_field.name)
            li_ele = ''
            for o in m2m_field_obj.select_related():
                li_ele += '''<li>%s: %s</li>''' % (m2m_field.verbose_name, o.__str__().strip('<>'))
            sub_ul_ele += li_ele
            sub_ul_ele += '</ul>'
            ul_ele += sub_ul_ele

        for related_obj in obj._meta.related_objects:
            if 'ManyToManyRel' in related_obj.__repr__():
                if hasattr(obj, related_obj.get_accessor_name()):
                    accessor_obj = getattr(obj, related_obj.get_accessor_name())

                    if hasattr(accessor_obj, 'select_related'):
                        target_objs = accessor_obj.select_related()
                    else:
                        target_objs = accessor_obj

                    sub_ul_ele = "<ul>"
                    for o in target_objs:
                        li_ele += '''<li>%s: %s</li>''' % (o._meta.verbose_name, o.__str__().strip('<>'))
                        sub_ul_ele += li_ele
                    sub_ul_ele += "</ul>"
                    ul_ele += sub_ul_ele

            elif hasattr(obj, related_obj.get_accessor_name()):
                accessor_obj = getattr(obj, related_obj.get_accessor_name())

                if hasattr(accessor_obj, 'select_related'):
                    target_objs = accessor_obj.select_related()
                else:
                    target_objs = accessor_obj

                if len(target_objs) > 0:
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes
    ul_ele += '</ul>'
    return ul_ele