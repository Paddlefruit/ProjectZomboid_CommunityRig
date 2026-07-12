# pyright: reportInvalidTypeForm=false
'''
PROJECT ZOMBOID HUMAN RIG V4.0.0 SCRIPT

This python script manages all aspects of the rig, as well as the supplementary tools 
it uses to perform its functions. The reason it is all consolidated in one massive file
is for ease of portability, as a single packed python script is easier to move around than
an addon. For easier viewing, it is reccomended to open it in an IDE like VSCode, where you
can use foldable regions.

Written by Paddlefruit
DirectX Importer by SaintBaron

---------------------------------------------------------------------------------------
!!!! NOTICE !!!!
If you are importing the rig as an asset from another Blend file, this script will NOT 
automatically run on import. You need to restart the Blend file and accept the auto-run
popup for it to begin execution; otherwise, you cannot interract with the rig.

Make sure that you set your Project Zomboid directory in the 'Zomboid Assets' tab
found in the 'Scene' tab in the Properties Editor, and then make sure that you 
press the 'Parse All Assets' button found in the same tab after doing so.
Otherwise, the operators will have no idea what they are looking for.

Additionally, make sure that you have the 'DirectX .X Importer' extension by SaintBaron
installed and enabled. It can be found on the official Blender Extensions website 
(https://extensions.blender.org/add-ons/io-directx-x/)

If you run into any issues, errors, or questions, please contact me at the Official Project 
Zomboid Discord or the PZ Modding Discord @Paddlefruit

---------------------------------------------------------------------------------------
CONFIRMED WORKING VERSIONS

- Blender 5.1.2
- DirectX .X Importer 1.3.1
- Project Zomboid 42.19.0

RECCOMENDED MODS

- The Frockin' Splendor! Series
- Spongies Open Jackets
- Spongies Hair
- Fluffy Hair
- MedievalZ

INCOMPATIBLE MODS

- Yaki's Hair Salon
- Yaki's Barbershop
- SoulFilcher's Beautifying Time

Some mods like Yaki's store their data in weird ways that are near impossible to parse through.
If you encounter errors on importing a modded asset, try to ascertain which mod it was and
remove it from your mod directories, then parse the assets again.
'''

# =================================================================================================================================================
# =================================================================================================================================================

# region Importing

import bpy  # type: ignore
import os
import sys
import math
import time
import re
import functools
import xml.etree.ElementTree as ET
import numpy as np

from bpy.types import PropertyGroup, Collection, Object, Operator, Panel, UIList, Scene, Image, Material  # type: ignore
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty  # type: ignore
from bpy_extras import anim_utils  # type: ignore
from bpy.app.handlers import persistent # type: ignore

from random import randint, choices, random, uniform
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion  # type: ignore

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Objects

'''
These PropertyGroups are the data structures used by the rig to manage and consolidate
data across various areas.
'''

# ============================================================================================
# RIG OBJECT
# ============================================================================================


class PZ_HumanRigObject(PropertyGroup):
    name: StringProperty()
    obj: PointerProperty(type=Object)

# ============================================================================================
# BODY LOCATION
# ============================================================================================


class PZ_BodyLocationRef(PropertyGroup):
    pass


class PZ_BodyLocationProperties(PropertyGroup):
    # This body location will be hidden any of the body locations in this collection are occupied
    hide_locations: CollectionProperty(type=PZ_BodyLocationRef)
    # This body location will use an alternate model if any of the body locations in this collection are occupied
    alt_locations: CollectionProperty(type=PZ_BodyLocationRef)
    # This body location cannot be equipped if any of the body locations in this collection are occupied (No effect in Blender)
    exclusive_locations: CollectionProperty(type=PZ_BodyLocationRef)


class PZ_BodyLocation(PropertyGroup):
    name: StringProperty(default='NONE')
    properties: PointerProperty(type=PZ_BodyLocationProperties)

# ============================================================================================
# SKIN TEXTURE
# ============================================================================================


class PZ_SkinTexture(PropertyGroup):
    texture_path: StringProperty()
    skin_tone: IntProperty(default=0)
    sex: StringProperty(default='BOTH')
    chest_hair : BoolProperty(default=False)
    body_type: StringProperty()
    zombification: IntProperty(default=0)
    origin: StringProperty()

# ============================================================================================
# STUBBLE TEXTURE
# ============================================================================================


class PZ_StubbleTexture(PropertyGroup):
    texture_path: StringProperty()
    stubble_type: StringProperty()
    sex: StringProperty()
    origin: StringProperty()

# ============================================================================================
# SHIRT DECAL SLOT
# ============================================================================================


class PZ_ShirtDecal(PropertyGroup):
    texture_path: StringProperty()
    x_pos: IntProperty()
    y_pos: IntProperty()
    width: IntProperty()
    height: IntProperty()


class PZ_ShirtDecalGroup(PropertyGroup):
    decals: CollectionProperty(type=PZ_ShirtDecal)

# ============================================================================================
# BODY TEXTURE SLOT
# ============================================================================================


class PZ_BodyTextureSlot(PropertyGroup):
    name: StringProperty(default="New Body Texture")
    texture_path: StringProperty(name="Texture Path")
    tintable: BoolProperty(name="Tintable", default=False)
    tint_color: FloatVectorProperty(
        name="Tint Color", subtype='COLOR', default=(1.0, 1.0, 1.0), max=1.0, min=0.0)
    opacity: FloatProperty(name="Opacity", default=1.0,
                           min=0.0, max=1.0, subtype='FACTOR')
    decal_group: StringProperty(default='None')
    bloodiness: FloatProperty(default=0.0, min=0.0, max=1.0)
    origin: StringProperty()
    # decal : PointerProperty(type=PZ_ShirtDecal)

# ============================================================================================
# ZOMBIE INJURY
# ============================================================================================


class PZ_ZombieInjury(PropertyGroup):
    texture_path: StringProperty()

# ============================================================================================
# BODY INJURY
# ============================================================================================


class PZ_BodyInjury(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()
    damage_type: StringProperty()
    sex: StringProperty()

# ============================================================================================
# VISIBILITY MASK
# ============================================================================================


class PZ_VisibilityMask(PropertyGroup):
    texture_path: StringProperty()
    mask_set: StringProperty(default='Vanilla')
    body_part: StringProperty()

# ============================================================================================
# OVERLAY MASK
# ============================================================================================


class PZ_OverlayMask(PropertyGroup):
    texture_path: StringProperty()
    body_part: StringProperty()

# ============================================================================================
# CLOTHING MESH SLOT
# ============================================================================================


class PZ_ClothingMeshSlot(PropertyGroup):

    def update_model_visibility(self, context):
        update_clothing_sex_visibility(self, context)

    def update_model_render(self, context):
        update_clothing_sex_render(self, context)

    name: StringProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_path: StringProperty()
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    slot_hide_render: BoolProperty(
        name="Visible in Render",
        default=True,
        update=update_model_render
    )
    slot_hide_viewport: BoolProperty(
        name="Visible in Viewport",
        default=True,
        update=update_model_visibility
    )
    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )
    bloodiness: FloatProperty(default=0.0, min=0.0, max=1.0)
    hat_category: IntProperty()
    origin: StringProperty()

# ============================================================================================
# PROP MESH SLOT
# ============================================================================================


class PZ_PropMeshSlot(PropertyGroup):

    def update_model_visibility(self, context):
        update_prop_sex_visibility(self, context)

    def update_model_render(self, context):
        update_prop_sex_render(self, context)

    name: StringProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_path: StringProperty()
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    attach_bone: StringProperty()
    slot_hide_render: BoolProperty(
        name="Visible in Render",
        default=True,
        update=update_model_render
    )
    slot_hide_viewport: BoolProperty(
        name="Visible in Viewport",
        default=True,
        update=update_model_visibility
    )
    hat_category: IntProperty()
    origin: StringProperty()

# ============================================================================================
# CLOTHING ITEM SLOT
# ============================================================================================


class PZ_ClothingItemTextureChoices(PropertyGroup):
    texture_path: StringProperty()


class PZ_ClothingItemSlot(PropertyGroup):
    name: StringProperty()
    guid: StringProperty()
    is_body_texture: BoolProperty()
    male_model_path: StringProperty()
    female_model_path: StringProperty()
    model_type: StringProperty()
    texture_choices: CollectionProperty(type=PZ_ClothingItemTextureChoices)
    tintable: BoolProperty(
        name="Tintable",
        default=False
    )
    tint_color: FloatVectorProperty(
        name="Tint Color",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        max=1.0,
        min=0.0
    )
    attach_bone: StringProperty()
    static: BoolProperty()
    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )
    hat_category: IntProperty()
    decal_group: StringProperty(default='None')
  #  body_location: PointerProperty(type=PZ_BodyLocation)
    origin: StringProperty()

# ============================================================================================
# OUTFIT SLOT
# ============================================================================================


class PZ_OutfitItemChoices(PropertyGroup):
    guid: StringProperty()
    name: StringProperty()


class PZ_OutfitItem(PropertyGroup):
    probability: FloatProperty(default=1.0)
    choices: CollectionProperty(type=PZ_OutfitItemChoices)


class PZ_OutfitSlot(PropertyGroup):
    name: StringProperty()
    search_name: StringProperty()
    guid: StringProperty()
    sex: StringProperty()
    random_top: BoolProperty()
    random_pants: BoolProperty()
    allow_tint: BoolProperty()
    allow_shirt_decal: BoolProperty()
    origin: StringProperty()

    outfit_items: CollectionProperty(type=PZ_OutfitItem)

# ============================================================================================
# HAIR STYLE SLOT
# ============================================================================================


class PZ_HairStyleHatStyle(PropertyGroup):
    hat_group: IntProperty()
    style_name: StringProperty()


class PZ_HairStyleSlot(PropertyGroup):
    name: StringProperty()
    model_path: StringProperty()
    texture_path: StringProperty()
    sex: StringProperty()
    level: IntProperty()
    hat_styles: CollectionProperty(type=PZ_HairStyleHatStyle)
    origin: StringProperty()

# ============================================================================================
# IMPORTED ANIMATION
# ============================================================================================


class PZ_ImportedAnimation(PropertyGroup):
    file_type: StringProperty()
    anim_path: StringProperty()
    origin: StringProperty()
    character_type: StringProperty()

# ============================================================================================
# MOD DIRECTORY SLOT
# ============================================================================================


class PZ_ModDirectorySlot(PropertyGroup):
    name: StringProperty(
        default='Unknown Mod'
    )
    active: BoolProperty(
        default=False
    )
    author: StringProperty(
        default='Unknown Author'
    )
    mod_dir: StringProperty(
        subtype='DIR_PATH'
    )
    latest_pz_version: FloatProperty(
        default=42.0
    )

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Methods


'''
These are the various functions that do not warrant their own Operators.
'''

# region Path Methods

# ============================================================================================
# IS DIRECTX IMPORTER ENABLED
# ============================================================================================


def directx_import_available():
    checks = ['bl_ext.blender_org.io_directx_x',
              'bl_ext.user_default.io_directx_x'
              ]
    for check in checks:
        if check in bpy.context.preferences.addons.keys():
            return True
    return False

# ============================================================================================
# GET ZOMBOID ASSET
# ============================================================================================


@functools.lru_cache(maxsize=256)
def get_zomboid_asset_folders(context, parent_path):
    g = context.scene.pz_human_global_props
    mods = context.scene.pz_human_mod_directory_slots

    results = []

    vanilla_results = [dir for dir in Path(g.pz_directory).rglob(
        parent_path, case_sensitive=False) if dir.is_dir()]
    for path in vanilla_results:
        results.append((path, 'Project Zomboid'))

    for mod in mods:
        if mod.active:
            print(mod)
            candidate_paths = [
                Path(mod.mod_dir),
                Path(mod.mod_dir).parent / 'common'
            ]
            for path in candidate_paths:
                modded_results = [dir for dir in path.rglob(
                    parent_path, case_sensitive=False) if dir.is_dir()]
                for path in modded_results:
                    results.append((path, mod.name))
    return results


def get_zomboid_asset(context, item_path):
    item_path = item_path.replace('\\', '/')
    parent_name = Path(item_path).parent.name
    asset_name = Path(item_path).stem

    for folder, mod_name in get_zomboid_asset_folders(context, parent_name):
        for file in folder.glob(f"{asset_name}.*", case_sensitive=False):
            if file.is_file():
                return file, file.suffix.lower()

    print('Could not find ' + item_path)
    return (None, None)

# endregion

# region Texture & Material Methods

# ============================================================================================
# FLIP UVS
# ============================================================================================


def flip_uvs(obj):
    uv_layer = obj.data.uv_layers.active.data

    for poly in obj.data.polygons:
        for loop_index in poly.loop_indices:
            uv_coord = uv_layer[loop_index].uv
            uv_coord.x = 1.0 - uv_coord.x

# ============================================================================================
# CREATE MODEL MATERIAL
# ============================================================================================


def create_model_material(context, texture_path, category, hair_type=None):
    p = context.active_object.pz_human_props

    m_list = None
    m = None

    match category:
        case 'PROP':
            m_list = context.active_object.pz_human_prop_mesh_slots
            m = m_list[p.prop_mesh_slot_active_index]
        case 'CLOTHING':
            m_list = context.active_object.pz_human_clothing_mesh_slots
            m = m_list[p.clothing_mesh_slot_active_index]

    instance_str = ' (' + str(p.rig_instance) + ')'

    mat_name = ''
    match category:
        case 'PROP':
            mat_name = 'MAT-PropMaterial' + \
                str(p.prop_mesh_slot_active_index) + instance_str
        case 'CLOTHING':
            mat_name = 'MAT-ClothingMaterial' + \
                str(p.clothing_mesh_slot_active_index) + instance_str
        case 'BODY':
            mat_name = 'MAT-HumanBody' + instance_str
        case 'HAIR':
            match hair_type:
                case 'M':
                    mat_name = 'MAT-MaleHair' + instance_str
                case 'F':
                    mat_name = 'MAT-FemaleHair' + instance_str
                case 'B':
                    mat_name = 'MAT-Beard' + instance_str
                

    old_mat = bpy.data.materials.get(mat_name)
    if old_mat:
        bpy.data.materials.remove(old_mat, do_unlink=True)

    # if Path(texture_path).is_file():
    mat = bpy.data.materials.get('MAT-PZMaterialBoilerplate').copy()

    mat.name = mat_name

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Get the existing nodes

    tex_node = nodes.get('NDE-TexSlot')
    mask_node = nodes.get('NDE-MaskData')
    tint_node = nodes.get('NDE-TexTint')
    emission_node = nodes.get('NDE-EmissionShader')
    pbr_node = nodes.get('NDE-PBRShader')
    custom_shader_node = nodes.get('NDE-CustomShader')
    mix_transparent_emission_node = nodes.get('NDE-MixTransparentEmission')
    mix_custom_shader_node = nodes.get('NDE-MixCustomShader')
    dirt_mix_node = nodes.get('NDE-DirtMix')
    alpha_mix_node = nodes.get('NDE-AlphaMix')

    ## Set the texture node properties and drivers ##

    if category != 'BODY':
        tex_node.image = bpy.data.images.load(texture_path)
    else:
        tex_node.image = p.body_tex
    
    mask_node.image = p.mask_tex

    print(context.active_object)

    # Interpolation Driver
    path = 'nodes["NDE-TexSlot"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.texture_interpolation_index"

    ### Set the color tint node properties ###
    tint_node.data_type = 'RGBA'
    tint_node.blend_type = 'MULTIPLY'

    if category == 'CLOTHING' or category == 'PROP':
        # Factor Driver
        path = 'nodes["NDE-TexTint"].inputs[0].default_value'
        fcurve = mat.node_tree.driver_add(path)
        driver = fcurve.driver
        driver.type = 'AVERAGE'

        var = driver.variables.new()
        target = var.targets[0]
        target.id = context.active_object
        if category == 'PROP':
            target.data_path = "pz_human_prop_mesh_slots[" + \
                str(p.prop_mesh_slot_active_index) + "].tintable"
        else:
            target.data_path = "pz_human_clothing_mesh_slots[" + \
                str(p.prop_mesh_slot_active_index) + "].tintable"
    elif category == 'HAIR':
        tint_node.inputs[0].default_value = 1.0
    else:
        tint_node.inputs[0].default_value = 0.0

    # Color Drivers

    if category == 'CLOTHING' or category == 'PROP' or category == 'HAIR':
        for i in range(3):
            path = 'nodes["NDE-TexTint"].inputs[7].default_value'
            fcurve = mat.node_tree.driver_add(path, i)
            driver = fcurve.driver
            driver.type = 'AVERAGE'

            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object

            if category == 'CLOTHING':
                target.data_path = "pz_human_clothing_mesh_slots[" + str(
                p.prop_mesh_slot_active_index) + "].tint_color[" + str(i) + "]"
            if category == 'PROP':
                target.data_path = "pz_human_prop_mesh_slots[" + str(
                p.prop_mesh_slot_active_index) + "].tint_color[" + str(i) + "]"
            elif category == 'HAIR':
                target.data_path = "pz_human_props.hair_color[" + str(i) + "]"


    ### Set the mix shader node properties ###

    # Factor Driver
    path = 'nodes["NDE-MixShader"].inputs[0].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.shading_type_index"

    ### Set the emission node properties ###

    # Strength Driver
    path = 'nodes["NDE-EmissionShader"].inputs[1].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.emission_strength"

    ### Set the PBR node properties ###

    # Roughness Driver
    path = 'nodes["NDE-PBRShader"].inputs[2].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.roughness"

    # Metallic Driver
    path = 'nodes["NDE-PBRShader"].inputs[1].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.metallic"

    ### Set the custom shader node properties ###
    selected_group = bpy.data.node_groups.get(
        context.active_object.pz_human_props.custom_shading_group_name)
    
    if selected_group:
        custom_shader_node.node_tree = selected_group

        if custom_shader_node.inputs.get('Color') is not None:
            links.new(dirt_mix_node.outputs['Result'],
                    custom_shader_node.inputs['Color'])

        if custom_shader_node.outputs.get('Shader') is not None:
            links.new(custom_shader_node.outputs['Shader'],
                    mix_custom_shader_node.inputs[2])

    # Make sure that the links are correct

    ### Set the mix custom shader node properties ###
    path = 'nodes["NDE-MixCustomShader"].inputs[0].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'SCRIPTED'

    var = driver.variables.new()
    var.name = 'factor'
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.shading_type_index"

    driver.expression = 'factor == 2'

    ### Set the interpolations on all the mask and overlay textures

    # Mask Data
    path = 'nodes["NDE-MaskData"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.texture_interpolation_index"

    # Blood Overlay
    path = 'nodes["NDE-BloodTex"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.texture_interpolation_index"

    # Dirt Overlay
    path = 'nodes["NDE-DirtTex"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_human_props.texture_interpolation_index"

    # Skip overlay links if this is an accessory or hair

    if category == 'PROP' or category == 'HAIR':
        links.new(tint_node.outputs['Result'], emission_node.inputs['Color'])
        links.new(tint_node.outputs['Result'], pbr_node.inputs['Base Color'])
        if custom_shader_node.inputs.get('Color') is not None:
            links.new(tint_node.outputs['Result'], custom_shader_node.inputs['Color'])
    
    if category != 'BODY':
        for link in links:
            if link.from_node == alpha_mix_node:
                links.remove(link)

    return ({'FINISHED'})

# ============================================================================================
# REMOVE MODEL MATERIAL
# ============================================================================================


def remove_model_material(context, category):
    p = context.active_object.pz_human_props
    instance_str = ' (' + str(p.rig_instance) + ')'
    index = -1
    a_list = None

    mat_name = ''
    match category:
        case 'PROP':
            mat_name = 'MAT-PropMaterial' + str(index) + instance_str
            a_list = context.active_object.pz_human_prop_mesh_slots
            index = p.prop_mesh_slot_active_index
        case 'CLOTHING':
            mat_name = 'MAT-ClothingMaterial' + str(index) + instance_str
            a_list = context.active_object.pz_human_clothing_mesh_slots
            index = p.clothing_mesh_slot_active_index

    old_mat = bpy.data.materials.get(mat_name)
    if old_mat:

        drivers = old_mat.node_tree.animation_data.drivers
        for i in range(len(drivers) - 1, -1, -1):
            drivers.remove(drivers[i])

        bpy.data.materials.remove(old_mat, do_unlink=True)

    for i in range(index, len(a_list)):
        index_mat = bpy.data.materials.get(mat_name)
        if index_mat:
            match category:
                case 'PROP':
                    index_mat.name = 'MAT-PropMaterial' + \
                        str(i - 1) + instance_str
                case 'CLOTHING':
                    index_mat.name = 'MAT-ClothingMaterial' + \
                        str(i - 1) + instance_str

            for fcurve in index_mat.node_tree.animation_data.drivers:
                driver = fcurve.driver
                target = driver.variables[0].targets[0]

                match category:
                    case 'PROP':
                        old_path = "pz_human_prop_mesh_slots[" + str(i) + "]"
                        new_path = "pz_human_prop_mesh_slots[" + \
                            str(i - 1) + "]"
                    case 'CLOTHING':
                        old_path = "pz_human_clothing_mesh_slots[" + str(
                            i) + "]"
                        new_path = "pz_human_clothing_mesh_slots[" + str(
                            i - 1) + "]"

                target.data_path = target.data_path.replace(old_path, new_path)

# ============================================================================================
# DYNAMIC OBJECT PARENTING
# ============================================================================================


def update_lookpoint_parent_object(self, context):
    p = context.active_object.pz_human_props

    lookpoint = context.active_object.pose.bones.get('CTRL-LookPoint')
    copy_constraint = lookpoint.constraints.get('Copy Location')

    copy_constraint.target = p.lookpoint_parent_object


def update_left_prop_parent_object(self, context):
    p = context.active_object.pz_human_props

    prop = context.active_object.pose.bones.get('CTRL-Prop.L')
    copy_constraint = prop.constraints.get('Copy Location')

    copy_constraint.target = p.left_prop_parent_object


def update_right_prop_parent_object(self, context):
    p = context.active_object.pz_human_props

    prop = context.active_object.pose.bones.get('CTRL-Prop.R')
    copy_constraint = prop.constraints.get('Copy Location')

    copy_constraint.target = p.right_prop_parent_object

# endregion

# region Visibility Methods

# ============================================================================================
# SEX VISIBILITY & RENDER UPDATERS
# ============================================================================================

# -------------------------------------------------------------#
# Clothing Sex Visibility


def update_clothing_sex_visibility(self, context):
    p = context.active_object.pz_human_props
    m_list = context.active_object.pz_human_clothing_mesh_slots

    instance_str = ' (' + str(p.rig_instance) + ')'

    male_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Male_Clothes' + instance_str)
    female_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Female_Clothes' + instance_str)

    current_sex = p.model_sex_index

    for i in range(len(m_list)):
        m = m_list[i]

        obj = male_collection.objects.get(
            'OBJ-MaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not m.slot_hide_viewport

        obj = female_collection.objects.get(
            'OBJ-FemaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not m.slot_hide_viewport


def update_clothing_sex_render(self, context):
    p = context.active_object.pz_human_props
    m_list = context.active_object.pz_human_clothing_mesh_slots

    instance_str = ' (' + str(p.rig_instance) + ')'

    male_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Male_Clothes' + instance_str)
    female_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Female_Clothes' + instance_str)

    current_sex = p.model_sex_index

    for i in range(len(m_list)):
        m = m_list[i]

        obj = male_collection.objects.get(
            'OBJ-MaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not m.slot_hide_render

        obj = female_collection.objects.get(
            'OBJ-FemaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not m.slot_hide_render

# -------------------------------------------------------------#
# Prop Sex Visibility


def update_prop_sex_visibility(self, context):
    p = context.active_object.pz_human_props
    a_list = context.active_object.pz_human_prop_mesh_slots

    instance_str = ' (' + str(p.rig_instance) + ')'

    male_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Male_Props' + instance_str)
    female_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Female_Props' + instance_str)

    current_sex = p.model_sex_index

    for i in range(len(a_list)):
        prop_prop = a_list[i]

        obj = male_collection.objects.get(
            'OBJ-MalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not prop_prop.slot_hide_viewport

        obj = female_collection.objects.get(
            'OBJ-FemalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not prop_prop.slot_hide_viewport


def update_prop_sex_render(self, context):
    p = context.active_object.pz_human_props
    a_list = context.active_object.pz_human_prop_mesh_slots

    instance_str = ' (' + str(p.rig_instance) + ')'

    male_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Male_Props' + instance_str)
    female_collection = bpy.data.collections.get(
        'GEO-PZ_Human_Female_Props' + instance_str)

    current_sex = p.model_sex_index

    for i in range(len(a_list)):
        prop_prop = a_list[i]

        obj = male_collection.objects.get(
            'OBJ-MalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not prop_prop.slot_hide_render

        obj = female_collection.objects.get(
            'OBJ-FemalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not prop_prop.slot_hide_render

# -------------------------------------------------------------#
# Hair Sex Visibility


def update_hair_sex_visibility(self, context):
    p = context.active_object.pz_human_props

    instance_str = ' (' + str(p.rig_instance) + ')'
    hair_collection = p.rig_collection.children.get(
        'GEO-PZ_Human' + instance_str).children.get('GEO-PZ_Human_Hair' + instance_str)
    male_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Male' + instance_str)
    female_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Female' + instance_str)
    beard_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Beard' + instance_str)

    current_sex = p.model_sex_index

    obj = male_collection.objects.get('OBJ-MaleHair' + instance_str)
    if obj:
        obj.hide_viewport = obj['sex'] != current_sex

    obj = female_collection.objects.get('OBJ-FemaleHair' + instance_str)
    if obj:
        obj.hide_viewport = obj['sex'] != current_sex

    obj = beard_collection.objects.get('OBJ-Beard' + instance_str)
    if obj:
        obj.hide_viewport = obj['sex'] != current_sex


def update_hair_sex_render(self, context):
    p = context.active_object.pz_human_props

    instance_str = ' (' + str(p.rig_instance) + ')'
    hair_collection = p.rig_collection.children.get(
        'GEO-PZ_Human' + instance_str).children.get('GEO-PZ_Human_Hair' + instance_str)
    male_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Male' + instance_str)
    female_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Female' + instance_str)
    beard_collection = hair_collection.children.get(
        'GEO-PZ_Human_Hair_Beard' + instance_str)

    current_sex = p.model_sex_index

    obj = male_collection.objects.get('OBJ-MaleHair' + instance_str)
    if obj:
        obj.hide_render = obj['sex'] != current_sex

    obj = female_collection.objects.get('OBJ-FemaleHair' + instance_str)
    if obj:
        obj.hide_render = obj['sex'] != current_sex

    obj = beard_collection.objects.get('OBJ-Beard' + instance_str)
    if obj:
        obj.hide_render = obj['sex'] != current_sex

# endregion

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Operators

# region Snapping Operators


class PZ_SnapFKToIK(Operator):
    bl_idname = "zomboid.snap_fk_to_ik"
    bl_label = "Snap FK to IK"

    first_fk_bone: StringProperty()
    second_fk_bone: StringProperty()
    first_ik_bone: StringProperty()
    second_ik_bone: StringProperty()
    extremity_bone: StringProperty()
    ik_control_bone: StringProperty()

    ik_fk_prop: StringProperty()

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        bones = context.active_object.pose.bones

        first_fk_bone = bones.get(self.first_fk_bone)
        second_fk_bone = bones.get(self.second_fk_bone)
        first_ik_bone = bones.get(self.first_ik_bone)
        second_ik_bone = bones.get(self.second_ik_bone)
        ik_control_bone = bones.get(self.ik_control_bone)
        extremity_bone = bones.get(self.extremity_bone)

        if first_fk_bone and second_fk_bone and first_ik_bone and second_ik_bone and ik_control_bone and extremity_bone:

            first_fk_bone.matrix = first_ik_bone.matrix.copy()
            context.view_layer.update()

            second_fk_bone.matrix = second_ik_bone.matrix.copy()
            context.view_layer.update()

            extremity_bone.matrix = ik_control_bone.matrix.copy()
            context.view_layer.update()

            if g.auto_switch_kinematics:
                setattr(p, self.ik_fk_prop, 0.0)
                context.active_object.update_tag()
                context.view_layer.update()
            
            if g.auto_key_snaps:
                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current - 1)

                setattr(p, self.ik_fk_prop, 1.0)
                context.active_object.update_tag()
                context.view_layer.update()

                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current + 1)

            return ({'FINISHED'})

        print('Could not find all bones')
        return ({'CANCELLED'})


class PZ_SnapIKToFK(Operator):
    bl_idname = "zomboid.snap_ik_to_fk"
    bl_label = "Snap IK to FK"

    fk_bone: StringProperty()
    ik_control_bone: StringProperty()
    ik_pole_bone: StringProperty()
    extremity_bone: StringProperty()

    limb_type: StringProperty()

    ik_fk_prop: StringProperty()

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        bones = context.active_object.pose.bones

        fk_bone = bones.get(self.fk_bone)
        ik_control_bone = bones.get(self.ik_control_bone)
        ik_pole_bone = bones.get(self.ik_pole_bone)
        extremity_bone = bones.get(self.extremity_bone)

        if fk_bone and extremity_bone and ik_control_bone and ik_pole_bone:

            orig_fk_matrix = fk_bone.matrix.copy()

            ik_control_bone.matrix = extremity_bone.matrix.copy()
            context.view_layer.update()

            bone_dir = Vector(fk_bone.tail - fk_bone.head).normalized()

            ik_pole_bone.matrix = orig_fk_matrix
            context.view_layer.update()

            if self.limb_type == 'ARM':
                ik_pole_bone.location -= bone_dir * 15
            elif self.limb_type == 'LEG':
                ik_pole_bone.location += bone_dir * 15
            context.view_layer.update()

            if self.limb_type == 'ARM':
                shift_location = Vector((0.023 * 200, 0, 0))
            elif self.limb_type == 'LEG':
                shift_location = Vector((0.023 * -1000, 0, 0))
            ik_pole_bone.location = ik_pole_bone.location + shift_location
            context.view_layer.update()

            flip_rads = math.radians(180)
            flip_quaternion = Quaternion((math.cos(flip_rads / 2), math.sin(flip_rads / 2), 0, 0))
            ik_pole_bone.rotation_quaternion = ik_pole_bone.rotation_quaternion @ flip_quaternion
            context.view_layer.update()

            if g.auto_switch_kinematics:
                setattr(p, self.ik_fk_prop, 1.0)
                context.active_object.update_tag()
                context.view_layer.update()

            if g.auto_key_snaps:
                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current - 1)

                setattr(p, self.ik_fk_prop, 0.0)
                context.active_object.update_tag()
                context.view_layer.update()

                context.active_object.keyframe_insert(data_path='pz_human_props.' + self.ik_fk_prop, frame=context.scene.frame_current)
                context.scene.frame_set(context.scene.frame_current + 1)

        return ({'FINISHED'})

# endregion

# region Body Texture Operators

# ============================================================================================
# GENERATE BODY TEXTURE
# ============================================================================================


class PZ_ConstructBodyTexture(Operator):
    bl_idname = "zomboid.construct_body_texture"
    bl_label = "Construct Body Texture"

    # -------------------------------------------------------------#
    # Get All Body Textures

    body_textures = []

    def get_all_body_textures(self, context, p):
        skin_textures = context.scene.pz_human_skin_textures
        stubble_textures = context.scene.pz_human_stubble_textures
        body_injury_textures = context.scene.pz_human_body_injuries
        zombie_injuries = context.active_object.pz_human_zombie_injuries
        clothing_textures = context.active_object.pz_human_body_texture_slots

        # Get the base skin texture
        match p.skin_set:
            case 'HUMAN':
                if p.zombification == 0:
                    sex = 'MaleBody' if p.model_sex == 'MALE' else 'FemaleBody'
                    chest_hair = 'a' if p.chest_hair and p.model_sex == 'MALE' else ''
                    skin_color = '0' + str(p.skin_color + 1)

                    self.body_textures.append(skin_textures.get(sex + skin_color + chest_hair).texture_path)
                else:
                    skin_5_fix = p.skin_color == 4 and p.zombification != 0
                    zombie_3_fix = p.skin_color == 2 and p.zombification > 1 and p.model_sex == 'MALE'

                    sex = 'M_ZedBody' if p.model_sex == 'MALE' else 'F_ZedBody'
                    skin_color = '0' + str(p.skin_color + 1) if not skin_5_fix else '0' + str(p.skin_color)
                    intensity = '_level' + str(p.zombification) if not zombie_3_fix else '_level1'

                    self.body_textures.append(skin_textures.get(sex + skin_color + intensity).texture_path)
            case 'SKELETON':
                match p.skeleton_type:
                    case 0:
                        self.body_textures.append(skin_textures.get('Skeleton').texture_path)
                    case 1:
                        self.body_textures.append(skin_textures.get('SkeletonBurned').texture_path)
                    case 2:
                        self.body_textures.append(skin_textures.get('SkeletonMuscle').texture_path)
            case 'MANNEQUIN':
                if p.mannequin_type == 0:
                    self.body_textures.append(skin_textures.get('M_Mannequin_White').texture_path)
                else:
                    self.body_textures.append(skin_textures.get('M_Mannequin_Black').texture_path)
            case 'SCARECROW':
                self.body_textures.append(skin_textures.get('Male_Scarecrow').texture_path)

        # Get the stubble textures
        if p.skin_set == 'HUMAN':
            if p.hair_stubble:
                if p.model_sex == 'MALE':
                    self.body_textures.append(stubble_textures.get('M_Hair_Stubble').texture_path)
                else:
                    self.body_textures.append(stubble_textures.get('F_Hair_Stubble').texture_path)
            
            if p.beard_stubble and p.model_sex == 'MALE':
                self.body_textures.append(stubble_textures.get('M_Beard_Stubble').texture_path)

            # Get the body injury textures
            injury_props = [p.upper_torso_injury, p.lower_torso_injury, p.left_hand_injury,
                            p.right_hand_injury, p.left_forearm_injury, p.right_forearm_injury,
                            p.left_upperarm_injury, p.right_upperarm_injury, p.head_injury,
                            p.neck_injury, p.groin_injury, p.left_thigh_injury,
                            p.right_thigh_injury, p.left_shin_injury, p.right_shin_injury,
                            p.left_foot_injury, p.right_foot_injury]

            body_injury_lookup = {
                (tex.sex, tex.damage_type, tex.body_part): tex.texture_path for tex in body_injury_textures
            }

            body_part_dict = {
                0: 'chest',
                1: 'abdomen',
                2: 'left_hand',
                3: 'right_hand',
                4: 'lower_left_arm',
                5: 'lower_right_arm',
                6: 'upper_left_arm',
                7: 'upper_right_arm',
                8: 'head',
                9: 'neck',
                10: 'groin',
                11: 'left_thigh',
                12: 'right_thigh',
                13: 'left_calf',
                14: 'right_calf',
                15: 'left_foot',
                16: 'right_foot'
            }

            sex = p.model_sex

            for index, injury in enumerate(injury_props):
                if injury != 'NONE':
                    if injury == 'BANDAGE' or injury == 'BANDAGEBLOODY':
                        key = ('MALE', injury, body_part_dict[index])
                    else:
                        key = (sex, injury, body_part_dict[index])
                    if key in body_injury_lookup:
                        self.body_textures.append(body_injury_lookup[key])

            # Get the zombie injury textures
            for injury in zombie_injuries:
                self.body_textures.append(injury.texture_path)

        if p.skin_set != 'SKELETON':
            # Get the clothing textures
            for clothing in clothing_textures:
                self.body_textures.append(clothing.texture_path)

    # -------------------------------------------------------------#
    # Create Body Texture

    # TODO Optimize

    def generate_body_texture(self, context, p):
        generated_image = bpy.data.images.get(
            'TEX-BodyTexture (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='TEX-BodyTexture (' + str(p.rig_instance) + ')', width=256, height=256, alpha=True)
        
        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-TexSlot').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the alpha channel
        generated_pixels[3::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        body_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.body_textures:
            body_texture = bpy.data.images.load(tex_path)
            body_texture.scale(256, 256)

            body_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            body_texture.pixels.foreach_get(body_pixels)

            generated_rgba = generated_pixels.reshape(-1, 4)
            body_rgba = body_pixels.reshape(-1, 4)

            body_alpha = body_rgba[:, 3:4]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + body_alpha * (1.0 - generated_alpha)
            rgb = (body_rgba[:, :3] * body_alpha + generated_rgba[:,
                   :3] * generated_alpha * (1.0 - body_alpha))

            generated_rgba[:, :3] = rgb
            generated_rgba[:, 3] = alpha.squeeze()

            body_texture.user_clear()
            bpy.data.images.remove(body_texture)

        generated_image.pixels.foreach_set(generated_rgba.flatten())
        generated_image.update()


    # -------------------------------------------------------------#
    # Default Textures
    def initialize_default_textures(self, context, p):
        # Assign the default image to the body material node tree
        if p.body_mat:
            img = bpy.data.images.get('TEX-DefaultMale') if p.model_sex == 'MALE' else bpy.data.images.get('TEX-DefaultFemale')
            p.body_mat.node_tree.nodes.get('NDE-TexSlot').image = img

    # -------------------------------------------------------------#
    # Execute

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        
        if g.assets_parsed:
            self.body_textures.clear()

            self.get_all_body_textures(context, p)
            self.generate_body_texture(context, p)
        else:
            self.initialize_default_textures(context, p)

        return ({'FINISHED'})

# ============================================================================================
# CREATE BODY BLOODINESS MASK
# ============================================================================================


class PZ_HumanRig_CreateBodyBloodinessTexture(Operator):

    '''
    This operator will draw the full bloodiness mask texture that combines all of 
    the body part health location masks at a specified intensity from 0.0 to 5.0 for each.
    It draws it to each rig's specific MaskData texture on the red channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_body_bloodiness_texture"
    bl_label = "Create Body Bloodiness Texture"
    bl_description = "Create a combined blood image from the blood textures"

    blood_textures = []

    def get_blood_textures(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        overlay_masks = context.scene.pz_human_overlay_masks

        self.blood_textures.clear()

        blood_props = [p.upper_torso_bloodiness, p.lower_torso_bloodiness, p.left_hand_bloodiness,
                       p.right_hand_bloodiness, p.left_forearm_bloodiness, p.right_forearm_bloodiness,
                       p.left_upperarm_bloodiness, p.right_upperarm_bloodiness, p.head_bloodiness,
                       p.neck_bloodiness, p.groin_bloodiness, p.left_thigh_bloodiness,
                       p.right_thigh_bloodiness, p.left_shin_bloodiness, p.right_shin_bloodiness,
                       p.left_foot_bloodiness, p.right_foot_bloodiness, p.back_bloodiness]

        body_part_dict = {
            0: 'Chest',
            1: 'Stomach',
            2: 'HandL',
            3: 'HandR',
            4: 'LArmL',
            5: 'LArmR',
            6: 'UArmL',
            7: 'UArmR',
            8: 'Head',
            9: 'Neck',
            10: 'Groin',
            11: 'ULegL',
            12: 'ULegR',
            13: 'LLegL',
            14: 'LLegR',
            15: 'FootL',
            16: 'FootR',
            17: 'Back'
        }

        index = 0
        for blood in blood_props:
            if blood != 0:
                self.blood_textures.append((overlay_masks.get(body_part_dict[index]).texture_path, blood))
            index = index + 1

        return ({'FINISHED'})

    def generate_bloodiness_texture(self, context):

        p = context.active_object.pz_human_props

        generated_image = bpy.data.images.get(
            'MASK-MaskData (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData (' + str(p.rig_instance) + ')', 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )

        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the red channel
        generated_pixels[0::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        blood_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.blood_textures:
            blood_texture = bpy.data.images.load(tex_path[0])
            blood_texture.scale(256, 256)
            
            blood_texture.pixels.foreach_get(blood_pixels)
            blood_rgba = blood_pixels.reshape(-1, 4)

            blood_alpha = blood_rgba[:, 3:4] * tex_path[1]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + blood_alpha * (1.0 - generated_alpha)
            red = (blood_rgba[:, 0:1] * blood_alpha + generated_rgba[:,0:1])

            generated_rgba[:, 0:1] = red
            #generated_rgba[:, 3] = alpha.squeeze()

            blood_texture.user_clear()
            bpy.data.images.remove(blood_texture)

        generated_image.pixels.foreach_set(generated_pixels)
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        g = context.scene.pz_human_global_props

        if g.pz_directory != '':
            self.get_blood_textures(context)
            self.generate_bloodiness_texture(context)

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})

# ============================================================================================
# CREATE BODY DIRTINESS MASK
# ============================================================================================


class PZ_HumanRig_CreateBodyDirtinessTexture(Operator):

    '''
    This operator will draw the full dirtiness mask texture that combines all of 
    the body part health location masks at a specified intensity from 0.0 to 2.0 for each.
    It draws it to each rig's specific MaskData texture on the green channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_body_dirtiness_texture"
    bl_label = "Create Body Dirtiness Texture"
    bl_description = "Create a combined dirt image from the blood mask textures"

    dirt_textures = []

    def get_dirt_textures(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        overlay_masks = context.scene.pz_human_overlay_masks

        self.dirt_textures.clear()

        dirt_props = [p.upper_torso_dirtiness, p.lower_torso_dirtiness, p.left_hand_dirtiness,
                      p.right_hand_dirtiness, p.left_forearm_dirtiness, p.right_forearm_dirtiness,
                      p.left_upperarm_dirtiness, p.right_upperarm_dirtiness, p.head_dirtiness,
                      p.neck_dirtiness, p.groin_dirtiness, p.left_thigh_dirtiness,
                      p.right_thigh_dirtiness, p.left_shin_dirtiness, p.right_shin_dirtiness,
                      p.left_foot_dirtiness, p.right_foot_dirtiness, p.back_dirtiness]

        body_part_dict = {
            0: 'Chest',
            1: 'Stomach',
            2: 'HandL',
            3: 'HandR',
            4: 'LArmL',
            5: 'LArmR',
            6: 'UArmL',
            7: 'UArmR',
            8: 'Head',
            9: 'Neck',
            10: 'Groin',
            11: 'ULegL',
            12: 'ULegR',
            13: 'LLegL',
            14: 'LLegR',
            15: 'FootL',
            16: 'FootR',
            17: 'Back'
        }

        index = 0
        for dirt in dirt_props:
            if dirt != 0:
                self.dirt_textures.append((overlay_masks.get(body_part_dict[index]).texture_path, dirt))
            index = index + 1

        return ({'FINISHED'})

    def generate_dirtiness_texture(self, context):

        p = context.active_object.pz_human_props

        generated_image = bpy.data.images.get(
            'MASK-MaskData (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData (' + str(p.rig_instance) + ')', 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )

        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the green channel
        generated_pixels[1::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        dirt_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.dirt_textures:
            dirt_texture = bpy.data.images.load(tex_path[0])
            dirt_texture.scale(256, 256)

            dirt_texture.pixels.foreach_get(dirt_pixels)
            dirt_rgba = dirt_pixels.reshape(-1, 4)

            dirt_alpha = dirt_rgba[:, 3:4] * tex_path[1]
            generated_alpha = generated_rgba[:, 3:4]

            alpha = generated_alpha + dirt_alpha * (1.0 - generated_alpha)
            green = (dirt_rgba[:, 1:2] * dirt_alpha + generated_rgba[:,1:2])

            generated_rgba[:, 1:2] = green
            #generated_rgba[:, 3] = alpha.squeeze()

            dirt_texture.user_clear()
            bpy.data.images.remove(dirt_texture)

        generated_image.pixels.foreach_set(generated_rgba.flatten())
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        g = context.scene.pz_human_global_props

        if g.pz_directory != '':
            self.get_dirt_textures(context)
            self.generate_dirtiness_texture(context)
            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})

# ============================================================================================
# CREATE VISIBILITY MASK
# ============================================================================================


class PZ_HumanRig_CreateMaskTexture(Operator):

    '''
    This operator will draw the full visibility mask texture from the 17 different mask options
    used in game. It draws it to each rig's specific MaskData texture on the blue channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_mask_texture"
    bl_label = "Create Mask Texture"
    bl_description = "Create a combined mask image from the mask textures"

    mask_textures = []

    def get_mask_textures(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        visibility_masks = context.scene.pz_human_visibility_masks

        self.mask_textures.clear()

        mask_dict = {
            0: "Head",
            1: "Chest",
            2: "Crotch",
            3: "LeftArm",
            4: "LeftHand",
            5: "RightArm",
            6: "RightHand",
            7: "LeftLeg",
            8: "LeftFoot",
            9: "RightLeg",
            10: "RightFoot",
            11: "Dress",
            12: "Chest",
            13: "Waist",
            14: "Belt",
            15: "Crotch",
            16: "FullBody"
        }

        index = 0
        for hide in p.mask_array:
            if hide:
                self.mask_textures.append(visibility_masks.get(mask_dict[index]).texture_path)
            index = index + 1

        return ({'FINISHED'})

    def generate_mask_texture(self, context):
        p = context.active_object.pz_human_props

        generated_image = bpy.data.images.get(
            'MASK-MaskData (' + str(p.rig_instance) + ')')
        if generated_image is None:
            generated_image = bpy.data.images.new(
                name='MASK-MaskData (' + str(p.rig_instance) + ')', 
                width=256, 
                height=256, 
                alpha=True,
                float_buffer=True
            )

        # Assign the image to the body material node tree
        if p.body_mat:
            p.body_mat.node_tree.nodes.get('NDE-MaskData').image = generated_image

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the blue channel
        generated_pixels[2::4] = 0.0

        generated_rgba = generated_pixels.reshape(-1, 4)

        mask_pixels = np.empty(num_pixels * 4, dtype=np.float32)

        for tex_path in self.mask_textures:
            mask_texture = bpy.data.images.load(tex_path)
            mask_texture.scale(256, 256)

            mask_texture.pixels.foreach_get(mask_pixels)
            mask_rgba = mask_pixels.reshape(-1, 4)

            mask_alpha = mask_rgba[:, 3:4]

            generated_rgba[:, 2:3] += mask_alpha
            #generated_rgba[:, 3:4] += mask_alpha

            mask_texture.user_clear()
            bpy.data.images.remove(mask_texture)

        generated_image.pixels.foreach_set(generated_pixels)
        generated_image.update()

        return ({'FINISHED'})

    def execute(self, context):
        g = context.scene.pz_human_global_props

        if g.pz_directory != '':
            self.get_mask_textures(context)
            self.generate_mask_texture(context)
            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})

# endregion

# region List Operators

# ============================================================================================
# LIST OPERATIONS
# ============================================================================================

# -------------------------------------------------------------#
# Mod Directory Slot List Operations


class PZ_HumanRig_AddModDirectorySlot(Operator):
    bl_idname = "zomboid.add_mod_directory_slot"
    bl_label = "Add Mod Directory Mesh Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_mod_directory_slots",
            active_index_path="scene.pz_human_global_props.mod_directory_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveModDirectorySlot(Operator):
    bl_idname = "zomboid.remove_mod_directory_slot"
    bl_label = "Remove Mod Directory Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_mod_directory_slots",
            active_index_path="scene.pz_human_global_props.mod_directory_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Body Texture Slot List Operations


class PZ_HumanRig_AddBodyTextureSlot(Operator):
    bl_idname = "zomboid.add_body_texture_slot"
    bl_label = "Add Texture Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveBodyTextureSlot(Operator):
    bl_idname = "zomboid.remove_body_texture_slot"
    bl_label = "Remove Texture Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index"
        )

        bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})


class PZ_HumanRig_MoveBodyTextureSlotUp(Operator):
    bl_idname = "zomboid.move_body_texture_slot_up"
    bl_label = "Move Texture Slot Up"

    def execute(self, context):

        bpy.ops.uilist.entry_move(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index",
            direction='UP'
        )

        bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})


class PZ_HumanRig_MoveBodyTextureSlotDown(Operator):
    bl_idname = "zomboid.move_body_texture_slot_down"
    bl_label = "Move Texture Slot Down"

    def execute(self, context):

        bpy.ops.uilist.entry_move(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index",
            direction='DOWN'
        )

        bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Clothing Mesh Slot List Operations


class PZ_HumanRig_AddClothingMeshSlot(Operator):
    bl_idname = "zomboid.add_clothing_mesh_slot"
    bl_label = "Add Clothing Mesh Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_clothing_mesh_slots",
            active_index_path="active_object.pz_human_props.clothing_mesh_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveClothingMeshSlot(Operator):
    bl_idname = "zomboid.remove_clothing_mesh_slot"
    bl_label = "Remove Clothing Mesh Slot"

    def execute(self, context):

        bpy.ops.zomboid.remove_clothing_mesh()

        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_clothing_mesh_slots",
            active_index_path="active_object.pz_human_props.clothing_mesh_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Prop Mesh Slot List Operations


class PZ_HumanRig_AddPropMeshSlot(Operator):
    bl_idname = "zomboid.add_prop_mesh_slot"
    bl_label = "Add Prop Mesh Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_prop_mesh_slots",
            active_index_path="active_object.pz_human_props.prop_mesh_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemovePropMeshSlot(Operator):
    bl_idname = "zomboid.remove_prop_mesh_slot"
    bl_label = "Remove Prop Mesh Slot"

    def execute(self, context):

        bpy.ops.zomboid.remove_prop_mesh()

        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_prop_mesh_slots",
            active_index_path="active_object.pz_human_props.prop_mesh_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Clothing Item Slot List Operations


class PZ_HumanRig_AddClothingItemSlot(Operator):
    bl_idname = "zomboid.add_clothing_item_slot"
    bl_label = "Add Clothing Item Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_clothing_item_slots",
            active_index_path="scene.pz_human_global_props.clothing_item_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveClothingItemSlot(Operator):
    bl_idname = "zomboid.remove_clothing_item_slot"
    bl_label = "Remove Clothing Item Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_clothing_item_slots",
            active_index_path="scene.pz_human_global_props.clothing_item_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Outfit Slot List Operations


class PZ_HumanRig_AddOutfitSlot(Operator):
    bl_idname = "zomboid.add_outfit_slot"
    bl_label = "Add Outfit Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_outfit_slots",
            active_index_path="scene.pz_human_global_props.outfit_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveOutfitSlot(Operator):
    bl_idname = "zomboid.remove_outfit_slot"
    bl_label = "Remove Outfit Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_outfit_slots",
            active_index_path="scene.pz_human_global_props.outfit_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Hair Style Slot List Operations


class PZ_HumanRig_AddHairStyleSlot(Operator):
    bl_idname = "zomboid.add_hair_style_slot"
    bl_label = "Add Hair Style Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_hair_style_slots",
            active_index_path="scene.pz_human_global_props.hair_style_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveHairStyleSlot(Operator):
    bl_idname = "zomboid.remove_hair_style_slot"
    bl_label = "Remove Hair Style Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_hair_style_slots",
            active_index_path="scene.pz_human_global_props.hair_style_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Beard Style Slot List Operations


class PZ_HumanRig_AddBeardStyleSlot(Operator):
    bl_idname = "zomboid.add_beard_style_slot"
    bl_label = "Add Beard Style Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_beard_styles",
            active_index_path="scene.pz_human_global_props.beard_style_slot_active_index"
        )

        return ({'FINISHED'})


class PZ_HumanRig_RemoveBeardStyleSlot(Operator):
    bl_idname = "zomboid.remove_beard_style_slot"
    bl_label = "Remove Beard Style Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_beard_styles",
            active_index_path="scene.pz_human_global_props.beard_style_slot_active_index"
        )

        return ({'FINISHED'})

# -------------------------------------------------------------#
# Zombie Injury List Operations


class PZ_HumanRig_RemoveZombieInjury(Operator):
    bl_idname = "zomboid.remove_zombie_injury"
    bl_label = "Remove Zombie Injury"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="object.pz_human_zombie_injuries",
            active_index_path="object.pz_human_props.zombie_injury_active_index"
        )

        bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})

# endregion

# region Import Operators

# ============================================================================================
# CLOTHING MESH IMPORTER
# ============================================================================================


class PZ_ImportClothingMesh(Operator):
    bl_idname = "zomboid.import_clothing_mesh"
    bl_label = "Import Clothing Mesh"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def import_clothing_model(self, context, model_path, model_type, sex):
        p = context.active_object.pz_human_props

        instance_str = ' (' + str(p.rig_instance) + ')'

        if Path(model_path).is_file():

            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects

            bpy.ops.object.mode_set(mode='OBJECT')

            objs_before = set(bpy.context.scene.objects)

            match model_type:
                case '.x':
                    if not directx_import_available():
                        print("The .x importer is not enabled or installed")
                        return ({'CANCELLED'})

                    bpy.ops.import_scene.directx_x(
                        filepath=model_path,
                        import_textures=False,
                        import_materials=False,
                        import_armature=False,
                        import_animation=False,
                        use_import_collection=False
                    )

                case '.fbx':
                    bpy.ops.import_scene.fbx(
                        filepath=model_path,
                        global_scale=100.0
                    )
                case '.glb':
                    bpy.ops.import_scene.gltf(
                        filepath=model_path,
                        disable_bone_shape=True
                    )

            objs_after = set(bpy.context.scene.objects)

            imported_objects = list(objs_after - objs_before)

            sex_collection_name = 'GEO-PZ_Human_Male_Clothes' if sex == 'MALE' else 'GEO-PZ_Human_Female_Clothes'
            clothing_collection = bpy.data.collections.get(
                sex_collection_name + instance_str)

            # Check for a special condition if the Bob_Trousers model is used. It has an issue where it has two meshes instead of one, which causes issues
            x = None
            y = None
            for obj in imported_objects:
                if obj.name == 'Bob_Trousers':
                    x = obj
                elif obj.name == 'Bob_LongShorts':
                    y = obj
            if x is not None and y is not None:
                imported_objects.remove(y)
                bpy.data.objects.remove(y, do_unlink=True)

            for obj in imported_objects:
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':

                    sex_name = 'OBJ-MaleClothingMesh' if sex == 'MALE' else 'OBJ-FemaleClothingMesh'
                    obj_name = sex_name + \
                        str(p.clothing_mesh_slot_active_index) + instance_str

                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    # -------------------------

                    # Fix for incorrectly assigned hats that have off rotations
                    if 'WeddingVeil' in obj.name:
                        obj.rotation_euler[0] += math.radians(2)

                    # -------------------------

                    obj.name = obj_name

                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)

                    if obj.name not in clothing_collection.objects:
                        clothing_collection.objects.link(obj)

                    matrix_world = obj.matrix_world.copy()
                    obj.parent = prev_active_object
                    obj.matrix_world = matrix_world

                    match model_type:
                        case '.x':
                            obj.rotation_euler[2] += math.pi
                            obj.scale[0] *= -1
                        case '.fbx':
                            obj.scale[0] = 100.0
                            obj.scale[1] = 100.0
                            obj.scale[2] = 100.0
                            obj.data.materials.clear()
                        case '.glb':
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0

                    obj.modifiers.clear()

                    arm_mod = obj.modifiers.new(
                        name="Armature", type='ARMATURE')
                    arm_mod.object = prev_active_object

                    obj.active_material = bpy.data.materials.get(
                        'MAT-ClothingMaterial' + str(p.clothing_mesh_slot_active_index) + instance_str)

                    obj["sex"] = 0 if sex == 'MALE' else 1
                    obj.hide_viewport = obj['sex'] != p.model_sex_index
                    obj.hide_render = obj['sex'] != p.model_sex_index

            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            for obj in prev_selected_objects:
                obj.select_set(True)
            if prev_active_object is not None:
                context.view_layer.objects.active = prev_active_object

            # Restore the context that was before the operation was called
            bpy.ops.object.mode_set(mode=prev_mode)
            return ({'FINISHED'})
        else:
            print("Could not find a model file at the path: " + model_path)
            return ({'CANCELLED'})

    def add_masks(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        m = m_list[p.clothing_mesh_slot_active_index]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for i in range(len(m.mask_array)):
            if m.mask_array[i] == True:
                p.mask_array[i] = True

        if self.halt_texture_updates:
            p.halt_texture_updates = False

        return ({'FINISHED'})

    def execute(self, context):

        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        m = m_list[p.clothing_mesh_slot_active_index]

        create_model_material(context, m.texture_path, 'CLOTHING')

        self.import_clothing_model(
            context, m.male_model_path, m.model_type, 'MALE')
        self.import_clothing_model(
            context, m.female_model_path, m.model_type, 'FEMALE')

        self.add_masks(context)

        bpy.ops.zomboid.check_hat_category()

        return ({'FINISHED'})

# ============================================================================================
# PROP MESH IMPORTER
# ============================================================================================


class PZ_ImportPropMesh(Operator):
    bl_idname = "zomboid.import_prop_mesh"
    bl_label = "Import Prop Mesh"

    def import_prop_model(self, context, model_path, model_type, attach_bone, sex):
        p = context.active_object.pz_human_props

        instance_str = ' (' + str(p.rig_instance) + ')'

        if Path(model_path).is_file():

            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects

            bpy.ops.object.mode_set(mode='OBJECT')

            objs_before = set(bpy.context.scene.objects)

            match model_type:
                case '.x':
                    if not directx_import_available():
                        self.report(
                            {"ERROR"}, "The .x importer is not enabled or installed")
                        return ({'CANCELLED'})

                    bpy.ops.import_scene.directx_x(
                        filepath=model_path,
                        import_textures=False,
                        import_materials=False,
                        import_armature=False,
                        import_animation=False,
                        use_import_collection=False
                    )

                case '.fbx':
                    bpy.ops.import_scene.fbx(
                        filepath=model_path,
                        global_scale=100.0
                    )
                case '.glb':
                    bpy.ops.import_scene.gltf(
                        filepath=model_path,
                        disable_bone_shape=True
                    )

            objs_after = set(bpy.context.scene.objects)

            imported_objects = list(objs_after - objs_before)

            sex_collection_name = 'GEO-PZ_Human_Male_Props' if sex == 'MALE' else 'GEO-PZ_Human_Female_Props'
            prop_collection = bpy.data.collections.get(
                sex_collection_name + instance_str)

            for obj in imported_objects:
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':

                    sex_name = 'OBJ-MalePropMesh' if sex == 'MALE' else 'OBJ-FemalePropMesh'
                    obj_name = sex_name + \
                        str(p.prop_mesh_slot_active_index) + instance_str

                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    obj.name = obj_name

                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)

                    if obj.name not in prop_collection.objects:
                        prop_collection.objects.link(obj)

                    bip01 = prev_active_object
                    bone = bip01.pose.bones.get(attach_bone)

                    obj.parent = bip01
                    obj.parent_type = 'BONE'
                    obj.parent_bone = bone.name

                    obj.matrix_parent_inverse = bone.matrix.inverted()

                    bone_world_matrix = bip01.matrix_world @ bone.matrix
                    obj.matrix_world = bone_world_matrix

                    match model_type:
                        case '.x':
                            obj.rotation_euler[0] += math.pi
                            obj.scale *= 100

                            # Wrist items are imported upside down and have off rotations, for some reason
                            if sex == 'MALE':
                                if bone.name == 'Bip01_L_Forearm':
                                    obj.scale[2] *= -1
                                    obj.rotation_euler[1] += math.radians(3)
                                if bone.name == 'Bip01_R_Forearm':
                                    obj.scale[2] *= -1
                                    obj.rotation_euler[1] -= math.radians(3)
                            elif sex == 'FEMALE':
                                if bone.name == 'Bip01_L_Forearm':
                                    obj.scale[2] *= -1
                                    obj.rotation_euler[1] -= math.radians(3)
                                if bone.name == 'Bip01_R_Forearm':
                                    obj.scale[2] *= -1
                                    obj.rotation_euler[1] += math.radians(3)
                        
                          #  flip_uvs(obj)

                        case '.fbx':
                            # matrix_world = obj.matrix_world.copy()
                            # obj.parent = None
                            # obj.matrix_world = matrix_world
                            obj.data.materials.clear()
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0
                            # obj.rotation_euler[0] = -math.pi / 2
                        case '.glb':
                            # matrix_world = obj.matrix_world.copy()
                            # obj.parent = None
                            # obj.matrix_world = matrix_world
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0

                    obj.modifiers.clear()

                    obj.active_material = bpy.data.materials.get(
                        'MAT-PropMaterial' + str(p.prop_mesh_slot_active_index) + instance_str)

                    obj["sex"] = 0 if sex == 'MALE' else 1
                    obj.hide_viewport = obj['sex'] != p.model_sex_index
                    obj.hide_render = obj['sex'] != p.model_sex_index

                    # Deselect all objects
                    bpy.ops.object.select_all(action='DESELECT')

                    for obj in prev_selected_objects:
                        obj.select_set(True)
                    if prev_active_object is not None:
                        context.view_layer.objects.active = prev_active_object

                    # Restore the context that was before the operation was called
                    bpy.ops.object.mode_set(mode=prev_mode)
                    return ({'FINISHED'})
                else:
                    self.report(
                        {'ERROR'}, "Could not find a model file at the path: " + model_path)
                    return ({'CANCELLED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_prop_mesh_slots
        m = m_list[p.prop_mesh_slot_active_index]

        create_model_material(context, m.texture_path, 'PROP')

        self.import_prop_model(context, m.male_model_path,
                               m.model_type, m.attach_bone, 'MALE')
        self.import_prop_model(context, m.female_model_path,
                               m.model_type, m.attach_bone, 'FEMALE')

        bpy.ops.zomboid.check_hat_category()

        return ({'FINISHED'})

# ============================================================================================
# HAIR MESH IMPORTER
# ============================================================================================


class PZ_ImportHairMesh(Operator):
    bl_idname = "zomboid.import_hair_mesh"
    bl_label = "Import Hair Mesh"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        hair_styles = context.scene.pz_human_hair_style_slots
        beard_styles = context.scene.pz_human_beard_styles

        hair_style = None
        match self.hair_type:
            case 'M':
                for hair in hair_styles:
                    if hair.name == p.current_male_hair_style and hair.sex == 'MALE':
                        hair_style = hair
            case 'F':
                for hair in hair_styles:
                    if hair.name == p.current_female_hair_style and hair.sex == 'FEMALE':
                        hair_style = hair
            case 'B':
                for beard in beard_styles:
                    if beard.name == p.current_beard_style:
                        hair_style = beard

        instance_str = ' (' + str(p.rig_instance) + ')'

        model_path = hair_style.model_path

        filepath = None
        extension = None

        if Path(model_path).name != 'None':
            filepath, extension = get_zomboid_asset(context, model_path)
        else:
            bpy.ops.zomboid.remove_hair_mesh(hair_type=self.hair_type)
            return ({'FINISHED'})
        if filepath is None:
            return ({'CANCELLED'})

        col = None
        prev_obj = None
        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Male' + instance_str)
                prev_obj = col.objects.get('OBJ-MaleHair' + instance_str)
            case 'F':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Female' + instance_str)
                prev_obj = col.objects.get('OBJ-FemaleHair' + instance_str)
            case 'B':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Beard' + instance_str)
                prev_obj = col.objects.get('OBJ-Beard' + instance_str)

        if prev_obj:
            bpy.data.objects.remove(prev_obj, do_unlink=True)
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True, do_linked_ids=True, do_recursive=True)

        create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)

        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        if context.active_object is not None:
            prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        bpy.ops.object.mode_set(mode='OBJECT')

        objs_before = set(bpy.context.scene.objects)

        match extension:
            case '.x' | '.X':
                if not directx_import_available():
                    self.report(
                        {"ERROR"}, "The .x importer is not enabled or installed")
                    return ({'CANCELLED'})

                bpy.ops.import_scene.directx_x(
                    filepath=str(filepath),
                    import_textures=False,
                    import_materials=False,
                    import_armature=False,
                    import_animation=False,
                    use_import_collection=False
                )

            case '.fbx':
                bpy.ops.import_scene.fbx(
                    filepath=str(filepath),
                    global_scale=100.0
                )
            case '.glb':
                bpy.ops.import_scene.gltf(
                    filepath=str(filepath),
                    disable_bone_shape=True
                )

        objs_after = set(bpy.context.scene.objects)

        imported_objects = list(objs_after - objs_before)

        objs_to_remove = []
        for obj in imported_objects:
            if obj.type == 'ARMATURE' or obj.type == 'EMPTY':
                objs_to_remove.append(obj)
            elif obj.type == 'MESH':
                match self.hair_type:
                    case 'M':
                        obj.name = 'OBJ-MaleHair' + instance_str
                        obj["sex"] = 0
                    case 'F':
                        obj.name = 'OBJ-FemaleHair' + instance_str
                        obj["sex"] = 1
                    case 'B':
                        obj.name = 'OBJ-Beard' + instance_str
                        obj["sex"] = 0

                obj.hide_viewport = obj['sex'] != p.model_sex_index
                obj.hide_render = obj['sex'] != p.model_sex_index

                matrix_world = obj.matrix_world.copy()
                obj.parent = prev_active_object
                obj.matrix_world = matrix_world

                match extension:
                    case '.x' | '.X':
                        obj.rotation_euler[2] += math.pi
                        obj.scale[0] *= -1
                        if self.hair_type == 'B':
                            obj.location[1] -= 0.125
                    case '.fbx':
                        obj.data.materials.clear()
                        obj.scale[0] = 1.0
                        obj.scale[1] = 1.0
                        obj.scale[2] = 1.0
                    case '.glb':
                        obj.scale[0] = 100.0
                        obj.scale[1] = 100.0
                        obj.scale[2] = 100.0

                for collection in obj.users_collection[:]:
                    collection.objects.unlink(obj)

                if obj.name not in col.objects:
                    col.objects.link(obj)

                obj.modifiers.clear()

                arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                arm_mod.object = prev_active_object
                
                match self.hair_type:
                    case 'M':
                        obj.active_material = bpy.data.materials.get('MAT-MaleHair' + instance_str)
                    case 'F':
                        obj.active_material = bpy.data.materials.get('MAT-FemaleHair' + instance_str)
                    case 'B':
                        obj.active_material = bpy.data.materials.get('MAT-Beard' + instance_str)

        for obj in objs_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in prev_selected_objects:
            obj.select_set(True)
        if prev_active_object is not None:
            context.view_layer.objects.active = prev_active_object

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        return ({'FINISHED'})

# endregion

# region Remove Operators

# ============================================================================================
# CLOTHING MESH REMOVER
# ============================================================================================


class PZ_RemoveClothingMesh(Operator):
    bl_idname = "zomboid.remove_clothing_mesh"
    bl_label = "Remove Clothing Mesh"

    halt_texture_updates: BoolProperty(
        default=True
    )

    # -------------------------------------------------------------#
    # Remove Clothing Material

    def remove_clothing_material(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_mesh_slot_active_index

        old_mat = bpy.data.materials.get(
            'MAT-ClothingMaterial' + str(index) + instance_str)
        if old_mat:

            drivers = old_mat.node_tree.animation_data.drivers
            for i in range(len(drivers) - 1, -1, -1):
                drivers.remove(drivers[i])

            bpy.data.materials.remove(old_mat, do_unlink=True)

        for i in range(index, len(m_list)):
            index_mat = bpy.data.materials.get(
                'MAT-ClothingMaterial' + str(i) + instance_str)
            if index_mat:
                index_mat.name = 'MAT-ClothingMaterial' + \
                    str(i - 1) + instance_str

                for fcurve in index_mat.node_tree.animation_data.drivers:
                    driver = fcurve.driver
                    target = driver.variables[0].targets[0]

                    old_path = "pz_human_clothing_mesh_slots[" + str(i) + "]"
                    new_path = "pz_human_clothing_mesh_slots[" + str(
                        i - 1) + "]"

                    target.data_path = target.data_path.replace(
                        old_path, new_path)

        return ({'FINISHED'})

    # -------------------------------------------------------------#
    # Remove Male Clothing Object

    def remove_male_clothing_mesh(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_mesh_slot_active_index

        old_obj = bpy.data.objects.get(
            'OBJ-MaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(m_list)):
            index_obj = bpy.data.objects.get(
                'OBJ-MaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-MaleClothingMesh' + \
                    str(i - 1) + instance_str

        return ({'FINISHED'})

    # -------------------------------------------------------------#
    # Remove Female Clothing Object

    def remove_female_clothing_mesh(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_mesh_slot_active_index

        old_obj = bpy.data.objects.get(
            'OBJ-FemaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(m_list)):
            index_obj = bpy.data.objects.get(
                'OBJ-FemaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-FemaleClothingMesh' + \
                    str(i - 1) + instance_str

        return ({'FINISHED'})

    def check_masks(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        m = m_list[p.clothing_mesh_slot_active_index]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for i in range(len(p.mask_array)):
            test = False
            for j in range(len(m_list)):
                if m_list[j].name != m.name and m_list[j].mask_array[i] == True:
                    test = True
                    break
            p.mask_array[i] = test
            p.mask_array[i] = p.mask_array[i]

        if self.halt_texture_updates:
            p.halt_texture_updates = False
            bpy.ops.zomboid.create_mask_texture()

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props

        remove_model_material(context, 'CLOTHING')
        self.remove_male_clothing_mesh(context)
        self.remove_female_clothing_mesh(context)

        self.check_masks(context)

        bpy.ops.zomboid.check_hat_category(count_self=False)

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})

# ============================================================================================
# PROP MESH REMOVER
# ============================================================================================


class PZ_RemovePropMesh(Operator):
    bl_idname = "zomboid.remove_prop_mesh"
    bl_label = "Remove Prop Mesh"

    def remove_prop_mesh(self, context, sex):
        p = context.active_object.pz_human_props
        a_list = context.active_object.pz_human_prop_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.prop_mesh_slot_active_index

        obj_name = 'OBJ-MalePropMesh' if sex == 'MALE' else 'OBJ-FemalePropMesh'
        orig_obj_name = obj_name + str(index) + instance_str

        old_obj = bpy.data.objects.get(orig_obj_name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(a_list)):
            index_obj = bpy.data.objects.get(obj_name + str(i) + instance_str)
            if index_obj:
                index_obj.name = obj_name + str(i - 1) + instance_str

        return ({'FINISHED'})

    def execute(self, context):
        remove_model_material(context, 'PROP')

        self.remove_prop_mesh(context, 'MALE')
        self.remove_prop_mesh(context, 'FEMALE')

        bpy.ops.zomboid.check_hat_category(count_self=False)

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})

# ============================================================================================
# HAIR MESH REMOVER
# ============================================================================================


class PZ_RemoveHairMesh(Operator):
    bl_idname = "zomboid.remove_hair_mesh"
    bl_label = "Remove Hair Mesh"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        instance_str = ' (' + str(p.rig_instance) + ')'

        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Male' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-MaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'F':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Female' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-FemaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'B':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Beard' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-Beard' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})

# endregion

# region Randomize Operators

# ============================================================================================
# HAIR MESH RANDOMIZER
# ============================================================================================


class PZ_HairRandomizer(Operator):
    bl_idname = "zomboid.randomize_hair_mesh"
    bl_label = "Randomize Hair Mesh"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        match self.hair_type:
            case 'M':
                rnd = randint(
                    0, len(context.scene.pz_human_male_hair_styles) - 1)
                p.selected_male_hair_style = context.scene.pz_human_male_hair_styles[rnd].name
            case 'F':
                rnd = randint(
                    0, len(context.scene.pz_human_female_hair_styles) - 1)
                p.selected_female_hair_style = context.scene.pz_human_female_hair_styles[
                    rnd].name
            case 'B':
                rnd = randint(0, len(context.scene.pz_human_beard_styles) - 1)
                p.selected_beard_style = context.scene.pz_human_beard_styles[rnd].name

        return ({'FINISHED'})

# ============================================================================================
# HAIR COLOR RANDOMIZER
# ============================================================================================


class PZ_HairColorRandomizer(Operator):
    bl_idname = "zomboid.randomize_hair_color"
    bl_label = "Randomize Hair Color"

    def execute(self, context):
        p = context.active_object.pz_human_props
        color = (1.0, 1.0, 1.0)
        if p.natural_hair_color:
            hair_color_array = [
                (0.658, 0.408, 0.060),  # Mustard Yellow
                (0.397, 0.265, 0.082),  # Coffee
                (0.347, 0.150, 0.024),  # Leather
                (0.333, 0.223, 0.093),  # Dark Beige
                (0.314, 0.162, 0.072),  # Mocha
                (0.298, 0.192, 0.100),  # Dull Brown
                (0.159, 0.095, 0.045),  # Dark Taupe
                (0.093, 0.056, 0.026),  # Dark Brown
                (0.098, 0.036, 0.016),  # Chocolate
                (0.040, 0.022, 0.011),  # Darker Brown
                (0.034, 0.031, 0.029),  # Dark Grey
                (0.011, 0.009, 0.008),  # Black
                (0.201, 0.188, 0.162),  # Medium Grey
                (0.382, 0.342, 0.216),  # Stone
                (0.502, 0.439, 0.338),  # Greyish
                (0.381, 0.371, 0.347),  # Grey
                (0.515, 0.235, 0.136),  # Pinkish Tan
                (0.381, 0.110, 0.061),  # Clay
                (0.300, 0.051, 0.051),  # Light Maroon
                (0.238, 0.055, 0.029)  # Earth
            ]

            rnd = randint(0, len(hair_color_array) - 1)
            color = hair_color_array[rnd]
        else:
            color = (random(), random(), random())

        p.hair_color[0] = color[0]
        p.hair_color[1] = color[1]
        p.hair_color[2] = color[2]

        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY INJURIES
# ============================================================================================


class PZ_HumanRig_RandomizeBodyInjuries(Operator):
    bl_idname = "zomboid.randomize_body_injuries"
    bl_label = "Randomize Body Injuries"
    bl_description = "Randomize the values of all the body intensity options based on a set intensity"

    def execute(self, context):
        p = context.active_object.pz_human_props

        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury",
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]

        p.halt_texture_updates = True

        for injury in injury_props:
            setattr(p, injury, 'NONE')

        options = ['SCRATCH', 'LACERATION', 'BITE']
        chances = [p.random_scratch_chance,
                   p.random_laceration_chance, p.random_bite_chance]

        injury_num = 0
        match p.random_injury_intensity:
            case 'MINOR':
                injury_num = randint(1, 2)
            case 'MODERATE':
                injury_num = randint(3, 4)
            case 'SERIOUS':
                injury_num = randint(5, 6)
            case 'SEVERE':
                injury_num = randint(7, 10)
            case 'INSANE':
                injury_num = randint(11, 16)
            case 'RANDOM':
                injury_num = randint(0, 16)

        for i in range(1, injury_num):
            selected_injury = injury_props[randint(0, len(injury_props) - 1)]
            final_injury = ''
            if randint(1, 100) <= p.random_bandage_chance or selected_injury is p.head_injury:
                if randint(1, 100) <= p.random_bloody_bandage_chance:
                    final_injury = 'BANDAGEBLOODY'
                else:
                    final_injury = 'BANDAGE'
            else:
                final_injury = choices(options, weights=chances)[0]

            if selected_injury == 'head_injury' and selected_injury not in ('NONE', 'BANDAGE', 'BANDAGEBLOODY'):
                continue

            setattr(p, selected_injury, final_injury)

            injury_props.remove(selected_injury)

        bpy.ops.zomboid.construct_body_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE ZOMBIE INJURIES
# ============================================================================================


def filter_zombie_injuries(self, context):
    items = []
    items.append(('NONE', 'None', ''))
    for index, injury in enumerate(context.scene.pz_human_zombie_injuries):
        items.append((injury.name, injury.name, ''))
    return items


class PZ_HumanRig_RandomizeZombieInjuries(Operator):
    bl_idname = "zomboid.randomize_zombie_injuries"
    bl_label = "Randomize Zombie Injuries"
    bl_description = "Add a set or random amount of random zombie specific injuries"

    def execute(self, context):
        p = context.active_object.pz_human_props

        injury_choices = filter_zombie_injuries(self, context)

        zombie_injuries = context.active_object.pz_human_zombie_injuries

        p.halt_texture_updates = True

        zombie_injuries.clear()

        injury_num = 0
        match p.random_zombie_injury_intensity:
            case 'INTACT':
                injury_num = randint(1, 3)
            case 'DAMAGED':
                injury_num = randint(3, 5)
            case 'HACKED APART':
                injury_num = randint(5, 15)
            case 'MUTILATED':
                injury_num = randint(20, 40)
            case 'RENDED APART':
                injury_num = randint(40, 73)
            case 'RANDOM':
                injury_num = randint(0, 73)

        for i in range(1, injury_num):
            selected_injury = injury_choices[randint(
                0, len(injury_choices) - 1)]

            if selected_injury[0] == 'NONE':
                injury_choices.remove(selected_injury)
                continue

            new_injury = zombie_injuries.add()
            new_injury.name = selected_injury[0]
            new_injury.texture_path = context.scene.pz_human_zombie_injuries.get(
                selected_injury[0]).texture_path

            injury_choices.remove(selected_injury)

        bpy.ops.zomboid.construct_body_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY BLOODINESS
# ============================================================================================


class PZ_HumanRig_RandomizeBodyBloodiness(Operator):
    bl_idname = "zomboid.randomize_body_bloodiness"
    bl_label = "Randomize Body Bloodiness"
    bl_description = "Randomize the values of all the body bloodiness options based on a set intensity"

    def execute(self, context):
        p = context.active_object.pz_human_props

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                       "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                       "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                       "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                       "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                       "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

        p.halt_texture_updates = True

        for blood in blood_props:
            setattr(p, blood, 0)
            bloodiness = 0
            match p.random_bloodiness_intensity:
                case 'SOME':
                    bloodiness = uniform(0.0, 1.5)
                case 'MODERATE':
                    bloodiness = uniform(0.0, 2.5)
                case 'LOTS':
                    bloodiness = uniform(0.0, 3.5)
                case 'DRENCHED':
                    bloodiness = uniform(0.0, 5.0)

            setattr(p, blood, bloodiness)

        bpy.ops.zomboid.create_body_bloodiness_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY DIRTINESS
# ============================================================================================


class PZ_HumanRig_RandomizeBodyDirtiness(Operator):
    bl_idname = "zomboid.randomize_body_dirtiness"
    bl_label = "Randomize Body Dirtiness"
    bl_description = "Randomize the values of all the body dirtiness options based on a set intensity"

    def execute(self, context):
        p = context.active_object.pz_human_props

        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                      "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                      "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                      "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness",
                      "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                      "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]

        p.halt_texture_updates = True

        for dirt in dirt_props:
            setattr(p, dirt, 0)
            dirtiness = 0
            match p.random_dirtiness_intensity:
                case 'SOME':
                    dirtiness = uniform(0.0, 0.5)
                case 'MODERATE':
                    dirtiness = uniform(0.0, 0.8)
                case 'LOTS':
                    dirtiness = uniform(0.0, 1.2)
                case 'DISGUSTING':
                    dirtiness = uniform(0.0, 2.0)

            setattr(p, dirt, dirtiness)

        bpy.ops.zomboid.create_body_dirtiness_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})

# endregion

# region Zeroing Operators

# ============================================================================================
# REMOVE BLOODINESS
# ============================================================================================


class PZ_HumanRig_RemoveBodyBloodiness(Operator):
    bl_idname = "zomboid.remove_body_bloodiness"
    bl_label = "Remove Bloodiness"
    bl_description = "Sets all bloodiness on the body to zero"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                       "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                       "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                       "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                       "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                       "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for blood in blood_props:
            setattr(p, blood, 0)

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_body_bloodiness_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE DIRTINESS
# ============================================================================================


class PZ_HumanRig_RemoveBodyDirtiness(Operator):
    bl_idname = "zomboid.remove_body_dirtiness"
    bl_label = "Remove Dirtiness"
    bl_description = "Sets all dirtiness on the body to zero"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                      "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                      "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                      "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness",
                      "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                      "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for dirt in dirt_props:
            setattr(p, dirt, 0)

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_body_dirtiness_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL BODY INJURIES
# ============================================================================================


class PZ_HumanRig_RemoveAllBodyInjuries(Operator):
    bl_idname = "zomboid.remove_all_body_injuries"
    bl_label = "Remove All Body Injuries"
    bl_description = "Removes all body injuries"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury",
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for injury in injury_props:
            setattr(p, injury, 'NONE')

        if self.halt_texture_updates:
            bpy.ops.zomboid.construct_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL ZOMBIE INJURIES
# ============================================================================================


class PZ_HumanRig_RemoveAllZombieInjuries(Operator):
    bl_idname = "zomboid.remove_all_zombie_injuries"
    bl_label = "Remove All Zombie Injuries"
    bl_description = "Removes all zombie injuries"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        context.active_object.pz_human_zombie_injuries.clear()

        if self.halt_texture_updates:
            bpy.ops.zomboid.construct_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})


# ============================================================================================
# REMOVE ALL BODY DAMAGE
# ============================================================================================

class PZ_HumanRig_RemoveAllBodyDamage(Operator):
    bl_idname = "zomboid.remove_all_body_damage"
    bl_label = "Remove All Body Damage"
    bl_description = "Removes all body damage"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        bpy.ops.zomboid.remove_body_bloodiness(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_body_dirtiness(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_all_body_injuries(halt_texture_updates=self.halt_texture_updates)
        bpy.ops.zomboid.remove_all_zombie_injuries(halt_texture_updates=self.halt_texture_updates)

        if self.halt_texture_updates:
            bpy.ops.zomboid.construct_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})

# endregion

# region Parsing Operators

# ============================================================================================
# GET ALL MOD DIRECTORIES
# ============================================================================================


class PZ_HumanRig_GetAllModDirectories(Operator):
    bl_idname = "zomboid.get_all_mod_directories"
    bl_label = "Get All Mod Directories"
    bl_description = "Automatically grabs all installed mods and populates the directories folder for you. It does this by traversing upwards twice from the Project Zomboid directory into \'steamapps\', then goes into the workshop/common/108600 folder where your mods are installed"

    @classmethod
    def poll(cls, context):
        g = context.scene.pz_human_global_props
        return g.pz_directory != ''

    def execute(self, context):
        g = context.scene.pz_human_global_props
        dirs = context.scene.pz_human_mod_directory_slots

        dirs.clear()

        pz_dir = Path(g.pz_directory)
        steamapps_dir = pz_dir.parent.parent
        mods_dir = steamapps_dir / 'workshop' / 'content' / '108600'

        mod_folders = [item for item in mods_dir.iterdir() if item.is_dir()]

        for mod_path in mod_folders:
            submods_dir = mod_path / 'mods'
            submod_folders = [
                item for item in submods_dir.iterdir() if item.is_dir()]
            for submod_path in submod_folders:
                # For now, just ignore any mods that don't have a 42 version
                version_folders = [
                    item for item in submod_path.iterdir() if item.is_dir()]

                latest_submod_version_folder = None
                latest_submod_version_num = 0.0
                for folder in version_folders:
                    try:
                        if float(folder.name) > latest_submod_version_num:
                            latest_submod_version_folder = folder
                            latest_submod_version_num = float(folder.name)
                    except ValueError:
                        continue
                if latest_submod_version_folder is not None:
                    mod_name = ''
                    mod_author = ''
                    try:
                        with open(latest_submod_version_folder / 'mod.info', 'r') as file:
                            for line in file:
                                info_line = line.strip()

                                if ('name=') in info_line:
                                    mod_name = info_line.split('name=')[1]
                                elif ('author=') in info_line:
                                    mod_author = info_line.split('author=')[1]

                        new_dir = dirs.add()
                        if mod_name != '':
                            new_dir.name = mod_name
                        if mod_author != '':
                            new_dir.author = mod_author
                        new_dir.mod_dir = str(latest_submod_version_folder)
                        new_dir.latest_pz_version = round(
                            latest_submod_version_num, 2)

                    except FileNotFoundError:
                        pass

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL MOD DIRECTORIES
# ============================================================================================


class PZ_HumanRig_RemoveAllModDirectories(Operator):
    bl_idname = "zomboid.remove_all_mod_directories"
    bl_label = "Remove All Mod Directories"
    bl_description = "Removes all of the loaded mod directories"

    def execute(self, context):
        context.scene.pz_human_mod_directory_slots.clear()
        context.scene.pz_human_global_props.mod_directory_slot_active_index = -1
        return ({'FINISHED'})

# ============================================================================================
# GET ALL ANIMATIONS
# ============================================================================================


class PZ_HumanRig_GetAllAnimations(Operator):
    bl_idname = "zomboid.get_all_animations"
    bl_label = "Get All Animations"
    bl_description = "Find all humanoid animations and create a list for them"

    def parse_anim_folder(self, context, path: Path, origin: str, anim_list):

        allowed_suffixes = ['.x', '.fbx', '.glb']

        for file in path.iterdir():
            if file.is_dir():
                self.parse_anim_folder(context, file, origin, anim_list)
            if file.is_file() and file.suffix.lower() in allowed_suffixes:
                a = anim_list.add()

                a.name = file.name
                a.file_type = file.suffix.lower()
                a.anim_path = str(file)
                a.origin = origin

                if 'Bob' in a.name:
                    a.character_type = 'Bob'
                elif 'Kate' in a.name:
                    a.character_type = 'Kate'
                elif 'Zombie' in a.name:
                    a.character_type = 'Zombie'

                print(a.name)

    def execute(self, context):
        a_list = context.scene.pz_human_imported_animations

        a_list.clear()

        all_anim_folders = []

        # TODO Cleanup

        # Check if these are the anims_x folders
        for folder, mod_name in get_zomboid_asset_folders(context, 'Bob'):
            if folder.parent.name.lower() == 'anims_x':
                all_anim_folders.append((folder, mod_name))
        for folder, mod_name in get_zomboid_asset_folders(context, 'Kate'):
            if folder.parent.name.lower() == 'anims_x':
                all_anim_folders.append((folder, mod_name))
        for folder, mod_name in get_zomboid_asset_folders(context, 'Zombie'):
            if folder.parent.name.lower() == 'anims_x':
                all_anim_folders.append((folder, mod_name))

        # Parse the folders
        for folder, mod_name in all_anim_folders:
            self.parse_anim_folder(context, folder, mod_name, a_list)

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL ANIMATIONS
# ============================================================================================

# ============================================================================================
# CLOTHING XML PARSER
# ============================================================================================


class PZ_HumanRig_ParseClothingXMLs(Operator):
    bl_idname = "zomboid.parse_clothing_xmls"
    bl_label = "Parse Clothing XMLs"
    bl_description = "Parse all the clothing xmls to get the data needed to import into Blender"

    item_count = 0

    def parse_folder(self, context, dir, clothing_items, origin):
        for file in dir.glob("*.xml"):
            if file.is_file():
                try:
                    # Begin parsing the XML contents of the file
                    tree = ET.parse(file)
                    root = tree.getroot()

                    # If there is an existing clothing item with the same name as the file we are about to evaluate, remove it and overwrite it
                    overwrite_check = clothing_items.find(
                        os.path.splitext(file.name)[0])
                    if overwrite_check != -1:
                        clothing_items.remove(
                            overwrite_check)

                    # Create and fill out the clothing item slot
                    item = clothing_items.add()

                    # Name
                    item.name = os.path.splitext(file.name)[0]

                    # GUID
                    m = root.find('m_GUID')
                    if m is not None:
                        item.guid = m.text

                    # Models
                    def get_model(xml_id):
                        m = root.find(xml_id)
                        if m is not None and m.text is not None:
                            path = m.text
                            start = path.find(':') + 1
                            end = path.find('.')
                            if end == -1:
                                path = path[start:]
                            else:
                                path = path[start:end]
                            if 'media\\models_X' not in path:
                                path = str(Path('media') /
                                           'models_X' / Path(path))
                            x, y = get_zomboid_asset(context, path)
                            if y is not None:
                                return (str(x), y, False)
                            else:
                                return ('None', 'N/A', True)
                        else:
                            return ('None', 'N/A', True)

                    item.male_model_path, item.model_type, item.is_body_texture = get_model(
                        'm_MaleModel')
                    item.female_model_path, item.model_type, item.is_body_texture = get_model(
                        'm_FemaleModel')

                    # Textures
                    base_texture = root.find('m_BaseTextures')
                    textures = root.findall('textureChoices')
                    if base_texture is not None:
                        tex = item.texture_choices.add()
                        x = get_zomboid_asset(context, base_texture.text)
                        tex.texture_path = str(x[0])
                    for t in textures:
                        tex = item.texture_choices.add()
                        x = get_zomboid_asset(context, t.text)
                        tex.texture_path = str(x[0])

                    # Tintable
                    m = root.find('m_AllowRandomTint')
                    if m is not None and m.text == 'true':
                        item.tintable = True
                    else:
                        item.tintable = False

                    # Attach Bone
                    m = root.find('m_AttachBone')
                    if m is not None and m.text is not None:
                        item.attach_bone = m.text
                    else:
                        item.attach_bone = 'None'

                    # Static
                    m = root.find('m_Static')
                    if m is not None and m.text == 'true':
                        item.static = True
                    else:
                        item.static = False

                    # Masks
                    masks = root.findall('m_Masks')
                    for m in masks:
                        item.mask_array[int(m.text)] = True

                    # Hat Category
                    m = root.find('m_HatCategory')
                    if m is not None:
                        match m.text:
                            case 'default':
                                item.hat_category = 0
                            case 'Group01':
                                item.hat_category = 1
                            case 'Group02':
                                item.hat_category = 2
                            case 'Group03':
                                item.hat_category = 3
                            case 'Group04':
                                item.hat_category = 4
                            case 'Group05':
                                item.hat_category = 5
                            case 'Group06':
                                item.hat_category = 6
                            case 'Group07':
                                item.hat_category = 7
                            case 'nohair':
                                item.hat_category = 8
                            case 'nohairnobeard':
                                item.hat_category = 9
                    else:
                        item.hat_category = -1

                    # Decal Group
                    m = root.find('m_DecalGroup')
                    if m is not None:
                        item.decal_group = m.text

                    # Origin
                    item.origin = origin

                    self.item_count = self.item_count + 1
                except ET.ParseError:
                    continue

    def execute(self, context):
        clothing_items = context.scene.pz_human_clothing_item_slots
        for folder in get_zomboid_asset_folders(context, 'clothingItems'):
            self.parse_folder(context, folder[0], clothing_items, folder[1])

        self.report({'INFO'}, "Parsed " +
                    str(self.item_count) + " Clothing Item XMLs")
        return ({'FINISHED'})

# ============================================================================================
# OUTFIT XML PARSER
# ============================================================================================


class PZ_HumanRig_ParseOutfitXMLs(Operator):
    bl_idname = "zomboid.parse_outfit_xmls"
    bl_label = "Parse Outfit XMLs"
    bl_description = "Parse all the outfit xmls to get the data needed to import into Blender"

    outfit_count = 0

    def parse_xml(self, context, dir, outfits, origin, lookup):
        g = context.scene.pz_human_global_props

        # Begin parsing the XML contents of the file
        tree = ET.parse(dir)
        root = tree.getroot()

        female_outfits = root.findall('m_FemaleOutfits')
        male_outfits = root.findall('m_MaleOutfits')

        for outfit in female_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = context.scene.pz_human_outfit_slots.find(
                outfit.find('m_Name').text)
            if overwrite_index != -1:
                if context.scene.pz_human_outfit_slots.get(outfit.find('m_Name').text).sex == 'FEMALE':
                    context.scene.pz_human_outfit_slots.remove(overwrite_index)
                    female_outfits.remove(outfit)

            item = outfits.add()

            item.name = outfit.find('m_Name').text
            item.search_name = item.name + ' (Female)'
            item.sex = 'FEMALE'
            item.guid = outfit.find('m_Guid').text
            item.origin = origin

            if outfit.find('m_Top') is not None and outfit.find('m_Top').text != 'true':
                item.random_top = False
            else:
                item.random_top = True

            if outfit.find('m_Pants') is not None and outfit.find('m_Pants').text != 'true':
                item.random_pants = False
            else:
                item.random_pants = True

            clothing_items = outfit.findall('m_items')
            for clothing_item in clothing_items:
                new_clothing_item = item.outfit_items.add()

                # Get item probability
                if clothing_item.find('probability') is not None:
                    new_clothing_item.probability = float(
                        clothing_item.find('probability').text)

                # Get first item choice
                choice = new_clothing_item.choices.add()

                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    if choice.guid in lookup:
                        choice.name = lookup[choice.guid]

                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        if choice.guid in lookup:
                            choice.name = lookup[choice.guid]

            self.outfit_count = self.outfit_count + 1
        for outfit in male_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = context.scene.pz_human_outfit_slots.find(
                outfit.find('m_Name').text)
            if overwrite_index != -1:
                if context.scene.pz_human_outfit_slots.get(outfit.find('m_Name').text).sex == 'MALE':
                    context.scene.pz_human_outfit_slots.remove(overwrite_index)
                    male_outfits.remove(outfit)

            item = outfits.add()

            item.name = outfit.find('m_Name').text
            item.search_name = item.name + ' (Male)'
            item.sex = 'MALE'
            item.guid = outfit.find('m_Guid').text
            item.origin = origin

            if outfit.find('m_Top') is not None and outfit.find('m_Top').text != 'true':
                item.random_top = False
            else:
                item.random_top = True

            if outfit.find('m_Pants') is not None and outfit.find('m_Pants').text != 'true':
                item.random_pants = False
            else:
                item.random_pants = True

            clothing_items = outfit.findall('m_items')
            for clothing_item in clothing_items:
                new_clothing_item = item.outfit_items.add()

                # Get item probability
                if clothing_item.find('probability') is not None:
                    new_clothing_item.probability = float(
                        clothing_item.find('probability').text)

                # Get first item choice
                choice = new_clothing_item.choices.add()

                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    if choice.guid in lookup:
                        choice.name = lookup[choice.guid]

                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        if choice.guid in lookup:
                            choice.name = lookup[choice.guid]

            self.outfit_count = self.outfit_count + 1

    def execute(self, context):
        g = context.scene.pz_human_global_props
        outfits = context.scene.pz_human_outfit_slots

        g.outfit_slot_active_index = 0
        outfits.clear()

        clothing_lookup = {
            clothing.guid : clothing.name for clothing in context.scene.pz_human_clothing_item_slots
        }

        for folder, mod_name in get_zomboid_asset_folders(context, 'clothing'):
            if (folder / 'clothing.xml').is_file():
                self.parse_xml(context, str(folder / 'clothing.xml'), outfits, mod_name, clothing_lookup)

        self.report({'INFO'}, "Parsed " + str(self.outfit_count) + " Outfits")
        return {'FINISHED'}

# ============================================================================================
# HAIR STYLE XML PARSER
# ============================================================================================


class PZ_HumanRig_ParseHairStyleXMLs(Operator):
    bl_idname = "zomboid.parse_hair_style_xmls"
    bl_label = "Parse Hair Style XMLs"
    bl_description = "Parse all the hair style xmls to get the data needed to import into Blender"

    hair_count = 0
    beard_count = 0

    def parse_hair_xml(self, context, dir, hair_styles, male_styles, female_styles, origin):
        g = context.scene.pz_human_global_props

        tree = ET.parse(dir)
        root = tree.getroot()

        male_hair_styles = root.findall('male')
        female_hair_styles = root.findall('female')

        for hair in male_hair_styles:
            m = hair.find('name')
            if m is not None and m.text is not None:
                overwrite_index = hair_styles.find(m.text)
                if overwrite_index != -1:
                    if hair_styles.get(m.text).sex == 'MALE':
                        hair_styles.remove(overwrite_index)
                        male_styles.remove(male_styles.find(m.text))

            item = hair_styles.add()

            item.name = hair.find('name').text
            item.sex = 'MALE'

            m = hair.find('level')
            if m is not None and m.text is not None:
                item.level = int(hair.find('level').text)
            else:
                item.level = 0

            texture = hair.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'

            for hat_group in hair.findall('alternate'):
                x = -1
                match hat_group.get('category'):
                    case 'default':
                        x = 0
                    case 'Group01':
                        x = 1
                    case 'Group02':
                        x = 2
                    case 'Group03':
                        x = 3
                    case 'Group04':
                        x = 4
                    case 'Group05':
                        x = 5
                    case 'Group06':
                        x = 6
                    case 'Group07':
                        x = 7
                if x != -1:
                    group = item.hat_styles.add()
                    group.hat_group = x
                    group.style_name = hat_group.get('style')

            no_choose = hair.find('noChoose')

            if no_choose is not None and no_choose.text == 'true':
                pass
            else:
                new = male_styles.add()
                new.name = item.name

            item.origin = origin

            self.hair_count = self.hair_count + 1

        for hair in female_hair_styles:
            m = hair.find('name')
            if m is not None and m.text is not None:
                overwrite_index = hair_styles.find(m.text)
                if overwrite_index != -1:
                    if hair_styles.get(m.text).sex == 'FEMALE':
                        hair_styles.remove(overwrite_index)
                        female_styles.remove(female_styles.find(m.text))

            item = hair_styles.add()

            item.name = hair.find('name').text
            item.sex = 'FEMALE'

            m = hair.find('level')
            if m is not None and m.text is not None:
                item.level = int(hair.find('level').text)
            else:
                item.level = 0

            texture = hair.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            # match hair.find('texture').text:
            #     case 'F_Hair_White':
            #         item.texture_type = 'NORMAL'
            #     case 'F_Hair_Braids':
            #         item.texture_type = 'BRAIDS'
            #     case 'F_HairCurly_Short':
            #         item.texture_type = 'SHORTCURLY'
            #     case 'F_HairCurly_Long':
            #         item.texture_type = 'LONGCURLY'

            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'

            for hat_group in hair.findall('alternate'):
                x = -1
                match hat_group.get('category'):
                    case 'default':
                        x = 0
                    case 'Group01':
                        x = 1
                    case 'Group02':
                        x = 2
                    case 'Group03':
                        x = 3
                    case 'Group04':
                        x = 4
                    case 'Group05':
                        x = 5
                    case 'Group06':
                        x = 6
                    case 'Group07':
                        x = 7
                if x != -1:
                    group = item.hat_styles.add()
                    group.hat_group = x
                    group.style_name = hat_group.get('style')

            no_choose = hair.find('noChoose')

            if no_choose is not None and no_choose.text == 'true':
                pass
            else:
                new = female_styles.add()
                new.name = item.name

            item.origin = origin

            self.hair_count = self.hair_count + 1

    def parse_beard_xml(self, context, dir, beard_styles, origin):
        g = context.scene.pz_human_global_props

        tree = ET.parse(dir)
        root = tree.getroot()

        beard_styles = root.findall('style')

        for beard in beard_styles:
            bpy.ops.zomboid.add_beard_style_slot()
            item = context.scene.pz_human_beard_styles[g.beard_style_slot_active_index]

            item.name = beard.find('name').text

            m = beard.find('level')
            if m is not None and m.text is not None:
                item.level = int(beard.find('level').text)
            else:
                item.level = 0

            texture = beard.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            item.model_path = beard.find('model').text

            self.beard_count = self.beard_count + 1

    def execute(self, context):
        g = context.scene.pz_human_global_props
        hair_styles = context.scene.pz_human_hair_style_slots
        male_styles = context.scene.pz_human_male_hair_styles
        female_styles = context.scene.pz_human_female_hair_styles
        beard_styles = context.scene.pz_human_beard_styles

        g.hair_style_slot_active_index = 0
        hair_styles.clear()
        male_styles.clear()
        female_styles.clear()
        beard_styles.clear()

        # Add a 'clean' beard option
        item = beard_styles.add()
        item.name = 'None'
        item.model_path = 'None'
        item.level = 0

        for folder, mod_name in get_zomboid_asset_folders(context, 'hairStyles'):
            if (folder / 'hairStyles.xml').is_file():
                self.parse_hair_xml(context, str(folder / 'hairStyles.xml'), hair_styles, male_styles, female_styles, mod_name)
            if (folder / 'beardStyles.xml').is_file():
                self.parse_beard_xml(context, str(folder / 'beardStyles.xml'), beard_styles, mod_name)

        self.report({'INFO'}, "Parsed " + str(self.hair_count) +
                    " Hair Styles & " + str(self.beard_count) + " Beard Styles")
        return ({'FINISHED'})

# ============================================================================================
# DECAL XML PARSER
# ============================================================================================


class PZ_HumanRig_ParseDecalXMLs(Operator):
    bl_idname = "zomboid.parse_decal_xmls"
    bl_label = "Parse Decal XMLs"
    bl_description = "Parse all the clothing xmls to get the data needed to import into Blender"

    def parse_decals(self, context):
        g = context.scene.pz_human_global_props

        g.decal_slot_active_index = 0

        decals = context.scene.pz_human_decals
        decals.clear()

        xmls_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xmls_dir = g.pz_directory + '\\media\\clothing\\clothingDecals'
        elif sys.platform == 'linux':
            xmls_dir = g.pz_directory + '/projectzomboid/media/clothing/clothingDecals'

        xmls_dir = Path(xmls_dir)

        item_count = 0
        for file in xmls_dir.glob("*.xml"):
            if file.is_file():
                decal = decals.add()

                # Parse the file name
                decal.name = os.path.splitext(file.name)[0]

                # Begin parsing the XML contents of the file
                tree = ET.parse(file)
                root = tree.getroot()

                decal.texture_path = root.find('texture').text
                decal.x = int(root.find('x').text)
                decal.y = int(root.find('y').text)
                decal.width = int(root.find('width').text)
                decal.height = int(root.find('height').text)

                item_count += 1

        return ({'FINISHED'})

    def parse_decal_groups(self, context):
        g = context.scene.pz_human_global_props
        current_groups = context.scene.pz_human_decal_groups

        g.decal_group_slot_active_index = 0
        current_groups.clear()

        xmls_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xml_dir = g.pz_directory + 'media\\clothing\\clothingDecals.xml'
        elif sys.platform == 'linux':
            xml_dir = g.pz_directory + 'projectzomboid/media/clothing/clothingDecals.xml'

        decal_count = 0

        # Begin parsing the XML contents of the hair file
        tree = ET.parse(xml_dir)
        root = tree.getroot()

        decal_groups = root.findall('group')
        for decal_group in decal_groups:
            new_group = context.scene.pz_human_decal_groups.add()
            new_group.name = decal_group.find('name').text

            decals = decal_group.findall('decal')
            for decal in decals:
                new_decal = new_group.decals.add()
                new_decal.name = decal.text

        return ({'FINISHED'})

    def execute(self, context):
        self.parse_decals(context)
        self.parse_decal_groups(context)

        return ({'FINISHED'})

# ============================================================================================
# BODYLOCATION LUA PARSER
# ============================================================================================


class PZ_HumanRig_ParseBodyLocationLua(Operator):
    bl_idname = "zomboid.parse_body_location_lua"
    bl_label = "Parse Body Location Lua"
    bl_description = "Parse the BodyLocations.lua file to get all the available body locations and their interactions with other body locations"

    def parse_body_locations_lua(self, context):
        g = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations

        body_locations.clear()

        g.body_location_active_index = 0

        file_dir = ''

        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = g.pz_directory + 'media\\lua\\shared\\NPCs\\BodyLocations.lua'
        elif sys.platform == 'linux':
            file_dir = g.pz_directory + 'projectzomboid/media/lua/shared/NPCs/BodyLocations.lua'

        with open(file_dir, 'r', encoding='utf-8') as file:
            for line in file:
                lua_line = line.strip()

                # Line creates a new body location
                if 'getOrCreateLocation' in lua_line:
                    pattern = r'\.(.*?)\)'
                    body_location = body_locations.add()
                    body_location.name = re.findall(pattern, lua_line)[0]

                elif 'setExclusive' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.exclusive_locations.add()
                            hide_loc.name = matches[0]
                            break

                elif 'setHideModel' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.hide_locations.add()
                            hide_loc.name = matches[0]
                            break

                elif 'setAltModel' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.alt_locations.add()
                            hide_loc.name = matches[0]
                            break

        return ({'FINISHED'})

    def parse_clothing_txt(self, context):
        g = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations
        clothing_items = context.scene.pz_human_clothing_item_slots

        file_dir = ''

        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = g.pz_directory + 'media\\scripts\\generated\\items\\clothing.txt'
        elif sys.platform == 'linux':
            file_dir = g.pz_directory + 'projectzomboid/media/scripts/generated/items/clothing.txt'

        in_main_portion = False
        in_item_block = False

        current_clothing_item = ''
        current_body_location = ''

        with open(file_dir, 'r', encoding='utf-8') as file:
            # TODO: Replace with albion's more sophisticated parser
            for line in file:
                txt_line = line.strip()

                if not in_main_portion and '{' in txt_line:
                    in_main_portion = True
                    continue

                if in_main_portion and not in_item_block:
                    if 'item' in txt_line:
                        current_clothing_item = txt_line.split('item ')[1]
                        continue
                    if '{' in txt_line:
                        in_item_block = True
                        continue
                    if '}' in txt_line:
                        in_main_portion = False
                        continue

                if in_main_portion and in_item_block:
                    if 'BodyLocation' in txt_line:
                        current_body_location = txt_line.split(
                            ':')[1].split(',')[0].upper()
                        # print(current_body_location)

                    if 'ClothingItem' in txt_line:
                        current_clothing_item = txt_line.split('= ')[
                            1].split(',')[0]
                        # print(current_clothing_item)

                    if '}' in txt_line:
                        in_item_block = False

                        for clothing_item in clothing_items:
                            if clothing_item.name == current_clothing_item:
                                for body_location in body_locations:
                                    if body_location.name == current_body_location:

                                        current_clothing_item = ''
                                        current_body_location = ''
                                    break
                                break

                        continue

        return ({'FINISHED'})

    def execute(self, context):
        self.parse_body_locations_lua(context)
        self.parse_clothing_txt(context)

        return ({'FINISHED'})

# ============================================================================================
# PARSE INJURIES
# ============================================================================================


class PZ_HumanRig_ParseInjuries(Operator):
    bl_idname = "zomboid.parse_injuries"
    bl_label = "Parse Injuries"
    bl_description = "Parse all the injury textures so Blender can pull them later"

    body_parts = ['chest', 'abdomen', 'left_hand', 'right_hand', 'lower_left_arm',
                  'lower_right_arm', 'upper_left_arm', 'upper_right_arm', 'head',
                  'neck', 'groin', 'left_thigh', 'right_thigh',
                  'left_calf', 'right_calf', 'left_foot', 'right_foot']

    body_part_pattern = r"(?:" + "|".join(re.escape(part)
                                          for part in body_parts) + r")"
    body_part_regex = re.compile(body_part_pattern)

    injury_types = ['scratches', 'lacerations', 'bites', 'bandages']

    injury_type_pattern = r"(?:" + "|".join(re.escape(injury)
                                            for injury in injury_types) + r")"
    injury_type_regex = re.compile(injury_type_pattern)

    def execute(self, context):
        body_injuries = context.scene.pz_human_body_injuries
        zombie_injuries = context.scene.pz_human_zombie_injuries

        body_injuries.clear()
        zombie_injuries.clear()

        for folder, mod_name in get_zomboid_asset_folders(context, 'BodyDmg'):
            for file in folder.iterdir():
                if file.is_file() and file.suffix == '.png':
                    if 'M_ZedDmg' in file.name:
                        injury = zombie_injuries.add()
                        injury.name = file.name
                        injury.texture_path = str(file)
                        continue

                injury = body_injuries.add()

                injury.sex = 'FEMALE' if 'FemaleBody' in file.name else 'MALE'

                body_part = self.body_part_regex.search(file.name)
                if body_part is not None:
                    injury.body_part = body_part.group()

                damage_type = self.injury_type_regex.search(file.name)
                if damage_type is not None:
                    match damage_type.group():
                        case 'scratches':
                            injury.damage_type = 'SCRATCH'
                        case 'lacerations':
                            injury.damage_type = 'LACERATION'
                        case 'bites':
                            injury.damage_type = 'BITE'
                        case 'bandages':
                            if '_blood' in file.name:
                                injury.damage_type = 'BANDAGEBLOODY'
                            else:
                                injury.damage_type = 'BANDAGE'
                injury.texture_path = str(file)

        return ({'FINISHED'})

# ============================================================================================
# PARSE SKIN, STUBBLE, AND MASK TEXTURES
# ============================================================================================

class PZ_HumanRig_ParseSkinTextures(Operator):
    bl_idname = "zomboid.parse_skin_textures"
    bl_label = "Parse Skin & Stubble Textures"
    bl_description = "Parse all the skin and stubble textures so Blender can pull them later"

    def execute(self, context):
        g = context.scene.pz_human_global_props

        skin_textures = context.scene.pz_human_skin_textures
        stubble_textures = context.scene.pz_human_stubble_textures
        visibility_masks = context.scene.pz_human_visibility_masks
        overlay_masks = context.scene.pz_human_overlay_masks

        skin_textures.clear()
        stubble_textures.clear()
        visibility_masks.clear()
        overlay_masks.clear()

        #TODO Find a way to find the texture names without being predetermined, and optimize

        human_skin_tex_names = [
            'MaleBody01',
            'MaleBody01a',
            'MaleBody02',
            'MaleBody02a',
            'MaleBody03',
            'MaleBody03a',
            'MaleBody04',
            'MaleBody04a',
            'MaleBody05',
            'MaleBody05a',
            'FemaleBody01',
            'FemaleBody02',
            'FemaleBody03',
            'FemaleBody04',
            'FemaleBody05',
        ]

        zombie_skin_tex_names = [
            'M_ZedBody01_level1',
            'M_ZedBody01_level2',
            'M_ZedBody01_level3',
            'M_ZedBody02_level1',
            'M_ZedBody02_level2',
            'M_ZedBody02_level3',
            'M_ZedBody03_level1',
            'M_ZedBody03_level2',
            'M_ZedBody03_level3',
            'M_ZedBody04_level1',
            'M_ZedBody04_level2',
            'M_ZedBody04_level3',
            'M_ZedBody05_level1',
            'M_ZedBody05_level2',
            'M_ZedBody05_level3',

            'F_ZedBody01_level1',
            'F_ZedBody01_level2',
            'F_ZedBody01_level3',
            'F_ZedBody02_level1',
            'F_ZedBody02_level2',
            'F_ZedBody02_level3',
            'F_ZedBody03_level1',
            'F_ZedBody03_level2',
            'F_ZedBody03_level3',
            'F_ZedBody04_level1',
            'F_ZedBody04_level2',
            'F_ZedBody04_level3',
            'F_ZedBody05_level1',
            'F_ZedBody05_level2',
            'F_ZedBody05_level3',
        ]

        mannequin_tex_names = [
            'M_Mannequin_Black',
            'M_Mannequin_White'
        ]

        scarecrow_tex_names = [
            'Male_Scarecrow'
        ]

        skeleton_tex_names = [
            'Skeleton',
            'SkeletonBurned',
            'SkeletonMuscle'
        ]

        tone_pattern = r'(?<=Body)(\d+)'
        tone_regex = re.compile(tone_pattern)

        zombification_pattern = r'(?<=level)(\d+)'
        zombification_regex = re.compile(zombification_pattern)

        overlay_mask_pattern = r'(?<=BloodMask).*'
        overlay_mask_regex = re.compile(overlay_mask_pattern)

        for folder, mod_name in get_zomboid_asset_folders(context, 'Body'):
            if folder.parent.name.lower() == 'textures':

                # Skin Textures
                for file in folder.iterdir():
                    if file.is_file():
                        if file.stem in human_skin_tex_names + zombie_skin_tex_names + mannequin_tex_names + scarecrow_tex_names + skeleton_tex_names:    
                            overwrite_check = skin_textures.find(file.stem)
                            if overwrite_check != -1:
                                if g.allow_overwriting:
                                    skin_textures.remove(overwrite_check)
                                else:
                                    continue
                            
                            item = skin_textures.add()

                            item.name = file.stem
                            item.texture_path = str(file)
                            item.origin = mod_name

                            if file.stem in human_skin_tex_names:
                                item.body_type = 'HUMAN'
                                item.sex = 'FEMALE' if 'FemaleBody' in file.stem else 'MALE'
                                item.skin_tone = int(tone_regex.search(file.stem).group())
                                item.chest_hair = file.stem.endswith('a')
                                continue

                            if file.stem in zombie_skin_tex_names:
                                item.body_type = 'ZOMBIE'
                                item.zombification = int(zombification_regex.search(file.stem).group())
                                item.sex = 'FEMALE' if 'F_' in file.stem else 'MALE'
                                item.skin_tone = int(tone_regex.search(file.stem).group())
                                continue
                                
                            if file.stem in mannequin_tex_names:
                                item.body_type = 'MANNEQUIN'
                                item.sex = 'FEMALE' if 'F_' in file.stem else 'MALE'
                                continue

                            if file.stem in skeleton_tex_names:
                                item.body_type = 'SKELETON'
                                continue

                            if file.stem in scarecrow_tex_names:
                                item.body_type = 'SCARECROW'
                                continue
                    
                    if file.is_dir():

                        # Stubble Textures
                        if file.name.lower() == 'stubble':
                            for subfile in file.iterdir():
                                overwrite_check = stubble_textures.find(subfile.stem)
                                if overwrite_check != -1:
                                    if g.allow_overwriting:
                                        stubble_textures.remove(overwrite_check)
                                    else:
                                        continue
                                
                                item = stubble_textures.add()
                                
                                item.texture_path = str(subfile)
                                item.name = subfile.stem
                                item.sex = 'FEMALE' if 'F_' in subfile.stem else 'MALE'
                                item.stubble_type = 'BEARD' if 'Beard' in subfile.stem else 'HAIR'
                                item.origin = mod_name
                        
                        # Visibility Masks
                        if file.name.lower() == 'masks':
                            for subfile in file.iterdir():
                                overwrite_check = visibility_masks.find(subfile.stem)
                                if overwrite_check != -1:
                                    if g.allow_overwriting:
                                        visibility_masks.remove(overwrite_check)
                                    else:
                                        continue

                                item = visibility_masks.add()
                                
                                item.name = 'FullBody' if subfile.stem == 'Mask' else subfile.stem
                                item.texture_path = str(subfile)

            # Overlay Masks
            if (folder.parent / 'BloodTextures').is_dir():

                for file in (folder.parent / 'BloodTextures').iterdir():
                    # No need for overwriting
                    if 'BloodMask' in file.stem:
                        item = overlay_masks.add()
                        
                        item.name = overlay_mask_regex.search(file.stem).group()
                        item.texture_path = str(file)

        return ({'FINISHED'})

# ============================================================================================
# PARSE ALL ASSETS
# ============================================================================================


class PZ_HumanRig_ParseAllXMLs(Operator):
    bl_idname = "zomboid.parse_all_xmls"
    bl_label = "Parse All Assets"
    bl_description = "Parse all the relevant xmls to get the data needed to import into Blender"

    @classmethod
    def poll(cls, context):
        g = context.scene.pz_human_global_props
        return g.pz_directory != ''

    def execute(self, context):
        g = context.scene.pz_human_global_props

        get_zomboid_asset_folders.cache_clear()

        bpy.ops.zomboid.clear_all_xmls()

     #   bpy.ops.zomboid.parse_body_location_lua()
        bpy.ops.zomboid.parse_skin_textures()
        bpy.ops.zomboid.parse_clothing_xmls()
        bpy.ops.zomboid.parse_outfit_xmls()
        bpy.ops.zomboid.parse_skin_textures()
        bpy.ops.zomboid.parse_hair_style_xmls()
     #   bpy.ops.zomboid.parse_decal_xmls()
        bpy.ops.zomboid.parse_injuries()
     #   bpy.ops.zomboid.get_all_animations()

        g.assets_parsed = True

        bpy.ops.zomboid.construct_body_texture()
        bpy.ops.zomboid.create_body_bloodiness_texture()
        bpy.ops.zomboid.create_body_dirtiness_texture()
        bpy.ops.zomboid.create_mask_texture()

        return ({'FINISHED'})

# ============================================================================================
# CLEAR ALL ASSETS
# ============================================================================================


class PZ_HumanRig_ClearAllXMLs(Operator):
    bl_idname = "zomboid.clear_all_xmls"
    bl_label = "Clear All Assets"
    bl_description = "Clear all the parsed asset entries"

    def execute(self, context):
        g = context.scene.pz_human_global_props

        g.clothing_item_slot_active_index = -1
        g.outfit_slot_active_index = -1
        g.skin_texture_active_index = -1
        g.stubble_texture_active_index = -1
        g.visibility_mask_active_index = -1
        g.overlay_mask_active_index = -1
        g.hair_style_slot_active_index = -1
        g.beard_style_slot_active_index = -1
     #   g.decal_slot_active_index = -1
     #   g.body_location_active_index = -1
     #   g.imported_animation_active_index = -1

        context.scene.pz_human_clothing_item_slots.clear()
        context.scene.pz_human_outfit_slots.clear()
        context.scene.pz_human_skin_textures.clear()
        context.scene.pz_human_stubble_textures.clear()
        context.scene.pz_human_visibility_masks.clear()
        context.scene.pz_human_overlay_masks.clear()
        context.scene.pz_human_hair_style_slots.clear()
        context.scene.pz_human_male_hair_styles.clear()
        context.scene.pz_human_female_hair_styles.clear()
        context.scene.pz_human_beard_styles.clear()
     #   context.scene.pz_human_decals.clear()
     #   context.scene.pz_human_decal_groups.clear()
      #  context.scene.pz_human_body_locations.clear()
      #  context.scene.pz_human_imported_animations.clear()

        g.assets_parsed = False

       # bpy.ops.zomboid.construct_body_texture()

        return ({'FINISHED'})

# endregion

# region Clothing & Outfit Operators

# ============================================================================================
# APPLY OUTFIT
# ============================================================================================


class PZ_HumanRig_ApplyOutfit(Operator):
    bl_idname = "zomboid.apply_outfit"
    bl_label = "Apply Outfit"
    bl_description = "Applies the outfit from the selected XML with the same paramaters and probabilities as in game"

    selected_guids = []
    random_top = False
    random_pants = False

    @classmethod
    def poll(cls, context):
        return context.active_object.pz_human_props.selected_outfit != ''

    def select_guids(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        outfit_name = p.selected_outfit.split()[0]
        outfit_sex = ''
        if '(Male)' in p.selected_outfit:
            outfit_sex = 'MALE'
        elif '(Female)' in p.selected_outfit:
            outfit_sex = 'FEMALE'

        for outfit in context.scene.pz_human_outfit_slots:
            if outfit.name == outfit_name and outfit.sex == outfit_sex:
                # Outfit is found, begin getting GUIDs
                for outfit_item in outfit.outfit_items:
                    if random() > outfit_item.probability:
                        continue
                    rnd = randint(0, len(outfit_item.choices) - 1)
                    self.selected_guids.append(outfit_item.choices[rnd].guid)
                self.random_top = outfit.random_top
                self.random_pants = outfit.random_pants
                return ({'FINISHED'})

        return ({'CANCELLED'})

    def add_clothing_items(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_human_prop_mesh_slots

        # Select the model sex
        if '(Male)' in p.selected_outfit:
            p.model_sex = 'MALE'

            if p.random_hair_style:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='M')
            if randint(1, 100) <= p.random_beard_chance:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='B')
            else:
                p.beard_style = 'None'
        elif '(Female)' in p.selected_outfit:
            p.model_sex = 'FEMALE'

            if p.random_hair_style:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='F')

        # Select random body textures, if enabled
        if p.random_skin_color:
            p.skin_color = randint(0, 4)
        if p.random_zombie:
            p.zombification = randint(1, 3)
        else:
            p.zombification = 0

        # Select random hair color, if enabled
        if p.random_hair_color:
            bpy.ops.zomboid.randomize_hair_color()

        # Randomize injuries, if enabled
        if p.randomize_injuries:
            bpy.ops.zomboid.randomize_body_injuries()
            bpy.ops.zomboid.randomize_zombie_injuries()
            bpy.ops.zomboid.randomize_body_bloodiness()
            bpy.ops.zomboid.randomize_body_dirtiness()

        if self.random_top:
            match randint(1, 6):
                case 1:
                    # Standard Default T-Shirt
                    bpy.ops.zomboid.add_clothing_item(
                        guid='e4ec9087-006d-41dc-81f4-585b6d2e958c', generate_mask=False)
                case 2:
                    # Tintable Default T-Shirt
                    bpy.ops.zomboid.add_clothing_item(
                        guid='19af00e4-ed4d-49bc-a893-a4a3376fe6da', generate_mask=False)
                case 3:
                    # Standard Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(
                        guid='d0616b36-b727-4c08-9274-020cb2e72bf8', generate_mask=False)
                case 4:
                    # Tintable Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(
                        guid='53b95680-245b-4439-8ba7-5aa6d938e465', generate_mask=False)
                case 5:
                    # Standard Default Vest
                    bpy.ops.zomboid.add_clothing_item(
                        guid='903c06ea-78e7-4f42-a3da-768be61f216f', generate_mask=False)
                case 6:
                    # Tintable Default Vest
                    bpy.ops.zomboid.add_clothing_item(
                        guid='a700a956-32c2-49a6-bd5f-5a2895073f19', generate_mask=False)

        if self.random_pants:
            match randint(1, 3):
                case 1:
                    # Standard Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='e4b71599-604d-4cc7-9ce4-7723a7e37d8a', generate_mask=False)
                case 2:
                    # Hue-able Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='5b07d45e-84c9-4ddf-ad6e-4bc2f27cace7', generate_mask=False)
                case 3:
                    # Tintable Default Trousers
                    bpy.ops.zomboid.add_clothing_item(
                        guid='1e2ed52f-9ee7-464b-9581-a450f2fbb403', generate_mask=False)

        # Call the clothing item adder for each GUID
        for guid in self.selected_guids:
            bpy.ops.zomboid.add_clothing_item(guid=guid, generate_mask=False)

        bpy.ops.zomboid.create_mask_texture()

        return ({'FINISHED'})

    def execute(self, context):
        self.selected_guids.clear()
        self.select_guids(context)

        bpy.ops.zomboid.remove_all_clothing_items()

        self.add_clothing_items(context)

        return ({'FINISHED'})

# ============================================================================================
# APPLY RANDOM OUTFIT
# ============================================================================================


class PZ_HumanRig_ApplyRandomOutfit(Operator):
    bl_idname = "zomboid.apply_random_outfit"
    bl_label = "Apply Random Outfit"
    bl_description = "Applies a random outfit from all XMLs with the same paramaters and probabilities as in game"

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        outfits = context.scene.pz_human_outfit_slots

        rnd = randint(0, len(outfits)-1)
        p.selected_outfit = outfits[rnd].search_name

        bpy.ops.zomboid.apply_outfit()

        return ({'FINISHED'})

# ============================================================================================
# ADD CLOTHING ITEM TO MODEL
# ============================================================================================


class PZ_HumanRig_AddClothingItem(Operator):
    bl_idname = "zomboid.add_clothing_item"
    bl_label = "Add Clothing Item"
    bl_description = "Adds a clothing item onto the model"

    guid: StringProperty()
    generate_mask: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_human_prop_mesh_slots

        item = None
        for clothing_item in context.scene.pz_human_clothing_item_slots:
            if clothing_item.guid == self.guid:
                item = clothing_item

        if item is not None:

            # Body Texture
            if item.is_body_texture:
                bpy.ops.zomboid.add_body_texture_slot()
                t = t_list[p.body_texture_slot_active_index]

                rnd = randint(0, len(item.texture_choices) - 1)
                t.name = item.name
                t.decal_group = item.decal_group
                t.texture_path = item.texture_choices[rnd].texture_path

                bpy.ops.zomboid.construct_body_texture()

            # Clothing Mesh
            elif item.static == False and item.attach_bone == 'None' or item.static == True and item.attach_bone == 'None':
                bpy.ops.zomboid.add_clothing_mesh_slot()
                m = m_list[p.clothing_mesh_slot_active_index]

                m.male_model_path = item.male_model_path
                m.female_model_path = item.female_model_path
                m.model_type = item.model_type

                rnd = randint(0, len(item.texture_choices) - 1)
                m.texture_path = item.texture_choices[rnd].texture_path
                m.name = item.name

                for i in range(len(item.mask_array)):
                    if item.mask_array[i] == True:
                        m.mask_array[i] = True

                m.hat_category = item.hat_category

                bpy.ops.zomboid.import_clothing_mesh()

            # Prop Mesh
            else:
                bpy.ops.zomboid.add_prop_mesh_slot()
                prop_prop = a_list[p.prop_mesh_slot_active_index]

                prop_prop.male_model_path = item.male_model_path
                prop_prop.female_model_path = item.female_model_path
                prop_prop.model_type = item.model_type

                rnd = randint(0, len(item.texture_choices) - 1)
                prop_prop.texture_path = item.texture_choices[rnd].texture_path
                prop_prop.name = item.name

                prop_prop.attach_bone = item.attach_bone

                prop_prop.hat_category = item.hat_category

                bpy.ops.zomboid.import_prop_mesh()

            if self.generate_mask:
                bpy.ops.zomboid.create_mask_texture()

            return ({'FINISHED'})
        else:
            return ({'CANCELLED'})

# ============================================================================================
# REMOVE ALL CLOTHING ITEMS
# ============================================================================================


class PZ_HumanRig_RemoveAllClothingItems(Operator):
    bl_idname = "zomboid.remove_all_clothing_items"
    bl_label = "Remove All Clothing Items"
    bl_description = "Removes all clothing items from the model"

    halt_texture_updates: BoolProperty(
        default=True
    )

    # @classmethod
    # def poll(cls, context):
    #     g = context.scene.pz_human_global_props
    #     return g.assets_parsed and directx_import_available()

    def execute(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        t_list = context.active_object.pz_human_body_texture_slots
        a_list = context.active_object.pz_human_prop_mesh_slots

        # Remove all existing clothing meshes
        p.clothing_mesh_slot_active_index = len(m_list) - 1
        for i in range(len(m_list)):
            bpy.ops.zomboid.remove_clothing_mesh_slot()
        p.clothing_mesh_slot_active_index = -1

        # Remove all existing body textures

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        p.body_texture_slot_active_index = len(t_list) - 1
        for i in range(len(t_list)):
            bpy.ops.zomboid.remove_body_texture_slot()
        p.body_texture_slot_active_index = -1

        if self.halt_texture_updates:
            p.halt_texture_updates = False
            bpy.ops.zomboid.construct_body_texture()

        # Remove all existing prop meshes
        p.prop_mesh_slot_active_index = len(a_list) - 1
        for i in range(len(a_list)):
            bpy.ops.zomboid.remove_prop_mesh_slot()
        p.prop_mesh_slot_active_index = -1

        return ({'FINISHED'})

# ============================================================================================
# RESET MODEL
# ============================================================================================


class PZ_ResetModel(Operator):
    bl_idname = "zomboid.reset_model"
    bl_label = "Reset Model"
    bl_description = "Resets all changes to the model and sets all respective settings to default"

    def execute(self, context):
        p = context.active_object.pz_human_props

        p.halt_texture_updates = True

        bpy.ops.zomboid.remove_all_clothing_items(halt_texture_updates=False)
        bpy.ops.zomboid.remove_hair_mesh(hair_type='M')
        bpy.ops.zomboid.remove_hair_mesh(hair_type='F')
        bpy.ops.zomboid.remove_hair_mesh(hair_type='B')
       # bpy.ops.zomboid.remove_all_body_damage(halt_texture_updates=False)

        p.skin_set = 'HUMAN'
        p.model_sex = 'MALE'
        p.skin_color = 0
        p.zombification = 0
        p.chest_hair = False
        p.hair_stubble = False
        p.beard_stubble = False

        p.selected_male_hair_style = ''
        p.selected_female_hair_style = ''
        p.selected_beard_style = ''
        p.hair_color = (0.25, 0.15, 0.05)

        p.selected_outfit = ''

        p.random_zombie = False
        p.random_skin_color = True
        p.random_hair_style = True
        p.random_hair_color = True
        p.natural_hair_color = True
        p.random_beard_chance = 50

        p.randomize_injuries = False
        p.random_bloodiness_intensity = 'MODERATE'
        p.random_dirtiness_intensity = 'MODERATE'
        p.random_injury_intensity = 'MODERATE'
        p.random_zombie_injury_intensity = 'DAMAGED'

        p.random_scratch_chance = 65
        p.random_laceration_chance = 30
        p.random_bite_chance = 5

        p.random_bandage_chance = 35
        p.random_bloody_bandage_chance = 35

        p.halt_texture_updates = False

        bpy.ops.zomboid.construct_body_texture()
        bpy.ops.zomboid.create_body_bloodiness_texture()
        bpy.ops.zomboid.create_body_dirtiness_texture()
        bpy.ops.zomboid.create_mask_texture()


        return ({'FINISHED'})

# ============================================================================================
# CHECK HAT CATEGORY
# ============================================================================================


class PZ_CheckHatCategory(Operator):
    bl_idname = "zomboid.check_hat_category"
    bl_label = "Check Hat Category"

    count_self: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props
        a_list = context.active_object.pz_human_prop_mesh_slots
        clothing_prop_list = context.active_object.pz_human_clothing_mesh_slots

        # If there are no props or clothing meshes, set the hair style to the selected one
        if p.prop_mesh_slot_active_index == -1 and p.clothing_mesh_slot_active_index == -1:
            if p.current_male_hair_style != p.selected_male_hair_style:
                p.current_male_hair_style = p.selected_male_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
            if p.current_female_hair_style != p.selected_female_hair_style:
                p.current_female_hair_style = p.selected_female_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
            if p.current_beard_style != p.selected_beard_style:
                p.current_beard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            p.current_hat_category = -1

            return ({'FINISHED'})

        test = False
        if p.prop_mesh_slot_active_index != -1:
            prop_prop = a_list[p.prop_mesh_slot_active_index]

            for i in range(len(a_list)):
                if a_list[i].hat_category != -1:  # Found a p mesh that has a hat category
                    if (a_list[i].name == prop_prop.name and not self.count_self):
                        continue
                    test = True
                    if a_list[i].hat_category > p.current_hat_category:
                        p.current_hat_category = a_list[i].hat_category

        if p.clothing_mesh_slot_active_index != -1:
            clothing_prop = clothing_prop_list[p.clothing_mesh_slot_active_index]

            for i in range(len(clothing_prop_list)):
                # Found a clothing mesh that has a hat category
                if clothing_prop_list[i].hat_category != -1:
                    if (clothing_prop_list[i].name == clothing_prop.name and not self.count_self):
                        continue
                    test = True
                    if clothing_prop_list[i].hat_category > p.current_hat_category:
                        p.current_hat_category = clothing_prop_list[i].hat_category

        if test:
            if p.current_hat_category >= 8:
                p.current_male_hair_style = 'Bald'
                p.current_female_hair_style = 'Bald'
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
                if p.current_hat_category == 9:
                    p.current_beard_style = 'None'
                    bpy.ops.zomboid.import_hair_mesh(hair_type='B')
                else:
                    p.current_breard_style = p.selected_beard_style
                    bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            else:
                p.current_breard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')

                for hair in context.scene.pz_human_hair_style_slots:
                    if hair.name == p.selected_male_hair_style and hair.sex == 'MALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == p.current_hat_category:
                                if p.current_male_hair_style != hat_style.style_name:
                                    p.current_male_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_mesh(
                                        hair_type='M')
                                break

                    if hair.name == p.selected_female_hair_style and hair.sex == 'FEMALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == p.current_hat_category:
                                if p.current_female_hair_style != hat_style.style_name:
                                    p.current_female_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_mesh(
                                        hair_type='F')
                                break
        else:
            if p.current_male_hair_style != p.selected_male_hair_style:
                p.current_male_hair_style = p.selected_male_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
            if p.current_female_hair_style != p.selected_female_hair_style:
                p.current_female_hair_style = p.selected_female_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
            if p.current_beard_style != p.selected_beard_style:
                p.current_beard_style = p.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            p.current_hat_category = -1

        return ({'FINISHED'})

# endregion

# region Animation Operators

# ============================================================================================
# REMAP ANIMATION
# ============================================================================================


class PZ_HumanRig_RemapAnimation(Operator):
    bl_idname = "zomboid.remap_animation"
    bl_label = "Add Animation to Rig"
    bl_description = "Remaps a vanilla or modded animation from the game back onto the control rig, to the best of its ability"

    use_ik: BoolProperty(
        default=False
    )

    control_dict = {
        'Bip01': 'CTRL-Pelvis',
        'Bip01_Spine': 'CTRL-Spine1',
        'Bip01_Spine1': 'CTRL-Spine2',
        'Bip01_Neck': 'CTRL-Chest',
        'Bip01_Head': 'CTRL-Head',
        'Bip01_L_Clavicle': 'CTRL-Shoulder.L',
        'Bip01_R_Clavicle': 'CTRL-Shoulder.R',
        'Bip01_L_UpperArm': 'CTRL-UpperArmFK.L',
        'Bip01_R_UpperArm': 'CTRL-UpperArmFK.R',
        'Bip01_L_Forearm': 'CTRL-ForearmFK.L',
        'Bip01_R_Forearm': 'CTRL-ForearmFK.R',
        'Bip01_L_Hand': 'CTRL-Hand.L',
        'Bip01_R_Hand': 'CTRL-Hand.R',
        'Bip01_L_Finger0': 'CTRL-Thumb.L',
        'Bip01_R_Finger0': 'CTRL-Thumb.R',
        'Bip01_L_Finger1': 'CTRL-Fingers.L',
        'Bip01_R_Finger1': 'CTRL-Fingers.R',
        'Bip01_Prop2': 'CTRL-Prop.L',
        'Bip01_Prop1': 'CTRL-Prop.R',
        'Bip01_L_Thigh': 'CTRL-ThighFK.L',
        'Bip01_R_Thigh': 'CTRL-ThighFK.R',
        'Bip01_L_Calf': 'CTRL-CalfFK.L',
        'Bip01_R_Calf': 'CTRL-CalfFK.R',
        'Bip01_L_Foot': 'CTRL-Foot.L',
        'Bip01_R_Foot': 'CTRL-Foot.R',
        'Bip01_BackPack': 'CTRL-Backpack',
        'Bip01_DressFront': 'CTRL-DressFront1',
        'Bip01_DressFront02': 'CTRL-DressFront2',
        'Bip01_DressBack': 'CTRL-DressBack1',
        'Bip01_DressBack02': 'CTRL-DressBack2',
        'Translation_Data': 'CTRL-TranslationData'
    }

    rest_deltas = {}

    reference_rig = None
    target_rig = None

    reference_action = None
    target_action = None

    reference_slot = None
    target_slot = None

    def import_reference_rig(self, context, p, g):
        selected_anim = context.scene.pz_human_imported_animations[
            g.imported_animation_active_index]

        if Path(selected_anim.anim_path).is_file():

            if context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            objs_before = set(context.scene.objects)

            match selected_anim.file_type:
                case '.x':
                    if not directx_import_available():
                        print("The .x importer is not enabled or installed")
                        return ({'CANCELLED'})

                    bpy.ops.import_scene.directx_x(
                        filepath=selected_anim.anim_path,
                        use_import_collection=False
                    )

            objs_after = set(bpy.context.scene.objects)

            imported_objects = list(objs_after - objs_before)

            for obj in imported_objects:
                if obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'ARMATURE':
                    self.reference_rig = obj
                    self.reference_action = obj.animation_data.action
                    self.reference_slot = obj.animation_data.action_slot
                    obj.rotation_euler[2] += math.pi
                    obj.scale[0] = -1

            # Calculate and store the differences in rest position, using the edit bones

            reference_bones = self.reference_rig.data.bones
            target_bones = self.target_rig.data.bones

            for reference_bone in reference_bones:
                if reference_bone.name in target_bones:
                    target_bone = target_bones[reference_bone.name]

                    reference_matrix = reference_bone.matrix_local
                    target_matrix = target_bone.matrix_local

                    self.rest_deltas.update(
                        {reference_bone.name: target_matrix @ reference_matrix.inverted()})

                    loc, rot, scale = (
                        target_matrix @ reference_matrix.inverted()).decompose()

                    print(f"Bone: {reference_bone.name}")
                    print(f"  Location Offset: {loc}")
                    print(f"  Rotation Diff (Quaternion): {rot}")
                    print("-" * 40)

            # Reorient Bones
            # bones = self.reference_rig.data.edit_bones
            # for bone in bones:
            #     axis_z = bone.matrix.to_3x3().col[2]

            #     rot_matrix = (Matrix.Translation(bone.head) @
            #                   Matrix.Rotation(math.radians(-90), 4, axis_z) @
            #                   Matrix.Translation(-bone.head))

            #     bone.matrix = rot_matrix @ bone.matrix

        return ({'FINISHED'})

    def cleanup_animation(self, context, p, g):
        action = self.reference_action
        channelbag = anim_utils.action_get_channelbag_for_slot(
            action, action.slots[0])

        # TODO: Make the curves match how it was before cleanup

        for fcurve in channelbag.fcurves:
            final_keys = []
            increasing = False
            decreasing = False
            prev_value = 0

            for index, key in enumerate(fcurve.keyframe_points):
                if not decreasing and not increasing and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    if key.co[1] > prev_value:
                        increasing = True
                    elif key.co[1] < prev_value:
                        decreasing = True

                    final_keys.append(key)

                elif increasing and key.co[1] < prev_value and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    decreasing = True
                    increasing = False

                    final_keys.append(fcurve.keyframe_points[index - 1])

                elif decreasing and key.co[1] > prev_value and not math.isclose(key.co[1], prev_value, abs_tol=0.01):
                    decreasing = False
                    increasing = True

                    final_keys.append(fcurve.keyframe_points[index - 1])

                prev_value = key.co[1]

            for key in reversed(fcurve.keyframe_points[:]):
                if key not in final_keys:
                    fcurve.keyframe_points.remove(key)

        return ({'FINISHED'})

    def remap_animation(self, context, p, g):

        channelbag = anim_utils.action_get_channelbag_for_slot(
            self.reference_action, self.reference_slot)

        self.target_action = bpy.data.actions.new(
            self.reference_action.name + ' (IMPORT)')
        self.target_slot = self.target_action.slots.new(
            id_type='OBJECT', name='PZ_HumanRigSlot')
        self.target_rig.animation_data.action = self.target_action
        self.target_rig.animation_data.action_slot = self.target_slot

        bone_name_pattern = r'"(.*?)"'
        bone_name_regex = re.compile(bone_name_pattern)

        transform_type_pattern = r'\]\.(.*)'
        transform_type_regex = re.compile(transform_type_pattern)

        reference_bones = self.reference_rig.pose.bones
        target_bones = self.target_rig.pose.bones

        # # Capture the base pose for each bone
        # context.scene.frame_set(0)
        # for reference_bone_name, target_bone_name in self.control_dict.items():

        #     reference_bone = reference_bones.get(reference_bone_name)
        #     target_bone = target_bones.get(target_bone_name)

        #     self.base_poses.update({target_bone_name : reference_bone.matrix.copy()})

        #     data_path = 'pose.bones["' + target_bone_name + '"]'
        #     self.target_rig.keyframe_insert(data_path=data_path + '.location', frame=0)
        #     self.target_rig.keyframe_insert(data_path=data_path + '.rotation_quaternion', frame=0)

        # Capture the animation curves
        # TODO Optimize

        # Set the base pose

        for fcurve in channelbag.fcurves:
            bone_name = bone_name_regex.search(
                fcurve.data_path).group().replace('"', '')
            transform_type = transform_type_regex.search(
                fcurve.data_path).group().replace('].', '')

            if bone_name in self.control_dict:
                ctrl_bone_name = self.control_dict[bone_name]
                ctrl_bone = target_bones.get(ctrl_bone_name)
                target_data_path = fcurve.data_path.replace(
                    bone_name, self.control_dict[bone_name])

                for key in fcurve.keyframe_points:
                    context.scene.frame_set(int(key.co[0]))

                    axis_switch = 0

                    match transform_type:
                        case 'location':
                            match fcurve.array_index:
                                case 0:
                                    axis_switch = 1
                                case 1:
                                    axis_switch = 2
                                case 2:
                                    axis_switch = 0

                            ctrl_bone.location[axis_switch] = key.co[1] * 100
                            if bone_name in self.rest_deltas:
                                ctrl_bone.location[axis_switch] += self.rest_deltas[bone_name].to_translation()[
                                    axis_switch] / 100
                        case 'rotation_quaternion':
                            match fcurve.array_index:
                                case 0:
                                    # Let Blender calculate the quaternion w
                                    continue
                                case 1:
                                    axis_switch = 3
                                case 2:
                                    axis_switch = 1
                                case 3:
                                    axis_switch = 2

                            ctrl_bone.rotation_quaternion[axis_switch] = key.co[1]
                            if bone_name in self.rest_deltas:
                                ctrl_bone.rotation_quaternion[axis_switch] += self.rest_deltas[bone_name].to_quaternion()[
                                    axis_switch]

                    self.target_rig.keyframe_insert(
                        data_path=target_data_path, frame=int(key.co[0]))

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        # Store context to restore later
        prev_mode = context.mode
        prev_active_object = context.active_object
        if prev_active_object is not None:
            prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        self.target_rig = context.active_object

        self.import_reference_rig(context, p, g)
        # self.cleanup_animation(context, p, g)
        self.remap_animation(context, p, g)

        bpy.data.objects.remove(self.reference_rig, do_unlink=True)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in prev_selected_objects:
            obj.select_set(True)
        if prev_active_object is not None:
            context.view_layer.objects.active = prev_active_object

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        return ({'FINISHED'})

# endregion

# region Instancing Operators

# ============================================================================================
# DUPLICATE RIG
# ============================================================================================


class PZ_HumanRig_DuplicateRig(Operator):
    bl_idname = "zomboid.duplicate_rig"
    bl_label = "Duplicate Rig"
    bl_description = "Creates a new instance of the rig that copies all of the selected rigs attributes"

    def recursively_duplicate_collection(self, context, source_collection, parent_collection=None):

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props

        self.recursively_duplicate_collection(
            context, p.rig_collection, context.collection)

        return ({'FINISHED'})

# endregion

# region Export Operators

# ============================================================================================
# GLB EXPORTER
# ============================================================================================


class PZ_HumanRig_Export(Operator):
    bl_idname = "zomboid.export_glb"
    bl_label = "Export GLBs for Project Zomboid"
    bl_description = "Export your animations as GLB files that are adjusted for Project Zomboid"


    @classmethod
    def poll(cls, context):
        p = context.active_object.pz_human_props

        if p.file_output_path != '':
            if p.batch_export:
                return True
            else:
                return context.active_object.animation_data.action is not None
        else:
            return False

# ------------------------------------------------------------------------#
#  Main Function

    def export_anim(self, context, action):
        # Get reference to the rig's properties
        p = context.active_object.pz_human_props

        # Force set the animation to export at 30 FPS, which is what Project Zomboid evaluates animations at
        context.scene.render.fps = 30

        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        # Get references to the objects that will be exported
        dummy01 = p.dummy01_empty
        bip01 = prev_active_object
        mesh = p.male_body_object
        translation_data = p.translation_data_empty

        # Rename the objects to their PZ names and store their Blender names to restore later
        prev_dummy01_name = dummy01.name
        dummy01.name = 'Dummy01'

        prev_bip01_name = bip01.name
        bip01.name = 'Bip01'

        prev_translation_data_name = translation_data.name
        translation_data.name = 'Translation_Data'

        # Set the mode to Object Mode and deselect all objects
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Select the objects that will be exported
        dummy01.select_set(True)
        bip01.select_set(True)
        mesh.select_set(True)
        translation_data.select_set(True)

        # Create animation data for TranslationData if it does not have any
        translation_data.animation_data_create()

        # Create a new temporary NLA track that will be used to export to PZ for both Bip01 and TranslationData
        bip01_track = bip01.animation_data.nla_tracks.new()
        # NLA track will have the same name as the action
        bip01_track.name = action.name
        translation_data_track = translation_data.animation_data.nla_tracks.new()
        translation_data_track.name = action.name
        
        start_frame = int(action.frame_range[0])
        end_frame = int(action.frame_range[1])

        bip01.animation_data.action = action
        bip01_strip = bip01_track.strips.new(action.name, start_frame, action)
        bip01_strip.frame_end = end_frame

        translation_data.animation_data.action = action
        translation_data_strip = translation_data_track.strips.new(action.name, start_frame, action)
        translation_data_strip.frame_end = end_frame

        # bip01.animation_data.action = action
        # # Subtract 1 frame from the frame range to avoid an empty frame
        # anim_length = int(action.frame_range[0]) - 1
        # bip01_strip = bip01_track.strips.new(action.name, anim_length, action)

        # translation_data.animation_data.action = action
        # translation_data_strip = translation_data_track.strips.new(
        #     action.name, anim_length, action)
        # translation_data_strip.frame_end = bip01_strip.frame_end

        # Call the Blender gltf exporter with specific settings tailored for our setup and Project Zomboid
        bpy.ops.export_scene.gltf(
            filepath=p.file_output_path + '/' + action.name + '.glb',
            use_selection=True,
            export_hierarchy_flatten_objs=True,
            export_bake_animation=True,
            export_materials='NONE',
            export_morph=False,
            export_def_bones=True,
            export_animation_mode="NLA_TRACKS"
        )

        # Remove all of the NLA tracks and strips that we created
        for strip in bip01_track.strips:
            bip01_track.strips.remove(strip)
        for strip in translation_data_track.strips:
            translation_data_track.strips.remove(strip)

        bip01.animation_data.nla_tracks.remove(bip01_track)
        translation_data.animation_data.nla_tracks.remove(
            translation_data_track)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Restore Object Names
        dummy01.name = prev_dummy01_name
        bip01.name = prev_bip01_name
        translation_data.name = prev_translation_data_name

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        context.scene.render.fps = 30

        for obj in prev_selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = prev_active_object

        return {'FINISHED'}

# ------------------------------------------------------------------------#
#  Execute

    def execute(self, context):

        # Get reference to the rig's properties
        p = context.active_object.pz_human_props

        if len(p.file_output_path) > 0:
            if p.batch_export:
                for action in bpy.data.actions:
                    if p.action_filter in action.name:
                        self.export_anim(context, action)
            else:
                if context.active_object.animation_data.action is not None:
                    self.export_anim(
                        context, context.active_object.animation_data.action)
                else:
                    print("Selected rig has no active action selected.")
        else:
            self.report({"WARNING"}, "Declare a filepath to export to")

        return {'FINISHED'}

# endregion

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Rig Properties


'''
This is the main PropertyGroup attatched to each instance of the rig. It contains all
of the attributes relating to animation, visuals, important data blocks, etc.
'''


class PZ_HumanRigProperties(PropertyGroup):

# ============================================================================================
# IMPORTANT OBJECTS
# ============================================================================================

    rig_collection: PointerProperty(type=Collection)

    male_body_object: PointerProperty(type=Object)
    male_dress_object: PointerProperty(type=Object)
    female_body_object: PointerProperty(type=Object)
    female_dress_object: PointerProperty(type=Object)
    male_skeleton_object: PointerProperty(type=Object)
    female_skeleon_object: PointerProperty(type=Object)
    translation_data_empty: PointerProperty(type=Object)
    dummy01_empty: PointerProperty(type=Object)

    mask_tex: PointerProperty(type=Image)
    body_tex: PointerProperty(type=Image)
    
    body_mat: PointerProperty(type=Material)

# ============================================================================================
# INSTANCING
# ============================================================================================

    '''
    When updating the rig instance index, update the name of all instance-specific
    data blocks to match
    '''

    def update_rig_instance(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        old_instance_pattern = r' \([0-9]+\)'
        
        # Check if this instance number is already used. If so, increment by one and return.
        for rig in context.scene.pz_human_rigs:
            if rig.obj != context.active_object:
                if self.rig_instance == rig.obj.pz_human_props.rig_instance:
                    self.rig_instance += 1
                    return

        # Recursively go through the rig collection and change all '({old rig instance})'
        # to '({new rig instance})'

        p.rig_collection.name = re.sub(
            old_instance_pattern, instance_str, p.rig_collection.name)
        for obj in p.rig_collection.objects:
            obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
            # if obj.data and isinstance(obj.data, bpy.types.ID):
            #     obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
        for col in p.rig_collection.children_recursive:
            col.name = re.sub(old_instance_pattern, instance_str, col.name)
            for obj in col.objects:
                obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
                # if obj.data and isinstance(obj.data, bpy.types.ID):
                #     obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
                if obj.active_material:
                    obj.active_material.name = re.sub(
                        old_instance_pattern, instance_str, obj.active_material.name)
        
        if self.mask_tex:
            self.mask_tex.name = re.sub(old_instance_pattern, instance_str, self.mask_tex.name)
        if self.body_tex:
            self.body_tex.name = re.sub(old_instance_pattern, instance_str, self.body_tex.name)

    rig_instance: IntProperty(
        default=0,
        min=0,
        update=update_rig_instance,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# HEAD ROTATION
# ============================================================================================

    head_lookpoint: FloatProperty(
        name="Use Look Point",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 will have the head rotate with CTRL-Head, 1 will make the head rotate towards CTRL-LookPoint",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# IK/FK SWITCHING
# ============================================================================================

    arm_ik_l: FloatProperty(
        name="Left Arm IK",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    arm_ik_r: FloatProperty(
        name="Right Arm IK",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    leg_ik_l: FloatProperty(
        name="Left Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )
    leg_ik_r: FloatProperty(
        name="Right Leg IK",
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# CONSTRAINTS
# ============================================================================================

    fk_constrain: BoolProperty(
        name="Limit FK Rotations",
        default=True,
        description="When true, FK controls have rotation constraints, not letting limbs bend beyond what they can realistically bend. Disable if you need to make an animation for breaking bones",
        override={"LIBRARY_OVERRIDABLE"}
    )

    root_is_ik_floor: BoolProperty(
        name="Root is IK Floor",
        default=True,
        description="When true, the leg IK controls cannot go below CTRL-Root",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Lookpoint Parenting

    def update_lookpoint_parent_index(self, context):
        self.lookpoint_parent_index = context.active_object.pz_human_props['lookpoint_parent']

    lookpoint_parent: EnumProperty(
        name="Look Point Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Lookpoint is not child of anything", 0),
            ('ROOT', "Root", "Lookpoint is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Lookpoint is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Lookpoint is the child of CTRL-Chest", 3),
            ('OBJECT', "Object", "Copies the location of a selected object", 4)
        ],
        default='ROOT',
        update=update_lookpoint_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    lookpoint_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_lookpoint_parent_object(self, context):
        update_lookpoint_parent_object(self, context)

    lookpoint_parent_object: PointerProperty(
        name="LookPoint Parent Object",
        type=Object,
        update=update_lookpoint_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Prop Parenting

    def update_left_prop_parent_index(self, context):
        self.left_prop_parent_index = context.active_object.pz_human_props['left_prop_parent']

    left_prop_parent: EnumProperty(
        name="Left Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Left Prop is not child of anything", 0),
            ('ROOT', "Root", "Left Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Left Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_left_prop_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_prop_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_left_prop_parent_object(self, context):
        # update_left_prop_parent_object(self, context)
        pass

    left_prop_parent_object: PointerProperty(
        name="Left Prop Parent Object",
        type=Object,
        update=update_left_prop_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Prop Parenting

    def update_right_prop_parent_index(self, context):
        self.right_prop_parent_index = context.active_object.pz_human_props['right_prop_parent']

    right_prop_parent: EnumProperty(
        name="Right Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Right Prop is not child of anything", 0),
            ('ROOT', "Root", "Right Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Right Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_right_prop_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_prop_parent_index: IntProperty(
        default=2
    )

    def update_right_prop_parent_object(self, context):
     #   update_right_prop_parent_object(self, context)
        pass

    right_prop_parent_object: PointerProperty(
        name="Right Prop Parent Object",
        type=Object,
        update=update_right_prop_parent_object,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Backpack Parenting

    def update_backpack_parent_index(self, context):
        self.backpack_parent_index = context.active_object.pz_human_props['backpack_parent']

    backpack_parent: EnumProperty(
        name="Backpack Parent",
        description="What the backpack is parented to",
        items=[
            ('NONE', "None", "Backpack is not child of anything", 0),
            ('ROOT', "Root", "Backpack is the child of CTRL-Root", 1),
            ('SPINE', "Spine", "Backpack is the child of the spine", 2)
        ],
        default='SPINE',
        update=update_backpack_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    backpack_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Dress Parenting

    def update_dress_parent_index(self, context):
        self.dress_parent_index = context.active_object.pz_human_props['dress_parent']

    dress_parent: EnumProperty(
        name="Dress Parent",
        description="What the dress is parented to",
        items=[
            ('NONE', "None", "Dress is not child of anything", 0),
            ('ROOT', "Root", "Dress is the child of CTRL-Root", 1),
            ('LEGS', "Legs", "Dress bones are calculated between the legs", 2)
        ],
        default='LEGS',
        update=update_dress_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    dress_parent_index: IntProperty(
        default=2,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Control Parenting

    def update_right_arm_ik_control_parent_index(self, context):
        self.right_arm_ik_control_parent_index = context.active_object.pz_human_props[
            'right_arm_ik_control_parent']

    right_arm_ik_control_parent: EnumProperty(
        name="Right Arm IK Control Parent",
        description="What the right arm IK control is parented to",
        items=[
            ('NONE', "None", "Right arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Right arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Right arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_right_arm_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_arm_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Pole Parenting

    def update_right_arm_ik_pole_parent_index(self, context):
        self.right_arm_ik_pole_parent_index = context.active_object.pz_human_props[
            'right_arm_ik_pole_parent']

    right_arm_ik_pole_parent: EnumProperty(
        name="Right Arm IK Pole Parent",
        description="What the right arm IK pole is parented to",
        items=[
            ('NONE', "None", "Right arm IK pole is not child of anything", 0),
            ('ROOT', "Root", "Right arm IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right arm IK pole is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Right arm IK pole is the child of CTRL-Chest", 3),
            ('CONTROL', "Control", "Right arm IK pole is the child of the IK control", 4),
            ('ELBOW', "Elbow", "Right arm IK pole is the child of the calculated position of the middle of the arm", 5)
        ],
        default='ROOT',
        update=update_right_arm_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_arm_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Control Parenting

    def update_left_arm_ik_control_parent_index(self, context):
        self.left_arm_ik_control_parent_index = context.active_object.pz_human_props[
            'left_arm_ik_control_parent']

    left_arm_ik_control_parent: EnumProperty(
        name="Left Arm IK Control Parent",
        description="What the left arm IK control is parented to",
        items=[
            ('NONE', "None", "Left arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Left arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Left arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_left_arm_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_arm_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Pole Parenting

    def update_left_arm_ik_pole_parent_index(self, context):
        self.left_arm_ik_pole_parent_index = context.active_object.pz_human_props[
            'left_arm_ik_pole_parent']

    left_arm_ik_pole_parent: EnumProperty(
        name="Left Arm IK Pole Parent",
        description="What the left arm IK pole is parented to",
        items=[
            ('NONE', "None", "Left arm IK pole is not child of anything", 0),
            ('ROOT', "Root", "Left arm IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left arm IK pole is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Left arm IK pole is the child of CTRL-Chest", 3),
            ('CONTROL', "Control", "Left arm IK pole is the child of the IK control", 4),
            ('ELBOW', "Elbow", "Left arm IK pole is the child of the calculated position of the middle of the arm", 5)
        ],
        default='ROOT',
        update=update_left_arm_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_arm_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Control Parenting

    def update_right_leg_ik_control_parent_index(self, context):
        self.right_leg_ik_control_parent_index = context.active_object.pz_human_props[
            'right_leg_ik_control_parent']

    right_leg_ik_control_parent: EnumProperty(
        name="Right Leg IK Control Parent",
        description="What the right leg IK control is parented to",
        items=[
            ('NONE', "None", "Right leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_right_leg_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_leg_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Pole Parenting

    def update_right_leg_ik_pole_parent_index(self, context):
        self.right_leg_ik_pole_parent_index = context.active_object.pz_human_props[
            'right_leg_ik_pole_parent']

    right_leg_ik_pole_parent: EnumProperty(
        name="Right Leg IK Pole Parent",
        description="What the right leg IK pole is parented to",
        items=[
            ('NONE', "None", "Right leg IK pole is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK pole is the child of CTRL-Pelvis", 2),
            ('CONTROL', "Control", "Right leg IK pole is the child of the IK control", 3),
            ('KNEE', "Knee", "Right leg IK pole is the child of the calculated position of the middle of the leg", 4)
        ],
        default='ROOT',
        update=update_right_leg_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    right_leg_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Control Parenting

    def update_left_leg_ik_control_parent_index(self, context):
        self.left_leg_ik_control_parent_index = context.active_object.pz_human_props[
            'left_leg_ik_control_parent']

    left_leg_ik_control_parent: EnumProperty(
        name="Left Leg IK Control Parent",
        description="What the left leg IK control is parented to",
        items=[
            ('NONE', "None", "Left leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_left_leg_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_leg_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Pole Parenting

    def update_left_leg_ik_pole_parent_index(self, context):
        self.left_leg_ik_pole_parent_index = context.active_object.pz_human_props[
            'left_leg_ik_pole_parent']

    left_leg_ik_pole_parent: EnumProperty(
        name="Left Leg IK Pole Parent",
        description="What the left leg IK pole is parented to",
        items=[
            ('NONE', "None", "Left leg IK pole is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK pole is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK pole is the child of CTRL-Pelvis", 2),
            ('CONTROL', "Control", "Left leg IK pole is the child of the IK control", 3),
            ('KNEE', "Knee", "Left leg IK pole is the child of the calculated position of the middle of the leg", 4)
        ],
        default='ROOT',
        update=update_left_leg_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    left_leg_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  All IK Control Parent

    def update_all_ik_control_parent_index(self, context):
        self.all_ik_control_parent_index = context.active_object.pz_human_props[
            'all_ik_control_parent']
        i = self.all_ik_control_parent_index

        if i == 3:
            self.left_arm_ik_control_parent = 'CHEST'
            self.right_arm_ik_control_parent = 'CHEST'
            self.left_leg_ik_control_parent = 'PELVIS'
            self.right_leg_ik_control_parent = 'PELVIS'
        else:
            self.left_arm_ik_control_parent = self.all_ik_control_parent
            self.right_arm_ik_control_parent = self.all_ik_control_parent
            self.left_leg_ik_control_parent = self.all_ik_control_parent
            self.right_leg_ik_control_parent = self.all_ik_control_parent

    all_ik_control_parent: EnumProperty(
        name="Set Parent For All IK Controls: ",
        description="Sets the parent for all IK controls instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Controls are not parented to anything", 0),
            ('ROOT', "Root", "IK Controls are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Controls are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Controls are parented to CTRL-Chest, Leg IK Controls are parented to CTRL-Pelvis", 3)
        ],
        default='ROOT',
        update=update_all_ik_control_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    all_ik_control_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  All IK Pole Parent

    def update_all_ik_pole_parent_index(self, context):
        self.all_ik_pole_parent_index = context.active_object.pz_human_props[
            'all_ik_pole_parent']

        i = self.all_ik_pole_parent_index
        if i < 3:
            self.left_arm_ik_pole_parent = self.all_ik_pole_parent
            self.right_arm_ik_pole_parent = self.all_ik_pole_parent
            self.left_leg_ik_pole_parent = self.all_ik_pole_parent
            self.right_leg_ik_pole_parent = self.all_ik_pole_parent
        elif i == 3:
            self.left_arm_ik_pole_parent = 'CHEST'
            self.right_arm_ik_pole_parent = 'CHEST'
            self.left_leg_ik_pole_parent = 'PELVIS'
            self.right_leg_ik_pole_parent = 'PELVIS'
        elif i == 4:
            self.left_arm_ik_pole_parent = 'CONTROL'
            self.right_arm_ik_pole_parent = 'CONTROL'
            self.left_leg_ik_pole_parent = 'CONTROL'
            self.right_leg_ik_pole_parent = 'CONTROL'
        elif i == 5:
            self.left_arm_ik_pole_parent = 'ELBOW'
            self.right_arm_ik_pole_parent = 'ELBOW'
            self.left_leg_ik_pole_parent = 'KNEE'
            self.right_leg_ik_pole_parent = 'KNEE'

    all_ik_pole_parent: EnumProperty(
        name="Set Parent For All IK Poles: ",
        description="Sets the parent for all IK poles instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Poles are not parented to anything", 0),
            ('ROOT', "Root", "IK Poles are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Poles are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Poles are parented to CTRL-Chest, Leg IK Poles are parented to CTRL-Pelvis", 3),
            ('CONTROL', "Control",
             "IK Poles are parented to their corresponding IK controls", 4),
            ('JOINT', "Joint", "IK Poles are parented to the calculated position between the start and end of their corresponding limb", 5)
        ],
        default='ROOT',
        update=update_all_ik_pole_parent_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    all_ik_pole_parent_index: IntProperty(
        default=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Auto Wrist Twist

    wrist_twist_amount: FloatProperty(
        name="Wrist Twist Amount",
        description="How strongly the forearm follows the hand's X rotation. Can cause snapping issues at higher levels",
        default=0.25,
        min=0.0,
        max=1.0,
        subtype='FACTOR',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# MODEL
# ============================================================================================

    def update_selected_clothing_item(self, context):
        if self.selected_clothing_item != '':
            for clothing_item in context.scene.pz_human_clothing_item_slots:
                if clothing_item.name == self.selected_clothing_item:
                    bpy.ops.zomboid.add_clothing_item(guid=clothing_item.guid)
                    break
            self.selected_clothing_item = ''

    selected_clothing_item: StringProperty(
        name='Add Clothing Item',
        update=update_selected_clothing_item,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body Mesh

    '''
    Almost every clothing model has a different verson for both sexes.
    So, whenever the sex is changed, call functions that properly
    hide and show the correct sex's clothing in both the viewport and renders
    '''

    def update_skin_texture(self, context):
        bpy.ops.zomboid.construct_body_texture()

    def update_clothing_sex_visibility_settings(self, context):
        update_clothing_sex_visibility(self, context)
        update_clothing_sex_render(self, context)

    def update_prop_sex_visibility_settings(self, context):
        update_prop_sex_visibility(self, context)
        update_prop_sex_render(self, context)

    def update_hair_sex_visibility_settings(self, context):
        update_hair_sex_visibility(self, context)
        update_hair_sex_render(self, context)

    def update_sex_index(self, context):
        self.model_sex_index = 0 if self.model_sex == 'MALE' else 1
        self.update_clothing_sex_visibility_settings(context)
        self.update_prop_sex_visibility_settings(context)
        self.update_hair_sex_visibility_settings(context)
        self.update_skin_texture(context)

    def update_body_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('GEO-PZ_Human_Bodies' + instance_str)
        if col:
            col.hide_viewport = not self.show_body
            col.hide_render = not self.show_body

    model_sex: EnumProperty(
        name="Model Sex",
        description="Which human model to use",
        items=[
            ('MALE', "Male", "The male model and clothing", 0),
            ('FEMALE', "Female", "The female model and clothing", 1),
        ],
        default='MALE',
        update=update_sex_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    model_sex_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    show_body: BoolProperty(
        name="Body Enabled",
        default=True,
        description="Show the body of the character",
        update=update_body_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )
    use_skeleton: BoolProperty(
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Masking

    def update_mask_array(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_mask_texture()

    mask_array: BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False),
        update=update_mask_array,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body Injuries

    def update_body_injury(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.construct_body_texture()

    upper_torso_injury: EnumProperty(  # 0
        name='Upper Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_injury: EnumProperty(  # 1
        name='Lower Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_injury: EnumProperty(  # 2
        name='Left Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_injury: EnumProperty(  # 3
        name='Right Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_injury: EnumProperty(  # 4
        name='Left Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_injury: EnumProperty(  # 5
        name='Right Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_injury: EnumProperty(  # 6
        name='Left Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_injury: EnumProperty(  # 7
        name='Right Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_injury: EnumProperty(  # 8
        name='Head Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('BANDAGE', "Bandage", "Bandage injury texture", 1),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 2)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_injury: EnumProperty(  # 9
        name='Neck Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_injury: EnumProperty(  # 10
        name='Groin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_injury: EnumProperty(  # 11
        name='Left Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_injury: EnumProperty(  # 12
        name='Right Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_injury: EnumProperty(  # 13
        name='Left Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_injury: EnumProperty(  # 14
        name='Right Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_injury: EnumProperty(  # 15
        name='Left Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_injury: EnumProperty(  # 16
        name='Right Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)",
             "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Zombie Injuries

    def update_selected_zombie_injury(self, context):
        if self.selected_zombie_injury != 'NONE':
            new_injury = context.active_object.pz_human_zombie_injuries.add()
            new_injury.name = self.selected_zombie_injury
            new_injury.texture_path = context.scene.pz_human_zombie_injuries.get(self.selected_zombie_injury).texture_path

            self.selected_zombie_injury = 'NONE'
            bpy.ops.zomboid.construct_body_texture()

    selected_zombie_injury: EnumProperty(
        name='Add Zombie Injury',
        items=filter_zombie_injuries,
        update=update_selected_zombie_injury,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Bloodiness

    def update_bloodiness_texture(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_body_bloodiness_texture()

    upper_torso_bloodiness: FloatProperty(
        name='Upper Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_bloodiness: FloatProperty(
        name='Lower Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_bloodiness: FloatProperty(
        name='Left Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_bloodiness: FloatProperty(
        name='Right Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_bloodiness: FloatProperty(
        name='Left Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_bloodiness: FloatProperty(
        name='Right Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_bloodiness: FloatProperty(
        name='Left Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_bloodiness: FloatProperty(
        name='Right Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_bloodiness: FloatProperty(
        name='Head Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_bloodiness: FloatProperty(
        name='Neck Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_bloodiness: FloatProperty(
        name='Groin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_bloodiness: FloatProperty(
        name='Left Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_bloodiness: FloatProperty(
        name='Right Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_bloodiness: FloatProperty(
        name='Left Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_bloodiness: FloatProperty(
        name='Right Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_bloodiness: FloatProperty(
        name='Left Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_bloodiness: FloatProperty(
        name='Right Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    back_bloodiness: FloatProperty(
        name='Back Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        step=0.25,
        subtype='FACTOR',
        update=update_bloodiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Dirtiness

    def update_dirtiness_texture(self, context):
        p = context.active_object.pz_human_props
        if not p.halt_texture_updates:
            bpy.ops.zomboid.create_body_dirtiness_texture()

    upper_torso_dirtiness: FloatProperty(
        name='Upper Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    lower_torso_dirtiness: FloatProperty(
        name='Lower Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_hand_dirtiness: FloatProperty(
        name='Left Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_hand_dirtiness: FloatProperty(
        name='Right Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_forearm_dirtiness: FloatProperty(
        name='Left Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_forearm_dirtiness: FloatProperty(
        name='Right Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_upperarm_dirtiness: FloatProperty(
        name='Left Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_upperarm_dirtiness: FloatProperty(
        name='Right Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    head_dirtiness: FloatProperty(
        name='Head Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    neck_dirtiness: FloatProperty(
        name='Neck Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    groin_dirtiness: FloatProperty(
        name='Groin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_thigh_dirtiness: FloatProperty(
        name='Left Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_thigh_dirtiness: FloatProperty(
        name='Right Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_shin_dirtiness: FloatProperty(
        name='Left Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_shin_dirtiness: FloatProperty(
        name='Right Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    left_foot_dirtiness: FloatProperty(
        name='Left Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    right_foot_dirtiness: FloatProperty(
        name='Right Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )
    back_dirtiness: FloatProperty(
        name='Back Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        step=0.25,
        subtype='FACTOR',
        update=update_dirtiness_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Body Textures

    # Skin ---------------------------------------

    def update_skin_set(self, context):
        self.use_skeleton = self.skin_set == 'SKELETON'
        self.update_skin_texture(context)

    skin_set: EnumProperty(
        name='Skin Set',
        items=[
            ('HUMAN', "Human", "Human and zombie textures", 0),
            ('SKELETON', "Skeleton", "Skeleton model and textures", 1),
            ('MANNEQUIN', "Mannequin", "Mannequin textures", 2),
            ('SCARECROW', "Scarecrow", "Long curly hair texture", 3),
        ],
        default='HUMAN',
        update=update_skin_set,
        override={"LIBRARY_OVERRIDABLE"}
    )

    skin_color: IntProperty(
        name="Skin Color",
        default=0,
        min=0,
        max=4,
        description="Which skin color texture set to use",
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    chest_hair: BoolProperty(
        name='Chest Hair',
        default=False,
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    zombification: IntProperty(
        name="Zombification",
        default=0,
        min=0,
        max=3,
        description="Level of zombification texture to use",
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    skeleton_type: IntProperty(
        name="Skeleton Type",
        default=0,
        min=0,
        max=2,
        description="Which skeleton texture to use",
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    mannequin_type: IntProperty(
        name="Mannequin Type",
        default=0,
        min=0,
        max=1,
        description="Which mannequin texture to use",
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Hair Mesh

    '''
    There are three hair types:
    - Male Hair
    - Female Hair
    - Beard

    Each category is only visible when the respective model sex is selected.
    For every hair type, there is a 'selected' property and a 'current' property.
    The 'selected' property is the desired hairstyle from the animator, and the 
    'current' property dicates which hair model will actually be used, given the 
    rig's current 'hat category' property and the selected hairstyle's 
    respective alternate hat hair model specified in the hairstyle XML
    '''

    current_hat_category: IntProperty(
        default=-1
    )

    # Male Hair ---------------------------------------

    def update_male_hair_style(self, context):
        if self.selected_male_hair_style == '':
            self.selected_male_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_male_hair_style: StringProperty(
        name="Male Hair",
        update=update_male_hair_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_male_hair_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Beard ---------------------------------------

    def update_beard_style(self, context):
        if self.selected_beard_style == '':
            self.selected_beard_style = 'None'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_beard_style: StringProperty(
        name="Beard",
        update=update_beard_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_beard_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Female Hair ---------------------------------------

    def update_female_hair_style(self, context):
        if self.selected_female_hair_style == '':
            self.selected_female_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()

    selected_female_hair_style: StringProperty(
        name="Female Hair",
        update=update_female_hair_style,
        override={"LIBRARY_OVERRIDABLE"}
    )

    current_female_hair_style: StringProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Stubble ---------------------------------------

    hair_stubble: BoolProperty(
        name='Hair Stubble',
        default=False,
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    beard_stubble: BoolProperty(
        name='Beard Stubble',
        default=False,
        update=update_skin_texture,
        override={"LIBRARY_OVERRIDABLE"}
    )

    # ---------------------------------------------------

    def update_hair_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('GEO-PZ_Human_Hair' + instance_str)
        if col:
            col.hide_viewport = not self.show_hair
            col.hide_render = not self.show_hair

    show_hair: BoolProperty(
        name="Hair Enabled",
        default=True,
        description="Show the hair of the character",
        update=update_hair_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Hair Texture

    hair_color: FloatVectorProperty(
        name="Hair Color",
        subtype='COLOR',
        default=(0.25, 0.15, 0.05),
        min=0,
        max=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# RANDOMNESS
# ============================================================================================

    random_zombie: BoolProperty(
        name='Zombie',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_skin_color: BoolProperty(
        name='Random Skin Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_hair_style: BoolProperty(
        name='Random Hair Style',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )

    random_hair_color: BoolProperty(
        name='Random Hair Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )
    natural_hair_color: BoolProperty(
        name='Natural Hair Color',
        default=True,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_beard_chance: IntProperty(
        name='Random Beard Chance',
        default=50,
        min=0,
        max=100,
        subtype='PERCENTAGE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    randomize_injuries: BoolProperty(
        name='Randomize Injuries',
        description='Randomly apply injuries on the body',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_injury_intensity: EnumProperty(
        name='Random Injury Intensity',
        description='How many injuries should appear on the body',
        items=[
            ('NONE', "None", "No injury textures", 0),
            ('MINOR', "Minor", "1-2 injury textures", 1),
            ('MODERATE', "Moderate", "3-4 injury textures", 2),
            ('SERIOUS', "Serious", "5-6 injury textures", 3),
            ('SEVERE', "Severe", "7-10 injury textures", 4),
            ('INSANE', "Insane", "11-16 injury textures", 5),
            ('RANDOM', "Random", "0-16 injury textures", 6)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_zombie_injury_intensity: EnumProperty(
        name='Random Zombie Injury Intensity',
        description='How many zombie injuries should appear on the body',
        items=[
            ('NONE', "None", "No injury textures", 0),
            ('INTACT', "Intact", "1-3 injury textures", 1),
            ('DAMAGED', "Damaged", "3-5 injury textures", 2),
            ('HACKED APART', "Hacked Apart", "5-15 injury textures", 3),
            ('MUTILATED', "Mutilated", "20-40 injury textures", 4),
            ('RENDED APART', "Rended Apart", "40-73 injury textures", 5),
            ('RANDOM', "Random", "0-73 injury textures", 6)
        ],
        default='DAMAGED',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_scratch_chance: FloatProperty(
        name='Random Scratch Chance',
        description='Weighted chance injury will be a scratch (chances are automatically evened out to add up to 100%)',
        default=65,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_laceration_chance: FloatProperty(
        name='Random Laceration Chance',
        description='Weighted chance injury will be a laceration (chances are automatically evened out to add up to 100%)',
        default=30,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bite_chance: FloatProperty(
        name='Random Bite Chance',
        description='Weighted chance injury will be a bite (chances are automatically evened out to add up to 100%)',
        default=5,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bandage_chance: FloatProperty(
        name='Random Bandage Chance',
        description='Weighted chance injury will be covered with a bandage',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bloody_bandage_chance: FloatProperty(
        name='Random Bloody Bandage Chance',
        description='Weighted chance a bandage will be bloody',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0,
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_bloodiness_intensity: EnumProperty(
        name='Random Bloodiness Intensity',
        description='How much blood should appear on the body',
        items=[
            ('SOME', "Some", "A bit of bloodiness", 0),
            ('MODERATE', "Moderate", "Quite a bit of bloodiness", 1),
            ('LOTS', "Lots", "A lot of bloodiness", 2),
            ('DRENCHED', "Drenched", "Absolutely soaked in blood", 3)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )
    random_dirtiness_intensity: EnumProperty(
        name='Random Dirtiness Intensity',
        description='How much dirt should appear on the body',
        items=[
            ('SOME', "Some", "A bit of dirt", 0),
            ('MODERATE', "Moderate", "Quite a bit of dirt", 1),
            ('LOTS', "Lots", "A lot of dirt", 2),
            ('DISGUSTING', "Disgusting", "Absolutely covered in dirt", 3)
        ],
        default='MODERATE',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# SHADING
# ============================================================================================

    def update_shading_type_index(self, context):
        self.shading_type_index = context.active_object.pz_human_props['shading_type']

    shading_type: EnumProperty(
        name="Shading Type",
        description="What type of shading to use",
        items=[
            ('EMISSION', "Emission",
             "The model will be unshaded, which is more akin to what it will look like in Project Zomboid", 0),
            ('PBR', "PBR", "The model will have shading, which is good for more high graphical fidelity renders", 1),
            ('CUSTOM', "Custom", "The model will use a specified shading node group using the generated color and alpha from the main material. Make sure the group has 'Color' as the first input, 'Alpha' as the second, and 'Shader' as the only output", 2)
        ],
        default='EMISSION',
        update=update_shading_type_index,
        override={"LIBRARY_OVERRIDABLE"}
    )

    shading_type_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Emission

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
        default=0.9,
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
        

        p = context.active_object.pz_human_props

        mat_names = ['MAT-HumanBody', 'MAT-PropMaterial', 'MAT-ClothingMaterial', 'MAT-Hair']

        for col in p.rig_collection.children_recursive:
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
        self.texture_interpolation_index = context.active_object.pz_human_props[
            'texture_interpolation']

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

# ============================================================================================
# COMPOSITING
# ============================================================================================

# ------------------------------------------------------------------------#
#  Outline

    use_outline: BoolProperty(
        name='Outline',
        description='Use the Compositor to create an outline around the model. Intended for still shots',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

    outline_size: IntProperty(
        name='Outline Size',
        description='How many pixels wide the outline is',
        default=4,
        min=1,
        max=8,
        override={"LIBRARY_OVERRIDABLE"}
    )

    outline_color: FloatVectorProperty(
        name="Outline Color",
        subtype='COLOR',
        default=(1.00, 1.00, 1.00),
        min=0,
        max=1,
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# CONTROLS
# ============================================================================================

# ------------------------------------------------------------------------#
#  Misc. Widget Settings

    widgets_size: FloatProperty(
        name="Widget Size",
        default=2.5,
        min=1.0,
        max=10.0,
        subtype="PIXEL",
        description="The size of the control widgets",
        override={"LIBRARY_OVERRIDABLE"}
    )
    auto_hide_controls: BoolProperty(
        name="Auto Hide Controls",
        default=True,
        description="When true, control bones that can not contribute to the end result are automatically hidden",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ------------------------------------------------------------------------#
#  Control Toggles

    # FK Toggles

    toggle_left_arm_fk_controls: BoolProperty(
        name="Arm FK.L",
        default=True,
        description="Show the left arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_arm_fk_controls: BoolProperty(
        name="Arm FK.R",
        default=True,
        description="Show the right arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_left_leg_fk_controls: BoolProperty(
        name="Leg FK.L",
        default=True,
        description="Show the left arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_leg_fk_controls: BoolProperty(
        name="Leg FK.R",
        default=True,
        description="Show the right arm FK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # IK Toggles

    toggle_left_arm_ik_controls: BoolProperty(
        name="Arm IK.L",
        default=True,
        description="Show the left arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_arm_ik_controls: BoolProperty(
        name="Arm IK.R",
        default=True,
        description="Show the right arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_left_leg_ik_controls: BoolProperty(
        name="Leg IK.L",
        default=True,
        description="Show the left arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_leg_ik_controls: BoolProperty(
        name="Leg IK.R",
        default=True,
        description="Show the right arm IK controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Root Toggles

    toggle_root_controls: BoolProperty(
        name="Root",
        default=True,
        description="Show the root controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_translation_data_controls: BoolProperty(
        name="Translation Data",
        default=True,
        description="Show the translation data controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Head Toggles

    toggle_look_point_controls: BoolProperty(
        name="Look Point",
        default=True,
        description="Show the look point controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_head_controls: BoolProperty(
        name="Head",
        default=True,
        description="Show the head controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Finger Toggles

    toggle_left_finger_controls: BoolProperty(
        name="Fingers.L",
        default=True,
        description="Show the left fingers controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_finger_controls: BoolProperty(
        name="Fingers.R",
        default=True,
        description="Show the right fingers controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Prop Toggles

    toggle_left_prop_controls: BoolProperty(
        name="Prop.L",
        default=True,
        description="Show the left prop controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_prop_controls: BoolProperty(
        name="Prop.R",
        default=True,
        description="Show the right prop controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_backpack_controls: BoolProperty(
        name="Backpack",
        default=True,
        description="Show the backpack controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_dress_controls: BoolProperty(
        name="Dress",
        default=True,
        description="Show the dress controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Shoulder Toggles

    toggle_left_shoulder_controls: BoolProperty(
        name="Shoulder.L",
        default=True,
        description="Show the left shoulder controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_right_shoulder_controls: BoolProperty(
        name="Shoulder.R",
        default=True,
        description="Show the right shoulder controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Torso Toggles

    toggle_pelvis_controls: BoolProperty(
        name="Pelvis",
        default=True,
        description="Show the pelvis controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_spine_controls: BoolProperty(
        name="Spine",
        default=True,
        description="Show the spine controls",
        override={"LIBRARY_OVERRIDABLE"}
    )
    toggle_chest_controls: BoolProperty(
        name="Chest",
        default=True,
        description="Show the chest controls",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# EXPORT
# ============================================================================================

    file_output_path: StringProperty(
        name="Output Directory",
        default="",
        description="The folder in which your animations will be stored. Most of the time, it should be in the 'anims_X' folder in your mod's media folder",
        subtype='DIR_PATH',
        override={"LIBRARY_OVERRIDABLE"}
    )
    batch_export: BoolProperty(
        name="Batch Export",
        default=True,
        description="If true, every individual action on Bip01 that has the substring from the Action Filter will be exported as a .glb file to the directory. If false, only export the active action on Bip01",
        override={"LIBRARY_OVERRIDABLE"}
    )
    action_filter: StringProperty(
        name="Action Filter",
        default="Bob_",
        description="If an action contains this substring, it will be exported as a .glb",
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# TESTING
# ============================================================================================

    # def update_body_texture_slots(self, context):
    #     return update_body_texture_slots(self, context)

    body_texture_slot_active_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    clothing_mesh_slot_active_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    prop_mesh_slot_active_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    zombie_injury_active_index: IntProperty(
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_clothing_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('GEO-PZ_Human_Clothes' + instance_str)
        if col:
            col.hide_viewport = not self.show_clothing
            col.hide_render = not self.show_clothing

    show_clothing: BoolProperty(
        name="Clothing Enabled",
        default=True,
        update=update_clothing_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

    def update_prop_visibility(self, context):
        p = context.active_object.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        col = bpy.data.collections.get('GEO-PZ_Human_Props' + instance_str)
        if col:
            col.hide_viewport = not self.show_props
            col.hide_render = not self.show_props

    show_props: BoolProperty(
        name="Props Enabled",
        default=True,
        update=update_prop_visibility,
        override={"LIBRARY_OVERRIDABLE"}
    )

    selected_outfit: StringProperty(
        name='Selected Outfit',
        override={"LIBRARY_OVERRIDABLE"}
    )

# ============================================================================================
# DEBUG
# ============================================================================================

    debug_toggle: BoolProperty(
        name='Debug',
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )
    halt_texture_updates: BoolProperty(
        default=False,
        override={"LIBRARY_OVERRIDABLE"}
    )

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Scene Properties


'''
This is the main PropertyGroup that carries some global info,
stored on the Scene. Note that the most important info is stored
in various CollectionProperties stored on the Scene, as you can see
in register()
'''


class PZ_HumanRigGlobalProperties(PropertyGroup):

# ============================================================================================
# ASSET DIRECTORIES
# ============================================================================================

    pz_directory: StringProperty(
        name="Project Zomboid Directory",
        default="",
        description="The location of your Project Zomboid install, most commonly found in the 'common' folder in the Steam directory",
        subtype='DIR_PATH'
    )
    mod_directory: StringProperty(
        name="Mod Directory",
        default="",
        description="The location of your custom mod, which will be used if a texture name cannot be found in the vanilla directory",
        subtype='DIR_PATH'
    )
    mod_directory_slot_active_index: IntProperty()

# ============================================================================================
# LISTS
# ============================================================================================

    clothing_item_slot_active_index: IntProperty()
    outfit_slot_active_index: IntProperty()
    skin_texture_active_index: IntProperty()
    stubble_texture_active_index: IntProperty()
    visibility_mask_active_index: IntProperty()
    overlay_mask_active_index: IntProperty()
    hair_style_slot_active_index: IntProperty()
    beard_style_slot_active_index: IntProperty()
    decal_slot_active_index: IntProperty()
   # body_location_active_index: IntProperty()
   # imported_animation_active_index: IntProperty()

# endregion

# ============================================================================================
# SETTINGS
# ============================================================================================

    auto_switch_kinematics: BoolProperty(
        name='Auto Switch Kinematics on Snap',
        description='When a snap from FK to IK or vice versa is performed, automatically switch the limb to the target context',
        default=True
    )
    auto_key_snaps: BoolProperty(
        name='Auto Key Snaps',
        description='When a snap from FK to IK or vice versa is performed, automatically key the toggle state and the positions of the affected controls',
        default=False
    )
    allow_overwriting: BoolProperty(
        name='Allow Overwriting',
        description='If an asset entry has the same name as an already registered asset, remove that asset and replace it with the new one. Useful for mods that modify vanilla assets, such as Fluffy Hair',
        default=True
    )

# ============================================================================================
# OTHER
# ============================================================================================

    assets_parsed: BoolProperty(
        default=False
    )

# =================================================================================================================================================
# =================================================================================================================================================

# region UI

# region Scene Rigs UI


class PZ_HumanRig_SceneRigsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_scene_rigs_panel"
    bl_label = "Zomboid Human Scene Rigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

# endregion

# region Rig UI

# ============================================================================================
# MAIN PANEL
# ============================================================================================


class PZ_HumanRig_MainPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_label = "Zomboid Human Rig Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        try:
            return context.active_object.get("rig_id") == "ZOMBOID_Human"
        except:
            return False

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

     #   layout.label(text='Rig Instance: ' + str(p.rig_instance))
        # 
        layout.prop(p, 'debug_toggle')

     #   layout.operator('zomboid.duplicate_rig')

        if p.debug_toggle:
            layout.prop(p, 'rig_instance')

            layout.prop(p, 'rig_collection')
            layout.prop(p, 'male_body_object')
            layout.prop(p, 'translation_data_empty')
            layout.prop(p, 'dummy01_empty')

            layout.separator()

            layout.prop(p, 'body_mat')
            layout.prop(p, 'mask_tex')
            layout.prop(p, 'body_tex')

            layout.separator()

            layout.prop(p, 'current_male_hair_style')
            layout.prop(p, 'current_beard_style')
            layout.prop(p, 'current_female_hair_style')
            layout.prop(p, 'current_hat_category')

# ============================================================================================
# CONSTRAINTS PANEL
# ============================================================================================


class PZ_HumanRig_ConstraintsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_constraints_panel"
    bl_label = "Constraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        main_column = layout.column()

        subpanel, panel_area = main_column.panel(
            "head_rotation_subpanel", default_closed=False)
        subpanel.label(text='Head Rotation')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            column.use_property_split = True

            column.prop(p, "head_lookpoint")
            column.prop(p, "lookpoint_parent")
            if p.lookpoint_parent_index == 4:
                column.prop(p, "lookpoint_parent_object")

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "ik_fk_subpanel", default_closed=False)
        subpanel.label(text='Inverse Kinematics')

        if panel_area:
            box = panel_area.box()

            column = box.column()

            column.prop(g, 'auto_switch_kinematics')
            column.prop(g, 'auto_key_snaps')

            main_row = box.row()

            left_column = main_row.column()
            left_column.use_property_split = True

            sub_box = left_column.box()

            sub_box.label(text="Left Arm")
            sub_box.prop(p, "arm_ik_l", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_l > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-UpperArmFK.L'
            op.second_fk_bone = 'CTRL-ForearmFK.L'
            op.first_ik_bone = 'IK-UpperArm.L'
            op.second_ik_bone = 'IK-Forearm.L'
            op.ik_control_bone = 'CTRL-ArmIK.L'
            op.extremity_bone = 'CTRL-HandFK.L'
            op.ik_fk_prop = 'arm_ik_l'

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_l < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-ForearmFK.L'
            op.ik_control_bone = 'CTRL-ArmIK.L'
            op.ik_pole_bone = 'CTRL-ElbowTarget.L'
            op.extremity_bone = 'CTRL-HandFK.L'
            op.limb_type = 'ARM'
            op.ik_fk_prop = 'arm_ik_l'

            sub_box.prop(p, "left_arm_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "left_arm_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            left_column.separator()

            sub_box = left_column.box()

            sub_box.label(text="Left Leg")
            sub_box.prop(p, "leg_ik_l", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_l > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-ThighFK.L'
            op.second_fk_bone = 'CTRL-CalfFK.L'
            op.first_ik_bone = 'IK-Thigh.L'
            op.second_ik_bone = 'IK-Calf.L'
            op.ik_control_bone = 'CTRL-LegIK.L'
            op.extremity_bone = 'CTRL-FootFK.L'
            op.ik_fk_prop = 'leg_ik_l'

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_l < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-CalfFK.L'
            op.ik_control_bone = 'CTRL-LegIK.L'
            op.ik_pole_bone = 'CTRL-KneeTarget.L'
            op.extremity_bone = 'CTRL-FootFK.L'
            op.limb_type = 'LEG'
            op.ik_fk_prop = 'leg_ik_l'

            sub_box.prop(p, "left_leg_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "left_leg_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            right_column = main_row.column()
            right_column.use_property_split = True

            sub_box = right_column.box()

            sub_box.label(text="Right Arm")
            sub_box.prop(p, "arm_ik_r", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_r > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-UpperArmFK.R'
            op.second_fk_bone = 'CTRL-ForearmFK.R'
            op.first_ik_bone = 'IK-UpperArm.R'
            op.second_ik_bone = 'IK-Forearm.R'
            op.ik_control_bone = 'CTRL-ArmIK.R'
            op.extremity_bone = 'CTRL-HandFK.R'
            op.ik_fk_prop = 'arm_ik_r'

            op_col = sub_box.column()
            op_col.enabled = p.arm_ik_r < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-ForearmFK.R'
            op.ik_control_bone = 'CTRL-ArmIK.R'
            op.ik_pole_bone = 'CTRL-ElbowTarget.R'
            op.extremity_bone = 'CTRL-HandFK.R'
            op.limb_type = 'ARM'
            op.ik_fk_prop = 'arm_ik_r'

            sub_box.prop(p, "right_arm_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "right_arm_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            right_column.separator()

            sub_box = right_column.box()

            sub_box.label(text="Right Leg")
            sub_box.prop(p, "leg_ik_r", text='IK')

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_r > 0

            op = op_col.operator('zomboid.snap_fk_to_ik')
            op.first_fk_bone = 'CTRL-ThighFK.R'
            op.second_fk_bone = 'CTRL-CalfFK.R'
            op.first_ik_bone = 'IK-Thigh.R'
            op.second_ik_bone = 'IK-Calf.R'
            op.ik_control_bone = 'CTRL-LegIK.R'
            op.extremity_bone = 'CTRL-FootFK.R'
            op.ik_fk_prop = 'leg_ik_r'

            op_col = sub_box.column()
            op_col.enabled = p.leg_ik_r < 1

            op = op_col.operator('zomboid.snap_ik_to_fk')
            op.fk_bone = 'CTRL-CalfFK.R'
            op.ik_control_bone = 'CTRL-LegIK.R'
            op.ik_pole_bone = 'CTRL-KneeTarget.R'
            op.extremity_bone = 'CTRL-FootFK.R'
            op.limb_type = 'LEG'
            op.ik_fk_prop = 'leg_ik_r'

            sub_box.prop(p, "right_leg_ik_control_parent",
                         text='Control Parent')
            sub_box.prop(p, "right_leg_ik_pole_parent", text='Pole Parent')

            sub_box.separator(factor=0.5)

            box.separator()
            column = box.column()
            column.prop(p, 'all_ik_control_parent')
            column.prop(p, 'all_ik_pole_parent')

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "dress_prop_backpack_subpanel", default_closed=False)
        subpanel.label(text='Props & Dress')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()

            left_column = row.column()
            left_column.use_property_split = True
            left_column.prop(p, 'left_prop_parent')
            if p.left_prop_parent_index == 3:
                left_column.prop(p, 'left_prop_parent_object')

            right_column = row.column()
            right_column.use_property_split = True
            right_column.prop(p, 'right_prop_parent')
            if p.right_prop_parent_index == 3:
                right_column.prop(p, 'right_prop_parent_object')

            column.separator(factor=2.0, type='LINE')

            row = column.row()
            row.use_property_split = True
            row.prop(p, 'backpack_parent')

            column.separator(factor=2.0, type='LINE')

            row = column.row()
            row.use_property_split = True
            row.prop(p, 'dress_parent')

        main_column.separator(factor=2.0, type='LINE')

        subpanel, panel_area = main_column.panel(
            "wrist_twist_subpanel", default_closed=False)
        subpanel.label(text='Extremity Rotation')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()

            row.prop(p, 'wrist_twist_amount')

# ============================================================================================
# CONTROLS PANEL
# ============================================================================================


class PZ_HumanRig_ControlsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_controls_panel"
    bl_label = "Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

        column = layout.column()

        row = column.row()

        row.prop(p, "widgets_size")
        row.prop(p, "auto_hide_controls")

        column.separator(factor=2.5, type="LINE")

        row = column.row()
        row.prop(p, "toggle_root_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_translation_data_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_finger_controls", toggle=True)
        row.prop(p, "toggle_right_finger_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_prop_controls", toggle=True)
        row.prop(p, "toggle_right_prop_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_backpack_controls", toggle=True)

        row = column.row()
        row.prop(p, "toggle_dress_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_left_shoulder_controls", toggle=True)
        row.prop(p, "toggle_right_shoulder_controls", toggle=True)

        column.separator()

        row = column.row()
        row.prop(p, "toggle_pelvis_controls", toggle=True)
        row.prop(p, "toggle_spine_controls", toggle=True)
        row.prop(p, "toggle_chest_controls", toggle=True)

        if not p.auto_hide_controls:

            column.separator()

            # Head Control Toggles
            row = column.row()
            row.prop(p, "toggle_head_controls", toggle=True)
            row = column.row()
            row.prop(p, "toggle_look_point_controls", toggle=True)

            column.separator()

            # FK Arm Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_arm_fk_controls", toggle=True)
            row.prop(p, "toggle_right_arm_fk_controls", toggle=True)

            # FK Leg Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_leg_fk_controls", toggle=True)
            row.prop(p, "toggle_right_leg_fk_controls", toggle=True)

            column.separator()

            # IK Arm Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_arm_ik_controls", toggle=True)
            row.prop(p, "toggle_right_arm_ik_controls", toggle=True)

            # IK Leg Control Toggles
            row = column.row()
            row.prop(p, "toggle_left_leg_ik_controls", toggle=True)
            row.prop(p, "toggle_right_leg_ik_controls", toggle=True)

# ============================================================================================
# MODEL PANEL
# ============================================================================================


class PZ_UL_BodyTextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)


class PZ_UL_ClothingMeshList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)

        viewport_icon = "RESTRICT_VIEW_OFF" if item.slot_hide_viewport else "RESTRICT_VIEW_ON"
        row.prop(item, 'slot_hide_viewport', text="", icon=viewport_icon)

        render_icon = "RESTRICT_RENDER_OFF" if item.slot_hide_render else "RESTRICT_RENDER_ON"
        row.prop(item, 'slot_hide_render', text="", icon=render_icon)


class PZ_UL_PropMeshList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)
        row.label(text=item.attach_bone)

        viewport_icon = "RESTRICT_VIEW_OFF" if item.slot_hide_viewport else "RESTRICT_VIEW_ON"
        row.prop(item, 'slot_hide_viewport', text="", icon=viewport_icon)

        render_icon = "RESTRICT_RENDER_OFF" if item.slot_hide_render else "RESTRICT_RENDER_ON"
        row.prop(item, 'slot_hide_render', text="", icon=render_icon)


class PZ_UL_ZombieInjuryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.name)


class PZ_HumanRig_ModelPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_model_panel"
    bl_label = "Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props
        g = context.scene.pz_human_global_props

        main_column = layout.column()

        column = main_column.column()

        sub_column = column.column(align=True)
        sub_column.scale_y = 0.7
        if not directx_import_available():
            sub_column.label(text='The .x importer extension is not installed or enabled.', icon='WARNING_LARGE')
            sub_column.label(text='         The link to it is on the rig GitHub.')
            sub_column.separator(factor=2.0)

        if not g.assets_parsed:
            sub_column.label(text='Zomboid\'s assets have not been parsed yet.', icon='WARNING_LARGE')
            sub_column.label(text='         In the Properties Editor, open the \'Scene\' tab,')
            sub_column.label(text='         then find the \'Zomboid Assets\' panel.')
            sub_column.label(text='         Assign the path to your Project Zomboid install')
            sub_column.label(text='         in \'Directories\', then click \'Parse All Assets\'')
            sub_column.label(text='         in \'Assets\'.')
            sub_column.separator(factor=2.0)

        row = column.row()
        row.operator('zomboid.reset_model')

        column.separator(factor=2.0)

        row = column.row()
        #row.enabled = g.assets_parsed and directx_import_available()
        row.scale_y = 1.5
        row.prop(p, "model_sex", expand=True)

        row = column.row()
        row.enabled = g.assets_parsed and directx_import_available()
        row.prop(p, 'skin_set')

        column.separator(factor=2)

        row = column.row()
        row.enabled = g.assets_parsed and directx_import_available()
        row.prop_search(p, 'selected_clothing_item',
                        context.scene, 'pz_human_clothing_item_slots')

        row = column.row()
        row.operator('zomboid.remove_all_clothing_items')

        

        column.separator(factor=2)

        subpanel, panel_area = column.panel(
            "body_model_subpanel", default_closed=False)
        subpanel.label(text='Body')

        icon = "HIDE_OFF" if p.show_body else "HIDE_ON"
        subpanel.prop(p, "show_body", text='', icon=icon)

        if p.show_body and panel_area:
            box = panel_area.box()
            column = box.column()
            column.enabled = g.assets_parsed and directx_import_available()

            if p.skin_set != 'SKELETON':

                if p.debug_toggle:
                    column.label(text="Body Masks")
                    column.separator(factor=0.5)

                    subcolumn = column.column(align=True)

                    row = subcolumn.row(align=True)
                    for index in range(6):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    row = subcolumn.row(align=True)
                    for index in range(6, 12):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    row = subcolumn.row(align=True)
                    for index in range(12, 17):
                        row.prop(p, "mask_array", text=str(
                            index), index=index, toggle=True)

                    subcolumn.separator()
                    column.separator(factor=3, type='LINE')
            
            column.label(text="Skin Texture")
            column.separator(factor=0.5)

            box = column.box()
            sub_col = box.column()
            row = sub_col.row()

            match p.skin_set:
                case 'HUMAN':
                    row.prop(p, "skin_color")
                    row.prop(p, "zombification")
                    if p.model_sex == 'MALE':
                        row = sub_col.row()
                        row.prop(p, 'chest_hair')
                    column.separator(factor=3, type='LINE')
                case 'SKELETON':
                    row.prop(p, "skeleton_type")
                    column.separator(factor=3, type='LINE')
                case 'MANNEQUIN':
                    row.prop(p, "mannequin_type")
                    column.separator(factor=3, type='LINE')

            if p.skin_set == 'HUMAN':

                column.label(text="Body Damage")
                column.separator(factor=0.5)

                box = column.box()

                body_injury_subpanel, body_injury_panel_area = box.panel(
                    "body_injury_subpanel", default_closed=False)
                body_injury_subpanel.label(text='Body Injuries')

                if body_injury_panel_area:
                    sub_col = body_injury_panel_area.column()
                    sub_col.prop(p, 'upper_torso_injury')
                    sub_col.prop(p, 'lower_torso_injury')
                    sub_col.prop(p, 'left_hand_injury')
                    sub_col.prop(p, 'right_hand_injury')
                    sub_col.prop(p, 'left_forearm_injury')
                    sub_col.prop(p, 'right_forearm_injury')
                    sub_col.prop(p, 'left_upperarm_injury')
                    sub_col.prop(p, 'right_upperarm_injury')
                    sub_col.prop(p, 'head_injury')
                    sub_col.prop(p, 'neck_injury')
                    sub_col.prop(p, 'groin_injury')
                    sub_col.prop(p, 'left_thigh_injury')
                    sub_col.prop(p, 'right_thigh_injury')
                    sub_col.prop(p, 'left_shin_injury')
                    sub_col.prop(p, 'right_shin_injury')
                    sub_col.prop(p, 'left_foot_injury')
                    sub_col.prop(p, 'right_foot_injury')

                    sub_box = sub_col.box()

                    sub_box.prop(p, 'random_scratch_chance')
                    sub_box.prop(p, 'random_laceration_chance')
                    sub_box.prop(p, 'random_bite_chance')
                    sub_box.prop(p, 'random_bandage_chance')
                    sub_box.prop(p, 'random_bloody_bandage_chance')

                    row = sub_box.row()
                    row.prop(p, 'random_injury_intensity')
                    row.operator('zomboid.randomize_body_injuries')

                    sub_col.operator('zomboid.remove_all_body_injuries')

                zombie_injury_subpanel, zombie_injury_panel_area = box.panel(
                    "zombie_injury_subpanel", default_closed=False)
                zombie_injury_subpanel.label(text='Zombie Injuries')

                if zombie_injury_panel_area:
                    sub_col = zombie_injury_panel_area.column()
                    sub_col.prop(p, 'selected_zombie_injury')
                    sub_col.template_list("PZ_UL_ZombieInjuryList", "pz_zombie_injury_list", context.object,
                                          "pz_human_zombie_injuries", context.object.pz_human_props, "zombie_injury_active_index")
                    if p.zombie_injury_active_index != -1:
                        sub_col.operator('zomboid.remove_zombie_injury')

                    row = sub_col.row()
                    row.prop(p, 'random_zombie_injury_intensity')
                    row.operator('zomboid.randomize_zombie_injuries')
                    sub_col.operator('zomboid.remove_all_zombie_injuries')

            if p.skin_set != 'SKELETON':

                bloodiness_subpanel, bloodiness_panel_area = box.panel(
                    "bloodiness_subpanel", default_closed=False)
                bloodiness_subpanel.label(text='Bloodiness')

                if bloodiness_panel_area:
                    sub_col = bloodiness_panel_area.column()
                    sub_col.prop(p, 'upper_torso_bloodiness')
                    sub_col.prop(p, 'lower_torso_bloodiness')
                    sub_col.prop(p, 'left_hand_bloodiness')
                    sub_col.prop(p, 'right_hand_bloodiness')
                    sub_col.prop(p, 'left_forearm_bloodiness')
                    sub_col.prop(p, 'right_forearm_bloodiness')
                    sub_col.prop(p, 'left_upperarm_bloodiness')
                    sub_col.prop(p, 'right_upperarm_bloodiness')
                    sub_col.prop(p, 'head_bloodiness')
                    sub_col.prop(p, 'neck_bloodiness')
                    sub_col.prop(p, 'groin_bloodiness')
                    sub_col.prop(p, 'left_thigh_bloodiness')
                    sub_col.prop(p, 'right_thigh_bloodiness')
                    sub_col.prop(p, 'left_shin_bloodiness')
                    sub_col.prop(p, 'right_shin_bloodiness')
                    sub_col.prop(p, 'left_foot_bloodiness')
                    sub_col.prop(p, 'right_foot_bloodiness')
                    sub_col.prop(p, 'back_bloodiness')

                    row = sub_col.row()
                    row.prop(p, 'random_bloodiness_intensity')
                    row.operator('zomboid.randomize_body_bloodiness')
                    sub_col.operator('zomboid.remove_body_bloodiness')

                dirtiness_subpanel, dirtiness_panel_area = box.panel(
                    "dirtiness_subpanel", default_closed=False)
                dirtiness_subpanel.label(text='Dirtiness')

                if dirtiness_panel_area:
                    sub_col = dirtiness_panel_area.column()
                    sub_col.prop(p, 'upper_torso_dirtiness')
                    sub_col.prop(p, 'lower_torso_dirtiness')
                    sub_col.prop(p, 'left_hand_dirtiness')
                    sub_col.prop(p, 'right_hand_dirtiness')
                    sub_col.prop(p, 'left_forearm_dirtiness')
                    sub_col.prop(p, 'right_forearm_dirtiness')
                    sub_col.prop(p, 'left_upperarm_dirtiness')
                    sub_col.prop(p, 'right_upperarm_dirtiness')
                    sub_col.prop(p, 'head_dirtiness')
                    sub_col.prop(p, 'neck_dirtiness')
                    sub_col.prop(p, 'groin_dirtiness')
                    sub_col.prop(p, 'left_thigh_dirtiness')
                    sub_col.prop(p, 'right_thigh_dirtiness')
                    sub_col.prop(p, 'left_shin_dirtiness')
                    sub_col.prop(p, 'right_shin_dirtiness')
                    sub_col.prop(p, 'left_foot_dirtiness')
                    sub_col.prop(p, 'right_foot_dirtiness')
                    sub_col.prop(p, 'back_dirtiness')

                    row = sub_col.row()
                    row.prop(p, 'random_dirtiness_intensity')
                    row.operator('zomboid.randomize_body_dirtiness')
                    sub_col.operator('zomboid.remove_body_dirtiness')

                box.operator('zomboid.remove_all_body_damage')

                column.separator(factor=3, type='LINE')

            row = column.row()

            row.label(text="Body Clothing Textures")

            row = column.row(align=True)

            row.template_list("PZ_UL_BodyTextureList", "pz_body_texture_list", context.object,
                                "pz_human_body_texture_slots", context.object.pz_human_props, "body_texture_slot_active_index")

            side_column = row.column(align=True)

            if p.body_texture_slot_active_index != -1:
                side_column.operator(
                    "zomboid.remove_body_texture_slot", text="", icon="REMOVE")

                column.separator()

                side_column.operator(
                    "zomboid.move_body_texture_slot_up", icon="TRIA_UP", text="")
                side_column.operator(
                    "zomboid.move_body_texture_slot_down", icon="TRIA_DOWN", text="")

            # column.separator(factor=1.5)
            # row = column.row()

            # if p.body_texture_slot_active_index != -1:
            #     row.label(text="Current Slot Properties")
            #     t = context.active_object.pz_human_body_texture_slots[
            #         p.body_texture_slot_active_index]

            #     box = column.box()
            #     column = box.column()

            #     row = column.row()
            #     row.prop(t, "tintable")
            #     if t.tintable:
            #         row.prop(t, "tint_color")


        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "clothing_model_subpanel", default_closed=True)
        subpanel.label(text='Clothes')

        icon = "HIDE_OFF" if p.show_clothing else "HIDE_ON"
        subpanel.prop(p, "show_clothing", text ='', icon=icon)

        if panel_area and p.show_clothing:
            box = panel_area.box()
            column = box.column()
            column.enabled = g.assets_parsed and directx_import_available()

            row = column.row()
            row.label(text="Clothing Models")
            column.separator(factor=0.5)

            row = column.row(align=True)
            side_column = row.column(align=True)

            side_column.template_list("PZ_UL_ClothingMeshList", "pz_clothing_mesh_list", context.object,
                                      "pz_human_clothing_mesh_slots", context.object.pz_human_props, "clothing_mesh_slot_active_index")

            side_column = row.column(align=True)

            if p.clothing_mesh_slot_active_index != -1:
                side_column.operator(
                    "zomboid.remove_clothing_mesh_slot", text="", icon="REMOVE")

            # column.separator(factor=1.5)
            # row = column.row()

            # if p.clothing_mesh_slot_active_index != -1:
            #     row.label(text="Current Slot Properties")
            #     m = context.active_object.pz_human_clothing_mesh_slots[
            #         p.clothing_mesh_slot_active_index]

            #     box = column.box()
            #     column = box.column()

            #     row = column.row()
            #     row.prop(m, "tintable")
            #     if m.tintable:
            #         row.prop(m, "tint_color")

        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "prop_model_subpanel", default_closed=True)
        subpanel.label(text='Props')

        icon = "HIDE_OFF" if p.show_props else "HIDE_ON"
        subpanel.prop(p, "show_props", text='', icon=icon)

        if panel_area and p.show_hair:
            box = panel_area.box()
            column = box.column()
            column.enabled = g.assets_parsed and directx_import_available()

            row = column.row()
            row.label(text="Prop Models")
            column.separator(factor=0.5)

            row = column.row(align=True)
            side_column = row.column(align=True)

            side_column.template_list("PZ_UL_PropMeshList", "pz_prop_mesh_list", context.object,
                                      "pz_human_prop_mesh_slots", context.object.pz_human_props, "prop_mesh_slot_active_index")

            side_column = row.column(align=True)

            if p.prop_mesh_slot_active_index != -1:
                side_column.operator(
                    "zomboid.remove_prop_mesh_slot", text="", icon="REMOVE")

            # column.separator(factor=1.5)
            # row = column.row()

            # if p.prop_mesh_slot_active_index != -1:
            #     row.label(text="Current Slot Properties")
            #     m = context.active_object.pz_human_prop_mesh_slots[p.prop_mesh_slot_active_index]

            #     box = column.box()
            #     column = box.column()

            #     row = column.row()
            #     row.prop(m, "tintable")
            #     if m.tintable:
            #         row.prop(m, "tint_color")

        main_column.separator(factor=1.5, type='LINE')

        subpanel, panel_area = main_column.panel(
            "hair_model_subpanel", default_closed=True)
        subpanel.label(text='Hair')

        icon = "HIDE_OFF" if p.show_hair else "HIDE_ON"
        subpanel.prop(p, "show_hair", text='', icon=icon)

        if panel_area and p.show_hair:
            box = panel_area.box()
            column = box.column()
            column.enabled = g.assets_parsed and directx_import_available()

            row = column.row()

            row.prop(p, 'hair_color')
            row.operator('zomboid.randomize_hair_color',
                         text='', icon='FILE_REFRESH')

            column.separator(factor=1.5, type='LINE')

            row = column.row(align=True)

            if p.model_sex_index == 0:
                row.prop_search(p, 'selected_male_hair_style',
                                context.scene, 'pz_human_male_hair_styles')
                row.operator('zomboid.randomize_hair_mesh', text='',
                             icon='FILE_REFRESH').hair_type = 'M'

                column.separator()

                row = column.row(align=True)
                row.prop_search(p, 'selected_beard_style',
                                context.scene, 'pz_human_beard_styles')
                row.operator('zomboid.randomize_hair_mesh', text='',
                             icon='FILE_REFRESH').hair_type = 'B'
            else:
                row.prop_search(p, 'selected_female_hair_style',
                                context.scene, 'pz_human_female_hair_styles')
                row.operator('zomboid.randomize_hair_mesh', text='',
                             icon='FILE_REFRESH').hair_type = 'F'
            
            column.separator(factor=1.5, type='LINE')

            row = column.row()

            row.prop(p, 'hair_stubble')

            if p.model_sex == 'MALE':
                row.prop(p, 'beard_stubble')

        main_column.separator(factor=1.5)

        main_column.separator(factor=3.0)

        subpanel, panel_area = main_column.panel(
            "presets_subpanel", default_closed=False)
        subpanel.label(text='Outfits')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            column.enabled = g.assets_parsed and directx_import_available()

            row = column.row()

            row.prop_search(p, 'selected_outfit', context.scene,
                            'pz_human_outfit_slots', item_search_property='search_name')

            row = column.row()

            row.prop(p, 'random_zombie')
            row.prop(p, 'random_skin_color')

            row = column.row()

            row.prop(p, 'random_hair_style')
            row.prop(p, 'random_hair_color')

            row = column.row()

            row.prop(p, 'natural_hair_color')

            row = column.row()

            row.prop(p, 'random_beard_chance', slider=True)

            row = column.row()
            row.prop(p, 'randomize_injuries')

            if p.randomize_injuries:
                box = column.box()

                box.prop(p, 'random_bloodiness_intensity')
                box.prop(p, 'random_dirtiness_intensity')

                box.separator()

                box.prop(p, 'random_injury_intensity')
                box.prop(p, 'random_zombie_injury_intensity')

                box.separator()

                box.prop(p, 'random_scratch_chance')
                box.prop(p, 'random_laceration_chance')
                box.prop(p, 'random_bite_chance')

                box.separator()

                box.prop(p, 'random_bandage_chance')
                box.prop(p, 'random_bloody_bandage_chance')

            row = column.row()
            row.scale_y = 2.0

            row.operator('zomboid.apply_outfit')

            row = column.row()
            row.scale_y = 1.5

            row.operator('zomboid.apply_random_outfit')

#        main_column.separator(factor=1.5)
#
#        subpanel, panel_area = main_column.panel("compositing_subpanel", default_closed=False)
#        subpanel.label(text='Compositing')
#
#        if panel_area:
#            box = panel_area.box()
#            column = box.column()
#
#            row = column.row()
#            row.prop(p, "use_outline")
#            if p.use_outline:
#                column.separator()
#                row = column.row()
#                row.prop(p, "outline_size")
#                row.prop(p, "outline_color")

# ============================================================================================
# SHADING PANEL
# ============================================================================================


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

# ============================================================================================
# EXPORT PANEL
# ============================================================================================


class PZ_HumanRig_ExportPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_export_panel"
    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        p = context.active_object.pz_human_props

        column = layout.column()

        row = column.row()
        row.prop(p, "file_output_path")

        row = column.row()
        row.alignment = 'LEFT'
        row.prop(p, "batch_export")

        if p.batch_export:
            row.prop(p, "action_filter")

        row = column.row()
        row.operator("zomboid.export_glb")

# endregion

# region Assets UI

# ============================================================================================
# MAIN ASSETS PANEL
# ============================================================================================


class PZ_HumanRig_GlobalPanel(Panel):
    bl_idname = "PROPERTIES_PT_pz_human_rig_global_panel"
    bl_label = "Zomboid Assets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

# ============================================================================================
# DIRECTORIES PANEL
# ============================================================================================


class PZ_UL_ModDirectoryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.prop(item, 'active', text='')


class PZ_HumanRig_DirectoriesPanel(Panel):
    bl_idname = "PROPERTIES_PT_pz_human_rig_directories_panel"
    bl_label = "Directories"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = "PROPERTIES_PT_pz_human_rig_global_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        g = context.scene.pz_human_global_props

        sub_column = layout.column(align=True)
        sub_column.scale_y = 0.7
        
        sub_column.label(text='In Steam, select \'Manage\' on Project Zomboid in your library.', icon='QUESTION_LARGE')
        sub_column.label(text='        Then, go to the \'Installed Files\' tab. Click on \'Browse\'.')
        sub_column.label(text='        The directory it opens up to is the directory you should put here.')

        layout.separator(factor=0.5)

        column = layout.column()

        column.prop(g, "pz_directory")

        column.separator(factor=5, type='LINE')

        column.label(text="Mod Directories (EXPERIMENTAL)")

        column.separator(factor=0.5)

        row = column.row()

        row.operator('zomboid.get_all_mod_directories')
        row.operator('zomboid.remove_all_mod_directories')

        row = column.row(align=True)

        row.template_list("PZ_UL_ModDirectoryList", "pz_mod_directory_list", context.scene,
                          "pz_human_mod_directory_slots", context.scene.pz_human_global_props, "mod_directory_slot_active_index")

        side_column = row.column(align=True)

        side_column.operator(
            "zomboid.add_mod_directory_slot", text="", icon="ADD")

        if g.mod_directory_slot_active_index != -1:
            side_column.operator(
                "zomboid.remove_mod_directory_slot", text="", icon="REMOVE")

            dir_prop = context.scene.pz_human_mod_directory_slots[g.mod_directory_slot_active_index]

            box = column.box()

            box.label(
                text='Mod Author:                                            ' + dir_prop.author)
            box.label(text='Latest PZ Version:                                   ' +
                      str(round(dir_prop.latest_pz_version, 2)))
            box.prop(dir_prop, 'mod_dir')

        column.separator()

# ============================================================================================
# ASSETS PANEL
# ============================================================================================


class PZ_UL_ClothingItemList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)


class PZ_UL_OutfitList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.label(text=item.sex)

class PZ_UL_SkinTextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.label(text=item.body_type)

class PZ_UL_StubbleTextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_StubbleTextureList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_VisibilityMaskList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_OverlayMaskList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_HairStyleList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.label(text=item.sex)

class PZ_UL_BeardStyleList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_DecalsList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_BodyLocationList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_UL_ImportedAnimationList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)
        row.label(text=item.character_type)


class PZ_HumanRig_AssetsPanel(Panel):
    bl_idname = "PROPERTIES_PT_pz_human_rig_assets_panel"
    bl_label = "Assets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = "PROPERTIES_PT_pz_human_rig_global_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        g = context.scene.pz_human_global_props

        main_column = layout.column()

        main_column.operator('zomboid.parse_all_xmls')
        main_column.operator('zomboid.clear_all_xmls')

        # ------------------------------------------------------------------------#
        #  Clothing Items
        
        subpanel, panel_area = main_column.panel(
            "clothing_items_subpanel", default_closed=True)
        subpanel.label(text='Clothing Items')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            # row = column.row()

            # row.operator("zomboid.parse_clothing_xmls")

            row = column.row(align=True)

            row.template_list("PZ_UL_ClothingItemList", "pz_clothing_item_list", context.scene,
                              "pz_human_clothing_item_slots", context.scene.pz_human_global_props, "clothing_item_slot_active_index")

            column.separator()

            row = column.row()

            if g.clothing_item_slot_active_index != -1:
                row.label(text="Clothing Item Properties")
                item_prop = context.scene.pz_human_clothing_item_slots[
                    g.clothing_item_slot_active_index]

                box = column.box()
                split = box.split()
                sub_column = split.column()

                sub_column.label(
                    text="GUID:                             " + item_prop.guid)
                sub_column.label(
                    text="Male Model Path:         " + item_prop.male_model_path)
                sub_column.label(text="Female Model Path:     " +
                                 item_prop.female_model_path)
                sub_column.label(
                    text="Model Type:                  " + item_prop.model_type)
                sub_column.label(
                    text="Tintable:                        " + str(item_prop.tintable))
                # sub_column.label(
                #     text="Body Location:             " + item_prop.body_location.name)

                sub_column = split.column()

                sub_column.label(
                    text="Static:                                         " + str(item_prop.static))
                sub_column.label(
                    text="Attach Bone:                             " + item_prop.attach_bone)
                sub_column.label(
                    text="Is Body Texture:                       " + str(item_prop.is_body_texture))
                sub_column.label(
                    text="Hat Category:                           " + str(item_prop.hat_category))
                sub_column.label(
                    text="Decal Group:                             " + str(item_prop.decal_group))
                sub_column.label(
                    text="Origin:                                        " + item_prop.origin)

                row = column.row()
                row.label(text="Texture Choices")

                texture_choices = item_prop.texture_choices

                box = column.box()
                split = box.split()
                sub_column = split.column()

                for texture in texture_choices:
                    sub_column.label(text=texture.texture_path)

                row = column.row()
                row.label(text="Masks")

                box = column.box()
                split = box.split()
                sub_column = split.column()

                masks = item_prop.mask_array
                for i in range(len(masks)):
                    if masks[i] == True:
                        sub_column.label(text=str(i))

        # ------------------------------------------------------------------------#
        #  Outfits

        subpanel, panel_area = main_column.panel(
            "outfits_subpanel", default_closed=True)
        subpanel.label(text='Outfits')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            # row = column.row()

            # row.operator("zomboid.parse_outfit_xmls")

            row = column.row(align=True)

            row.template_list("PZ_UL_OutfitList", "pz_outfit_list", context.scene,
                              "pz_human_outfit_slots", context.scene.pz_human_global_props, "outfit_slot_active_index")

            column.separator()

            row = column.row()

            if g.outfit_slot_active_index != -1:
                row.label(text="Outfit Properties")
                item_prop = context.scene.pz_human_outfit_slots[g.outfit_slot_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text="GUID:                             " + item_prop.guid)
                column.label(text="Random Top:                " +
                             str(item_prop.random_top))
                column.label(text="Random Pants:             " +
                             str(item_prop.random_pants))
                column.label(
                    text="Origin:                            " + str(item_prop.origin))

                for outfit_item in item_prop.outfit_items:
                    column.separator(factor=2.0)
                    column.label(text=str(
                        round(outfit_item.probability * 100, 2)) + '% chance for one of the following:')
                    for choice in outfit_item.choices:
                        column.label(text='- ' + choice.name)

        # ------------------------------------------------------------------------#
        #  Hair Styles

        subpanel, panel_area = main_column.panel(
            "hair_styles_subpanel", default_closed=True)
        subpanel.label(text='Hair Styles')

        if panel_area:
            box = panel_area.box()
            column = box.column()
            # row = column.row()

            # row.operator("zomboid.parse_hair_style_xmls")

            row = column.row(align=True)

            row.template_list("PZ_UL_HairStyleList", "pz_hair_style_list", context.scene,
                              "pz_human_hair_style_slots", context.scene.pz_human_global_props, "hair_style_slot_active_index")

            column.separator()

            row = column.row()

            if g.hair_style_slot_active_index != -1:
                row.label(text="Hair Properties")
                item_prop = context.scene.pz_human_hair_style_slots[g.hair_style_slot_active_index]

                box = column.box()
                split = box.split()
                sub_column = split.column()

                sub_column.label(text='Model Path:        ' +
                                 item_prop.model_path)
                sub_column.label(text='Texture Path:      ' +
                                 item_prop.texture_path)
                sub_column.label(
                    text='Hair Level:           ' + str(item_prop.level))
                sub_column.label(
                    text="Origin:                  " + str(item_prop.origin))

                column.separator()
                column.label(text="Alternate Hat Styles")
                box = column.box()
                split = box.split()
                left_column = split.column()
                right_column = split.column()

                hat_styles = item_prop.hat_styles
                for i in range(len(hat_styles)):
                    left_column.label(text=str(hat_styles[i].hat_group))
                    right_column.label(text=hat_styles[i].style_name)

        # ------------------------------------------------------------------------#
        #  Beard Styles

        subpanel, panel_area = main_column.panel(
            "beard_styles_subpanel", default_closed=True)
        subpanel.label(text='Beard Styles')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row(align=True)

            row.template_list("PZ_UL_BeardStyleList", "pz_beard_style_list", context.scene,
                              "pz_human_beard_styles", context.scene.pz_human_global_props, "beard_style_slot_active_index")

            column.separator()

            row = column.row()

            if g.beard_style_slot_active_index != -1:
                row.label(text="Beard Properties")
                item_prop = context.scene.pz_human_beard_styles[g.beard_style_slot_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(text='Model Path:        ' + item_prop.model_path)
                column.label(text='Beard Level:           ' +
                             str(item_prop.level))

        # ------------------------------------------------------------------------#
        #  Decals

        # subpanel, panel_area = main_column.panel(
        #     "decals_subpanel", default_closed=True)
        # subpanel.label(text='Decals')

        # if panel_area:
        #     box = panel_area.box()
        #     column = box.column()

        #     # row = column.row()

        #     # row.operator("zomboid.parse_decal_xmls")

        #     row = column.row(align=True)

        #     row.template_list("PZ_UL_DecalsList", "pz_decals_list", context.scene,
        #                       "pz_human_decals", context.scene.pz_human_global_props, "decal_slot_active_index")

        #     column.separator()

        #     row = column.row()

        #     if g.decal_slot_active_index != -1:
        #         row.label(text="Decal Properties")
        #         item_prop = context.scene.pz_human_decals[g.decal_slot_active_index]

        #         box = column.box()
        #         split = box.split()
        #         column = split.column()

        #         column.label(text='Texture Path:         ' +
        #                      item_prop.texture_path)
        #         column.label(text='X Position:             ' +
        #                      str(item_prop.x_pos))
        #         column.label(text='Y Position:             ' +
        #                      str(item_prop.y_pos))
        #         column.label(text='Width:                    ' +
        #                      str(item_prop.width))
        #         column.label(text='Height:                   ' +
        #                      str(item_prop.height))

        # ------------------------------------------------------------------------#
        #  Body Locations

        # subpanel, panel_area = main_column.panel(
        #     "body_locations_subpanel", default_closed=True)
        # subpanel.label(text='Body Locations')

        # if panel_area:
        #     box = panel_area.box()
        #     column = box.column()

        #     row = column.row()

        #     row.template_list("PZ_UL_BodyLocationList", "pz_body_location_list", context.scene,
        #                       "pz_human_body_locations", context.scene.pz_human_global_props, "body_location_active_index")

        #     column.separator()

        #     row = column.row()

        #     if g.body_location_active_index != -1:
        #         row.label(text="Body Location Properties")
        #         item_prop = context.scene.pz_human_body_locations[g.body_location_active_index]

        #         box = column.box()
        #         split = box.split()
        #         column = split.column()

        #         if len(item_prop.properties.hide_locations) > 0:
        #             column.label(
        #                 text='Body Location will be hidden if any of these locations are used:')
        #             column.separator(factor=0.5)

        #             for loc in item_prop.properties.hide_locations:
        #                 column.label(text=loc.name)

        #             column.separator()

        #         if len(item_prop.properties.alt_locations) > 0:
        #             column.label(
        #                 text='Body Location will use an alternate model if any of these locations are used:')
        #             column.separator(factor=0.5)

        #             for loc in item_prop.properties.alt_locations:
        #                 column.label(text=loc.name)

        #             column.separator()

        #         if len(item_prop.properties.exclusive_locations) > 0:
        #             column.label(
        #                 text='Body Location cannot be equpped if any of these locations are used (will be hidden in Blender):')
        #             column.separator(factor=0.5)

        #             for loc in item_prop.properties.exclusive_locations:
        #                 column.label(text=loc.name)

        #             column.separator()

        # ------------------------------------------------------------------------#
        #  Skin Textures

        subpanel, panel_area = main_column.panel(
            "skin_textures_subpanel", default_closed=True)
        subpanel.label(text='Skin Textures')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_SkinTextureList", "pz_skin_texture_list", context.scene,
                              "pz_human_skin_textures", context.scene.pz_human_global_props, "skin_texture_active_index")

            column.separator()

            row = column.row()

            if g.skin_texture_active_index != -1:

                row.label(text="Skin Properties")
                item_prop = context.scene.pz_human_skin_textures[
                    g.skin_texture_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)
                column.label(
                    text='Sex:                              ' + item_prop.sex)
                column.label(
                    text='Chest Hair:                              ' + str(item_prop.chest_hair))
                column.label(
                    text='Origin:                              ' + item_prop.origin)
        
        # ------------------------------------------------------------------------#
        #  Stubble Textures

        subpanel, panel_area = main_column.panel(
            "stubble_textures_subpanel", default_closed=True)
        subpanel.label(text='Stubble Textures')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_StubbleTextureList", "pz_stuble_texture_list", context.scene,
                              "pz_human_stubble_textures", context.scene.pz_human_global_props, "stubble_texture_active_index")

            column.separator()

            row = column.row()

            if g.stubble_texture_active_index != -1:

                row.label(text="Stubble Properties")
                item_prop = context.scene.pz_human_stubble_textures[
                    g.stubble_texture_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)
                column.label(
                    text='Sex:                              ' + item_prop.sex)
                column.label(
                    text='Type:                              ' + item_prop.stubble_type)
                column.label(
                    text='Origin:                              ' + item_prop.origin)

        # ------------------------------------------------------------------------#
        #  Visibility Masks

        subpanel, panel_area = main_column.panel(
            "visibility_masks_subpanel", default_closed=True)
        subpanel.label(text='Visibility Masks')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_VisibilityMaskList", "pz_visibility_mask_list", context.scene,
                              "pz_human_visibility_masks", context.scene.pz_human_global_props, "visibility_mask_active_index")

            column.separator()

            row = column.row()

            if g.visibility_mask_active_index != -1:

                row.label(text="Mask Properties")
                item_prop = context.scene.pz_human_visibility_masks[
                    g.visibility_mask_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)

        # ------------------------------------------------------------------------#
        #  Overlay Masks

        subpanel, panel_area = main_column.panel(
            "overlay_masks_subpanel", default_closed=True)
        subpanel.label(text='Overlay Masks')

        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row()

            row.template_list("PZ_UL_OverlayMaskList", "pz_overlay_mask_list", context.scene,
                              "pz_human_overlay_masks", context.scene.pz_human_global_props, "overlay_mask_active_index")

            column.separator()

            row = column.row()

            if g.overlay_mask_active_index != -1:

                row.label(text="Mask Properties")
                item_prop = context.scene.pz_human_overlay_masks[
                    g.overlay_mask_active_index]

                box = column.box()
                split = box.split()
                column = split.column()

                column.label(
                    text='Texture Path:                  ' + item_prop.texture_path)

        # ------------------------------------------------------------------------#
        #  Imported Animations

        # subpanel, panel_area = main_column.panel(
        #     "imported_animations_subpanel", default_closed=True)
        # subpanel.label(text='Imported Animations')

        # if panel_area:
        #     box = panel_area.box()
        #     column = box.column()

        #     row = column.row()

        #     row.template_list("PZ_UL_ImportedAnimationList", "pz_imported_animation_list", context.scene,
        #                       "pz_human_imported_animations", context.scene.pz_human_global_props, "imported_animation_active_index")

        #     column.separator()

        #     row = column.row()

        #     if g.imported_animation_active_index != -1:
        #         column.operator('zomboid.remap_animation')

        #         row.label(text="Animation Properties")
        #         item_prop = context.scene.pz_human_imported_animations[
        #             g.imported_animation_active_index]

        #         box = column.box()
        #         split = box.split()
        #         column = split.column()

        #         column.label(
        #             text='Animation Path:                  ' + item_prop.anim_path)
        #         column.label(
        #             text='File Type:                              ' + item_prop.file_type)

# endregion

# endregion

# =================================================================================================================================================
# =================================================================================================================================================

# region Registering


'''
This is the area that registers all of the custom classes for the rig into Blender.
There are a lot of classes, so it's a bit of a mess. Note that order matters.
'''

object_classes = [PZ_BodyLocationRef, PZ_BodyLocationProperties, PZ_BodyLocation,
                  PZ_SkinTexture, PZ_StubbleTexture, PZ_VisibilityMask, PZ_OverlayMask,
                  PZ_ShirtDecal, PZ_ShirtDecalGroup, PZ_ZombieInjury, PZ_BodyInjury,
                  PZ_BodyTextureSlot, PZ_ClothingMeshSlot, PZ_PropMeshSlot,
                  PZ_ClothingItemTextureChoices, PZ_ClothingItemSlot,
                  PZ_OutfitItemChoices, PZ_OutfitItem, PZ_OutfitSlot,
                  PZ_HairStyleHatStyle, PZ_HairStyleSlot,
                  PZ_ModDirectorySlot, PZ_ImportedAnimation, PZ_HumanRigObject]

operator_classes = [PZ_SnapFKToIK, PZ_SnapIKToFK,
                    PZ_ConstructBodyTexture,
                    PZ_HumanRig_CreateBodyBloodinessTexture, PZ_HumanRig_CreateBodyDirtinessTexture, PZ_HumanRig_CreateMaskTexture,
                    PZ_HumanRig_AddModDirectorySlot, PZ_HumanRig_RemoveModDirectorySlot,
                    PZ_HumanRig_AddBodyTextureSlot, PZ_HumanRig_RemoveBodyTextureSlot,
                    PZ_HumanRig_MoveBodyTextureSlotUp, PZ_HumanRig_MoveBodyTextureSlotDown,
                    PZ_HumanRig_AddClothingMeshSlot, PZ_HumanRig_RemoveClothingMeshSlot,
                    PZ_HumanRig_AddPropMeshSlot, PZ_HumanRig_RemovePropMeshSlot,
                    PZ_HumanRig_AddClothingItemSlot, PZ_HumanRig_RemoveClothingItemSlot,
                    PZ_HumanRig_AddOutfitSlot, PZ_HumanRig_RemoveOutfitSlot,
                    PZ_HumanRig_AddHairStyleSlot, PZ_HumanRig_RemoveHairStyleSlot,
                    PZ_HumanRig_AddBeardStyleSlot, PZ_HumanRig_RemoveBeardStyleSlot, PZ_HumanRig_RemoveZombieInjury,
                    PZ_ImportClothingMesh, PZ_ImportPropMesh, PZ_ImportHairMesh,
                    PZ_RemoveClothingMesh, PZ_RemovePropMesh, PZ_RemoveHairMesh,
                    PZ_HairRandomizer, PZ_HairColorRandomizer,
                    PZ_HumanRig_RandomizeBodyInjuries, PZ_HumanRig_RandomizeZombieInjuries,
                    PZ_HumanRig_RandomizeBodyBloodiness, PZ_HumanRig_RandomizeBodyDirtiness,
                    PZ_HumanRig_RemoveBodyDirtiness, PZ_HumanRig_RemoveBodyBloodiness,
                    PZ_HumanRig_RemoveAllBodyInjuries, PZ_HumanRig_RemoveAllZombieInjuries,
                    PZ_HumanRig_RemoveAllBodyDamage, PZ_HumanRig_GetAllModDirectories, PZ_HumanRig_RemoveAllModDirectories,
                    PZ_HumanRig_GetAllAnimations, PZ_HumanRig_RemapAnimation,
                    PZ_HumanRig_ParseClothingXMLs, PZ_HumanRig_ParseOutfitXMLs, PZ_HumanRig_ParseSkinTextures,
                    PZ_HumanRig_ParseHairStyleXMLs, PZ_HumanRig_ParseDecalXMLs, PZ_HumanRig_ParseInjuries,
                    PZ_HumanRig_ParseBodyLocationLua, PZ_HumanRig_ParseAllXMLs, PZ_HumanRig_ClearAllXMLs,
                    PZ_HumanRig_ApplyOutfit, PZ_HumanRig_ApplyRandomOutfit, PZ_HumanRig_AddClothingItem,
                    PZ_HumanRig_RemoveAllClothingItems, PZ_CheckHatCategory, PZ_HumanRig_Export,
                    PZ_HumanRig_DuplicateRig, PZ_ResetModel
                    ]

property_classes = [PZ_HumanRigProperties, PZ_HumanRigGlobalProperties]

scene_rig_ui_classes = [PZ_HumanRig_SceneRigsPanel]

rig_ui_classes = [PZ_UL_BodyTextureList, PZ_UL_ClothingMeshList, PZ_UL_PropMeshList,
                  PZ_UL_ZombieInjuryList,
                  PZ_HumanRig_MainPanel, PZ_HumanRig_ConstraintsPanel, PZ_HumanRig_ControlsPanel,
                  PZ_HumanRig_ModelPanel, PZ_HumanRig_ShadingPanel, PZ_HumanRig_ExportPanel,
                  ]

scene_ui_classes = [PZ_UL_ModDirectoryList, PZ_UL_ClothingItemList, PZ_UL_OutfitList,
                    PZ_UL_SkinTextureList, PZ_UL_StubbleTextureList, PZ_UL_VisibilityMaskList,
                    PZ_UL_OverlayMaskList,
                    PZ_UL_HairStyleList, PZ_UL_BeardStyleList, PZ_UL_DecalsList,
                    PZ_UL_BodyLocationList, PZ_UL_ImportedAnimationList, PZ_HumanRig_GlobalPanel,
                    PZ_HumanRig_DirectoriesPanel, PZ_HumanRig_AssetsPanel]

classes = object_classes + operator_classes + property_classes + \
     rig_ui_classes + scene_ui_classes # + scene_rig_ui_classes


def initialize_rigs():
    rigs = bpy.context.scene.pz_human_rigs
    g = bpy.context.scene.pz_human_global_props

    # TEMP FOR TESTING
    # rigs.clear()

    # Check if there are any rigs in the scene that are not already
    # in the scene rigs collection
    for obj in bpy.data.objects:
        if 'rig_id' in obj and obj['rig_id'] == 'ZOMBOID_Human':
            exists = False
            for rig in rigs:
                if rig.obj is obj:
                    exists = True
                    break
            if not exists:
                p = obj.pz_human_props

                new_rig = rigs.add()
                new_rig.obj = obj

                p.rig_instance = len(rigs) - 1

                new_rig.name = 'PZ Human Rig ' + \
                    str(obj.pz_human_props.rig_instance)
                
    for rig in rigs:
        p = rig.obj.pz_human_props
        instance_str = ' (' + str(p.rig_instance) + ')'

        bpy.context.view_layer.objects.active = rig.obj
        rig.obj.select_set(True)

        # Material
        body_mat = bpy.data.materials.get(
            'MAT-HumanBody' + instance_str)
        if body_mat:
            p.body_mat = body_mat
        else:
            create_model_material(bpy.context, None, 'BODY')
            p.body_mat = bpy.data.materials.get(
                'MAT-HumanBody' + instance_str)
        
        # Textures
        bpy.ops.zomboid.construct_body_texture()

        if g.assets_parsed:
            bpy.ops.zomboid.create_body_bloodiness_texture()
            bpy.ops.zomboid.create_body_dirtiness_texture()
            bpy.ops.zomboid.create_mask_texture()

        # Collection
        p.rig_collection = bpy.data.collections.get(
            'CH-PZ_Human' + instance_str)
        
        # Objects
        p.male_body_object = bpy.data.objects.get(
            'OBJ-MaleBody' + instance_str)
        p.female_body_object = bpy.data.objects.get(
            'OBJ-FemaleBody' + instance_str)
        p.male_dress_object = bpy.data.objects.get(
            'OBJ-MaleDress' + instance_str)
        p.female_dress_object = bpy.data.objects.get(
            'OBJ-FemaleDress' + instance_str)
        p.male_skeleon_object = bpy.data.objects.get(
            'OBJ-MaleSkeleton' + instance_str)
        p.female_skeleon_object = bpy.data.objects.get(
            'OBJ-FemaleSkeleton' + instance_str)
        
        p.translation_data_empty = bpy.data.objects.get(
            'OBJ-TranslationData' + instance_str)
        p.dummy01_empty = bpy.data.objects.get(
            'OBJ-Dummy01' + instance_str)

        
        rig_meshes = [p.male_body_object, p.female_body_object,
                      p.male_dress_object, p.female_dress_object,
                      p.male_skeleon_object, p.female_skeleon_object]

        for obj in rig_meshes:
            if obj.data:
                obj.data.materials.clear()
                obj.active_material = p.body_mat

        # Textures
        mask_tex = bpy.data.images.get(
            'MASK-MaskData' + instance_str)
        if mask_tex:
            p.mask_tex = mask_tex
            p.body_mat.node_tree.nodes.get('NDE-MaskData').image = p.mask_tex

        body_tex = bpy.data.images.get(
            'TEX-BodyTexture' + instance_str)
        if body_tex:
            p.body_tex = body_tex
            p.body_mat.node_tree.nodes.get('NDE-TexSlot').image = p.body_tex

# # Cleanup on loading new file
# @persistent
# def cleanup_on_load(dummy):
#     for cls in classes:
#         try:
#             bpy.utils.unregister_class(cls)
#         except RuntimeError:
#             pass 
    
#     if cleanup_on_load in bpy.app.handlers.load_pre:
#         bpy.app.handlers.load_pre.remove(cleanup_on_load)

def register():

    # Register our classes
    for cls in classes:
        # try:
        bpy.utils.register_class(cls)
        # except ValueError:
        #     pass

    # -------------------------------------------

    # # Add app handlers
    # if cleanup_on_load not in bpy.app.handlers.load_pre:
    #     bpy.app.handlers.load_pre.append(cleanup_on_load)

    # -------------------------------------------

    # Store our scene properties on the scene
    Scene.pz_human_global_props = PointerProperty(
        type=PZ_HumanRigGlobalProperties,
        name="PZ Human Rig Global Properties"
    )

    # Store our scene collections on the scene
    Scene.pz_human_rigs = CollectionProperty(type=PZ_HumanRigObject)
    Scene.pz_human_mod_directory_slots = CollectionProperty(
        type=PZ_ModDirectorySlot)
    Scene.pz_human_clothing_item_slots = CollectionProperty(
        type=PZ_ClothingItemSlot)
    Scene.pz_human_outfit_slots = CollectionProperty(type=PZ_OutfitSlot)
    Scene.pz_human_hair_style_slots = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_male_hair_styles = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_female_hair_styles = CollectionProperty(
        type=PZ_HairStyleSlot)
    Scene.pz_human_beard_styles = CollectionProperty(type=PZ_HairStyleSlot)
  #  Scene.pz_human_decal_groups = CollectionProperty(type=PZ_ShirtDecalGroup)
 #   Scene.pz_human_decals = CollectionProperty(type=PZ_ShirtDecal)
 #   Scene.pz_human_body_locations = CollectionProperty(type=PZ_BodyLocation)
    Scene.pz_human_body_injuries = CollectionProperty(type=PZ_BodyInjury)
    Scene.pz_human_zombie_injuries = CollectionProperty(type=PZ_ZombieInjury)
    Scene.pz_human_skin_textures = CollectionProperty(type=PZ_SkinTexture)
    Scene.pz_human_stubble_textures = CollectionProperty(type=PZ_StubbleTexture)
    Scene.pz_human_visibility_masks = CollectionProperty(type=PZ_VisibilityMask)
    Scene.pz_human_overlay_masks = CollectionProperty(type=PZ_OverlayMask)
    Scene.pz_human_imported_animations = CollectionProperty(
        type=PZ_ImportedAnimation)

    # -------------------------------------------

    # Filter method so we only get Zomboid Human rigs
    def poll_bip01(self, object):
        return object.type == 'ARMATURE' and object.name == 'Bip01'

    # Store our rig properties on the Zomboid rig object
    Object.pz_human_props = PointerProperty(
        type=PZ_HumanRigProperties,
        name="PZ Human Rig Properties",
        poll=poll_bip01,
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Store the rig collections on the rig object
    Object.pz_human_body_texture_slots = CollectionProperty(
        type=PZ_BodyTextureSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_clothing_mesh_slots = CollectionProperty(
        type=PZ_ClothingMeshSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_prop_mesh_slots = CollectionProperty(
        type=PZ_PropMeshSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_zombie_injuries = CollectionProperty(
        type=PZ_ZombieInjury,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )

    initialize_rigs()


def unregister():

    # Unregister our classes
    for cls in classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass 

    # -------------------------------------------

    # Remove properties and collections from the rig objects
    del Object.pz_human_props
    del Object.pz_human_body_texture_slots
    del Object.pz_human_clothing_mesh_slots
    del Object.pz_human_prop_mesh_slots
    del Object.pz_human_zombie_injuries

    # -------------------------------------------

    # Remove properties and collections from the scene
    del Scene.pz_human_rigs
    del Scene.pz_human_mod_directory_slots
    del Scene.pz_human_clothing_item_slots
    del Scene.pz_human_outfit_slots
    del Scene.pz_human_hair_style_slots
    del Scene.pz_human_male_hair_styles
    del Scene.pz_human_female_hair_styles
    del Scene.pz_human_beard_styles
  #  del Scene.pz_human_decal_groups
  #  del Scene.pz_human_decals
  #  del Scene.pz_human_body_locations
    del Scene.pz_human_body_injuries
    del Scene.pz_human_zombie_injuries
    del Scene.pz_human_skin_textures
    del Scene.pz_human_stubble_textures
    del Scene.pz_human_visibility_masks
    del Scene.pz_human_overlay_masks
    del Scene.pz_human_imported_animations

# Script Entry Point
if __name__ == "__main__":
    register()

# endregion
