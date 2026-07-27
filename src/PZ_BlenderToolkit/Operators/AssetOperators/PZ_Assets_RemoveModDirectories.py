# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
from bpy.types import Operator 

class PZ_Assets_RemoveModDirectories(Operator):
    bl_idname = "zomboid.remove_mod_directories"
    bl_label = "Remove Mod Directories"
    bl_description = "Removes all of the loaded mod directories"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        addon_prefs.pz_human_mod_directory_slots.clear()
        addon_prefs.mod_directory_slot_active_index = -1
        return ({'FINISHED'})