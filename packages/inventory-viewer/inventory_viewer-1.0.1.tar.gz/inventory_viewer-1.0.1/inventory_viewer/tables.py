"""
project: IBT24/25, xkubec03
author: Viktor Kubec
file: tables.py

brief:
Defines a custom Django Tables2 table for displaying NetBox Module objects.
This table shows columns like SN, Datum, Ev. č., Umístění, Propoj, Poznámka,
and Měřicí bod (drawn from standard model fields or custom fields). It also
includes logic to format cable connections in a "Device/Port <-> Device/Port"
style when modules are cabled to other components.
"""

import django_tables2 as tables
from dcim.models import Module
from django.contrib.contenttypes.models import ContentType
from dcim.models import Interface as DeviceInterface, FrontPort, RearPort
from virtualization.models import VMInterface

class ModulyCustomTable(tables.Table):
    """
    A specialized table class for displaying Module objects with custom columns.

    Columns:
        - sn (SN): Serial number of the module
        - datum (Datum): Year introduced, taken from a custom field ("rok_zavedeni")
        - ev_cislo (Ev. č.): The module's asset tag
        - umisteni (Umístění): Derived from the module's related device (site, location, device name)
        - propojeni (Propoj): Shows cable connections to other interfaces/ports in a
        "Device/Port <-> Device/Port" format by retrieving the CableTerminations
        - poznamka (Poznámka): The module's comment field
        - merici_bod (Měřicí bod): Custom field ("merici_bod") for measurement point identification

    This table uses table attributes to limit width expansion and relies on
    Django Tables2's custom rendering methods (render_* functions) to produce
    user-friendly output in each column.
    """

    sn = tables.Column(
        accessor="serial",
        verbose_name="SN",
    )
    datum = tables.Column(
        verbose_name="Datum",
        empty_values=()
    )
    ev_cislo = tables.Column(
        accessor="asset_tag",
        verbose_name="Ev. č."
    )
    umisteni = tables.Column(
        verbose_name="Umístění",
        empty_values=()
    )
    propojeni = tables.Column(
        verbose_name="Propoj",
        empty_values=()
    )
    poznamka = tables.Column(
        accessor="comments",
        verbose_name="Poznámka",
    )
    merici_bod = tables.Column(
        verbose_name="Měřicí bod",
        empty_values=()
    )

    class Meta:
        model = Module
        fields = ()
        attrs = {
            "class": "table table-striped table-hover",
            "style": "width: auto; table-layout: auto;"
        }

    def render_datum(self, record):
        """
        Retrieve the 'rok_zavedeni' custom field from the Module's custom_field_data.
        If absent, return an empty string.
        """
        cf_data = record.custom_field_data or {}
        return cf_data.get("rok_zavedeni", "")

    def render_umisteni(self, record):
        """
        Build a string that combines site, location, and the device name in the format:
          "<site> <location> : <device>"
        Returns an empty string if no device is associated.
        """
        device = record.device
        if not device:
            return ""
        site_name = device.site.name if device.site else ""
        location_name = device.location.name if device.location else ""
        if site_name and location_name:
            return f"{site_name} {location_name} : {device.name}"
        elif site_name:
            return f"{site_name} : {device.name}"
        else:
            return device.name

    def render_propojeni(self, record):
        """
        Identify cables connecting ports (front, rear, and interfaces) on this module.
        For each cable, gather its CableTerminations, resolve the real endpoints (e.g.,
        a device interface, front port, VM interface, etc.), and produce a formatted
        string, e.g.:
          "DeviceA/PortA <-> DeviceB/PortB"
        If multiple cables are found, they are joined with "; ".
        """
        cables = set()
        device = record.device
        print(device)
        if device:
            port_collections = [
                device.frontports.filter(module=record),
                device.rearports.filter(module=record),
                device.interfaces.filter(module=record),
            ]
            for ports in port_collections:
                for port in ports:
                    if port.cable:
                        cables.add(port.cable)

        results = []

        def describe_real_term(real_term):
            """
            Convert a real termination object (Interface, VMInterface, FrontPort, RearPort) into
            a string "DeviceName/PortName" or a suitable fallback if device/VM is missing.
            """
            if isinstance(real_term, DeviceInterface):
                if real_term.device:
                    return f"{real_term.device.name}/{real_term.name}"
                return f"(No device)/{real_term.name}"
            if isinstance(real_term, VMInterface):
                if real_term.virtual_machine:
                    return f"{real_term.virtual_machine.name}/{real_term.name}"
                return f"(No VM)/{real_term.name}"
            if isinstance(real_term, (FrontPort, RearPort)):
                if real_term.device:
                    return f"{real_term.device.name}/{real_term.name}"
                return f"(Port no device)/{real_term.name}"
            return str(real_term)
        print(cables)

        for cable in cables:
            # Load every termination (A, B, …) linked to this cable
            endpoints = list(cable.terminations.all())

            # Skip cables with zero or more than two terminations (invalid cases)
            if len(endpoints) == 0 or len(endpoints) > 2:
                continue

            real_term_objs = []
            for cterm in endpoints:
                ct = cterm.termination_type
                obj_id = cterm.termination_id
                # Resolve the concrete termination object (Interface, VMInterface, FrontPort, RearPort)
                real_term_objs.append(ct.get_object_for_this_type(id=obj_id))

            # --- Build the human-readable description --------------------------
            if len(real_term_objs) == 2:
                desc_a = describe_real_term(real_term_objs[0])
                desc_b = describe_real_term(real_term_objs[1])
                results.append(f"{desc_a} <-> {desc_b}")

            elif len(real_term_objs) == 1:
                # Only one side present; mark the opposite side as unconnected
                desc_a = describe_real_term(real_term_objs[0])
                results.append(f"{desc_a} <-> (nezapojeno)")   # adjust wording if needed

            # Return a single string with semicolons between individual cable descriptions
            return "; ".join(results) if results else ""

    def render_merici_bod(self, record):
        """
        Retrieve the 'merici_bod' custom field from the Module's custom_field_data.
        If absent, return an empty string.
        """
        cf_data = record.custom_field_data or {}
        return cf_data.get("merici_bod", "")
