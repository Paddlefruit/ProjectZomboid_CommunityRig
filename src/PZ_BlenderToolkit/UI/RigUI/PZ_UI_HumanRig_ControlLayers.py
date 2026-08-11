# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_UI_HumanRig_ControlLayersPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_control_layers_panel"
    bl_label = "Rig Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        
        # Only show this panel if the rig is selected
        if context.active_object:
            return context.active_object.get("rig_id") == "ZOMBOID_Human"
        return False

    def draw(self, context):

        # Get all data
        control_properties = context.active_object.pz_control_properties

        # Get the initial layout
        layout = self.layout

        # The miscellaneous properties
        layout.prop(control_properties, 'widgets_size')
        layout.prop(control_properties, 'auto_hide_controls')

        # Create a column to store all of the control visibility toggles and sub layouts
        layout.label(text='Visibility')
        column = layout.column(align=True)
        column.scale_y = 1.25
    
        # Control toggles are sorted based on their height from the ground #

        # CTRL-Head and CTRL-Lookpoint
        subrow = column.row(align=True)
        subrow.prop(control_properties, 'toggle_head_controls', toggle=True)
        subrow.prop(control_properties, 'toggle_look_point_controls', toggle=True)

        # CTRL-Chest
        column.prop(control_properties, "toggle_chest_controls", toggle=True)

        # CTRL-Backpack
        column.prop(control_properties, "toggle_backpack_controls", toggle=True)

        # CTRL-Shoulder
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_shoulder_controls", text='Left Shoulder',toggle=True)
        subrow.prop(control_properties, "toggle_right_shoulder_controls", text='Right Shoulder', toggle=True)

        # CTRL-ArmFK
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_arm_fk_controls", text='Left Arm FK', toggle=True)
        subrow.prop(control_properties, "toggle_right_arm_fk_controls", text='Right Arm FK', toggle=True)

        # CTRL-ArmIK
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_arm_ik_controls", text='Left Arm IK', toggle=True)
        subrow.prop(control_properties, "toggle_right_arm_ik_controls", text='Right Arm IK', toggle=True)

        # CTRL-Fingers
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_finger_controls", text='Left Fingers', toggle=True)
        subrow.prop(control_properties, "toggle_right_finger_controls", text='Right Fingers', toggle=True)

        # CTRL-Prop
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_prop_controls", text='Left Prop', toggle=True)
        subrow.prop(control_properties, "toggle_right_prop_controls", text='Right Prop', toggle=True)

        # CTRL-Spine
        column.prop(control_properties, "toggle_spine_controls", toggle=True)

        # CTRL-Pelvis
        column.prop(control_properties, "toggle_pelvis_controls", toggle=True)

        # CTRL-LegFK
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_leg_fk_controls", text='Left Leg FK', toggle=True)
        subrow.prop(control_properties, "toggle_right_leg_fk_controls", text='Right Leg FK', toggle=True)

        # CTRL-LegIK
        subrow = column.row(align=True)
        subrow.prop(control_properties, "toggle_left_leg_ik_controls", text='Left Leg IK', toggle=True)
        subrow.prop(control_properties, "toggle_right_leg_ik_controls", text='Right Leg IK', toggle=True)

        # CTRL-Dress
        column.prop(control_properties, "toggle_dress_controls", toggle=True)

        # CTRL-Root 
        column.prop(control_properties, 'toggle_root_controls', toggle=True)

        # CTRL-TranslationData
        column.prop(control_properties, 'toggle_translation_data_controls', toggle=True)