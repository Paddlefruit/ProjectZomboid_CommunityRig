# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_GlobalPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_global_panel"
    bl_label = "Assets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    def draw(self, context):
        layout = self.layout