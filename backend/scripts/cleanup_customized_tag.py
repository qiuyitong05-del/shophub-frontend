import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop_app.models import Tag


def cleanup_customized_tag():
    keep_name = 'customized'
    remove_names = ['可定制的']

    keep_tag, _ = Tag.objects.get_or_create(name=keep_name)

    removed = 0
    for n in remove_names:
        removed += Tag.objects.filter(name=n).delete()[0]

    print(f"Kept tag: {keep_tag.name}")
    print(f"Removed tags: {removed}")


if __name__ == '__main__':
    cleanup_customized_tag()
