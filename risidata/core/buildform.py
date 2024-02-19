from django import forms
from django.contrib.admin import helpers
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from core.utils import label_for_field, help_text_for_field


class SiteForm(helpers.AdminForm):
    def __iter__(self):
        for name, options in self.fieldsets:
            yield Fieldset(
                self.form,
                name,
                readonly_fields=self.readonly_fields,
                model_admin=self.model_admin,
                **options,
            )


class Fieldset(helpers.Fieldset):

    @property
    def media(self):
        if "collapse" in self.classes:
            return forms.Media(js=["contract/js/collapse.js"])
        return forms.Media()

    def __iter__(self):
        for field in self.fields:
            yield Fieldline(
                self.form,
                field,
                self.readonly_fields,
                model_admin=self.model_admin,
            )


class Fieldline(helpers.Fieldline):
    def __iter__(self):
        for i, field in enumerate(self.fields):
            if field in self.readonly_fields:
                yield AdminReadonlyField(
                    self.form,
                    field,
                    is_first=(i == 0),
                    model_admin=self.model_admin,
                )
            else:
                yield helpers.AdminField(self.form, field, is_first=(i == 0))


class AdminReadonlyField(helpers.AdminReadonlyField):
    def __init__(self, form, field, is_first, model_admin=None):
        from django.db.models.fields.related import (
            ForeignObjectRel,
            OneToOneField,
        )

        super().__init__(form, field, is_first, model_admin)
        label = label_for_field(field, form._meta.model, form=form)
        help_text = help_text_for_field(field, form._meta.model, form)
        obj = form.instance
        try:
            f = obj._meta.get_field(field)
            if isinstance(f.remote_field, (ForeignObjectRel, OneToOneField)):
                value = getattr(obj, f.name).pk
            else:
                value = getattr(obj, field)
        except AttributeError:
            value = ''
        except FieldDoesNotExist:
            value = str(obj)

        self.field.update(label=label, help_text=help_text, value=value)

    def get_admin_url(self, remote_field, remote_obj):
        return str(remote_obj)

    def contents(self):
        result_repr = super().contents()
        if (
                not result_repr
                or result_repr == self.empty_value_display
                # or result_repr == '0,00'
        ):
            initial = self.form.fields[self.field['field']].initial
            result_repr = initial if initial is not None else result_repr

        return conditional_escape(result_repr)

    def errors(self):
        e = mark_safe(self.form[self.field['field']].errors.as_ul())
        return e
