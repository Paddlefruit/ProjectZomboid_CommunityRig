# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to
how the rig will export animations to PZ
'''

class PZ_HumanRigExportProperties(PropertyGroup):

    file_output_path: StringProperty(
        name="Output Directory",
        default="",
        description="The folder in which your animations will be stored. Most of the time, it should be in the 'anims_X' folder in your mod's media folder",
        subtype='DIR_PATH',
        override={"LIBRARY_OVERRIDABLE"}
    )

    batch_export: BoolProperty(
        name="Batch Export",
        default=True,
        description="If true, every individual action on Bip01 that has the substring from the Action Filter will be exported as a .glb file to the directory. If false, only export the active action on Bip01",
        override={"LIBRARY_OVERRIDABLE"}
    )
    
    action_filter: StringProperty(
        name="Action Filter",
        default="Bob_",
        description="If an action contains this substring, it will be exported as a .glb",
        override={"LIBRARY_OVERRIDABLE"}
    )