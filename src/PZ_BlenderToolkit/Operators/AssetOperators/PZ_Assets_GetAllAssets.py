# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from bpy.types import Operator

from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders

class PZ_Assets_GetAllAssets(Operator):
    bl_idname = "zomboid.get_all_assets"
    bl_label = "Get All Assets"
    bl_description = "Get all the relevant references to the assets needed to import data from Zomboid to Blender"

    @classmethod
    def poll(cls, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        return addon_prefs.pz_directory != ''

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        get_zomboid_asset_folders.cache_clear()

        bpy.ops.zomboid.clear_all_assets()

        # bpy.ops.zomboid.get_attachment_points()
        # bpy.ops.zomboid.get_attachments()
        bpy.ops.zomboid.get_skin_textures()
        bpy.ops.zomboid.parse_body_location_lua()
        bpy.ops.zomboid.parse_clothing_xmls()
        bpy.ops.zomboid.parse_body_location_txt()
        bpy.ops.zomboid.parse_outfit_xmls()
        bpy.ops.zomboid.get_skin_textures()
        bpy.ops.zomboid.parse_hair_style_xmls()
        bpy.ops.zomboid.get_injuries()
    

        addon_prefs.assets_parsed = True

        return ({'FINISHED'})