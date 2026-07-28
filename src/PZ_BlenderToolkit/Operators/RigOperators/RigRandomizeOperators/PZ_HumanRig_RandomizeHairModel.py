# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from random import randint

class PZ_RandomizeHairModel(Operator):
    bl_idname = "zomboid.randomize_hair_model"
    bl_label = "Randomize Hair Model"
    bl_options = {'REGISTER', 'UNDO'}

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        match self.hair_type:
            case 'M':
                rnd = randint(
                    0, len(addon_prefs.pz_human_male_hair_styles) - 1)
                p.selected_male_hair_style = addon_prefs.pz_human_male_hair_styles[rnd].name
            case 'F':
                rnd = randint(
                    0, len(addon_prefs.pz_human_female_hair_styles) - 1)
                p.selected_female_hair_style = addon_prefs.pz_human_female_hair_styles[
                    rnd].name
            case 'B':
                rnd = randint(0, len(addon_prefs.pz_human_beard_styles) - 1)
                p.selected_beard_style = addon_prefs.pz_human_beard_styles[rnd].name

        return ({'FINISHED'})