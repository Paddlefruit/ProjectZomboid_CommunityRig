# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to a rig's model
and appearance inside Blender
'''

class PZ_HumanRigModelProperties(PropertyGroup):
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

    random_tint_color: BoolProperty(
        name='Random Tint Color',
        description='Randomize the tint of all tintable clothing generated by this outfit',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )

    static_tint_color: FloatVectorProperty(
        name="Tint Color",
        description='Tint all tintable clothing generated by this outfit with this color',
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0,
        max=1,
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
# LIST INDICIES
# ============================================================================================

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

# ============================================================================================
# VISIBILITY
# ============================================================================================

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

# ============================================================================================
# MISC.
# ============================================================================================

    selected_outfit: StringProperty(
        name='Selected Outfit',
        override={"LIBRARY_OVERRIDABLE"}
    )

    halt_texture_updates: BoolProperty(
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )