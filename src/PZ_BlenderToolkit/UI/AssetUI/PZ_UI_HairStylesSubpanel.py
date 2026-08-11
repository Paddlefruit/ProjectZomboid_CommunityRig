# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_HairStyleList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout.split()
        left_column = split.column()
        right_column = split.column()

        left_column.label(text=item.name)
        right_column.label(text=item.sex)

def draw_hair_styles_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    # Draw the panel
    panel, panel_area = layout.panel("hair_styles_subpanel", default_closed=True)
    panel.label(text='Hair Styles')
    panel.label(text=str(len(addon_data.pz_hair_style_references)))

    if panel_area:
        if addon_data.debug:
            panel_area.operator('zomboid.parse_hair_style_xmls')
            panel_area.prop(addon_data, 'hair_style_reference_active_index')

        panel_area.template_list("PZ_UL_HairStyleList", "pz_hair_style_list", addon_data, "pz_hair_style_references", addon_data, "hair_style_reference_active_index")

        # The sub box with the clothing item properties
        if addon_data.hair_style_reference_active_index > -1 and addon_data.hair_style_reference_active_index < len(addon_data.pz_hair_style_references) - 1:

            # The specific item's data we want to see
            item = addon_data.pz_hair_style_references[addon_data.hair_style_reference_active_index]

            panel_area.separator(factor=0.5)
            panel_area.label(text='Outfit Properties')

            box = panel_area.box()

            split = box.split(factor=0.25)
            left_column = split.column()
            right_column = split.column()

            # General hair style properties
            left_column.label(text='Origin:')
            right_column.label(text=item.origin)

            if addon_data.debug:
                left_column.label(text='Hair Level:')
                right_column.label(text=str(item.level))

            if addon_data.debug:
                left_column.label(text='Model Type:')
                right_column.label(text=item.model_type)

            left_column.label(text='Model Path:')
            right_column.prop(item, 'model_path', text='')

            left_column.label(text='Texture Path:')
            right_column.prop(item, 'texture_path', text='')

            # The properties pertaining to hat styles
            if addon_data.debug:
                if len(item.hat_styles) > 0:

                    box.label(text='Hat Groups')
                    subbox = box.box()
                    box_split = subbox.split(factor=0.25)
                    box_left_column = box_split.column()
                    box_right_column = box_split.column()

                    for hat_style in item.hat_styles:
                        box_left_column.label(text='Group ' + str(hat_style.hat_group) + ' Style:')
                        box_right_column.label(text=hat_style.style_name)
                        




            
