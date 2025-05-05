from django.apps import AppConfig
from django.conf import settings

from . import app_settings as defaults

# Set some app default settings
for name in dir(defaults):
    if name.isupper() and not hasattr(settings, name):
        setattr(settings, name, getattr(defaults, name))


class NEMOBillingConfig(AppConfig):
    name = "NEMO_billing"
    verbose_name = "Billing"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from NEMO.plugins.utils import check_extra_dependencies

        check_extra_dependencies(self.name, ["NEMO", "NEMO-CE"])
