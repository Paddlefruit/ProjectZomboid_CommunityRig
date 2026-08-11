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

class PZ_HumanRigInjuryProperties(PropertyGroup):

    ### BODY INJURIES ###

    def update_body_injury(self, context):
        model_properties = context.active_object.pz_model_properties
        if not model_properties.stop_texture_updates:
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

    ### ZOMBIE INJURIES ###

    def update_selected_zombie_injury(self, context):
        if self.selected_zombie_injury != 'NONE':
            addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

            new_injury = context.active_object.pz_zombie_injuries.add()
            new_injury.name = self.selected_zombie_injury
            new_injury.texture_path = addon_data.pz_zombie_injury_references.get(self.selected_zombie_injury).texture_path

            self.selected_zombie_injury = 'NONE'
            bpy.ops.zomboid.create_body_texture()

    selected_zombie_injury: EnumProperty(
        name='Add Zombie Injury',
        items=filter_zombie_injuries,
        update=update_selected_zombie_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )

    zombie_injury_active_index: IntProperty(
        default=-1
    )
    
    ### BLOODINESS ###

    def update_bloodiness_mask(self, context):
            model_properties = context.active_object.pz_model_properties
            if not model_properties.stop_texture_updates:
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

    ### DIRTINESS ###

    def update_dirtiness_mask(self, context):
        model_properties = context.active_object.pz_model_properties
        if not model_properties.stop_texture_updates:
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