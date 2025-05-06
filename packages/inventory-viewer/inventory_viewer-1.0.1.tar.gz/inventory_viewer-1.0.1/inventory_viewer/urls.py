"""
project: IBT24/25, xkubec03
author: Viktor Kubec
file: urls.py

brief:
This file defines routing for each plugin view.
"""
from django.urls import path
from .views import ModulyListView

urlpatterns = [
    path("", ModulyListView.as_view(), name="moduly_list"),
]
