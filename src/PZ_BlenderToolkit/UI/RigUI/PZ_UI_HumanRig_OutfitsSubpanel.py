# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Panel

def draw_outfits_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties
    random_properties = context.active_object.pz_random_properties

    pz_icons = context.window_manager.pz_icons

    # Draw the panel
    panel, panel_area = layout.panel("outfits_subpanel", default_closed=True)
    panel.label(text='Outfits')

    if panel_area:

        subbox = panel_area.box()
        subbox.label(text='Selected Outfit')
        subbox.prop_search(model_properties, 'selected_outfit', addon_data, 'pz_outfit_references', item_search_property='search_name', text='')

        # Subpanel for outfit settings
        subpanel, subpanel_area = subbox.panel("outfit_settings_subpanel", default_closed=True)
        subpanel.label(text='Outfit Settings')

        if subpanel_area:

            # Random Outfit Box
            subbox = subpanel_area.box()

            subbox.prop(random_properties, 'random_skin_tone', text='Random Skin Tone')
            subbox.prop(random_properties, 'random_zombie', text='Zombie')

            # Random Injury Properties
            subbox.label(text='Injuries')
            injury_box = subbox.box()
            injury_box.prop(random_properties, 'randomize_outfit_injuries', text='Randomize Injuries')
            injury_box.popover(panel='VIEW3D_PT_pz_human_rig_random_injury_popover', text='Options', icon_value=pz_icons["pz_random_icon"].icon_id)

            # Random Hair Properties
            subbox.label(text='Hair')
            hair_box = subbox.box()
            hair_box.prop(random_properties, 'random_hair_style')
            hair_box.prop(random_properties, 'random_beard_chance')

            hair_box.separator(type='LINE')
            subsplit = hair_box.split()
            subsplit.prop(random_properties, 'random_hair_color')
            subrow = subsplit.row()
            subrow.prop(random_properties, 'natural_hair_color')
            subrow.enabled = random_properties.random_hair_color

            # Random Tint Properties
            subbox.label(text='Tinting')
            tint_box = subbox.box()
            subsplit = tint_box.split()
            subsplit.prop(random_properties, 'random_tint_color')
            subrow = subsplit.row()
            subrow.prop(random_properties, 'static_tint_color')
            subrow.enabled = not random_properties.random_tint_color

        subcolumn = subbox.column(align=True)
        op_row = subcolumn.row()
        op_row.scale_y = 2.0
        op_row.operator('zomboid.apply_outfit')

        op_row = subcolumn.row()
        op_row.scale_y = 1.5
        op_row.operator('zomboid.apply_random_outfit', icon_value=pz_icons["pz_random_icon"].icon_id)

        
