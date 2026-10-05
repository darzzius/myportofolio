import datetime
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from main.forms import ProjectForm , ExperienceForm, EducationForm
from main.models import Experience, Education, Project 
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required  # Tambahkan baris ini
from django.core.exceptions import PermissionDenied        # Tambahkan baris ini
from django.views.decorators.http import require_POST

def is_in_editor_group(user):
    return user.is_authenticated and user.groups.filter(name="Editor").exists()

def get_user_role_context(user):
    """Mengembalikan dictionary context peran pengguna untuk template."""
    return {
        "is_editor": is_in_editor_group(user),
        "is_owner": user.is_authenticated and user.is_superuser,
    }

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Rafael Darius Sagala",
        "npm": "2506584275",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Computer Science undergraduate at Universitas Indonesia with a keen focus on financial markets, equity analysis, and business strategy. Proven track record in competitive stock trading and digital initiatives, passionate about bridging quantitative technology with capital market insights. "
        ),
        "last_login": last_login,
        **get_user_role_context(request.user),
    }
    return render(request, "index.html", context)


def show_experience_json(request):
    experiences = Experience.objects.all()
    return HttpResponse(serializers.serialize("json", experiences), content_type="application/json")

def show_experience(request):
    experiences = Experience.objects.all()
    context = {
        "name": "Rafael Darius Sagala",
        "experience_list": experiences,
    }
    return render(request, "experience.html", context)

@login_required(login_url="/login/")
@require_POST
def toggle_star_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    if request.user in education.starred_by.all():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)
    
    return redirect("main:show_education")

@login_required(login_url="/login/")
def show_edit_experience(request):
    # Dua baris berikut yang ditambahkan pada langkah ini.
        # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
        # kalau bukan, hentikan permintaannya dengan 403.
    if not (request.user.is_superuser or is_in_editor_group(request.user)):
        raise PermissionDenied
    
    experiences = Experience.objects.all()
    context = {
        "name": "Rafael Darius Sagala",
        "experience_list": experiences,
    }
    return render(request, "edit_experience.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_edit_experience")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def edit_experience(request, experience_id):
    if not (request.user.is_superuser or is_in_editor_group(request.user)):
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_edit_experience")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_edit_experience")

def get_education_json(request):
    search_query = request.GET.get("q", "").strip()
    educations = Education.objects.prefetch_related("starred_by").all()

    if search_query:
        educations = educations.filter(
            institution__icontains=search_query
        ) | educations.filter(degree__icontains=search_query)

    # Urutkan berdasarkan tahun terbaru
    educations = educations.order_by("-start_year")

    data = []
    for edu in educations:
        starred_users = edu.starred_by.all()
        is_starred = (
            request.user in starred_users if request.user.is_authenticated else False
        )
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(edu.id),
            "fields": {
                "institution": edu.institution,
                "degree": edu.degree,
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "description": edu.description,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            },
        })

    return JsonResponse(data, safe=False)

def show_education(request):
    search_query = request.GET.get("q", "").strip()
    context = {
        "name": "Rafael Darius Sagala",
        "search_query": search_query,
        "form": EducationForm(), 
        **get_user_role_context(request.user),
    }
    return render(request, "education.html", context)

@login_required(login_url="/login/")
def show_edit_education(request):
    if not (request.user.is_superuser or is_in_editor_group(request.user)):
        raise PermissionDenied
    
    educations = Education.objects.all()
    context = {
        "name": "Rafael Darius Sagala",
        "education_list": educations,
    }
    return render(request, "edit_education.html", context)

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil ditambahkan!")
        return redirect("main:show_edit_education")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def edit_education(request, education_id):
    if not (request.user.is_superuser or is_in_editor_group(request.user)):
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_edit_education")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
        "education": education,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
            raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)
    education.delete()
    messages.success(request, "Riwayat pendidikan berhasil dihapus!")
    return redirect("main:show_edit_education")

@login_required(login_url="/login/")
def create_project(request):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
    
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def edit_project(request, project_id):
    if not (request.user.is_superuser or is_in_editor_group(request.user)):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Rafael Darius Sagala",
        "form": form,
        "project": project,
        **get_user_role_context(request.user),
    }
    return render(request, "projects_form.html", context)


def show_projects(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Burhan",
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Konstruksi data JSON secara manual agar bisa menyisipkan logika Star
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    # Dua baris berikut yang ditambahkan pada langkah ini.
    # Cek apakah akun yang sedang login adalah superuser (admin/kamu);
    # kalau bukan, hentikan permintaannya dengan 403.
    if not request.user.is_superuser:
        raise PermissionDenied
     
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Darius",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Darius",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

@require_POST
def create_education_ajax(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        return JsonResponse(
            {
                "message": (
                    "403 Forbidden: Hanya pemilik portofolio yang dapat menambahkan"
                    " data pendidikan."
                )
            },
            status=403,
        )

    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {
                "message": "Riwayat pendidikan berhasil ditambahkan!",
                "pk": str(education.id),
            },
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)