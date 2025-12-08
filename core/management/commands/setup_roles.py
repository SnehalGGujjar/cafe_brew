from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = "Create Employee group with limited admin access"

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="employee")
        # grant basic view/add change on orders and menu items
        app_models = [('orders','order'), ('orders','orderitem'), ('menu','item')]
        added = 0
        for app_label, model in app_models:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model)
                for codename in [f'view_{model}', f'change_{model}', f'add_{model}']:
                    try:
                        p = Permission.objects.get(content_type=ct, codename=codename)
                        group.permissions.add(p); added += 1
                    except Permission.DoesNotExist:
                        pass
            except ContentType.DoesNotExist:
                continue
        self.stdout.write(self.style.SUCCESS(f'Employee group ready. Permissions added: {added}'))
