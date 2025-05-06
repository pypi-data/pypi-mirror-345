"""
project: IBT24/25, xkubec03
author: Viktor Kubec
file: navigation.py

brief:
This file defines links in the plugin section for easy access to the plugin functions.
"""
from netbox.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:inventory_viewer:moduly_list',
        link_text='Inventory View',
    ),
)
