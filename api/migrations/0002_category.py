import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_company'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_comment='カテゴリ名', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_comment='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, db_comment='更新日時')),
                ('company', models.ForeignKey(db_comment='企業ID', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='api.company')),
                ('parent_category', models.ForeignKey(db_comment='親カテゴリID', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='api.category')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'db_table': 'categories',
                'db_table_comment': 'カテゴリテーブル',
                'indexes': [models.Index(fields=['company', 'name'], name='categories_company_18f426_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('company', 'name'), name='unique_company_category_combination'),
        ),
    ]
