# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from bpy.types import Operator

class PZ_Assets_ClearAllAssets(Operator):
    bl_idname = "zomboid.clear_all_assets"
    bl_label = "Clear All Assets"
    bl_description = "Clear all the parsed asset entries"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        addon_prefs.clothing_item_slot_active_index = -1
        addon_prefs.outfit_slot_active_index = -1
        addon_prefs.skin_texture_active_index = -1
        addon_prefs.stubble_texture_active_index = -1
        addon_prefs.visibility_mask_active_index = -1
        addon_prefs.overlay_mask_active_index = -1
        addon_prefs.hair_style_slot_active_index = -1
        addon_prefs.beard_style_slot_active_index = -1
     #   addon_prefs.decal_slot_active_index = -1
        addon_prefs.body_location_active_index = -1
     #   addon_prefs.imported_animation_active_index = -1

        addon_prefs.pz_human_clothing_item_slots.clear()
        addon_prefs.pz_human_outfit_slots.clear()
        addon_prefs.pz_human_skin_textures.clear()
        addon_prefs.pz_human_stubble_textures.clear()
        addon_prefs.pz_human_visibility_masks.clear()
        addon_prefs.pz_human_overlay_masks.clear()
        addon_prefs.pz_human_hair_style_slots.clear()
        addon_prefs.pz_human_male_hair_styles.clear()
        addon_prefs.pz_human_female_hair_styles.clear()
        addon_prefs.pz_human_beard_styles.clear()
     #   addon_prefs.pz_human_decals.clear()
     #   addon_prefs.pz_human_decal_groups.clear()
        addon_prefs.pz_human_body_locations.clear()
      #  addon_prefs.pz_human_imported_animations.clear()

        addon_prefs.assets_parsed = False

       # bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})