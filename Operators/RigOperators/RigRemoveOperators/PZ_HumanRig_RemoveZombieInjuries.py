# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveAllZombieInjuries(Operator):
    bl_idname = "zomboid.remove_all_zombie_injuries"
    bl_label = "Remove All Zombie Injuries"
    bl_description = "Removes all zombie injuries"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        context.active_object.pz_human_zombie_injuries.clear()

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})