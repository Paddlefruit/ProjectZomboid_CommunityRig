# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from pathlib import Path
from bpy.types import Operator

class PZ_HumanRig_RemoveRig(Operator):
    bl_idname = "zomboid.remove_rig"
    bl_label = "Remove Rig"
    bl_description = "Removes this instance of the rig from the scene"

    def execute(self, context):
        rigs = context.scene.pz_human_rigs
        
        return ({'FINISHED'})