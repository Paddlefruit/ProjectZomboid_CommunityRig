# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

'''
These property groups relate to the shirt decal system
used in Project Zomboid
'''

class PZ_ShirtDecal(PropertyGroup):
    texture_path: StringProperty()
    x_pos: IntProperty()
    y_pos: IntProperty()
    width: IntProperty()
    height: IntProperty()


class PZ_ShirtDecalGroup(PropertyGroup):
    decals: CollectionProperty(type=PZ_ShirtDecal)