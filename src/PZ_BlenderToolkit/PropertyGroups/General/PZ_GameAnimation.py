# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_GameAnimation(PropertyGroup):
    file_type: StringProperty()
    anim_path: StringProperty()
    origin: StringProperty()
    character_type: StringProperty()