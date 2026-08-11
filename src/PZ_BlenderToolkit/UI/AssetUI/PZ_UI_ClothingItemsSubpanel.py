# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_ClothingItemList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

def draw_clothing_items_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

    # Draw the panel
    panel, panel_area = layout.panel("clothing_items_subpanel", default_closed=True)
    panel.label(text='Clothing Items')
    panel.label(text=str(len(addon_data.pz_clothing_item_references)))

    if panel_area:
        if addon_data.debug:
            panel_area.operator('zomboid.parse_clothing_xmls')
            panel_area.prop(addon_data, 'clothing_item_reference_active_index')

        panel_area.template_list("PZ_UL_ClothingItemList", "pz_clothing_item_list", addon_data, "pz_clothing_item_references", addon_data, "clothing_item_reference_active_index")

        # The sub box with the clothing item properties
        if addon_data.clothing_item_reference_active_index > -1 and addon_data.clothing_item_reference_active_index < len(addon_data.pz_clothing_item_references) - 1:

            # The specific item's data we want to see
            item = addon_data.pz_clothing_item_references[addon_data.clothing_item_reference_active_index]

            panel_area.separator(factor=0.5)
            panel_area.label(text='Clothing Item Properties')

            box = panel_area.box()

            split = box.split(factor=0.25)
            left_column = split.column()
            right_column = split.column()

            # Misc general properties
            if addon_data.debug:
                left_column.label(text='GUID')
                right_column.label(text=item.guid)

            if addon_data.debug:
                left_column.label(text='Clothing Type:')
                right_column.label(text=item.clothing_type)

            left_column.label(text='Origin:')
            right_column.label(text=item.origin)

            if addon_data.debug:
                left_column.label(text='Body Location:')
                right_column.label(text=item.body_location)

            if addon_data.debug:
                left_column.label(text='Decal Group:')
                right_column.label(text=item.decal_group)

            if addon_data.debug:
                left_column.label(text='Hat Category:')
                right_column.label(text=str(item.hat_category))


            # Model properties
            if item.clothing_type != 'BODYTEXTURE':
                box.label(text='Model Proeprties')
                subbox = box.box()
                box_split = subbox.split(factor=0.25)
                box_left_column = box_split.column()
                box_right_column = box_split.column()

                if addon_data.debug:
                    box_left_column.label(text='Model Type:')
                    box_right_column.label(text=item.model_type)

                box_left_column.label(text='Male Model Path:')
                box_right_column.prop(item, 'male_model_path', text='')

                box_left_column.label(text='Female Model Path:')
                box_right_column.prop(item, 'female_model_path', text='')

                if item.male_alt_model_path and item.female_alt_model_path:
                    box_left_column.label(text='Male Alt Model Path:')
                    box_right_column.prop(item, 'male_alt_model_path', text='')

                    box_left_column.label(text='Female Alt Model Path:')
                    box_right_column.prop(item, 'female_alt_model_path', text='')

                if addon_data.debug:
                    if item.clothing_type == 'ATTACHMENT':
                        box_left_column.label(text='Attach Bone:')
                        box_right_column.label(text=item.attach_bone)


            # Texture Properties
            if len(item.texture_choices) > 0:
                box.label(text='Texture Proeprties')
                subbox = box.box()
                box_split = subbox.split(factor=0.25)
                box_left_column = box_split.column()
                box_right_column = box_split.column()

                # Misc Texture Properties
                box_left_column.label(text='Tintable:')
                box_right_column.label(text=str(item.tintable))

                if addon_data.debug:
                    box_left_column.label(text='Can Have Holes:')
                    box_right_column.label(text=str(item.can_have_holes))

                # Visibility Masks
                if addon_data.debug:
                    mask_str = ''
                    for index, mask in enumerate(item.visibility_mask_array):
                        if mask:
                            mask_str += str(index) + ', '

                    if mask_str:
                        mask_str = mask_str.removesuffix(', ')
                        box_left_column.label(text='Visibility Masks:')
                        box_right_column.label(text=mask_str)

                # Texture Choices
                for index, choice in enumerate(item.texture_choices):
                    box_left_column.label(text='Choice ' + str(index + 1) + ':')
                    box_right_column.prop(choice, 'texture_path', text='')

                





