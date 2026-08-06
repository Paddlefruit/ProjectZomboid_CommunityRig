# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

'''
This property group tracks specific skin texture assets
'''

class PZ_SkinTexture(PropertyGroup):
    texture_path: StringProperty()
    skin_tone: IntProperty(default=0)
    sex: StringProperty(default='BOTH')
    chest_hair : BoolProperty(default=False)
    body_type: StringProperty()
    zombification: IntProperty(default=0)
    origin: StringProperty()