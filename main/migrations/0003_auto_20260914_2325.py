from django.db import migrations

def populate_manual_data(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Education = apps.get_model('main', 'Education')

    Experience.objects.get_or_create(
        title='Staff Media Partner di COMPFEST',
        defaults={
            'category': 'part-time',
            'description': 'Menjalin dan mengelola kemitraan strategis dengan puluhan media partner berskala nasional untuk memperluas jangkauan publikasi rangkaian acara COMPFEST.',
            'ended_at': None,
        }
    )

    Experience.objects.get_or_create(
        title='Intern Divisi Marketing and Communications di RISTEK',
        defaults={
            'category': 'internship',
            'description': 'Bertanggung jawab dalam merancang strategi komunikasi, publikasi event, dan kolaborasi media.',
            'ended_at': None,
        }
    )

    Experience.objects.get_or_create(
        title='Intern BEM Fasilkom UI Divisi Seni dan Budaya',
        defaults={
            'category': 'internship',
            'description': 'Menginisiasi serta mengeksekusi berbagai program apresiasi seni dan kegiatan kebudayaan mahasiswa.',
            'ended_at': None,
        }
    )

    Education.objects.get_or_create(
        institution='Universitas Indonesia',
        defaults={
            'degree': 'S1 Ilmu Komputer / Sistem Informasi',
            'start_year': '2025',
            'end_year': 'Present',
            'description': 'Fakultas Ilmu Komputer, Universitas Indonesia.',
        }
    )

    Education.objects.get_or_create(
        institution='SMAS Santo Thomas 1',
        defaults={
            'degree': 'Sekolah Menengah Atas (MIPA)',
            'start_year': '2022',
            'end_year': '2025',
            'description': 'Menyelesaikan pendidikan tingkat menengah atas dengan fokus pada bidang sains dan matematika.',
        }
    )

def reverse_manual_data(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_education'), 
    ]

    operations = [
        migrations.RunPython(populate_manual_data, reverse_code=reverse_manual_data),
    ]