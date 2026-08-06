# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_OutfitItemChoices(PropertyGroup):
    guid: StringProperty()
    name: StringProperty()


class PZ_OutfitItem(PropertyGroup):
    probability: FloatProperty(default=1.0)
    choices: CollectionProperty(type=PZ_OutfitItemChoices)


class PZ_Outfit(PropertyGroup):
    name: StringProperty()
    search_name: StringProperty()
    guid: StringProperty()
    sex: StringProperty()
    random_top: BoolProperty()
    random_pants: BoolProperty()
    allow_tint: BoolProperty()
    allow_shirt_decal: BoolProperty()
    origin: StringProperty()

    outfit_items: CollectionProperty(type=PZ_OutfitItem)