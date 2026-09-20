from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from main.forms import ProjectForm , ExperienceForm
from main.models import Experience, Education, Project 
from django.shortcuts import get_object_or_404, redirect, render


def show_main(request):
    context = {
        "name": "Rafael Darius Sagala",
        "npm": "2506584275",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Computer Science undergraduate at Universitas Indonesia with a keen focus on financial markets, equity analysis, and business strategy. Proven track record in competitive stock trading and digital initiatives, passionate about bridging quantitative technology with capital market insights. "
        ),
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


def show_edit_experience(request):
    experiences = Experience.objects.all()
    context = {
        "name": "Rafael Darius Sagala",
        "experience_list": experiences,
    }
    return render(request, "edit_experience.html", context)


def create_experience(request):
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


def edit_experience(request, experience_id):
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


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience.delete()
    messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_edit_experience")

def show_education(request):
    context = {
        "name": "Rafael Darius Sagala",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def create_project(request):
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

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Rafael Darius Sagala",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")