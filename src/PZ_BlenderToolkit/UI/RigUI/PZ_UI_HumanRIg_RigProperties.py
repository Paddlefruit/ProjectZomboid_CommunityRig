# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_UI_HumanRig_RigPropertiesPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_ik_panel"
    bl_label = "Rig Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    @classmethod
    def poll(cls, context):

        valid_bones = [
            'CTRL-Head',
            'CTRL-LookPoint',

            'CTRL-ArmIK.R',
            'CTRL-ElbowTarget.R',
            'CTRL-UpperArmFK.R',
            'CTRL-ForearmFK.R',
            'CTRL-HandFK.R',
            'CTRL-Prop.R',

            'CTRL-ArmIK.L',
            'CTRL-ElbowTarget.L',
            'CTRL-UpperArmFK.L',
            'CTRL-ForearmFK.L',
            'CTRL-HandFK.L',
            'CTRL-Prop.L',

            'CTRL-Backpack',

            'CTRL-LegIK.R',
            'CTRL-KneeTarget.R',
            'CTRL-ThighFK.R',
            'CTRL-CalfFK.R',
            'CTRL-FootFK.R',

            'CTRL-LegIK.L',
            'CTRL-KneeTarget.L',
            'CTRL-ThighFK.L',
            'CTRL-CalfFK.L',
            'CTRL-FootFK.L',

            'CTRL-DressFront1',
            'CTRL-DressFront2',
            'CTRL-DressBack1',
            'CTRL-DressBack2'
        ]

        # Only show this panel if the rig is selected, and a relevant bone is selected
        if context.active_object:
            if context.active_object.get("rig_id") == "ZOMBOID_Human" and bpy.context.active_object.mode == 'POSE':
                for bone in context.selected_pose_bones:
                    if bone.name in valid_bones:
                        return True
        return False

    def draw(self, context):

        # Get all data
        animation_properties = context.active_object.pz_animation_properties
        control_properties = context.active_object.pz_control_properties

        # Tracker to see if there was a previous area drawn
        was_prev_area = False

        # Create the initial layout
        layout = self.layout


        ## IK / FK ##

        def draw_ik_area(heading, 
                         ik_fk_prop, 
                         ik_control_parent_prop, 
                         ik_pole_parent_prop, 
                         first_fk_bone,
                         second_fk_bone,
                         first_ik_bone,
                         second_ik_bone,
                         ik_control_bone,
                         ik_pole_bone,
                         extremity_bone,
                         limb_type):

            column = layout.column()

            # The header
            column.label(text=heading)

            # The main IK FK toggle property
            column.prop(animation_properties, ik_fk_prop, text='IK/FK')
            column.separator(factor=0.5)

            # The snapping operator box
            subbox = column.box()

            # The FK to IK Snap Operator
            op = subbox.operator('zomboid.snap_fk_to_ik')
            op.ik_fk_prop = ik_fk_prop
            op.first_fk_bone = first_fk_bone
            op.second_fk_bone = second_fk_bone
            op.first_ik_bone = first_ik_bone
            op.second_ik_bone = second_ik_bone
            op.ik_control_bone = ik_control_bone
            op.extremity_bone = extremity_bone

            # The IK to FK Snap Operator
            op = subbox.operator('zomboid.snap_ik_to_fk')
            op.ik_fk_prop = ik_fk_prop
            op.fk_bone = second_fk_bone
            op.ik_control_bone = ik_control_bone
            op.ik_pole_bone = ik_pole_bone
            op.extremity_bone = extremity_bone
            op.limb_type = limb_type

            column.separator(factor=0.5)
            
            # The bone parenting properties
            subbox = column.box()

            subbox.label(text='IK Control Parent')
            subbox.prop(control_properties, ik_control_parent_prop, expand=True)

            subbox.separator(type='LINE', factor=0.5)

            subbox.label(text='IK Pole Parent')
            subbox.prop(control_properties, ik_pole_parent_prop, expand=True)

        left_arm_controls = [
            'CTRL-ArmIK.L',
            'CTRL-ElbowTarget.L',
            'CTRL-UpperArmFK.L',
            'CTRL-ForearmFK.L',
            'CTRL-HandFK.L',
        ]

        for bone in context.selected_pose_bones:
            if bone.name in left_arm_controls:
                draw_ik_area('Left Arm Properties', 
                            'arm_ik_l', 
                            'left_arm_ik_control_parent', 
                            'left_arm_ik_pole_parent',
                            'CTRL-UpperArmFK.L',
                            'CTRL-ForearmFK.L',
                            'IK-UpperArm.L',
                            'IK-Forearm.L',
                            'CTRL-ArmIK.L',
                            'CTRL-ElbowTarget.L',
                            'CTRL-HandFK.L',
                            'ARM')
                was_prev_area = True
                break

        right_arm_controls = [
            'CTRL-ArmIK.R',
            'CTRL-ElbowTarget.R',
            'CTRL-UpperArmFK.R',
            'CTRL-ForearmFK.R',
            'CTRL-HandFK.R',
        ]
        
        for bone in context.selected_pose_bones:
            if bone.name in right_arm_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                draw_ik_area('Right Arm Properties', 
                            'arm_ik_r', 
                            'right_arm_ik_control_parent', 
                            'right_arm_ik_pole_parent',
                            'CTRL-UpperArmFK.R',
                            'CTRL-ForearmFK.R',
                            'IK-UpperArm.R',
                            'IK-Forearm.R',
                            'CTRL-ArmIK.R',
                            'CTRL-ElbowTarget.R',
                            'CTRL-HandFK.R',
                            'ARM')
                was_prev_area = True
                break

        left_leg_controls = [
            'CTRL-LegIK.L',
            'CTRL-KneeTarget.L',
            'CTRL-ThighFK.L',
            'CTRL-CalfFK.L',
            'CTRL-FootFK.L',
        ]
                
        for bone in context.selected_pose_bones:
            if bone.name in left_leg_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                draw_ik_area('Left Leg Properties', 
                            'leg_ik_l', 
                            'left_leg_ik_control_parent', 
                            'left_leg_ik_pole_parent',
                            'CTRL-ThighFK.L',
                            'CTRL-CalfFK.L',
                            'IK-Thigh.L',
                            'IK-Calf.L',
                            'CTRL-LegIK.L',
                            'CTRL-KneeTarget.L',
                            'CTRL-FootFK.L',
                            'LEG')
                was_prev_area = True
                break

        right_leg_controls = [
            'CTRL-LegIK.R',
            'CTRL-KneeTarget.R',
            'CTRL-ThighFK.R',
            'CTRL-CalfFK.R',
            'CTRL-FootFK.R',
        ]
                
        for bone in context.selected_pose_bones:
            if bone.name in right_leg_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                draw_ik_area('Right Leg Properties', 
                            'leg_ik_r', 
                            'right_leg_ik_control_parent', 
                            'right_leg_ik_pole_parent',
                            'CTRL-ThighFK.R',
                            'CTRL-CalfFK.R',
                            'IK-Thigh.R',
                            'IK-Calf.R',
                            'CTRL-LegIK.R',
                            'CTRL-KneeTarget.R',
                            'CTRL-FootFK.R',
                            'LEG')
                was_prev_area = True
                break


        ## HEAD ##
            
        head_controls = [
            'CTRL-Head',
            'CTRL-LookPoint'
        ]
        for bone in context.selected_pose_bones:
            if bone.name in head_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                column = layout.column()

                column.label(text='Head Properties')
                column.prop(animation_properties, 'head_lookpoint')

                column.separator(factor=0.5)
    
                subbox = column.box()
                subbox.label(text='Lookpoint Parent')
                subbox.prop(control_properties, 'lookpoint_parent', expand=True)
                if control_properties.lookpoint_parent == 'OBJECT':
                    subbox.prop(control_properties, 'lookpoint_parent_object')

                was_prev_area = True
                break


        ## DRESS ##
                
        dress_controls = [
            'CTRL-DressFront1',
            'CTRL-DressFront2',
            'CTRL-DressBack1',
            'CTRL-DressBack2'
        ]
        for bone in context.selected_pose_bones:
            if bone.name in dress_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                # The main column this method uses
                column = layout.column(heading='Dress Properties')

                column.label(text='Dress Properties')
    
                subbox = column.box()
                subbox.label(text='Dress Parent')
                subbox.prop(control_properties, 'dress_parent', expand=True)

                was_prev_area = True
                break


        ## BACKPACK ##
        
        for bone in context.selected_pose_bones:
            if bone.name == 'CTRL-Backpack':

                if was_prev_area:
                    layout.separator(type='LINE')

                column = layout.column()
                column.label(text='Backpack Properties')
                    
                subbox = column.box()
                subbox.label(text='Backpack Parent')
                subbox.prop(control_properties, 'backpack_parent', expand=True)

                was_prev_area = True
                break


        ## WRIST ##

        wrist_controls = [
            'CTRL-ArmIK.R',
            'CTRL-ArmIK.L',
            'CTRL-HandFK.R',
            'CTRL-HandFK.L',
            'CTRL-ForearmFK.R',
            'CTRL-ForearmFK.L'
        ]
        for bone in context.selected_pose_bones:
            if bone.name in wrist_controls:

                if was_prev_area:
                    layout.separator(type='LINE')

                column = layout.column()
                column.label(text='Wrist Properties')
                                    
                subbox = column.box()
                subbox.prop(animation_properties, 'wrist_twist_amount')
                
                was_prev_area = True
                break


        ## PROPS ##

        def draw_prop_area(heading, parent_prop, parent_obj_prop):
            column = layout.column()
            column.label(text=heading)
                                                
            subbox = column.box()
            subbox.label(text='Prop Parent')
            subbox.prop(control_properties, parent_prop, expand=True)
            if getattr(control_properties, parent_prop) == 'OBJECT':
                subbox.prop(control_properties, parent_obj_prop)

        for bone in context.selected_pose_bones:
            if bone.name == 'CTRL-Prop.L':

                if was_prev_area:
                    layout.separator(type='LINE')

                draw_prop_area('Left Prop Properties', 'left_prop_parent', 'left_prop_parent_object')
                was_prev_area = True
                break

        for bone in context.selected_pose_bones:
            if bone.name == 'CTRL-Prop.R':

                if was_prev_area:
                    layout.separator(type='LINE')

                draw_prop_area('Right Prop Properties', 'right_prop_parent', 'right_prop_parent_object')
                was_prev_area = True
                break
