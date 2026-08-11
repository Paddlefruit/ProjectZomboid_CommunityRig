# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.types import Operator

class PZ_ResetModel(Operator):
    bl_idname = "zomboid.reset_model"
    bl_label = "Reset Model"
    bl_description = "Resets all changes to the model and sets all respective settings to default"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main_properties = context.active_object.pz_main_properties
        model_properties = context.active_object.pz_model_properties
        random_properties = context.active_object.pz_random_properties

        main_properties.stop_texture_updates = True

        bpy.ops.zomboid.remove_all_clothing_items(stop_texture_updates=False)
        bpy.ops.zomboid.remove_hair_model(hair_type='M')
        bpy.ops.zomboid.remove_hair_model(hair_type='F')
        bpy.ops.zomboid.remove_hair_model(hair_type='B')
        bpy.ops.zomboid.remove_all_body_damage(stop_texture_updates=False)

        model_properties.human_subtype = 'HUMAN'
        model_properties.model_sex = 'MALE'
        model_properties.skin_tone = 'PORCELAIN'
        model_properties.zombification = 'NONE'
        model_properties.chest_hair = False
        model_properties.hair_stubble = False
        model_properties.beard_stubble = False

        model_properties.selected_male_hair_style = ''
        model_properties.selected_female_hair_style = ''
        model_properties.selected_beard_style = ''
        model_properties.hair_color = (0.25, 0.15, 0.05)

        model_properties.selected_outfit = ''

        random_properties.random_zombie = False
        random_properties.random_skin_tone = True
        random_properties.random_hair_style = True
        random_properties.random_hair_color = True
        random_properties.natural_hair_color = True
        random_properties.random_beard_chance = 50

        random_properties.randomize_outfit_injuries = False
        random_properties.randomize_body_injuries = True
        random_properties.randomize_zombie_injuries = False
        random_properties.randomize_bloodiness = True
        random_properties.randomize_dirtiness = True

        random_properties.min_random_body_injuries = 0
        random_properties.min_random_body_injuries = 5

        random_properties.min_random_zombie_injuries = 0
        random_properties.min_random_zombie_injuries = 5

        random_properties.min_random_bloodiness = 0
        random_properties.max_random_bloodiness = 2.5

        random_properties.min_random_dirtiness = 0
        random_properties.max_random_dirtiness = 1

        random_properties.random_scratch_chance = 65
        random_properties.random_laceration_chance = 30
        random_properties.random_bite_chance = 5

        random_properties.random_bandage_chance = 35
        random_properties.random_bloody_bandage_chance = 35

        main_properties.stop_texture_updates = False

        bpy.ops.zomboid.create_body_texture()
        bpy.ops.zomboid.create_bloodiness_mask()
        bpy.ops.zomboid.create_dirtiness_mask()
        bpy.ops.zomboid.create_visibility_mask()


        return ({'FINISHED'})