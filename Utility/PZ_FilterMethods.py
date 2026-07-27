# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def filter_zombie_injuries(self, context):
    addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    items = []
    items.append(('NONE', 'None', ''))
    for index, injury in enumerate(addon_prefs.pz_human_zombie_injuries):
        items.append((injury.name, injury.name, ''))
    return items