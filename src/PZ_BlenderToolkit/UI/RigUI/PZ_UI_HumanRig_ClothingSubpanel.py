# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList
from ...Utility.PZ_AssetMethods import directx_import_available

class PZ_UL_EquippedClothingItemsList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        row = layout.row()
        row.label(text=item.name)

        if addon_data.debug:
            row.label(text=item.data.clothing_type)
            row.label(text=str(index))


def draw_clothing_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties

    # Draw the panel
    panel, panel_area = layout.panel("clothing_subpanel", default_closed=True)
    panel.label(text='Clothing')

    if panel_area:
        panel_area.enabled = directx_import_available() and addon_data.references_obtained

        split = panel_area.split()
        left_column = split.column()
        right_column = split.column()

        left_column.label(text='Add Clothing Item')
        left_column.prop_search(model_properties, 'selected_clothing_item', addon_data, 'pz_clothing_item_references', text='')

        right_column.scale_y = 2.0
        right_column.operator('zomboid.remove_all_clothing_items', text='Remove All')

        panel_area.label(text='Equipped Clothing Items')
        panel_area.template_list("PZ_UL_EquippedClothingItemsList", "pz_equipped_clothing_items_list", context.object, "pz_equipped_clothing_items", model_properties, "equipped_clothing_item_active_index")

        if model_properties.equipped_clothing_item_active_index > -1 and model_properties.equipped_clothing_item_active_index < len(context.object.pz_equipped_clothing_items):

            # Show the properties of each equipped item here:
            current_clothing_item = context.object.pz_equipped_clothing_items[model_properties.equipped_clothing_item_active_index]

            split = panel_area.split()
            left_column = split.column()
            right_column = split.column()

            left_column.label(text='Clothing Item Properties')
            box = left_column.box()
            box.prop(current_clothing_item, 'tint_color')

            # Show debug pointers
            if addon_data.debug:
                if current_clothing_item.data.clothing_type != 'BODYTEXTURE':
                    subpanel, subpanel_area = box.panel("clothing_pointers_subpanel", default_closed=True)
                    subpanel.label(text='Object Pointers')

                    if subpanel_area:
                        column = subpanel_area.column()
                        column.prop(current_clothing_item, 'male_model_object')
                        column.prop(current_clothing_item, 'female_model_object')
                        column.prop(current_clothing_item, 'image')
                        column.prop(current_clothing_item, 'material')

            # Operators for the clothing items
            right_column.label(text='Operators')

            op_column = right_column.column()
            op_column.scale_y = 2.0
            op_column.operator('zomboid.remove_clothing_item')

