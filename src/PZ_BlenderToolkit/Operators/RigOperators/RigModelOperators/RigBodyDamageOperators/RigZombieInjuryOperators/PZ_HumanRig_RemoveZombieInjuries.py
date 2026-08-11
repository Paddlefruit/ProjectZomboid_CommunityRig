# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveAllZombieInjuries(Operator):
    bl_idname = "zomboid.remove_all_zombie_injuries"
    bl_label = "Remove All Zombie Injuries"
    bl_description = "Removes all zombie injuries"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties

        if self.stop_texture_updates:
            model_properties.stop_texture_updates = True

        context.active_object.pz_zombie_injuries.clear()

        if self.stop_texture_updates:
            bpy.ops.zomboid.create_body_texture()
            model_properties.stop_texture_updates = False

        return ({'FINISHED'})