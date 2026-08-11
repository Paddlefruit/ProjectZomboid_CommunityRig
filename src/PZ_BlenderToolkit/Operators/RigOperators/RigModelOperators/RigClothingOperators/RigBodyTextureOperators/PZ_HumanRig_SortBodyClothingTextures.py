# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

class PZ_HumanRig_SortBodyClothingTextures(Operator):
    bl_idname = "zomboid.sort_body_clothing_textures"
    bl_label = "Sort Body Clothing Textures"
    bl_description = "Sorts the body clothing textures with the same order as Project Zomboid's renderer"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        body_locations = addon_data.pz_body_locations
        equipped_clothing = context.active_object.pz_equipped_clothing_items
        body_clothing_textures = [item for item in equipped_clothing if item.data.clothing_type == 'BODYTEXTURE' and item.data.body_location]

        # Unfortunately there's not a simple way to reassign a collection, so we have to remake it here

        # Create a temporary list that will be sorted later
        temp_list = []

        # Store important data that the clothing item will need to remember
        for item in body_clothing_textures:
            texture_list = []
            for choice in item.data.texture_choices:
                texture_list.append(choice.texture_path)
                
            temp_list.append({
                'name' : item.name,
                'tintable' : item.data.tintable,
                'tint_color' : list(item.tint_color),
                'decal_group' : item.data.decal_group,
                'body_location' : item.data.body_location,
                'origin' : item.data.origin,
                'textures' : texture_list,

                'render_order' : body_locations.get(item.data.body_location).order
            })

        # Sort the temp list
        sorted_list = sorted(
            temp_list,
            key=lambda x: x['render_order']
        )

        # Remove all body clothing textures from the equipped clothing
        for i in range(len(equipped_clothing) - 1, -1, -1):
            clothing = equipped_clothing[i]

            if clothing.data.clothing_type == 'BODYTEXTURE' and item.data.body_location:
                equipped_clothing.remove(i)

        # Recreate the body clothing textures
        for item in sorted_list:
            sorted_item = equipped_clothing.add()

            sorted_item.name = item['name']
            sorted_item.data.clothing_type = 'BODYTEXTURE'
            sorted_item.data.tintable = item['tintable']
            sorted_item.tint_color = item['tint_color']
            sorted_item.data.decal_group = item['decal_group']
            sorted_item.data.body_location = item['body_location']
            sorted_item.data.origin = item['origin']

            for path in item['textures']:
                new_choice = sorted_item.data.texture_choices.add()
                new_choice.texture_path = path

        return ({'FINISHED'})