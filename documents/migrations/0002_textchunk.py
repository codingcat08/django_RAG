# Generated by Django 5.1.6 on 2025-02-26 17:31

import django.db.models.deletion
import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextChunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chunk_index', models.IntegerField()),
                ('text', models.TextField()),
                ('embedding', pgvector.django.vector.VectorField(dimensions=1536)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chunks', to='documents.document')),
            ],
            options={
                'indexes': [models.Index(fields=['document'], name='documents_t_documen_e9acde_idx')],
            },
        ),
    ]
