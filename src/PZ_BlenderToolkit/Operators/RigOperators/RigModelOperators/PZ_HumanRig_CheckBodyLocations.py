# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty

class PZ_CheckBodyLocations(Operator):
    bl_idname = "zomboid.check_body_locations"
    bl_label = "Check Body Locations"

    clothing_item_added: StringProperty()

    count_self: BoolProperty(
        default=True
    )

    def execute(self, context):
        # The addon preferences and data
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        # All known clothing items
        clothing_items = addon_prefs.pz_human_clothing_item_references

        # # The model properties of the rig
        #model_prefs = context.active_object.pz_human_props

        # # The clothing item collections on the rig
        # clothing_textures = context.active_object.pz_human_body_texture_slots
        # clothing_models = context.active_object.pz_clothing_models
        # accessory_models = context.active_object.pz_accessory_models

        # The used body locations on the rig
        used_locs = context.active_object.pz_used_body_locations

        # Get the clothing item that was added, if one was added
        clothing_item = None
        if self.clothing_item_added:
            clothing_item = clothing_items.get(self.clothing_item_added)

        # Check the list of used locations on the rig, and add to it if a new clothing item location is added
        new_used_loc = used_locs.add()
        new_used_loc.name = clothing_item.body_location

        # Loop through all already equipped clothing items, and check if they need to be updated

        return ({'FINISHED'})
        




