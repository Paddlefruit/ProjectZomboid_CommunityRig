# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
from bpy.types import Operator 

class PZ_Assets_RemoveModDirectories(Operator):
    bl_idname = "zomboid.remove_mod_directories"
    bl_label = "Remove Mod Directories"
    bl_description = "Removes all of the loaded mod directories"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        addon_data.pz_mod_directories.clear()
        addon_data.mod_directory_active_index = -1
        return ({'FINISHED'})