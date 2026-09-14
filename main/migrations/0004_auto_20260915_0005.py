from django.db import migrations

def update_and_add_data(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Education = apps.get_model('main', 'Education')

    Experience.objects.update_or_create(
        title='Asisten Dosen Kalkulus 1',
        defaults={
            'category': 'part-time',
            'description': 'Membantu menilai, mengawas, serta membantu mengajari mahasiswa untuk memahami mata kuliah kalkulus 1.',
            'ended_at': None, 
        }
    )

    Experience.objects.update_or_create(
        title='Staf Media Partner di COMPFEST',
        defaults={
            'category': 'part-time',
            'description': 'Menjadi penghubung antara COMPFEST dengan media partner.',
            'ended_at': None, 
        }
    )

    Experience.objects.get_or_create(
        title='Staff Hubungan Masyarakat BEM Fasilkom UI',
        defaults={
            'category': 'part-time',
            'description': 'BErtanggung jawab mengatur media sosial BEM Fasilkom UI.',
            'ended_at': None,
        }
    )

    Education.objects.get_or_create(
        institution='Universitas Indonesia',
        defaults={
            'degree': 'S1 Ilmu Komputer',
            'start_year': '2025',
            'end_year': 'Present',
            'description': 'Fakultas Ilmu Komputer, Universitas Indonesia.',
        }
    )

    Education.objects.get_or_create(
        institution='SMAS Santo Thomas 1',
        defaults={
            'degree': 'MIPA',
            'start_year': '2022',
            'end_year': '2025',
            'description': 'Menyelesaikan pendidikan menengah atas dengan fokus sains dan matematika.',
        }
    )

    Education.objects.get_or_create(
            institution='SSMP RK Bintang Timur Pematang Siantar',
            defaults={
                'degree': '',
                'start_year': '2019',
                'end_year': '2022',
                'description': 'Menyelesaikan pendidikan menengah pertama.',
            }
        )

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20260914_2325'), # Bergantung pada migrasi 0003
    ]

    operations = [
        migrations.RunPython(update_and_add_data),
    ]