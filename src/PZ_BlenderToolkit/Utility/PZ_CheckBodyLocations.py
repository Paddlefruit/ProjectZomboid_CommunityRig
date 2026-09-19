# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def check_body_location_eligibility(self, context):

    # The collection of equipped clothing items
    equipped_items = context.active_object.pz_equipped_clothing_items

    # The collection of used locations on the rig
    used_body_locations = context.active_object.pz_used_body_locations

    # Loop through all used body locations and all used clothing items to see if they still match
    true_used_locations = []

    for item in equipped_items:
        true_used_locations.append(item.data.body_location)

    for location in used_body_locations:
        if location.name not in true_used_locations:
            used_body_locations.remove(used_body_locations.find(location.name))

def check_body_location_properties(self, context, added_locations):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    # The collection of body location references
    all_body_locations = addon_data.pz_body_locations

    # The collection of used locations on the rig
    used_body_locations = context.active_object.pz_used_body_locations

    # The collection of equipped clothing items
    equipped_items = context.active_object.pz_equipped_clothing_items

    use_alt_model = False
    hide_model = False

    for item in equipped_items:
        item_location = all_body_locations.get(item.data.body_location)

        for used_location in used_body_locations:
            for hide_location in item_location.properties.hide_locations:
                if used_location.name == hide_location.name:
                    hide_model = True
            for alt_location in item_location.properties.alt_locations:
                if used_location.name == alt_location.name:
                    use_alt_model = True

        item.hide_model = hide_model
        item.use_alt_model = use_alt_model