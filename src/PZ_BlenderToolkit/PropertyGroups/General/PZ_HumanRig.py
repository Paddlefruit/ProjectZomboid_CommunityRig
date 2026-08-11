# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty
import re

from ...Utility.PZ_UpdateMethods import *

'''
This property group is used be the scene to keep track of all of the
current human rigs in the scene, and the objects that compose them
'''

class PZ_HumanRig(PropertyGroup):

    # The name of this rig instance
    name: StringProperty()
    rig_object: PointerProperty(
        type=Object
    )
    
