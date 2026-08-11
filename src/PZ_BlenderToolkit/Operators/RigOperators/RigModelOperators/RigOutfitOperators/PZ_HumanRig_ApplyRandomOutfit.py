# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from random import randint
from bpy.types import Operator

class PZ_HumanRig_ApplyRandomOutfit(Operator):
    bl_idname = "zomboid.apply_random_outfit"
    bl_label = "Apply Random Outfit"
    bl_description = "Applies a random outfit from all XMLs with the same paramaters and probabilities as in game"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties
        outfits = addon_data.pz_outfit_references

        if len(outfits) > 0:
            rnd = randint(0, len(outfits)-1)
            model_properties.selected_outfit = outfits[rnd].search_name

            bpy.ops.zomboid.apply_outfit()

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})