# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator

class PZ_HumanRig_RemoveZombieInjury(Operator):
    bl_idname = "zomboid.remove_zombie_injury"
    bl_label = "Remove Zombie Injury"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="object.pz_human_zombie_injuries",
            active_index_path="object.pz_human_props.zombie_injury_active_index"
        )

        bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})