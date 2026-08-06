# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_ModDirectory(PropertyGroup):

    # The name of the mod
    name: StringProperty(
        default='Unknown Mod'
    )

    # Whether this mod directory will be taken into account when gathering asset references
    active: BoolProperty(
        default=False
    )

    # The author of the mod
    author: StringProperty(
        default='Unknown Author'
    )

    # The path to the mod in your workshop folder
    mod_dir: StringProperty(
        subtype='DIR_PATH'
    )

    # What the latest version folder found is
    latest_pz_version: FloatProperty(
        default=42.0
    )