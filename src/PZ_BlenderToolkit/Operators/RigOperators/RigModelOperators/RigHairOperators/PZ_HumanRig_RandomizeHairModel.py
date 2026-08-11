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
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties

        match self.hair_type:
            case 'M':
                rnd = randint(0, len(addon_data.pz_male_hair_style_references) - 1)
                model_properties.selected_male_hair_style = addon_data.pz_male_hair_style_references[rnd].name
            case 'F':
                rnd = randint(0, len(addon_data.pz_female_hair_style_references) - 1)
                model_properties.selected_female_hair_style = addon_data.pz_female_hair_style_references[rnd].name
            case 'B':
                rnd = randint(0, len(addon_data.pz_beard_style_references) - 1)
                model_properties.selected_beard_style = addon_data.pz_beard_style_references[rnd].name

        return ({'FINISHED'})