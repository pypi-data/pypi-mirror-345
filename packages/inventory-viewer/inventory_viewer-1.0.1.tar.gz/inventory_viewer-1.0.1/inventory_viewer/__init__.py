"""
project: IBT24/25, xkubec03
author: Viktor Kubec
file: _init__.py

brief:
This file defines the "inventory_viewer" plugin configuration for NetBox.
The plugin provides a tabular view of devices and modules stored in NetBox.
"""

from netbox.plugins import PluginConfig

class InventoryViewerConfig(PluginConfig):
    """
    Configuration class for the "Inventory Viewer" plugin.

    Extends the default NetBox PluginConfig to set metadata about this plugin,
    such as name, version, and a short description. The ready() method
    imports signal handlers, ensuring additional setup steps (like creating
    custom fields) can be triggered after migrations.
    """

    name = "inventory_viewer"
    verbose_name = "Inventory Viewer"
    description = "Plugin that shows NetBox devices and modules in tables."
    version = "1.0"
    author = "Viktor Kubec"
    author_email = "Viktor.Kubec@gmail.com"
    base_url = "inventory-viewer"

config = InventoryViewerConfig
