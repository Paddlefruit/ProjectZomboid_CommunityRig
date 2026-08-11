# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_OutfitList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split()
        left_column = split.column()
        right_column = split.column()

        left_column.label(text=item.name)
        right_column.label(text=item.sex)

def draw_outfits_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    # Draw the panel
    panel, panel_area = layout.panel("outfits_subpanel", default_closed=True)
    panel.label(text='Outfits')
    panel.label(text=str(len(addon_data.pz_outfit_references)))

    if panel_area:
        if addon_data.debug:
            panel_area.operator('zomboid.parse_outfit_xmls')
            panel_area.prop(addon_data, 'outfit_reference_active_index')

        panel_area.template_list("PZ_UL_OutfitList", "pz_outfit_list", addon_data, "pz_outfit_references", addon_data, "outfit_reference_active_index")

        # The sub box with the clothing item properties
        if addon_data.outfit_reference_active_index > -1 and addon_data.outfit_reference_active_index < len(addon_data.pz_clothing_item_references) - 1:

            # The specific item's data we want to see
            item = addon_data.pz_outfit_references[addon_data.outfit_reference_active_index]

            panel_area.separator(factor=0.5)
            panel_area.label(text='Outfit Properties')

            box = panel_area.box()

            split = box.split(factor=0.25)
            left_column = split.column()
            right_column = split.column()

            # General outfit properties
            if addon_data.debug:
                left_column.label(text='GUID:')
                right_column.label(text=item.guid)
            
            left_column.label(text='Origin:')
            right_column.label(text=item.origin)

            if addon_data.debug:
                left_column.label(text='Random Top:')
                right_column.label(text=str(item.random_top))

            if addon_data.debug:
                left_column.label(text='Random Pants:')
                right_column.label(text=str(item.random_pants))

            if addon_data.debug:
                left_column.label(text='Allow Tint:')
                right_column.label(text=str(item.allow_tint))

            if addon_data.debug:
                left_column.label(text='Allow Shirt Decal:')
                right_column.label(text=str(item.allow_shirt_decal))

            if len(item.outfit_items) > 0:
                # The probabilities and chances for each outfit item
                box.label(text='Outfit Items')
                subbox = box.box()

                for outfit_item in item.outfit_items:
                    subbox.label(text=str(round(outfit_item.probability * 100, 2)) + '% chance for one of the following:')
                    choice_box = subbox.box()

                    for choice in outfit_item.choices:
                        choice_box.label(text=choice.name)
