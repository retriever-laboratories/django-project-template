# forms
from django_htmx_base.forms import BaseModelForm as Form

# enums
from core.form_enums import FormClass
from core.form_enums import FormAttribute


class BaseModelForm(Form):
    text_class = FormClass.TEXT 
    textarea_class = ""
    select_class = ""
    checkbox_class = ""

    text_attrs = FormAttribute.TEXT
    textarea_attrs = {}
    select_attrs = {}
    checkbox_attrs = {}
