# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup, Object
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty, PointerProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to a rig's
animation capabilities
'''

class PZ_HumanRigAnimationProperties(PropertyGroup):

    ### WRIST TWIST ###

    # The factor that dictates how much the forearm will follow the hand for each arm
    wrist_twist_amount: FloatProperty(
        name="Wrist Twist Amount",
        description="How strongly the forearm follows the hand's X rotation. Can cause snapping issues at higher levels",
        default=0.25,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        override={"LIBRARY_OVERRIDABLE"}
    )

    ### HEAD ROTATION ###
        
    # The factor of how much the head will use CTRL-LookPoint instead of CTRL-Head for rotation
    head_lookpoint: FloatProperty(
        name="Use Look Point",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 will have the head rotate with CTRL-Head, 1 will make the head rotate towards CTRL-LookPoint"
    )

    ### IK/FK SWITCHING ###

    # These factors dictate how much a limb will use IK instead of FK
    arm_ik_l: FloatProperty(
        name="Left Arm IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
    )
    arm_ik_r: FloatProperty(
        name="Right Arm IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
    )
    leg_ik_l: FloatProperty(
        name="Left Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
    )
    leg_ik_r: FloatProperty(
        name="Right Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
    )

    ### CONSTRAINTS ###

    fk_constrain: BoolProperty(
        name="Limit FK Rotations",
        default=True,
        description="When true, FK controls have rotation constraints, not letting limbs bend beyond what they can realistically bend. Disable if you need to make an animation for breaking bones"
    )

    root_is_ik_floor: BoolProperty(
        name="Root is IK Floor",
        default=True,
        description="When true, the leg IK controls cannot go below CTRL-Root"
    )