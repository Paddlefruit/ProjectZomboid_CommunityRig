# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveAllBodyDamage(Operator):
    bl_idname = "zomboid.remove_all_body_damage"
    bl_label = "Remove All Body Damage"
    bl_description = "Removes all body damage"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties

        if self.stop_texture_updates:
            model_properties.stop_texture_updates = True

        bpy.ops.zomboid.remove_body_bloodiness(stop_texture_updates=self.stop_texture_updates)
        bpy.ops.zomboid.remove_body_dirtiness(stop_texture_updates=self.stop_texture_updates)
        bpy.ops.zomboid.remove_all_body_injuries(stop_texture_updates=self.stop_texture_updates)
        bpy.ops.zomboid.remove_all_zombie_injuries(stop_texture_updates=self.stop_texture_updates)

        if self.stop_texture_updates:
            bpy.ops.zomboid.create_body_texture()
            model_properties.stop_texture_updates = False

        return ({'FINISHED'})