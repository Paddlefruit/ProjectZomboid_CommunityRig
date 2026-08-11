# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_HairStyleHatStyle(PropertyGroup):
    hat_group: IntProperty()
    style_name: StringProperty()

class PZ_HairStyle(PropertyGroup):
    name: StringProperty()
    model_path: StringProperty(
        subtype='FILE_PATH'
    )
    model_type: StringProperty()
    texture_path: StringProperty(
        subtype='FILE_PATH'
    )
    sex: StringProperty()
    level: IntProperty()
    hat_styles: CollectionProperty(type=PZ_HairStyleHatStyle)
    origin: StringProperty()