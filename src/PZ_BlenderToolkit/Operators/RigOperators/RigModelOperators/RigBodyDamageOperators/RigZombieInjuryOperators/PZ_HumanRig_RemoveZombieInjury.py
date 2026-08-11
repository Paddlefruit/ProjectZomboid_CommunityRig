# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator

class PZ_HumanRig_RemoveZombieInjury(Operator):
    bl_idname = "zomboid.remove_zombie_injury"
    bl_label = "Remove Zombie Injury"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Get all data
        injury_properties = context.active_object.pz_injury_properties
        model_properties = context.active_object.pz_model_properties

        # Remove the injury
        context.active_object.pz_zombie_injuries.remove(injury_properties.zombie_injury_active_index)
        injury_properties.zombie_injury_active_index -= 1

        if not model_properties.stop_texture_updates:
            bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})