# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.types import Operator

class PZ_ResetModel(Operator):
    bl_idname = "zomboid.reset_model"
    bl_label = "Reset Model"
    bl_description = "Resets all changes to the model and sets all respective settings to default"

    def execute(self, context):
        p = context.active_object.pz_human_props

        p.halt_texture_updates = True

        bpy.ops.zomboid.remove_all_clothing_items(halt_texture_updates=False)
        bpy.ops.zomboid.remove_hair_mesh(hair_type='M')
        bpy.ops.zomboid.remove_hair_mesh(hair_type='F')
        bpy.ops.zomboid.remove_hair_mesh(hair_type='B')
       # bpy.ops.zomboid.remove_all_body_damage(halt_texture_updates=False)

        p.skin_set = 'HUMAN'
        p.model_sex = 'MALE'
        p.skin_color = 0
        p.zombification = 0
        p.chest_hair = False
        p.hair_stubble = False
        p.beard_stubble = False

        p.selected_male_hair_style = ''
        p.selected_female_hair_style = ''
        p.selected_beard_style = ''
        p.hair_color = (0.25, 0.15, 0.05)

        p.selected_outfit = ''

        p.random_zombie = False
        p.random_skin_color = True
        p.random_hair_style = True
        p.random_hair_color = True
        p.natural_hair_color = True
        p.random_beard_chance = 50

        p.randomize_injuries = False
        p.random_bloodiness_intensity = 'MODERATE'
        p.random_dirtiness_intensity = 'MODERATE'
        p.random_injury_intensity = 'MODERATE'
        p.random_zombie_injury_intensity = 'DAMAGED'

        p.random_scratch_chance = 65
        p.random_laceration_chance = 30
        p.random_bite_chance = 5

        p.random_bandage_chance = 35
        p.random_bloody_bandage_chance = 35

        p.halt_texture_updates = False

        bpy.ops.zomboid.create_body_texture()
        bpy.ops.zomboid.create_bloodiness_mask()
        bpy.ops.zomboid.create_dirtiness_mask()
        bpy.ops.zomboid.create_visibility_mask()


        return ({'FINISHED'})