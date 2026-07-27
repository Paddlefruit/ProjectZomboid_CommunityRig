# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_ConstraintsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_constraints_panel"
    bl_label = "Constraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        main_column = layout.column()

        subpanel, panel_area = main_column.panel(
            "head_rotation_subpanel", default_closed=False)
        subpanel.label(text='Head Rotation')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            column.use_property_split = True

            column.prop(p, "head_lookpoint")
            column.prop(p, "lookpoint_parent")
            if p.lookpoint_parent_index == 4:
                column.prop(p, "lookpoint_parent_object")

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "ik_fk_subpanel", default_closed=False)
        subpanel.label(text='Inverse Kinematics')

        if panel_area:
            box = panel_area.box()

            column = box.column()

            column.prop(addon_prefs, 'auto_switch_kinematics')
            column.prop(addon_prefs, 'auto_key_snaps')

            main_row = box.row()

            left_column = main_row.column()
            left_column.use_property_split = True

            sub_box = left_column.box()

            sub_box.label(text="Left Arm")
            sub_box.prop(p, "arm_ik_l", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_l > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-UpperArmFK.L'
            op.second_fk_bone = 'CTRL-ForearmFK.L'
            op.first_ik_bone = 'IK-UpperArm.L'
            op.second_ik_bone = 'IK-Forearm.L'
            op.ik_control_bone = 'CTRL-ArmIK.L'
            op.extremity_bone = 'CTRL-HandFK.L'
            op.ik_fk_prop = 'arm_ik_l'

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_l < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-ForearmFK.L'
            op.ik_control_bone = 'CTRL-ArmIK.L'
            op.ik_pole_bone = 'CTRL-ElbowTarget.L'
            op.extremity_bone = 'CTRL-HandFK.L'
            op.limb_type = 'ARM'
            op.ik_fk_prop = 'arm_ik_l'

            sub_box.prop(p, "left_arm_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "left_arm_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            left_column.separator()

            sub_box = left_column.box()

            sub_box.label(text="Left Leg")
            sub_box.prop(p, "leg_ik_l", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_l > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-ThighFK.L'
            op.second_fk_bone = 'CTRL-CalfFK.L'
            op.first_ik_bone = 'IK-Thigh.L'
            op.second_ik_bone = 'IK-Calf.L'
            op.ik_control_bone = 'CTRL-LegIK.L'
            op.extremity_bone = 'CTRL-FootFK.L'
            op.ik_fk_prop = 'leg_ik_l'

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_l < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-CalfFK.L'
            op.ik_control_bone = 'CTRL-LegIK.L'
            op.ik_pole_bone = 'CTRL-KneeTarget.L'
            op.extremity_bone = 'CTRL-FootFK.L'
            op.limb_type = 'LEG'
            op.ik_fk_prop = 'leg_ik_l'

            sub_box.prop(p, "left_leg_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "left_leg_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            right_column = main_row.column()
            right_column.use_property_split = True

            sub_box = right_column.box()

            sub_box.label(text="Right Arm")
            sub_box.prop(p, "arm_ik_r", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_r > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-UpperArmFK.R'
            op.second_fk_bone = 'CTRL-ForearmFK.R'
            op.first_ik_bone = 'IK-UpperArm.R'
            op.second_ik_bone = 'IK-Forearm.R'
            op.ik_control_bone = 'CTRL-ArmIK.R'
            op.extremity_bone = 'CTRL-HandFK.R'
            op.ik_fk_prop = 'arm_ik_r'

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_r < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-ForearmFK.R'
            op.ik_control_bone = 'CTRL-ArmIK.R'
            op.ik_pole_bone = 'CTRL-ElbowTarget.R'
            op.extremity_bone = 'CTRL-HandFK.R'
            op.limb_type = 'ARM'
            op.ik_fk_prop = 'arm_ik_r'

            sub_box.prop(p, "right_arm_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "right_arm_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            right_column.separator()

            sub_box = right_column.box()

            sub_box.label(text="Right Leg")
            sub_box.prop(p, "leg_ik_r", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_r > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-ThighFK.R'
            op.second_fk_bone = 'CTRL-CalfFK.R'
            op.first_ik_bone = 'IK-Thigh.R'
            op.second_ik_bone = 'IK-Calf.R'
            op.ik_control_bone = 'CTRL-LegIK.R'
            op.extremity_bone = 'CTRL-FootFK.R'
            op.ik_fk_prop = 'leg_ik_r'

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_r < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-CalfFK.R'
            op.ik_control_bone = 'CTRL-LegIK.R'
            op.ik_pole_bone = 'CTRL-KneeTarget.R'
            op.extremity_bone = 'CTRL-FootFK.R'
            op.limb_type = 'LEG'
            op.ik_fk_prop = 'leg_ik_r'

            sub_box.prop(p, "right_leg_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "right_leg_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            box.separator()
            column = box.column()
            column.prop(p, 'all_ik_control_parent')
            column.prop(p, 'all_ik_pole_parent')

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "dress_prop_backpack_subpanel", default_closed=False)
        subpanel.label(text='Props & Dress')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()

            left_column = row.column()
            left_column.use_property_split = True
            left_column.prop(p, 'left_prop_parent')
            if p.left_prop_parent_index == 3:
                left_column.prop(p, 'left_prop_parent_object')

            right_column = row.column()
            right_column.use_property_split = True
            right_column.prop(p, 'right_prop_parent')
            if p.right_prop_parent_index == 3:
                right_column.prop(p, 'right_prop_parent_object')

            column.separator(factor=2.0, type='LINE')

            row = column.row()
            row.use_property_split = True
            row.prop(p, 'backpack_parent')

            column.separator(factor=2.0, type='LINE')

            row = column.row()
            row.use_property_split = True
            row.prop(p, 'dress_parent')

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "wrist_twist_subpanel", default_closed=False)
        subpanel.label(text='Extremity Rotation')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()

            row.prop(p, 'wrist_twist_amount')