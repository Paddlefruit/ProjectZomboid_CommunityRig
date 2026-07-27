# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_SceneRigsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_scene_rigs_panel"
    bl_label = "Scene Rigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    def draw(self, context):
        scene_props = context.scene.pz_human_global_props
        layout = self.layout

        layout.template_list("PZ_UL_RigList", "pz_human_rigs_list", context.scene,
                                "pz_human_rigs", scene_props, "human_rig_active_index")

        layout.prop(scene_props, 'rig_parent_collection')

        layout.operator('zomboid.create_rig')