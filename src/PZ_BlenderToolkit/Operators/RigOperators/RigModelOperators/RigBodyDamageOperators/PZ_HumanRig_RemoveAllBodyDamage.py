# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveAllBodyDamage(Operator):
    bl_idname = "zomboid.remove_all_body_damage"
    bl_label = "Remove All Body Damage"
    bl_description = "Removes all body damage"
    bl_options = {'REGISTER', 'UNDO'}

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        bpy.ops.zomboid.remove_body_bloodiness(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_body_dirtiness(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_all_body_injuries(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_all_zombie_injuries(halt_texture_updates=self.halt_texture_updates)

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})