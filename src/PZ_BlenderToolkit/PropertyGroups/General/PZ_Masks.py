# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_VisibilityMask(PropertyGroup):
    texture_path: StringProperty()
    mask_set: StringProperty(default='Vanilla')
    body_part: StringProperty()

class PZ_OverlayMask(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()

class PZ_HoleMask(PropertyGroup):
    texture_path: StringProperty()
    hole_type: StringProperty()
    body_part: StringProperty()