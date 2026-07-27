# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_ControlsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_controls_panel"
    bl_label = "Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

        column = layout.column()

        row = column.row()

        row.prop(p, "widgets_size")
        row.prop(p, "auto_hide_controls")

        column.separator(factor=2.5, type="LINE")

        row = column.row()
        row.prop(p, "toggle_root_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_translation_data_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_finger_controls", toggle=True)
        row.prop(p, "toggle_right_finger_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_prop_controls", toggle=True)
        row.prop(p, "toggle_right_prop_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_backpack_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_dress_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_shoulder_controls", toggle=True)
        row.prop(p, "toggle_right_shoulder_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_pelvis_controls", toggle=True)
        row.prop(p, "toggle_spine_controls", toggle=True)
        row.prop(p, "toggle_chest_controls", toggle=True)

        if not p.auto_hide_controls:

            column.separator()

            # Head Control Toggles
            row = column.row()
            row.prop(p, "toggle_head_controls", toggle=True)
            row = column.row()
            row.prop(p, "toggle_look_point_controls", toggle=True)

            column.separator()

            # FK Arm Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_arm_fk_controls", toggle=True)
            row.prop(p, "toggle_right_arm_fk_controls", toggle=True)

            # FK Leg Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_leg_fk_controls", toggle=True)
            row.prop(p, "toggle_right_leg_fk_controls", toggle=True)

            column.separator()

            # IK Arm Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_arm_ik_controls", toggle=True)
            row.prop(p, "toggle_right_arm_ik_controls", toggle=True)

            # IK Leg Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_leg_ik_controls", toggle=True)
            row.prop(p, "toggle_right_leg_ik_controls", toggle=True)