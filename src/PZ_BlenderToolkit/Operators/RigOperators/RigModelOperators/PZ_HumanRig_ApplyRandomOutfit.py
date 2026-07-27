# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from random import randint
from bpy.types import Operator

class PZ_HumanRig_ApplyRandomOutfit(Operator):
    bl_idname = "zomboid.apply_random_outfit"
    bl_label = "Apply Random Outfit"
    bl_description = "Applies a random outfit from all XMLs with the same paramaters and probabilities as in game"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        outfits = addon_prefs.pz_human_outfit_slots

        rnd = randint(0, len(outfits)-1)
        p.selected_outfit = outfits[rnd].search_name

        bpy.ops.zomboid.apply_outfit()

        return ({'FINISHED'})