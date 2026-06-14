import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(db_comment='企業ID', default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_comment='企業名', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
            ],
            options={
                'verbose_name': 'company',
                'verbose_name_plural': 'companies',
                'db_table': 'companies',
                'db_table_comment': '企業テーブル',
            },
        ),
    ]
