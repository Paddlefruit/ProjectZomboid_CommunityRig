# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_ZombieInjury(PropertyGroup):
    texture_path: StringProperty()

class PZ_BodyInjury(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()
    damage_type: StringProperty()
    sex: StringProperty()