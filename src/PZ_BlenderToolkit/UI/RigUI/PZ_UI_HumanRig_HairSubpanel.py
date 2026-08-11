# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def draw_hair_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties

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
            left_column.prop(model_properties, 'selected_male_hair_style', text='')
            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_male_hair_style)
        else:
            left_column.prop(model_properties, 'selected_female_hair_style', text='')
            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_female_hair_style)

        if model_properties.model_sex == 'MALE':
            left_column.label(text='Beard Style')
            left_column.prop(model_properties, 'selected_beard_style', text='')

            if addon_data.debug:
                left_column.label(text='Current: ' + model_properties.current_beard_style)

        # Hair color properties
        right_column.label(text='Hair Color')
        right_column.prop(model_properties, 'hair_color', text='')
        right_column.prop(model_properties, 'darken_zombie_hair')

        
