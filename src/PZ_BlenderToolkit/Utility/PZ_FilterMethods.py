# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def filter_zombie_injuries(self, context):
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    items = []
    items.append(('NONE', 'None', ''))
    for index, injury in enumerate(addon_data.pz_zombie_injury_references):
        items.append((injury.name, injury.name, ''))
    return items