import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

MIGRATED_DATA_FILE = Path("migrated_data_file.json")


# تابع برای بارگذاری داده‌ها از فایل JSON
def load_migrated_data():
    if MIGRATED_DATA_FILE.exists():
        with MIGRATED_DATA_FILE.open("r", encoding="utf-8") as f:
            migrated_data = json.load(f)
        return migrated_data
    else:
        return None


# تابع برای بروزرسانی یا ایجاد رکوردها
def update_or_create_records(model, records):
    for record in records:
        obj, created = model.objects.update_or_create(
            id=record.get("id"), defaults=record
        )


def reset_sequence(model):
    """
    تنظیم مجدد sequence ID به بالاترین مقدار id موجود
    """
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT setval(pg_get_serial_sequence('{model._meta.db_table}', 'id'), max(id)) FROM {model._meta.db_table};"
        )


def truncate_table(model):
    """
    پاک‌سازی (truncate) جدول برای جلوگیری از رکوردهای تکراری
    """
    with connection.cursor() as cursor:
        cursor.execute(f"TRUNCATE TABLE {model._meta.db_table} CASCADE;")


class Command(BaseCommand):
    help = "Load and update records from a JSON file into the database"

    def handle(self, *args, **kwargs):
        # بارگذاری داده‌ها از فایل JSON
        migrated_data = load_migrated_data()

        if migrated_data:
            # پردازش هر اپلیکیشن و مدل
            for app_label, models in migrated_data.items():
                for model_name, model_data in models.items():
                    # دریافت داده‌های truncate و رکوردها
                    truncate = model_data.get('truncate', False)
                    records = model_data.get('records', [])

                    # بارگذاری مدل از اپلیکیشن
                    try:
                        model = apps.get_model(app_label, model_name)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing model {model_name} in app {app_label}: {str(e)}"))


                    # اگر truncate فعال است، جدول پاک‌سازی می‌شود
                    if truncate:
                        self.stdout.write(self.style.NOTICE(f"Truncating table: {model._meta.db_table}"))
                        truncate_table(model)

                    # بروزرسانی یا ایجاد رکوردها
                    if records:
                        self.stdout.write(self.style.NOTICE(f"Updating or creating records for {model._meta.db_table}"))
                        update_or_create_records(model, records)

                        # تنظیم مجدد sequence برای جلوگیری از خطای تکرار id
                        self.stdout.write(self.style.NOTICE(f"Resetting sequence for {model._meta.db_table}"))
                        reset_sequence(model)

            self.stdout.write(self.style.SUCCESS(f"Data loaded and updated successfully!"))
        else:
            self.stdout.write(self.style.ERROR(f"Migration file not found: {MIGRATED_DATA_FILE}"))
