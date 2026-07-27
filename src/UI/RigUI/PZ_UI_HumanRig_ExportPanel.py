# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_ExportPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_export_panel"
    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

        column = layout.column()

        row = column.row()
        row.prop(p, "file_output_path")

        row = column.row()
        row.alignment = 'LEFT'
        row.prop(p, "batch_export")

        if p.batch_export:
            row.prop(p, "action_filter")

        row = column.row()
        row.operator("zomboid.export_glb")