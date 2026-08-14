# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def draw_hair_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties

    pz_icons = context.window_manager.pz_icons

    # Draw the panel
    panel, panel_area = layout.panel("hair_subpanel", default_closed=True)
    panel.label(text='Hair')

    if panel_area:

        # The stubble properties
        panel_area.prop(model_properties, 'hair_stubble')
        if model_properties.model_sex == 'MALE':
            panel_area.prop(model_properties, 'beard_stubble')

        panel_area.separator(type='LINE')
        
        split = panel_area.split()
        left_column = split.column()
        right_column = split.column()

        # Style selection properties
        left_column.label(text='Hair Style')
        if model_properties.model_sex == 'MALE':
            subrow = left_column.row(align=True)
            subrow.prop_search(model_properties, 'selected_male_hair_style', addon_data, 'pz_male_hair_style_references', text='')
            op = subrow.operator('zomboid.randomize_hair_model', text='', icon_value=pz_icons["pz_random_icon"].icon_id)
            op.hair_type = 'M'
            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_male_hair_style)
        else:
            subrow = left_column.row(align=True)
            subrow.prop_search(model_properties, 'selected_female_hair_style', addon_data, 'pz_female_hair_style_references', text='')
            op = subrow.operator('zomboid.randomize_hair_model', text='', icon_value=pz_icons["pz_random_icon"].icon_id)
            op.hair_type = 'F'
            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_female_hair_style)

        if model_properties.model_sex == 'MALE':
            left_column.label(text='Beard Style')
            subrow = left_column.row(align=True)
            subrow.prop_search(model_properties, 'selected_beard_style', addon_data, 'pz_beard_style_references', text='')
            op = subrow.operator('zomboid.randomize_hair_model', text='', icon_value=pz_icons["pz_random_icon"].icon_id)
            op.hair_type = 'B'
            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_beard_style)

        # Hair color properties
        right_column.label(text='Hair Color')
        subrow = right_column.row(align=True)
        subrow.prop(model_properties, 'hair_color', text='')
        subrow.operator('zomboid.randomize_hair_color', text='', icon_value=pz_icons["pz_random_icon"].icon_id)

        right_column.prop(model_properties, 'darken_zombie_hair')

        
