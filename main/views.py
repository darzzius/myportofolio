from django.shortcuts import render

from main.models import Experience


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


def show_experience(request):
    context = {
        "name": "Rafael Darius Sagala",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)
