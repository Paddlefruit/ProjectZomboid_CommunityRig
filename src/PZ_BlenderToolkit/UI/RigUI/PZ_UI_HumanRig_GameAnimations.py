# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_UI_HumanRig_GameAnimationsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_game_animations_panel"
    bl_label = "Game Animations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):

        # Only show this panel if the rig is selected, and a relevant bone is selected
        if context.active_object:
            if context.active_object.get("rig_id") == "ZOMBOID_Human":
                return True
        return False

    def draw(self, context):

        # Get all data
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        export_properties = context.active_object.pz_export_properties

        # Get the initial layout
        layout = self.layout

        # Panel for exporting animations
        panel, panel_area = layout.panel("anim_export_subpanel", default_closed=True)
        panel.label(text='Exporting')

        if panel_area:
            panel_area.label(text='Export Directory')
            panel_area.prop(export_properties, 'file_output_path', text='')

            box = panel_area.box()
            split = box.split(factor=0.35)
            split.prop(export_properties, 'batch_export')
            subrow = split.row()
            subrow.enabled = export_properties.batch_export
            subrow.prop(export_properties, 'action_filter')

            subrow = panel_area.row()
            subrow.scale_y = 1.5
            subrow.operator('zomboid.export_anim_glbs', text='Export GLBs')
