# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def move_statmaps(apps, schema_editor):
    Image = apps.get_model("statmaps", "Image")
    StatisticMap = apps.get_model("statmaps", "StatisticMap")
    for image in Image.objects.all():
        statisticmap = StatisticMap(image_ptr_id=image.pk)
        statisticmap.__dict__.update(image.__dict__)
        statisticmap.save() # save first time
        statisticmap.__dict__.update(image.__dict__)
        statisticmap.tmp_map_type = image.map_type
        statisticmap.tmp_statistic_parameters = image.statistic_parameters
        statisticmap.tmp_smoothness_fwhm = image.smoothness_fwhm
        statisticmap.tmp_contrast_definition = image.contrast_definition
        statisticmap.tmp_contrast_definition_cogatlas = image.contrast_definition_cogatlas
        statisticmap.save()

class Migration(migrations.Migration):

    dependencies = [
        ('statmaps', '0003_collection_journal_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatisticMap',
            fields=[
                ('image_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='statmaps.Image')),
                ('tmp_map_type', models.CharField(help_text=b'Type of statistic that is the basis of the inference', max_length=200, verbose_name=b'Map type', choices=[(b'T', b'T map'), (b'Z', b'Z map'), (b'F', b'F map'), (b'X2', b'Chi squared map'), (b'P', b'P map (given null hypothesis)'), (b'Other', b'Other')])),
                ('tmp_statistic_parameters', models.FloatField(help_text=b'Parameters of the null distribution of the test statisic, typically degrees of freedom (should be clear from the test statistic what these are).', null=True, verbose_name=b'Statistic parameters', blank=True)),
                ('tmp_smoothness_fwhm', models.FloatField(help_text=b'Noise smoothness for statistical inference; this is the estimated smoothness used with Random Field Theory or a simulation-based inference method.', null=True, verbose_name=b'Smoothness FWHM', blank=True)),
                ('tmp_contrast_definition', models.CharField(help_text=b"Exactly what terms are subtracted from what? Define these in terms of task or stimulus conditions (e.g., 'one-back task with objects versus zero-back task with objects') instead of underlying psychological concepts (e.g., 'working memory').", max_length=200, null=True, verbose_name=b'Contrast definition', blank=True)),
                ('tmp_contrast_definition_cogatlas', models.CharField(help_text=b"Link to <a href='http://www.cognitiveatlas.org/'>Cognitive Atlas</a> definition of this contrast", max_length=200, null=True, verbose_name=b'Cognitive Atlas definition', blank=True)),
            ],
            options={
            },
            bases=('statmaps.image',),
        ),
#         migrations.RunPython(move_statmaps),
#         migrations.RemoveField(
#             model_name='image',
#             name='contrast_definition',
#         ),
#         migrations.RemoveField(
#             model_name='image',
#             name='contrast_definition_cogatlas',
#         ),
#         migrations.RemoveField(
#             model_name='image',
#             name='map_type',
#         ),
#         migrations.RemoveField(
#             model_name='image',
#             name='smoothness_fwhm',
#         ),
#         migrations.RemoveField(
#             model_name='image',
#             name='statistic_parameters',
#         ),
#                   
#         migrations.RenameField(
#             model_name='statisticmap',
#             old_name='tmp_contrast_definition',
#             new_name='contrast_definition',
#         ),
#         migrations.RenameField(
#             model_name='statisticmap',
#             old_name='tmp_contrast_definition_cogatlas',
#             new_name='contrast_definition_cogatlas'
#         ),
#         migrations.RenameField(
#             model_name='statisticmap',
#             old_name='tmp_map_type',
#             new_name='map_type'
#         ),
#         migrations.RenameField(
#             model_name='statisticmap',
#             old_name='tmp_smoothness_fwhm',
#             new_name='smoothness_fwhm'
#         ),
#         migrations.RenameField(
#             model_name='statisticmap',
#             old_name='tmp_statistic_parameters',
#             new_name='statistic_parameters'
#         ),
    ]
