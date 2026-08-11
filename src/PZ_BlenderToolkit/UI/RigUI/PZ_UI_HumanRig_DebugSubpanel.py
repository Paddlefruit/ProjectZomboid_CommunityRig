# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import UIList

class PZ_UL_UsedBodyLocationList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

def draw_debug_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties

    # Draw the panel
    panel, panel_area = layout.panel("debug_subpanel", default_closed=True)
    panel.label(text='Debug')

    if panel_area:

        # General debug properties
        panel_area.label(text='General')
        box = panel_area.box()
        box.prop(model_properties, 'current_hat_category')
        box.prop(model_properties, 'use_skeleton')
        box.prop(model_properties, 'stop_texture_updates')

        # Show the properties for the visibility masks if debug is enabled
        if model_properties.human_subtype != 'SKELETON':
            panel_area.separator()
            panel_area.label(text='Visibility Masks')
            box = panel_area.box()
            grid_flow = box.grid_flow(align=True, columns=3, even_columns=True, even_rows=True)

            # Show the proper body part name for each mask
            mask_name_dict = {
                0 : 'Head',
                1 : 'Chest',
                2 : 'Groin',
                3 : 'Left Arm',
                4 : 'Left Hand',
                5 : 'Right Arm',
                6 : 'Right Hand',
                7 : 'Left Leg',
                8 : 'Left Foot',
                9 : 'Right Leg',
                10 : 'Right Foot',
                11 : 'Dress',
                12 : 'Chest',
                13 : 'Midriff',
                14 : 'Belt',
                15 : 'Groin',
                16 : 'Full Body'
            }

            for i in range(len(model_properties.visibility_mask_array)):
                grid_flow.prop(model_properties, 'visibility_mask_array', toggle=True, text=str(i) + ' (' + mask_name_dict[i] + ')', index=i)

        # List of used body locations
        panel_area.label(text='Body Locations')
        box = panel_area.box()
        box.label(text='Used Locations')
        box.template_list("PZ_UL_UsedBodyLocationList", "pz_used_body_location_list", context.object, "pz_used_body_locations", model_properties, "used_body_location_active_index")