# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from bpy.types import Operator

class PZ_Assets_ClearAllAssets(Operator):
    bl_idname = "zomboid.clear_all_assets"
    bl_label = "Clear All Assets"
    bl_description = "Clear all the parsed asset entries"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        addon_data.clothing_item_reference_active_index = -1
        addon_data.outfit_reference_active_index = -1
        addon_data.skin_texture_reference_active_index = -1
        addon_data.stubble_texture_reference_active_index = -1
        addon_data.visibility_mask_reference_active_index = -1
        addon_data.overlay_mask_reference_active_index = -1
        addon_data.hair_style_reference_active_index = -1
        addon_data.beard_style_reference_active_index = -1
     #   addon_data.decal_reference_active_index = -1
        addon_data.body_location_active_index = -1
      #   addon_data.attachment_point_active_index = -1
      #   addon_data.attachment_active_index = -1
     #   addon_data.imported_animation_active_index = -1

        addon_data.pz_clothing_item_references.clear()
        addon_data.pz_outfit_references.clear()
        addon_data.pz_skin_texture_references.clear()
        addon_data.pz_stubble_texture_references.clear()
        addon_data.pz_visibility_mask_references.clear()
        addon_data.pz_overlay_mask_references.clear()
        addon_data.pz_hair_style_references.clear()
        addon_data.pz_male_hair_style_references.clear()
        addon_data.pz_female_hair_style_references.clear()
        addon_data.pz_beard_style_references.clear()
     #   addon_data.pz_human_decals.clear()
     #   addon_data.pz_human_decal_groups.clear()
        addon_data.pz_body_locations.clear()
      #   addon_data.pz_attachment_points.clear()
      #   addon_data.pz_attachments.clear()
      #  addon_data.pz_game_animation_references.clear()

        addon_data.references_obtained = False

       # bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})