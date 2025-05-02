from netbox.plugins import PluginConfig
from .version import __version__
import logging

logger = logging.getLogger('netbox.netbox_hidebox')


class NetBoxHideBoxConfig(PluginConfig):
    name = 'netbox_hidebox'
    verbose_name = 'NetBox HideBox'
    description = 'Hide Fields of any Form'
    version = __version__
    author = 'Sofien Aouni'
    author_email = 'contact@sofien.meme'
    base_url = ''
    required_settings = ['HIDDEN_FIELDS']
    min_version = '4.3.0'

    def ready(self):
        from netbox.forms import NetBoxModelForm
        from .signals import hide_model_form_fields
        from .middleware import get_current_request

        original_init = NetBoxModelForm.__init__

        def patched_init(self, *args, **kwargs):
            user = None
            try:
                current_request = get_current_request()
                if current_request:
                    user = current_request.user
                elif 'request' in kwargs:
                    user = kwargs['request'].user
                elif hasattr(self, 'context') and 'request' in self.context:
                    user = self.context['request'].user
                elif 'initial' in kwargs and 'request' in kwargs['initial']:
                    user = kwargs['initial']['request'].user


            except Exception as e:
                logger.error(f"Error extracting user: {e}")

            original_init(self, *args, **kwargs)
            hide_model_form_fields(self, self._meta.model, user)

        NetBoxModelForm.__init__ = patched_init


config = NetBoxHideBoxConfig
