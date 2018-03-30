from django.forms import forms, ModelForm
from django.forms import ValidationError
from crm import models

# An ModelForm Example:
class CustomerModelForm(ModelForm):
    class Meta:
        model = models.Customer
        fields = '__all__'

def create_model_form(request, admin_class, flag):

    def __new__(cls, *args, **kwargs):
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'
            field_obj.widget.attrs['maxlength'] = field_obj.max_length if hasattr(field_obj, 'max_length') else ''

            if flag:
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'

            if hasattr(admin_class, 'clean_%s' % field_name):
                field_class_func = getattr(admin_class, 'clean_%s' %field_name)
                setattr(cls, 'clean_%s' %field_name, field_class_func)
        return ModelForm.__new__(cls)

    def default_clean(self):
        print('running default_clean...')
        error_list = []
        if flag:
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)
                if hasattr(field_val, 'select_related'):
                    m2m_objs = getattr(field_val, "select_related")()
                    m2m_vals = [i[0] for i in m2m_objs.values_list('id')]
                    set_m2m_vals = set(m2m_vals)
                    set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                    if set_m2m_vals != set_m2m_vals_from_frontend:
                        # error_list.append(ValidationError(
                        #     ('Field %(field)s is readonly'),
                        #     code='invalid',
                        #     params={'field': field},
                        # ))
                        self.add_error(field, 'Read-Only Field!')
                    continue

                field_val_from_frontend = self.cleaned_data.get(field)
                if field_val != field_val_from_frontend:
                     error_list.append(ValidationError(
                        ('Field %(field)s is readonly, data should be %(val)s'),
                        code='invalid',
                        params={'field': field, 'val': field_val},
                    ))

            if admin_class.readonly_table:
                raise   ValidationError(
                            ('Table is readonly, cannot be modified or added'),
                            code='invalid',
                        )

            self.ValidationError = ValidationError
            response = admin_class.default_form_validation(self)
            if response:
                error_list.append(response)

            if error_list:
                raise ValidationError(error_list)

    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields

    attrs = {'Meta':Meta, '__new__':__new__, 'clean':default_clean}
    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)


    return _model_form_class