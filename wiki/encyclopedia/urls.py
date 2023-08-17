from django.urls import path

from . import views

app_name='encyclopedia'

urlpatterns = [
    path("add-entry", views.edit, name="add", kwargs={"title": None}),
    path("edit-entry-<str:title>", views.edit, name="edit"),
    path("<str:title>", views.entry, name="entry"),
    path("", views.index, name="index")
]
