# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

class PZ_HumanRig_SortBodyClothingTextures(Operator):
    bl_idname = "zomboid.sort_body_clothing_textures"
    bl_label = "Sort Body Clothing Textures"
    bl_description = "Sorts the body clothing textures with the same order as Project Zomboid's renderer"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        props = context.active_object.pz_human_props
        clothes = context.active_object.pz_human_body_texture_slots

        # Unfortunately there's not a simple way to reassign a collection, so we have to remake it here
        temp_list = []

        for item in clothes:
            temp_list.append({
                'name' : item.name,
                'texture_path' : item.texture_path,
                'tintable' : item.tintable,
                'tint_color' : list(item.tint_color),
                'decal_group' : item.decal_group,
                'render_order' : item.render_order,
                'origin' : item.origin
            })

        sorted_list = sorted(
            temp_list,
            key=lambda x: x['render_order']
        )

        clothes.clear()

        for item in sorted_list:
            sorted_item = clothes.add()

            sorted_item.name = item['name']
            sorted_item.texture_path = item['texture_path']
            sorted_item.tintable = item['tintable']
            sorted_item.tint_color = item['tint_color']
            sorted_item.decal_group = item['decal_group']
            sorted_item.render_order = item['render_order']
            sorted_item.origin = item['origin']

        return ({'FINISHED'})