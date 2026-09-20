from django.urls import path

from main.views import (show_main, 
                        show_experience, 
                        show_education, 
                        show_projects, 
                        create_project, 
                        get_projects_json,
                        delete_project, 
                        show_experience_json,
                        show_edit_experience, 
                        create_experience, 
                        edit_experience, 
                        delete_experience,
                        show_edit_education,
                        create_education,
                        edit_education,
                        delete_education,
                        )
app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("projects/add/", create_project, name="create_project"),
    
    path('education/', show_education, name='show_education'),
    path('projects/', show_projects, name='show_projects'),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/",delete_project,name="delete_project"),

    path("experience/", show_experience, name="show_experience"),
    path("experience/edit/", show_edit_experience, name="show_edit_experience"),            
    path("experience/edit/form/", create_experience, name="create_experience"),             
    path("experience/edit/<uuid:experience_id>/form/", edit_experience, name="edit_experience"), 
    path("experience/delete/<uuid:experience_id>/", delete_experience, name="delete_experience"),
    path("experience/json/", show_experience_json, name="show_experience_json"),

    path('education/', show_education, name='show_education'),
    path('education/edit/', show_edit_education, name='show_edit_education'),
    path('education/create/', create_education, name='create_education'),
    path('education/edit/<uuid:education_id>/form/', edit_education, name='edit_education'),
    path('education/delete/<uuid:education_id>/', delete_education, name='delete_education'),
]