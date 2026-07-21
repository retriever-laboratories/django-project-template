# forms
from django_htmx_base.forms import BaseModelForm as Form

# enums
from core.form_enums import FormAttribute, FormClass


class BaseModelForm(Form):
    text_class = FormClass.TEXT
    textarea_class = FormClass.TEXTAREA
    select_class = FormClass.SELECT
    checkbox_class = FormClass.CHECKBOX

    text_attrs = FormAttribute.TEXT
    textarea_attrs = FormAttribute.TEXTAREA
    select_attrs = FormAttribute.SELECT
    checkbox_attrs = FormAttribute.CHECKBOX
