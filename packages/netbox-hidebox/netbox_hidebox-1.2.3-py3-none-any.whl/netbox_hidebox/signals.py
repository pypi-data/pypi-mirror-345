from django import forms
from django.conf import settings


def hide_model_form_fields(form, model, user=None):
    """
    Dynamically hide fields based on user groups.
    Can work with both class-based forms and form instances.

    Args:
        form (forms.ModelForm or Type[forms.ModelForm]): A form instance or class to modify.
        model (models.Model): The model class associated with the form.
        user (User, optional): The current user for whom the form is being customized.
    """
    hidden_fields_config = getattr(settings, 'PLUGINS_CONFIG', {}).get('netbox_hidebox', {}).get('HIDDEN_FIELDS', {})
    model_identifier = f"{model._meta.app_label}.{model._meta.model_name}"

    if model_identifier in hidden_fields_config:
        field_groups = hidden_fields_config[model_identifier]

        if isinstance(form, type) and issubclass(form, forms.ModelForm):
            base_fields = form.base_fields
        else:
            base_fields = form.fields

        for field_name, excluded_groups in field_groups.items():
            if field_name in base_fields:
                field = base_fields[field_name]

                should_hide = True

                if excluded_groups and user:
                    should_hide = not any(
                        user.groups.filter(name=group).exists()
                        for group in excluded_groups
                    )

                if should_hide:
                    field.widget = forms.HiddenInput()
                    field.required = False
                    field.label = ''
                    field.help_text = ''

    return form
