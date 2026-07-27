# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel

class PZ_HumanRig_ShadingPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_shading_panel"
    bl_label = "Shading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

        column = layout.column()
        row = column.row()
        row.scale_y = 1.5
        row.prop(p, "shading_type", expand=True)

        column.separator()

        row = column.row()

        match p.shading_type_index:
            case 0:
                row.prop(p, 'emission_strength')
            case 1:
                row.prop(p, 'roughness')
                row.prop(p, 'metallic')
            case 2:
                row.prop_search(p, 'custom_shading_group_name',
                                bpy.data, 'node_groups')

                selected_group = bpy.data.node_groups.get(
                    p.custom_shading_group_name)

                if selected_group.bl_idname != 'ShaderNodeTree':
                    column.label(
                        text='Selected group is not a Shader Node group',
                        icon='WARNING_LARGE'
                    )
                else:
                    inputs = 0
                    outputs = 0
                    for item in list(selected_group.interface.items_tree):
                        if item.in_out == 'INPUT':
                            if inputs > 1:
                                column.label(
                                    text='Inputs after the second input will not be read',
                                    icon='QUESTION_LARGE'
                                )
                            if inputs == 0:
                                if item.name != 'Color':
                                    column.label(
                                        text='The first input is not named \'Color\'',
                                        icon='WARNING_LARGE'
                                    )
                                if item.socket_type != 'NodeSocketColor':
                                    column.label(
                                        text='The first input is not a Color type',
                                        icon='WARNING_LARGE'
                                    )
                            elif inputs == 1:
                                if item.name != 'Alpha':
                                    column.label(
                                        text='The first input is not named \'Alpha\'')
                                if item.socket_type != 'NodeSocketFloat':
                                    column.label(
                                        text='The first input is not a Float type',
                                        icon='WARNING_LARGE'
                                    )
                            inputs = inputs + 1
                        elif item.in_out == 'OUTPUT':
                            if outputs > 0:
                                column.label(
                                    text='Outputs after the first output will not be evaluated',
                                    icon='QUESTION_LARGE'
                                )
                            if outputs == 0:
                                if item.name != 'Shader':
                                    column.label(
                                        text='The first output is not named \'Shader\'',
                                        icon='WARNING_LARGE'
                                    )
                                if item.socket_type != 'NodeSocketShader':
                                    column.label(
                                        text='The first output is not a Shader type',
                                        icon='WARNING_LARGE'
                                    )

        column.separator()

        row = column.row()
        row.prop(p, 'texture_interpolation')