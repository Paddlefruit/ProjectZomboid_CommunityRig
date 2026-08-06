# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

'''
These property groups relate to the BodyLocation system used
in Project Zomboid, keeping track of which other body locations
it is exclusive with, needs to use an alternate model with, etc.
'''

class PZ_BodyLocationRef(PropertyGroup):
    pass


class PZ_BodyLocationProperties(PropertyGroup):
    
    # This body location will be hidden any of the body locations in this collection are occupied
    hide_locations: CollectionProperty(
        type=PZ_BodyLocationRef
    )

    # This body location will use an alternate model if any of the body locations in this collection are occupied
    alt_locations: CollectionProperty(
        type=PZ_BodyLocationRef
    )

    # This body location cannot be equipped if any of the body locations in this collection are occupied (No effect in Blender)
    exclusive_locations: CollectionProperty(
        type=PZ_BodyLocationRef
    )


class PZ_BodyLocation(PropertyGroup):

    name: StringProperty(
        default='NONE'
    )

    properties: PointerProperty(
        type=PZ_BodyLocationProperties
    )
    
    order: IntProperty()