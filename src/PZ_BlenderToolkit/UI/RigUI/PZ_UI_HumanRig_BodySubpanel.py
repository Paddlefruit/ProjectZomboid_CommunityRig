# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def draw_body_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    model_properties = context.active_object.pz_model_properties

    # Draw the panel
    panel, panel_area = layout.panel("body_subpanel", default_closed=False)
    panel.label(text='Body')

    if panel_area:

        # The property dictating the model's sex
        sex_row = panel_area.row()
        sex_row.scale_y = 1.5
        sex_row.prop(model_properties, 'model_sex', expand=True)

        split = panel_area.split()
        left_column = split.column()
        right_column = split.column()

        left_column.label(text='Human Subtype')
        left_column.prop(model_properties, 'human_subtype', expand=True)

        # Show different properties based on the selected human subtype
        match model_properties.human_subtype:

            case 'HUMAN':
                right_column.label(text='Human Properties')
                box = right_column.box()

                box.label(text='Skin Tone')
                box.prop(model_properties, 'skin_tone', expand=True)

                box.label(text='Zombification')
                box.prop(model_properties, 'zombification', expand=True)

                if model_properties.model_sex == 'MALE' and model_properties.zombification == 'NONE':
                    box.prop(model_properties, 'chest_hair')

            case 'SKELETON':
                right_column.label(text='Skeleton Properties')
                box = right_column.box()

                box.label(text='Type')
                box.prop(model_properties, 'skeleton_type', expand=True)

            case 'MANNEQUIN':
                right_column.label(text='Mannequin Properties')
                box = right_column.box()

                box.label(text='Color')
                box.prop(model_properties, 'mannequin_type', expand=True)