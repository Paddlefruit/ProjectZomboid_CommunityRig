# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains all properties relating to
how the rig's models are shaded in Blender
'''

class PZ_HumanRigShadingProperties(PropertyGroup):
    def update_shading_type_index(self, context):
        self.shading_type_index = context.active_object.pz_shading_properties['shading_type']

    shading_type: EnumProperty(
        name="Shading Type",
        description="What type of shading to use",
        items=[
            ('UNSHADED', "Unshaded", "The model will be unshaded, which is more akin to what it will look like in Project Zomboid", 0),
            ('PBR', "PBR", "The model will have shading, which is good for more high graphical fidelity renders", 1),
            ('CUSTOM', "Custom", "The model will use a specified shading node group using the generated color and alpha from the main material. Make sure the group has 'Color' as the first input, 'Alpha' as the second, and 'Shader' as the only output", 2)
        ],
        default='PBR',
        update=update_shading_type_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    shading_type_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Unshaded

    emission_strength: FloatProperty(
        name="Emission Strength",
        description="How strong the emission shader is. Can be used to indicate if the character is in a darker area",
        default=1.0,
        min=0.0,
        max=5.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  PBR

    roughness: FloatProperty(
        name="Roughness",
        description="How 'rough' the model is. Lower values mean it is more reflective",
        default=1.0,
        min=0.0,
        max=1.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

    metallic: FloatProperty(
        name="Metallic",
        description="How 'metal' the model is",
        default=0.0,
        min=0.0,
        max=1.0,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Custom

    def update_custom_shading_group_name(self, context):
        object_pointers = context.active_object.pz_object_pointers

        mat_names = ['MAT-HumanBody', 'MAT-AccessoryMaterial', 'MAT-ClothingMaterial', 'MAT-Hair']

        for col in object_pointers.rig_collection.children_recursive:
            for obj in col.objects:
                if obj.active_material and any(name in obj.active_material.name for name in mat_names):
                    mat = obj.active_material
                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links

                    selected_group = bpy.data.node_groups.get(
                        self.custom_shading_group_name)

                    if selected_group.bl_idname != 'ShaderNodeTree':
                        return

                    custom_shader_switch_node = nodes.get('NDE-MixCustomShader')
                    alpha_mix_node = nodes.get('NDE-AlphaMix')
                    dirt_mix_node = nodes.get('NDE-DirtMix')
                    group_node = nodes.get('NDE-CustomShader')

                    group_node.node_tree = selected_group

                    # Ensure that the node is correctly linked

                    if group_node.inputs.get('Color') is not None:
                        links.new(dirt_mix_node.outputs['Result'],
                                group_node.inputs['Color'])

                    if group_node.inputs.get('Alpha') is not None and 'HumanBody' in mat.name:
                        links.new(
                            alpha_mix_node.outputs['Result'], group_node.inputs['Alpha'])

                    if group_node.outputs.get('Shader') is not None:
                        links.new(group_node.outputs['Shader'],
                                custom_shader_switch_node.inputs[2])

    custom_shading_group_name: StringProperty(
        name="Custom Group Name",
        description="The name of the custom shading node group to use",
        default='SHD-Placeholder',
        update=update_custom_shading_group_name,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Texture Interpolation

    def update_texture_interpolation_index(self, context):
        self.texture_interpolation_index = context.active_object.pz_shading_properties['texture_interpolation']

    texture_interpolation: EnumProperty(
        name="Texture Interpolation",
        description="Whether the textures have a more pixel-y look or a smoothed one",
        items=[
            ('LINEAR', "Linear", "Textures will be smoothed", 0),
            ('CLOSEST', "Closest", "Textures will be pixelated", 1)
        ],
        default='CLOSEST',
        update=update_texture_interpolation_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    texture_interpolation_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )