from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        try:
            from django.contrib.auth.models import User

            if not User.objects.filter(username='manas28').exists():
                User.objects.create_superuser(
                    'manas28',
                    'mayank.manas.28012gmail.com',
                    'sanam@82'
                )
        except:
            pass