# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

'''
This property group tracks specific stubble texture assets
'''

class PZ_StubbleTexture(PropertyGroup):
    texture_path: StringProperty()
    stubble_type: StringProperty()
    sex: StringProperty()
    origin: StringProperty()