# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def draw_shading_subpanel(context, layout):

    # Get all data
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    shading_properties = context.active_object.pz_shading_properties

    # Draw the panel
    panel, panel_area = layout.panel("shading_subpanel", default_closed=True)
    panel.label(text='Shading')

    if panel_area:

        split = panel_area.split()
        left_column = split.column()
        right_column = split.column()

        left_column.label(text='Shading Type')
        left_column.prop(shading_properties, 'shading_type', expand=True)

        # Show different properties based on the selected shading type
        match shading_properties.shading_type:

            case 'UNSHADED':
                right_column.label(text='Unshaded Properties')
                box = right_column.box()
                
                box.label(text='Emission Strength')
                box.prop(shading_properties, 'emission_strength', text='')

            case 'PBR':
                right_column.label(text='PBR Properties')
                box = right_column.box()
                
                box.label(text='Roughness')
                box.prop(shading_properties, 'roughness', text='')

                box.label(text='Metallic')
                box.prop(shading_properties, 'metallic', text='')

            case 'CUSTOM':
                right_column.label(text='Custom Shader Properties')
                box = right_column.box()

                box.label(text='Shader Group')
                box.prop_search(shading_properties, 'custom_shading_group_name', bpy.data, 'node_groups', text='')

                selected_group = bpy.data.node_groups.get(shading_properties.custom_shading_group_name)

                if selected_group:
                    if selected_group.bl_idname != 'ShaderNodeTree':
                        box.label(
                            text='Selected group is not a Shader Node group',
                            icon='WARNING_LARGE'
                        )
                    else:
                        inputs = 0
                        outputs = 0
                        for item in list(selected_group.interface.items_tree):
                            if item.in_out == 'INPUT':
                                if inputs > 1:
                                    box.label(
                                        text='Inputs after the second input will not be read',
                                        icon='QUESTION_LARGE'
                                    )
                                if inputs == 0:
                                    if item.name != 'Color':
                                        box.label(
                                            text='The first input is not named \'Color\'',
                                            icon='WARNING_LARGE'
                                        )
                                    if item.socket_type != 'NodeSocketColor':
                                        box.label(
                                            text='The first input is not a Color type',
                                            icon='WARNING_LARGE'
                                        )
                                elif inputs == 1:
                                    if item.name != 'Alpha':
                                        box.label(
                                            text='The first input is not named \'Alpha\'')
                                    if item.socket_type != 'NodeSocketFloat':
                                        box.label(
                                            text='The first input is not a Float type',
                                            icon='WARNING_LARGE'
                                        )
                                inputs = inputs + 1
                            elif item.in_out == 'OUTPUT':
                                if outputs > 0:
                                    box.label(
                                        text='Outputs after the first output will not be evaluated',
                                        icon='QUESTION_LARGE'
                                    )
                                if outputs == 0:
                                    if item.name != 'Shader':
                                        box.label(
                                            text='The first output is not named \'Shader\'',
                                            icon='WARNING_LARGE'
                                        )
                                    if item.socket_type != 'NodeSocketShader':
                                        box.label(
                                            text='The first output is not a Shader type',
                                            icon='WARNING_LARGE'
                                        )
        # Texture Interpolation
        panel_area.label(text='Texture Interpolation')
        panel_area.prop(shading_properties, 'texture_interpolation', expand=True)

