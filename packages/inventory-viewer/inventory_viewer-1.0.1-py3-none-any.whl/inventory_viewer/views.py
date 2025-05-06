"""
project: IBT24/25, xkubec03
author: Viktor Kubec
file: views.py

brief:
Provides a view class to display NetBox modules grouped by their module type.
Utilizes a custom Django Tables2 table (ModulyCustomTable) to format and render
the module data (e.g., SN, date, asset tag, location, cable connections, notes).
"""

from django.shortcuts import render
from django.views import View
from dcim.models import Module
from .tables import ModulyCustomTable

class ModulyListView(View):
    """
    A class-based view that gathers all Module objects from NetBox,
    groups them by their ModuleType, and renders separate tables for each type.

    The view uses:
        - ModulyCustomTable: A Django Tables2 table for module columns and formatting.
        - inventory_viewer/inventory_view.html: The template that displays multiple
        tables keyed by the module's type (typ_obj).
    """

    template_name = "inventory_viewer/inventory_view.html"

    def get(self, request):
        """
        Handles GET requests to display a consolidated page of module data,
        grouped by module_type. Each group is passed to ModulyCustomTable,
        and all tables are delivered to the template through the 'tabulky' context.
        """
        # Retrieve all modules
        moduly_qs = Module.objects.all()

        # Group modules by their module_type
        moduly_podle_typu = {}
        for modul in moduly_qs:
            typ = modul.module_type
            if typ not in moduly_podle_typu:
                moduly_podle_typu[typ] = []
            moduly_podle_typu[typ].append(modul)

        # For each module type, create a Django Tables2 table
        tabulky = {}
        for typ_obj, seznam_modulu in moduly_podle_typu.items():
            tabulky[typ_obj] = ModulyCustomTable(seznam_modulu)

        # Render the result
        context = {
            "tabulky": tabulky
        }
        return render(request, self.template_name, context)
