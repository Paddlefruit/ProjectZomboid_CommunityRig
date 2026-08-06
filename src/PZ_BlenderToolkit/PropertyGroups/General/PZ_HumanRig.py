# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

'''
This property group is used be the scene to keep track of all of the
current human rigs in the scene
'''

class PZ_HumanRig(PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(type=Object)