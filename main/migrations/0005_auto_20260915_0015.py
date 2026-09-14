from django.db import migrations

def sync_final_data(apps, schema_editor):
    Experience = apps.get_model('main', 'Experience')
    Education = apps.get_model('main', 'Education')

    Experience.objects.all().delete()
    Education.objects.all().delete()

    Experience.objects.create(
        title='Asisten Dosen Kalkulus 1',
        category='part-time',
        description='Membantu menilai, mengawas, serta membantu mengajari mahasiswa untuk memahami mata kuliah kalkulus 1.',
        ended_at=None,
    )

    Experience.objects.create(
        title='Staf Media Partner di COMPFEST',
        category='part-time',
        description='Menjadi penghubung antara COMPFEST dengan media partner.',
        ended_at=None,
    )

    Experience.objects.create(
        title='Staff Hubungan Masyarakat BEM Fasilkom UI',
        category='part-time',
        description='Bertanggung jawab mengatur media sosial BEM Fasilkom UI.',
        ended_at=None,
    )

    Education.objects.create(
        institution='Universitas Indonesia',
        degree='S1 Ilmu Komputer',
        start_year='2025',
        end_year='Present',
        description='Fakultas Ilmu Komputer, Universitas Indonesia.',
    )

    Education.objects.create(
        institution='SMAS Santo Thomas 1',
        degree='MIPA',
        start_year='2022',
        end_year='2025',
        description='Menyelesaikan pendidikan menengah atas dengan fokus sains dan matematika.',
    )

    Education.objects.create(
        institution='SMP RK Bintang Timur Pematang Siantar',
        degree='Sekolah Menengah Pertama',
        start_year='2019',
        end_year='2022',
        description='Menyelesaikan pendidikan menengah pertama.',
    )

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20260915_0005'), 
    ]

    operations = [
        migrations.RunPython(sync_final_data),
    ]