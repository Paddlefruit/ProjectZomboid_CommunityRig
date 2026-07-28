# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup, Collection, Object, Image, Material
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, PointerProperty, BoolVectorProperty

from ..Utility.PZ_UpdateMethods import *
from ..Utility.PZ_FilterMethods import filter_zombie_injuries

class PZ_HumanRigProperties(PropertyGroup):

# ============================================================================================
# IMPORTANT OBJECTS
# ============================================================================================

    rig_collection: PointerProperty(type=Collection)

    male_body_object: PointerProperty(type=Object)
    male_dress_object: PointerProperty(type=Object)
    female_body_object: PointerProperty(type=Object)
    female_dress_object: PointerProperty(type=Object)
    male_skeleton_object: PointerProperty(type=Object)
    female_skeleon_object: PointerProperty(type=Object)
    translation_data_empty: PointerProperty(type=Object)
    dummy01_empty: PointerProperty(type=Object)

    mask_tex: PointerProperty(type=Image)
    body_tex: PointerProperty(type=Image)
    
    body_mat: PointerProperty(type=Material)

# ============================================================================================
# INSTANCING
# ============================================================================================

    '''
    When updating the rig instance index, update the name of all instance-specific
    data blocks to match
    '''

    def update_rig_instance(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        old_instance_pattern = r' \([0-9]+\)| \(\[INSTANCE\]\)'
        
        # Check if this instance number is already used. If so, increment by one and return.
        for rig in context.scene.pz_human_rigs:
            if rig.obj != context.active_object:
                if self.rig_instance == rig.obj.pz_human_props.rig_instance:
                    self.rig_instance += 1
                    return

        # Recursively go through the rig collection and change all '({old rig instance})'
        # to '({new rig instance})'

        p.rig_collection.name = re.sub(
            old_instance_pattern, instance_str, p.rig_collection.name)
        for obj in p.rig_collection.objects:
            obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
            if obj.data and isinstance(obj.data, bpy.types.ID):
                obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
        for col in p.rig_collection.children_recursive:
            col.name = re.sub(old_instance_pattern, instance_str, col.name)
            for obj in col.objects:
                obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
                if obj.data and isinstance(obj.data, bpy.types.ID):
                    obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
                if obj.active_material:
                    obj.active_material.name = re.sub(
                        old_instance_pattern, instance_str, obj.active_material.name)
        
        if self.mask_tex:
            self.mask_tex.name = re.sub(old_instance_pattern, instance_str, self.mask_tex.name)
        if self.body_tex:
            self.body_tex.name = re.sub(old_instance_pattern, instance_str, self.body_tex.name)

    rig_instance: IntProperty(
        default=0,
        min=0,
        update=update_rig_instance,
        override={"LIBRARY_OVERRIDABLE"}
    )

    rig_name : StringProperty(
        name='Name',
        description='The identifier used for this rig instance',
        default='Human'
    )

# ============================================================================================
# HEAD ROTATION
# ============================================================================================

    head_lookpoint: FloatProperty(
        name="Use Look Point",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 will have the head rotate with CTRL-Head, 1 will make the head rotate towards CTRL-LookPoint",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# IK/FK SWITCHING
# ============================================================================================

    arm_ik_l: FloatProperty(
        name="Left Arm IK",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    arm_ik_r: FloatProperty(
        name="Right Arm IK",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    leg_ik_l: FloatProperty(
        name="Left Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    leg_ik_r: FloatProperty(
        name="Right Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# CONSTRAINTS
# ============================================================================================

    fk_constrain: BoolProperty(
        name="Limit FK Rotations",
        default=True,
        description="When true, FK controls have rotation constraints, not letting limbs bend beyond what they can realistically bend. Disable if you need to make an animation for breaking bones",
        override={"LIBRARY_OVERRIDABLE"}
    )

    root_is_ik_floor: BoolProperty(
        name="Root is IK Floor",
        default=True,
        description="When true, the leg IK controls cannot go below CTRL-Root",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Lookpoint Parenting

    def update_lookpoint_parent_index(self, context):
        self.lookpoint_parent_index = context.active_object.pz_human_props['lookpoint_parent']

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
        update=update_lookpoint_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    lookpoint_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_lookpoint_parent_object(self, context):
        update_lookpoint_parent_object(self, context)

    lookpoint_parent_object: PointerProperty(
        name="LookPoint Parent Object",
        type=Object,
        update=update_lookpoint_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Prop Parenting

    def update_left_prop_parent_index(self, context):
        self.left_prop_parent_index = context.active_object.pz_human_props['left_prop_parent']

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
        update=update_left_prop_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_prop_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_left_prop_parent_object(self, context):
        # update_left_prop_parent_object(self, context)
        pass

    left_prop_parent_object: PointerProperty(
        name="Left Prop Parent Object",
        type=Object,
        update=update_left_prop_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Prop Parenting

    def update_right_prop_parent_index(self, context):
        self.right_prop_parent_index = context.active_object.pz_human_props['right_prop_parent']

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
        update=update_right_prop_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_prop_parent_index: IntProperty(
        default=2
    )

    def update_right_prop_parent_object(self, context):
     #   update_right_prop_parent_object(self, context)
        pass

    right_prop_parent_object: PointerProperty(
        name="Right Prop Parent Object",
        type=Object,
        update=update_right_prop_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Backpack Parenting

    def update_backpack_parent_index(self, context):
        self.backpack_parent_index = context.active_object.pz_human_props['backpack_parent']

    backpack_parent: EnumProperty(
        name="Backpack Parent",
        description="What the backpack is parented to",
        items=[
            ('NONE', "None", "Backpack is not child of anything", 0),
            ('ROOT', "Root", "Backpack is the child of CTRL-Root", 1),
            ('SPINE', "Spine", "Backpack is the child of the spine", 2)
        ],
        default='SPINE',
        update=update_backpack_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    backpack_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Dress Parenting

    def update_dress_parent_index(self, context):
        self.dress_parent_index = context.active_object.pz_human_props['dress_parent']

    dress_parent: EnumProperty(
        name="Dress Parent",
        description="What the dress is parented to",
        items=[
            ('NONE', "None", "Dress is not child of anything", 0),
            ('ROOT', "Root", "Dress is the child of CTRL-Root", 1),
            ('LEGS', "Legs", "Dress bones are calculated between the legs", 2)
        ],
        default='LEGS',
        update=update_dress_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    dress_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Control Parenting

    def update_right_arm_ik_control_parent_index(self, context):
        self.right_arm_ik_control_parent_index = context.active_object.pz_human_props[
            'right_arm_ik_control_parent']

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
        update=update_right_arm_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_arm_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Pole Parenting

    def update_right_arm_ik_pole_parent_index(self, context):
        self.right_arm_ik_pole_parent_index = context.active_object.pz_human_props[
            'right_arm_ik_pole_parent']

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
        update=update_right_arm_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_arm_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Control Parenting

    def update_left_arm_ik_control_parent_index(self, context):
        self.left_arm_ik_control_parent_index = context.active_object.pz_human_props[
            'left_arm_ik_control_parent']

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
        update=update_left_arm_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_arm_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Pole Parenting

    def update_left_arm_ik_pole_parent_index(self, context):
        self.left_arm_ik_pole_parent_index = context.active_object.pz_human_props[
            'left_arm_ik_pole_parent']

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
        update=update_left_arm_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_arm_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Control Parenting

    def update_right_leg_ik_control_parent_index(self, context):
        self.right_leg_ik_control_parent_index = context.active_object.pz_human_props[
            'right_leg_ik_control_parent']

    right_leg_ik_control_parent: EnumProperty(
        name="Right Leg IK Control Parent",
        description="What the right leg IK control is parented to",
        items=[
            ('NONE', "None", "Right leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_right_leg_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_leg_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Pole Parenting

    def update_right_leg_ik_pole_parent_index(self, context):
        self.right_leg_ik_pole_parent_index = context.active_object.pz_human_props[
            'right_leg_ik_pole_parent']

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
        update=update_right_leg_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_leg_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Control Parenting

    def update_left_leg_ik_control_parent_index(self, context):
        self.left_leg_ik_control_parent_index = context.active_object.pz_human_props[
            'left_leg_ik_control_parent']

    left_leg_ik_control_parent: EnumProperty(
        name="Left Leg IK Control Parent",
        description="What the left leg IK control is parented to",
        items=[
            ('NONE', "None", "Left leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_left_leg_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_leg_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Pole Parenting

    def update_left_leg_ik_pole_parent_index(self, context):
        self.left_leg_ik_pole_parent_index = context.active_object.pz_human_props[
            'left_leg_ik_pole_parent']

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
        update=update_left_leg_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_leg_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  All IK Control Parent

    def update_all_ik_control_parent_index(self, context):
        self.all_ik_control_parent_index = context.active_object.pz_human_props[
            'all_ik_control_parent']
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
        update=update_all_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    all_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  All IK Pole Parent

    def update_all_ik_pole_parent_index(self, context):
        self.all_ik_pole_parent_index = context.active_object.pz_human_props[
            'all_ik_pole_parent']

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
        update=update_all_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    all_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Auto Wrist Twist

    wrist_twist_amount: FloatProperty(
        name="Wrist Twist Amount",
        description="How strongly the forearm follows the hand's X rotation. Can cause snapping issues at higher levels",
        default=0.25,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# MODEL
# ============================================================================================

    def update_selected_clothing_item(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        if self.selected_clothing_item != '':
            item = self.selected_clothing_item
            self.selected_clothing_item = ''
            
           # bpy.ops.ed.undo_push(message="Added manual clothing item")

            if item != '':
                for clothing_item in addon_prefs.pz_human_clothing_item_slots:
                    if clothing_item.name == item:
                        bpy.ops.zomboid.add_clothing_item(guid=clothing_item.guid)
                        break
            

    selected_clothing_item: StringProperty(
        name='Add Clothing Item',
        update=update_selected_clothing_item,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body Mesh

    '''
    Almost every clothing model has a different verson for both sexes.
    So, whenever the sex is changed, call functions that properly
    hide and show the correct sex's clothing in both the viewport and renders
    '''

    def update_body_texture(self, context):
        bpy.ops.zomboid.create_body_texture()

    def update_clothing_sex_visibility_settings(self, context):
        update_clothing_sex_visibility(self, context)
        update_clothing_sex_render(self, context)

    def update_prop_sex_visibility_settings(self, context):
        update_prop_sex_visibility(self, context)
        update_prop_sex_render(self, context)

    def update_hair_sex_visibility_settings(self, context):
        update_hair_sex_visibility(self, context)
        update_hair_sex_render(self, context)

    def update_sex_index(self, context):
        self.model_sex_index = 0 if self.model_sex == 'MALE' else 1
        self.update_clothing_sex_visibility_settings(context)
        self.update_prop_sex_visibility_settings(context)
        self.update_hair_sex_visibility_settings(context)
        self.update_body_texture(context)

    def update_body_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('COL-PZ_Human_Bodies' + instance_str)
        if col:
            col.hide_viewport = not self.show_body
            col.hide_render = not self.show_body

    model_sex: EnumProperty(
        name="Model Sex",
        description="Which human model to use",
        items=[
            ('MALE', "Male", "The male model and clothing", 0),
            ('FEMALE', "Female", "The female model and clothing", 1),
        ],
        default='MALE',
        update=update_sex_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    model_sex_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    show_body: BoolProperty(
        name="Body Enabled",
        default=True,
        description="Show the body of the character",
        update=update_body_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )
    use_skeleton: BoolProperty(
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Masking

    def update_mask_array(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_visibility_mask()

    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False),
        update=update_mask_array,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body Injuries

    def update_body_injury(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_body_texture()

    upper_torso_injury: EnumProperty(  # 0
        name='Upper Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_injury: EnumProperty(  # 1
        name='Lower Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_injury: EnumProperty(  # 2
        name='Left Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_injury: EnumProperty(  # 3
        name='Right Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_injury: EnumProperty(  # 4
        name='Left Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_injury: EnumProperty(  # 5
        name='Right Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_injury: EnumProperty(  # 6
        name='Left Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_injury: EnumProperty(  # 7
        name='Right Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_injury: EnumProperty(  # 8
        name='Head Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('BANDAGE', "Bandage", "Bandage injury texture", 1),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 2)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_injury: EnumProperty(  # 9
        name='Neck Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_injury: EnumProperty(  # 10
        name='Groin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_injury: EnumProperty(  # 11
        name='Left Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_injury: EnumProperty(  # 12
        name='Right Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_injury: EnumProperty(  # 13
        name='Left Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_injury: EnumProperty(  # 14
        name='Right Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_injury: EnumProperty(  # 15
        name='Left Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_injury: EnumProperty(  # 16
        name='Right Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Zombie Injuries

    def update_selected_zombie_injury(self, context):
        if self.selected_zombie_injury != 'NONE':
            addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

            new_injury = context.active_object.pz_human_zombie_injuries.add()
            new_injury.name = self.selected_zombie_injury
            new_injury.texture_path = addon_prefs.pz_human_zombie_injuries.get(self.selected_zombie_injury).texture_path

            self.selected_zombie_injury = 'NONE'
            bpy.ops.zomboid.create_body_texture()

    selected_zombie_injury: EnumProperty(
        name='Add Zombie Injury',
        items=filter_zombie_injuries,
        update=update_selected_zombie_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Bloodiness

    def update_bloodiness_mask(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_bloodiness_mask()

    upper_torso_bloodiness: FloatProperty(
        name='Upper Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_bloodiness: FloatProperty(
        name='Lower Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_bloodiness: FloatProperty(
        name='Left Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_bloodiness: FloatProperty(
        name='Right Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_bloodiness: FloatProperty(
        name='Left Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_bloodiness: FloatProperty(
        name='Right Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_bloodiness: FloatProperty(
        name='Left Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_bloodiness: FloatProperty(
        name='Right Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_bloodiness: FloatProperty(
        name='Head Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_bloodiness: FloatProperty(
        name='Neck Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_bloodiness: FloatProperty(
        name='Groin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_bloodiness: FloatProperty(
        name='Left Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_bloodiness: FloatProperty(
        name='Right Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_bloodiness: FloatProperty(
        name='Left Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_bloodiness: FloatProperty(
        name='Right Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_bloodiness: FloatProperty(
        name='Left Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_bloodiness: FloatProperty(
        name='Right Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    back_bloodiness: FloatProperty(
        name='Back Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Dirtiness

    def update_dirtiness_mask(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_dirtiness_mask()

    upper_torso_dirtiness: FloatProperty(
        name='Upper Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_dirtiness: FloatProperty(
        name='Lower Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_dirtiness: FloatProperty(
        name='Left Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_dirtiness: FloatProperty(
        name='Right Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_dirtiness: FloatProperty(
        name='Left Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_dirtiness: FloatProperty(
        name='Right Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_dirtiness: FloatProperty(
        name='Left Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_dirtiness: FloatProperty(
        name='Right Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_dirtiness: FloatProperty(
        name='Head Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_dirtiness: FloatProperty(
        name='Neck Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_dirtiness: FloatProperty(
        name='Groin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_dirtiness: FloatProperty(
        name='Left Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_dirtiness: FloatProperty(
        name='Right Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_dirtiness: FloatProperty(
        name='Left Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_dirtiness: FloatProperty(
        name='Right Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_dirtiness: FloatProperty(
        name='Left Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_dirtiness: FloatProperty(
        name='Right Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )
    back_dirtiness: FloatProperty(
        name='Back Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_mask,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body

    # Mesh ---------------------------------------

    current_character_model: StringProperty(
        default='MaleBody'
    )

    # Skin ---------------------------------------

    def update_skin_set(self, context):
        self.use_skeleton = self.skin_set == 'SKELETON'
        self.update_body_texture(context)

    skin_set: EnumProperty(
        name='Skin Set',
        items=[
            ('HUMAN', "Human", "Human and zombie textures", 0),
            ('SKELETON', "Skeleton", "Skeleton model and textures", 1),
            ('MANNEQUIN', "Mannequin", "Mannequin textures", 2),
            ('SCARECROW', "Scarecrow", "Long curly hair texture", 3),
        ],
        default='HUMAN',
        update=update_skin_set,
        override={"LIBRARY_OVERRIDABLE"}
    )

    skin_color: IntProperty(
        name="Skin Color",
        default=0,
        min=0,
        max=4,
        description="Which skin color texture set to use",
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    chest_hair: BoolProperty(
        name='Chest Hair',
        default=False,
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    zombification: IntProperty(
        name="Zombification",
        default=0,
        min=0,
        max=3,
        description="Level of zombification texture to use",
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    skeleton_type: IntProperty(
        name="Skeleton Type",
        default=0,
        min=0,
        max=2,
        description="Which skeleton texture to use",
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    mannequin_type: IntProperty(
        name="Mannequin Type",
        default=0,
        min=0,
        max=1,
        description="Which mannequin texture to use",
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Hair Mesh

    '''
    There are three hair types:
    - Male Hair
    - Female Hair
    - Beard

    Each category is only visible when the respective model sex is selected.
    For every hair type, there is a 'selected' property and a 'current' property.
    The 'selected' property is the desired hairstyle from the animator, and the 
    'current' property dicates which hair model will actually be used, given the 
    rig's current 'hat category' property and the selected hairstyle's 
    respective alternate hat hair model specified in the hairstyle XML
    '''

    current_hat_category: IntProperty(
        default=-1
    )

    # Male Hair ---------------------------------------

    def update_male_hair_style(self, context):
        if self.selected_male_hair_style == '':
            self.selected_male_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_male_hair_style: StringProperty(
        name="Male Hair",
        update=update_male_hair_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_male_hair_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Beard ---------------------------------------

    def update_beard_style(self, context):
        if self.selected_beard_style == '':
            self.selected_beard_style = 'None'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_beard_style: StringProperty(
        name="Beard",
        update=update_beard_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_beard_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Female Hair ---------------------------------------

    def update_female_hair_style(self, context):
        if self.selected_female_hair_style == '':
            self.selected_female_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_female_hair_style: StringProperty(
        name="Female Hair",
        update=update_female_hair_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_female_hair_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Stubble ---------------------------------------

    hair_stubble: BoolProperty(
        name='Hair Stubble',
        default=False,
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    beard_stubble: BoolProperty(
        name='Beard Stubble',
        default=False,
        update=update_body_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    # ---------------------------------------------------

    def update_hair_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('COL-PZ_Human_Hair' + instance_str)
        if col:
            col.hide_viewport = not self.show_hair
            col.hide_render = not self.show_hair

    show_hair: BoolProperty(
        name="Hair Enabled",
        default=True,
        description="Show the hair of the character",
        update=update_hair_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Hair Texture

    hair_color: FloatVectorProperty(
        name="Hair Color",
        subtype='COLOR',
        default=(0.25, 0.15, 0.05),
        min=0,
        max=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

    darken_zombie_hair: BoolProperty(
        name='Darken Zombie Hair',
        description='If character is a zombie, darken the hair color which is similar to how it looks in the game',
        default=True
    )

# ============================================================================================
# RANDOMNESS
# ============================================================================================

    random_zombie: BoolProperty(
        name='Zombie',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_skin_color: BoolProperty(
        name='Random Skin Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_hair_style: BoolProperty(
        name='Random Hair Style',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_hair_color: BoolProperty(
        name='Random Hair Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )
    natural_hair_color: BoolProperty(
        name='Natural Hair Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_beard_chance: IntProperty(
        name='Random Beard Chance',
        default=50,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    randomize_injuries: BoolProperty(
        name='Randomize Injuries',
        description='Randomly apply injuries on the body',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_injury_intensity: EnumProperty(
        name='Random Injury Intensity',
        description='How many injuries should appear on the body',
        items=[
            ('NONE', "None", "No injury textures", 0),
            ('MINOR', "Minor", "1-2 injury textures", 1),
            ('MODERATE', "Moderate", "3-4 injury textures", 2),
            ('SERIOUS', "Serious", "5-6 injury textures", 3),
            ('SEVERE', "Severe", "7-10 injury textures", 4),
            ('INSANE', "Insane", "11-16 injury textures", 5),
            ('RANDOM', "Random", "0-16 injury textures", 6)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_zombie_injury_intensity: EnumProperty(
        name='Random Zombie Injury Intensity',
        description='How many zombie injuries should appear on the body',
        items=[
            ('NONE', "None", "No injury textures", 0),
            ('INTACT', "Intact", "1-3 injury textures", 1),
            ('DAMAGED', "Damaged", "3-5 injury textures", 2),
            ('HACKED APART', "Hacked Apart", "5-15 injury textures", 3),
            ('MUTILATED', "Mutilated", "20-40 injury textures", 4),
            ('RENDED APART', "Rended Apart", "40-73 injury textures", 5),
            ('RANDOM', "Random", "0-73 injury textures", 6)
        ],
        default='DAMAGED',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_scratch_chance: FloatProperty(
        name='Random Scratch Chance',
        description='Weighted chance injury will be a scratch (chances are automatically evened out to add up to 100%)',
        default=65,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_laceration_chance: FloatProperty(
        name='Random Laceration Chance',
        description='Weighted chance injury will be a laceration (chances are automatically evened out to add up to 100%)',
        default=30,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bite_chance: FloatProperty(
        name='Random Bite Chance',
        description='Weighted chance injury will be a bite (chances are automatically evened out to add up to 100%)',
        default=5,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bandage_chance: FloatProperty(
        name='Random Bandage Chance',
        description='Weighted chance injury will be covered with a bandage',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bloody_bandage_chance: FloatProperty(
        name='Random Bloody Bandage Chance',
        description='Weighted chance a bandage will be bloody',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bloodiness_intensity: EnumProperty(
        name='Random Bloodiness Intensity',
        description='How much blood should appear on the body',
        items=[
            ('SOME', "Some", "A bit of bloodiness", 0),
            ('MODERATE', "Moderate", "Quite a bit of bloodiness", 1),
            ('LOTS', "Lots", "A lot of bloodiness", 2),
            ('DRENCHED', "Drenched", "Absolutely soaked in blood", 3)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_dirtiness_intensity: EnumProperty(
        name='Random Dirtiness Intensity',
        description='How much dirt should appear on the body',
        items=[
            ('SOME', "Some", "A bit of dirt", 0),
            ('MODERATE', "Moderate", "Quite a bit of dirt", 1),
            ('LOTS', "Lots", "A lot of dirt", 2),
            ('DISGUSTING', "Disgusting", "Absolutely covered in dirt", 3)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# SHADING
# ============================================================================================

    def update_shading_type_index(self, context):
        self.shading_type_index = context.active_object.pz_human_props['shading_type']

    shading_type: EnumProperty(
        name="Shading Type",
        description="What type of shading to use",
        items=[
            ('EMISSION', "Emission",
             "The model will be unshaded, which is more akin to what it will look like in Project Zomboid", 0),
            ('PBR', "PBR", "The model will have shading, which is good for more high graphical fidelity renders", 1),
            ('CUSTOM', "Custom", "The model will use a specified shading node group using the generated color and alpha from the main material. Make sure the group has 'Color' as the first input, 'Alpha' as the second, and 'Shader' as the only output", 2)
        ],
        default='EMISSION',
        update=update_shading_type_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    shading_type_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Emission

    emission_strength: FloatProperty(
        name="Emission Strength",
        description="How strong the emission shader is. Can be used to indicate if the character is in a darker area",
        default=1.0,
        min=0.0,
        max=5.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  PBR

    roughness: FloatProperty(
        name="Roughness",
        description="How 'rough' the model is. Lower values mean it is more reflective",
        default=0.9,
        min=0.0,
        max=1.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

    metallic: FloatProperty(
        name="Metallic",
        description="How 'metal' the model is",
        default=0.0,
        min=0.0,
        max=1.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Custom

    def update_custom_shading_group_name(self, context):
        

        p = context.active_object.pz_human_props

        mat_names = ['MAT-HumanBody', 'MAT-AccessoryMaterial', 'MAT-ClothingMaterial', 'MAT-Hair']

        for col in p.rig_collection.children_recursive:
            for obj in col.objects:
                if obj.active_material and any(name in obj.active_material.name for name in mat_names):
                    mat = obj.active_material
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links

                    selected_group = bpy.data.node_groups.get(
                        self.custom_shading_group_name)

                    if selected_group.bl_idname != 'ShaderNodeTree':
                        return

                    custom_shader_switch_node = nodes.get('NDE-MixCustomShader')
                    alpha_mix_node = nodes.get('NDE-AlphaMix')
                    dirt_mix_node = nodes.get('NDE-DirtMix')
                    group_node = nodes.get('NDE-CustomShader')

                    group_node.node_tree = selected_group

                    # Ensure that the node is correctly linked

                    if group_node.inputs.get('Color') is not None:
                        links.new(dirt_mix_node.outputs['Result'],
                                group_node.inputs['Color'])

                    if group_node.inputs.get('Alpha') is not None and 'HumanBody' in mat.name:
                        links.new(
                            alpha_mix_node.outputs['Result'], group_node.inputs['Alpha'])

                    if group_node.outputs.get('Shader') is not None:
                        links.new(group_node.outputs['Shader'],
                                custom_shader_switch_node.inputs[2])

    custom_shading_group_name: StringProperty(
        name="Custom Group Name",
        description="The name of the custom shading node group to use",
        default='SHD-Placeholder',
        update=update_custom_shading_group_name,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Texture Interpolation

    def update_texture_interpolation_index(self, context):
        self.texture_interpolation_index = context.active_object.pz_human_props[
            'texture_interpolation']

    texture_interpolation: EnumProperty(
        name="Texture Interpolation",
        description="Whether the textures have a more pixel-y look or a smoothed one",
        items=[
            ('LINEAR', "Linear", "Textures will be smoothed", 0),
            ('CLOSEST', "Closest", "Textures will be pixelated", 1)
        ],
        default='CLOSEST',
        update=update_texture_interpolation_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    texture_interpolation_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# COMPOSITING
# ============================================================================================

# ------------------------------------------------------------------------#
#  Outline

    use_outline: BoolProperty(
        name='Outline',
        description='Use the Compositor to create an outline around the model. Intended for still shots',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

    outline_size: IntProperty(
        name='Outline Size',
        description='How many pixels wide the outline is',
        default=4,
        min=1,
        max=8,
        override={"LIBRARY_OVERRIDABLE"}
    )

    outline_color: FloatVectorProperty(
        name="Outline Color",
        subtype='COLOR',
        default=(1.00, 1.00, 1.00),
        min=0,
        max=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# CONTROLS
# ============================================================================================

# ------------------------------------------------------------------------#
#  Misc. Widget Settings

    widgets_size: FloatProperty(
        name="Widget Size",
        default=2.5,
        min=1.0,
        max=10.0,
        subtype="PIXEL",
        description="The size of the control widgets",
        override={"LIBRARY_OVERRIDABLE"}
    )
    auto_hide_controls: BoolProperty(
        name="Auto Hide Controls",
        default=True,
        description="When true, control bones that can not contribute to the end result are automatically hidden",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Control Toggles

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

# ============================================================================================
# EXPORT
# ============================================================================================

    file_output_path: StringProperty(
        name="Output Directory",
        default="",
        description="The folder in which your animations will be stored. Most of the time, it should be in the 'anims_X' folder in your mod's media folder",
        subtype='DIR_PATH',
        override={"LIBRARY_OVERRIDABLE"}
    )
    batch_export: BoolProperty(
        name="Batch Export",
        default=True,
        description="If true, every individual action on Bip01 that has the substring from the Action Filter will be exported as a .glb file to the directory. If false, only export the active action on Bip01",
        override={"LIBRARY_OVERRIDABLE"}
    )
    action_filter: StringProperty(
        name="Action Filter",
        default="Bob_",
        description="If an action contains this substring, it will be exported as a .glb",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# TESTING
# ============================================================================================

    # def update_body_texture_slots(self, context):
    #     return update_body_texture_slots(self, context)

    body_texture_slot_active_index: IntProperty(
        default=-1
    )

    clothing_model_active_index: IntProperty(
        default=-1
    )

    accessory_model_active_index: IntProperty(
        default=-1
    )

    zombie_injury_active_index: IntProperty(
        default=-1
    )

    def update_clothing_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('COL-PZ_Human_Clothes' + instance_str)
        if col:
            col.hide_viewport = not self.show_clothing
            col.hide_render = not self.show_clothing

    show_clothing: BoolProperty(
        name="Clothing Enabled",
        default=True,
        update=update_clothing_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_prop_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('COL-PZ_Human_Props' + instance_str)
        if col:
            col.hide_viewport = not self.show_props
            col.hide_render = not self.show_props

    show_props: BoolProperty(
        name="Props Enabled",
        default=True,
        update=update_prop_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

    selected_outfit: StringProperty(
        name='Selected Outfit',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# DEBUG
# ============================================================================================

    debug_toggle: BoolProperty(
        name='Debug',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )
    halt_texture_updates: BoolProperty(
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )
