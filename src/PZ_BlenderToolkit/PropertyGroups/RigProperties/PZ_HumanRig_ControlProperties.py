# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup, Object
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty, PointerProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to a rig's 
control bones, behavior, and appearance
'''

class PZ_HumanRigControlProperties(PropertyGroup):

    widgets_size: FloatProperty(
        name="Widget Size",
        default=2.0,
        min=1.0,
        max=10.0,
        subtype="PIXEL",
        description="The size of the control widgets"
    )

    auto_hide_controls: BoolProperty(
        name="Auto Hide Controls",
        default=True,
        description="When true, control bones that can not contribute to the end result are automatically hidden"
    )

    ### CONTROL PARENTING ###

    ## Look Point Parenting ##

    def update_lookpoint_parent_index(self, context):
        self.lookpoint_parent_index = context.active_object.pz_control_properties['lookpoint_parent']

    lookpoint_parent: EnumProperty(
        name="Look Point Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Lookpoint is not child of anything", 0),
            ('ROOT', "Root", "Lookpoint is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Lookpoint is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Lookpoint is the child of CTRL-Chest", 3),
            ('OBJECT', "Object", "Copies the location of a selected object", 4)
        ],
        default='ROOT',
        update=update_lookpoint_parent_index
    )

    lookpoint_parent_index: IntProperty(
        default=1
    )

    def update_lookpoint_parent_object(self, context):
        update_lookpoint_parent_object(self, context)

    lookpoint_parent_object: PointerProperty(
        name="LookPoint Parent Object",
        type=Object,
        update=update_lookpoint_parent_object
    )

    ## Left Prop Parenting ##

    def update_left_prop_parent_index(self, context):
        self.left_prop_parent_index = context.active_object.pz_control_properties['left_prop_parent']

    left_prop_parent: EnumProperty(
        name="Left Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Left Prop is not child of anything", 0),
            ('ROOT', "Root", "Left Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Left Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_left_prop_parent_index
    )

    left_prop_parent_index: IntProperty(
        default=2
    )

    left_prop_parent_object: PointerProperty(
        name="Left Prop Parent Object",
        type=Object,
        update=update_left_prop_parent_object
    )

    ## Right Prop Parenting ##

    def update_right_prop_parent_index(self, context):
        self.right_prop_parent_index = context.active_object.pz_control_properties['right_prop_parent']

    right_prop_parent: EnumProperty(
        name="Right Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Right Prop is not child of anything", 0),
            ('ROOT', "Root", "Right Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Right Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_right_prop_parent_index
    )

    right_prop_parent_index: IntProperty(
        default=2
    )

    right_prop_parent_object: PointerProperty(
        name="Right Prop Parent Object",
        type=Object,
        update=update_right_prop_parent_object
    )

    ## Backpack Parenting ##

    def update_backpack_parent_index(self, context):
        self.backpack_parent_index = context.active_object.pz_control_properties['backpack_parent']

    backpack_parent: EnumProperty(
        name="Backpack Parent",
        description="What the backpack is parented to",
        items=[
            ('NONE', "None", "Backpack is not child of anything", 0),
            ('ROOT', "Root", "Backpack is the child of CTRL-Root", 1),
            ('SPINE', "Spine", "Backpack is the child of the spine", 2)
        ],
        default='SPINE',
        update=update_backpack_parent_index
    )

    backpack_parent_index: IntProperty(
        default=2
    )

    ## Dress Parenting ##

    def update_dress_parent_index(self, context):
        self.dress_parent_index = context.active_object.pz_control_properties['dress_parent']

    dress_parent: EnumProperty(
        name="Dress Parent",
        description="What the dress is parented to",
        items=[
            ('NONE', "None", "Dress is not child of anything", 0),
            ('ROOT', "Root", "Dress is the child of CTRL-Root", 1),
            ('LEGS', "Legs", "Dress bones are calculated between the legs", 2)
        ],
        default='LEGS',
        update=update_dress_parent_index
    )

    dress_parent_index: IntProperty(
        default=2
    )

    ## Right Arm IK Control Parenting ##

    def update_right_arm_ik_control_parent_index(self, context):
        self.right_arm_ik_control_parent_index = context.active_object.pz_control_properties['right_arm_ik_control_parent']

    right_arm_ik_control_parent: EnumProperty(
        name="Right Arm IK Control Parent",
        description="What the right arm IK control is parented to",
        items=[
            ('NONE', "None", "Right arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Right arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Right arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_right_arm_ik_control_parent_index
    )

    right_arm_ik_control_parent_index: IntProperty(
        default=1
    )

    ## Right Arm IK Pole Parenting ##

    def update_right_arm_ik_pole_parent_index(self, context):
        self.right_arm_ik_pole_parent_index = context.active_object.pz_control_properties['right_arm_ik_pole_parent']

    right_arm_ik_pole_parent: EnumProperty(
        name="Right Arm IK Pole Parent",
        description="What the right arm IK pole is parented to",
        items=[
            ('NONE', "None", "Right arm IK pole is not child of anything", 0),
            ('ROOT', "Root", "Right arm IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right arm IK pole is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Right arm IK pole is the child of CTRL-Chest", 3),
            ('CONTROL', "Control", "Right arm IK pole is the child of the IK control", 4),
            ('ELBOW', "Elbow", "Right arm IK pole is the child of the calculated position of the middle of the arm", 5)
        ],
        default='ROOT',
        update=update_right_arm_ik_pole_parent_index
    )

    right_arm_ik_pole_parent_index: IntProperty(
        default=1
    )

    ## Left Arm IK Control Parenting ##

    def update_left_arm_ik_control_parent_index(self, context):
        self.left_arm_ik_control_parent_index = context.active_object.pz_control_properties['left_arm_ik_control_parent']

    left_arm_ik_control_parent: EnumProperty(
        name="Left Arm IK Control Parent",
        description="What the left arm IK control is parented to",
        items=[
            ('NONE', "None", "Left arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Left arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Left arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_left_arm_ik_control_parent_index
    )

    left_arm_ik_control_parent_index: IntProperty(
        default=1
    )

    ## Left Arm IK Pole Parenting ##

    def update_left_arm_ik_pole_parent_index(self, context):
        self.left_arm_ik_pole_parent_index = context.active_object.pz_control_properties['left_arm_ik_pole_parent']

    left_arm_ik_pole_parent: EnumProperty(
        name="Left Arm IK Pole Parent",
        description="What the left arm IK pole is parented to",
        items=[
            ('NONE', "None", "Left arm IK pole is not child of anything", 0),
            ('ROOT', "Root", "Left arm IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left arm IK pole is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Left arm IK pole is the child of CTRL-Chest", 3),
            ('CONTROL', "Control", "Left arm IK pole is the child of the IK control", 4),
            ('ELBOW', "Elbow", "Left arm IK pole is the child of the calculated position of the middle of the arm", 5)
        ],
        default='ROOT',
        update=update_left_arm_ik_pole_parent_index
    )

    left_arm_ik_pole_parent_index: IntProperty(
        default=1
    )

    ## Right Leg IK Control Parenting ##

    def update_right_leg_ik_control_parent_index(self, context):
        self.right_leg_ik_control_parent_index = context.active_object.pz_control_properties['right_leg_ik_control_parent']

    right_leg_ik_control_parent: EnumProperty(
        name="Right Leg IK Control Parent",
        description="What the right leg IK control is parented to",
        items=[
            ('NONE', "None", "Right leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_right_leg_ik_control_parent_index
    )

    right_leg_ik_control_parent_index: IntProperty(
        default=1
    )

    ## Right Leg IK Pole Parenting ##

    def update_right_leg_ik_pole_parent_index(self, context):
            self.right_leg_ik_pole_parent_index = context.active_object.pz_control_properties['right_leg_ik_pole_parent']
    
    right_leg_ik_pole_parent: EnumProperty(
        name="Right Leg IK Pole Parent",
        description="What the right leg IK pole is parented to",
        items=[
            ('NONE', "None", "Right leg IK pole is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK pole is the child of CTRL-Pelvis", 2),
            ('CONTROL', "Control", "Right leg IK pole is the child of the IK control", 3),
            ('KNEE', "Knee", "Right leg IK pole is the child of the calculated position of the middle of the leg", 4)
        ],
        default='ROOT',
        update=update_right_leg_ik_pole_parent_index
    )

    right_leg_ik_pole_parent_index: IntProperty(
        default=1
    )

    ## Left Leg IK Control Parenting ##

    def update_left_leg_ik_control_parent_index(self, context):
        self.left_leg_ik_control_parent_index = context.active_object.pz_control_properties['left_leg_ik_control_parent']

    left_leg_ik_control_parent: EnumProperty(
        name="Left Leg IK Control Parent",
        description="What the left leg IK control is parented to",
        items=[
            ('NONE', "None", "Left leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_left_leg_ik_control_parent_index
    )

    left_leg_ik_control_parent_index: IntProperty(
        default=1
    )

    ## Left Leg IK Pole Parenting ##

    def update_left_leg_ik_pole_parent_index(self, context):
        self.left_leg_ik_pole_parent_index = context.active_object.pz_control_properties['left_leg_ik_pole_parent']

    left_leg_ik_pole_parent: EnumProperty(
        name="Left Leg IK Pole Parent",
        description="What the left leg IK pole is parented to",
        items=[
            ('NONE', "None", "Left leg IK pole is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK pole is the child of CTRL-Pelvis", 2),
            ('CONTROL', "Control", "Left leg IK pole is the child of the IK control", 3),
            ('KNEE', "Knee", "Left leg IK pole is the child of the calculated position of the middle of the leg", 4)
        ],
        default='ROOT',
        update=update_left_leg_ik_pole_parent_index
    )

    left_leg_ik_pole_parent_index: IntProperty(
        default=1
    )

    ## Update All IK Controls ##

    def update_all_ik_control_parent_index(self, context):
        self.all_ik_control_parent_index = context.active_object.pz_control_properties['all_ik_control_parent']
        i = self.all_ik_control_parent_index

        if i == 3:
            self.left_arm_ik_control_parent = 'CHEST'
            self.right_arm_ik_control_parent = 'CHEST'
            self.left_leg_ik_control_parent = 'PELVIS'
            self.right_leg_ik_control_parent = 'PELVIS'
        else:
            self.left_arm_ik_control_parent = self.all_ik_control_parent
            self.right_arm_ik_control_parent = self.all_ik_control_parent
            self.left_leg_ik_control_parent = self.all_ik_control_parent
            self.right_leg_ik_control_parent = self.all_ik_control_parent

    all_ik_control_parent: EnumProperty(
        name="Set Parent For All IK Controls: ",
        description="Sets the parent for all IK controls instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Controls are not parented to anything", 0),
            ('ROOT', "Root", "IK Controls are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Controls are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Controls are parented to CTRL-Chest, Leg IK Controls are parented to CTRL-Pelvis", 3)
        ],
        default='ROOT',
        update=update_all_ik_control_parent_index
    )

    all_ik_control_parent_index: IntProperty(
        default=1
    )

    ## Update All IK Poles ##

    def update_all_ik_pole_parent_index(self, context):
        self.all_ik_pole_parent_index = context.active_object.pz_control_properties['all_ik_pole_parent']

        i = self.all_ik_pole_parent_index
        if i < 3:
            self.left_arm_ik_pole_parent = self.all_ik_pole_parent
            self.right_arm_ik_pole_parent = self.all_ik_pole_parent
            self.left_leg_ik_pole_parent = self.all_ik_pole_parent
            self.right_leg_ik_pole_parent = self.all_ik_pole_parent
        elif i == 3:
            self.left_arm_ik_pole_parent = 'CHEST'
            self.right_arm_ik_pole_parent = 'CHEST'
            self.left_leg_ik_pole_parent = 'PELVIS'
            self.right_leg_ik_pole_parent = 'PELVIS'
        elif i == 4:
            self.left_arm_ik_pole_parent = 'CONTROL'
            self.right_arm_ik_pole_parent = 'CONTROL'
            self.left_leg_ik_pole_parent = 'CONTROL'
            self.right_leg_ik_pole_parent = 'CONTROL'
        elif i == 5:
            self.left_arm_ik_pole_parent = 'ELBOW'
            self.right_arm_ik_pole_parent = 'ELBOW'
            self.left_leg_ik_pole_parent = 'KNEE'
            self.right_leg_ik_pole_parent = 'KNEE'

    all_ik_pole_parent: EnumProperty(
        name="Set Parent For All IK Poles: ",
        description="Sets the parent for all IK poles instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Poles are not parented to anything", 0),
            ('ROOT', "Root", "IK Poles are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Poles are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Poles are parented to CTRL-Chest, Leg IK Poles are parented to CTRL-Pelvis", 3),
            ('CONTROL', "Control",
                "IK Poles are parented to their corresponding IK controls", 4),
            ('JOINT', "Joint", "IK Poles are parented to the calculated position between the start and end of their corresponding limb", 5)
        ],
        default='ROOT',
        update=update_all_ik_pole_parent_index
    )

    all_ik_pole_parent_index: IntProperty(
        default=1
    )

    ### CONTROL VISIBILITY ###

    # FK Toggles
    
    toggle_left_arm_fk_controls: BoolProperty(
        name="Arm FK.L",
        default=True,
        description="Show the left arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_arm_fk_controls: BoolProperty(
        name="Arm FK.R",
        default=True,
        description="Show the right arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_left_leg_fk_controls: BoolProperty(
        name="Leg FK.L",
        default=True,
        description="Show the left arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_leg_fk_controls: BoolProperty(
        name="Leg FK.R",
        default=True,
        description="Show the right arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # IK Toggles

    toggle_left_arm_ik_controls: BoolProperty(
        name="Arm IK.L",
        default=True,
        description="Show the left arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_arm_ik_controls: BoolProperty(
        name="Arm IK.R",
        default=True,
        description="Show the right arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_left_leg_ik_controls: BoolProperty(
        name="Leg IK.L",
        default=True,
        description="Show the left arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_leg_ik_controls: BoolProperty(
        name="Leg IK.R",
        default=True,
        description="Show the right arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Root Toggles

    toggle_root_controls: BoolProperty(
        name="Root",
        default=True,
        description="Show the root controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_translation_data_controls: BoolProperty(
        name="Translation Data",
        default=True,
        description="Show the translation data controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Head Toggles

    toggle_look_point_controls: BoolProperty(
        name="Look Point",
        default=True,
        description="Show the look point controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_head_controls: BoolProperty(
        name="Head",
        default=True,
        description="Show the head controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Finger Toggles

    toggle_left_finger_controls: BoolProperty(
        name="Fingers.L",
        default=True,
        description="Show the left fingers controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_finger_controls: BoolProperty(
        name="Fingers.R",
        default=True,
        description="Show the right fingers controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Prop Toggles

    toggle_left_prop_controls: BoolProperty(
        name="Prop.L",
        default=True,
        description="Show the left prop controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_prop_controls: BoolProperty(
        name="Prop.R",
        default=True,
        description="Show the right prop controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_backpack_controls: BoolProperty(
        name="Backpack",
        default=True,
        description="Show the backpack controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_dress_controls: BoolProperty(
        name="Dress",
        default=True,
        description="Show the dress controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Shoulder Toggles

    toggle_left_shoulder_controls: BoolProperty(
        name="Shoulder.L",
        default=True,
        description="Show the left shoulder controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_shoulder_controls: BoolProperty(
        name="Shoulder.R",
        default=True,
        description="Show the right shoulder controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Torso Toggles

    toggle_pelvis_controls: BoolProperty(
        name="Pelvis",
        default=True,
        description="Show the pelvis controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_spine_controls: BoolProperty(
        name="Spine",
        default=True,
        description="Show the spine controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_chest_controls: BoolProperty(
        name="Chest",
        default=True,
        description="Show the chest controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
