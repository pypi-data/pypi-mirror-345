import json
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand

MIGRATED_DATA_FILE = Path("migrated_data_file.json")

def get_all_subclasses(cls):
    subclasses = cls.__subclasses__()
    all_subclasses = []
    for subclass in subclasses:
        if not getattr(subclass._meta, 'abstract', False):
            all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


class Command(BaseCommand):
    help = "Generate a feature file with initial data"

    def handle(self, *args, **kwargs):
        from custom_base_django.models import BaseModelFiscalDelete as Model
        # from django.db.models import Model as Mo
        # print(Mo.__subclasses__())
        # ETLTask_etl_list_model = apps.get_model('etl_data', 'ETLTask_etl_list')
        # ETLTask_etl_list_model.migratable_data = True
        # ETLTask_etl_list_model.truncate_on_migrate_data = True
        # ETLData_pre_etls_model = apps.get_model('etl_data', 'ETLData_pre_etls')
        # ETLData_pre_etls_model.migratable_data = True
        # ETLData_pre_etls_model.truncate_on_migrate_data = True
        all_subclasses = get_all_subclasses(Model) #+ [ETLTask_etl_list_model, ETLData_pre_etls_model]
        migrated_data = dict()
        for cls in all_subclasses:
            meta = getattr(cls, "_meta", None)
            if getattr(cls, 'migratable_data', None):
                records = list(cls.objects.all().values())
                if not records:
                    continue
                app_label = meta.app_label
                model_name = meta.model_name
                if app_label not in migrated_data:
                    migrated_data[app_label] = {}
                migrated_data[app_label][model_name] = {"truncate": getattr(cls, "truncate_on_migrate_data", False),"records":records}

        migrated_data_file = MIGRATED_DATA_FILE
        with migrated_data_file.open("w", encoding="utf-8") as f:
            json.dump(migrated_data, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Feature data saved in {migrated_data_file}"))
