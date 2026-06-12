#pyright: reportInvalidTypeForm=false
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

---------------------------------------------------------------------------------------

If you run into any issues, errors, or questions, please contact me at the Official Project 
Zomboid Discord or the PZ Modding Discord @Paddlefruit
'''

#=================================================================================================================================================
#=================================================================================================================================================

# region Importing

import bpy # type: ignore
import os
import sys
import math
import time
import re
import xml.etree.ElementTree as ET
import numpy as np

from bpy.types import PropertyGroup, Collection, Object, Operator, Panel, UIList, Scene, Image, Material # type: ignore
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty # type: ignore

from random import randint, choices, random, uniform
from pathlib import Path

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

# region Objects

'''
These PropertyGroups are the data structures used by the rig to manage and consolidate
data across various areas.
'''

# ============================================================================================
# RIG OBJECT
# ============================================================================================

class PZ_HumanRigObject(PropertyGroup):
    name : StringProperty()
    obj : PointerProperty(type=Object)

# ============================================================================================
# BODY LOCATION
# ============================================================================================

class PZ_BodyLocationRef(PropertyGroup):
    pass

class PZ_BodyLocationProperties(PropertyGroup):
    hide_locations : CollectionProperty(type=PZ_BodyLocationRef)             # pyright: ignore[reportInvalidTypeForm] # This body location will be hidden any of the body locations in this collection are occupied
    alt_locations : CollectionProperty(type=PZ_BodyLocationRef)              # This body location will use an alternate model if any of the body locations in this collection are occupied
    exclusive_locations : CollectionProperty(type=PZ_BodyLocationRef)        # This body location cannot be equipped if any of the body locations in this collection are occupied (No effect in Blender)

class PZ_BodyLocation(PropertyGroup):
    name : StringProperty(default='NONE')
    properties : PointerProperty(type=PZ_BodyLocationProperties)

# ============================================================================================
# SHIRT DECAL SLOT
# ============================================================================================

class PZ_ShirtDecal(PropertyGroup):
    name : StringProperty()
    texture_path : StringProperty()
    x_pos : IntProperty()
    y_pos : IntProperty()
    width : IntProperty()
    height : IntProperty()

class PZ_ShirtDecalGroup(PropertyGroup):
    name : StringProperty()
    decals : CollectionProperty(type=PZ_ShirtDecal)    

# ============================================================================================
# BODY TEXTURE SLOT
# ============================================================================================

class PZ_BodyTextureSlot(PropertyGroup):
    
    def update_item_name(self, context):
        bpy.ops.zomboid.construct_body_texture()
    
    name : StringProperty(default="New Body Texture")
    texture_path : StringProperty(name="Texture Path", update=update_item_name)
    tintable : BoolProperty(name="Tintable", default=False)
    tint_color : FloatVectorProperty(name="Tint Color", subtype='COLOR', default=(1.0, 1.0, 1.0), max=1.0, min=0.0)
    opacity : FloatProperty(name="Opacity", default=1.0, min=0.0, max=1.0, subtype='FACTOR')
    decal_group : StringProperty(default='None')
    bloodiness : FloatProperty(default=0.0, min=0.0, max=1.0)
    origin : StringProperty()
    #decal : PointerProperty(type=PZ_ShirtDecal)

# ============================================================================================
# ZOMBIE INJURY
# ============================================================================================

class PZ_ZombieInjury(PropertyGroup):
    texture_path : StringProperty()

# ============================================================================================
# CLOTHING MESH SLOT
# ============================================================================================

class PZ_ClothingMeshSlot(PropertyGroup):
    
    def update_model_visibility(self, context):
        update_clothing_sex_visibility(self, context)
    
    def update_model_render(self, context):
        update_clothing_sex_render(self, context)
    
    name : StringProperty(
        default="New Clothing Model"
    )
    male_model_path : StringProperty(
        name="Male Model Path"
    )
    female_model_path : StringProperty(
        name="Female Model Path"
    )
    model_type : EnumProperty(
        name="Model Type",
        items=[
            ('X', "X", "Model type is .x", 0),
            ('FBX', "FBX", "Model type is .fbx", 1),
            ('GLB', "GLB", "Model type is .glb", 2)
        ]
    )
    texture_path : StringProperty(
        name="Texture Path"
    )
    tintable : BoolProperty(
        name="Tintable", 
        default=False
    )
    tint_color : FloatVectorProperty(
        name="Tint Color", 
        subtype='COLOR', 
        default=(1.0, 1.0, 1.0), 
        max=1.0, 
        min=0.0
    )
    slot_hide_render : BoolProperty(
        name="Visible in Render", 
        default=True, 
        update=update_model_render
    )
    slot_hide_viewport : BoolProperty(
        name="Visible in Viewport", 
        default=True, 
        update=update_model_visibility
    )
    mask_array : BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                False, False, False, False, False, False,
                False, False, False, False, False)
    )
    bloodiness : FloatProperty(default=0.0, min=0.0, max=1.0)
    hat_category : IntProperty()
    origin : StringProperty()

# ============================================================================================
# PROP MESH SLOT
# ============================================================================================

class PZ_PropMeshSlot(PropertyGroup):

    def update_model_visibility(self, context):
        update_prop_sex_visibility(self, context)
    
    def update_model_render(self, context):
        update_prop_sex_render(self, context)
    
    name : StringProperty(
        default="New Prop Model"
    )
    male_model_path : StringProperty(
        name="Male Model Path"
    )
    female_model_path : StringProperty(
        name="Female Model Path"
    )
    model_type : EnumProperty(
        name="Model Type",
        items=[
            ('X', "X", "Model type is .x", 0),
            ('FBX', "FBX", "Model type is .fbx", 1),
            ('GLB', "GLB", "Model type is .glb", 2)
        ]
    )
    texture_path : StringProperty(
        name="Texture Path"
    )
    tintable : BoolProperty(
        name="Tintable", 
        default=False
    )
    tint_color : FloatVectorProperty(
        name="Tint Color", 
        subtype='COLOR', 
        default=(1.0, 1.0, 1.0), 
        max=1.0, 
        min=0.0
    )
    attach_bone : StringProperty()
    slot_hide_render : BoolProperty(
        name="Visible in Render", 
        default=True, 
        update=update_model_render
    )
    slot_hide_viewport : BoolProperty(
        name="Visible in Viewport", 
        default=True, 
        update=update_model_visibility
    )
    hat_category : IntProperty()
    origin : StringProperty()

# ============================================================================================
# CLOTHING ITEM SLOT
# ============================================================================================

class PZ_ClothingItemTextureChoices(PropertyGroup):
    texture_path : StringProperty()

class PZ_ClothingItemSlot(PropertyGroup):
    name : StringProperty()
    guid : StringProperty(
        name="GUID"
    )
    is_body_texture : BoolProperty()
    male_model_path : StringProperty(
        name="Male Model Path", 
        subtype='FILE_PATH', 
    )
    female_model_path : StringProperty(
        name="Female Model Path", 
        subtype='FILE_PATH', 
    )
    model_type : EnumProperty(
        name="Model Type",
        items=[
            ('X', "X", "Model type is .x", 0),
            ('FBX', "FBX", "Model type is .fbx", 1),
            ('GLB', "GLB", "Model type is .glb", 2),
            ('NONE', "None", "Item has no model", 3)
        ]
    )
    texture_choices : CollectionProperty(type=PZ_ClothingItemTextureChoices)
    tintable : BoolProperty(
        name="Tintable", 
        default=False
    )
    tint_color : FloatVectorProperty(
        name="Tint Color", 
        subtype='COLOR', 
        default=(1.0, 1.0, 1.0), 
        max=1.0, 
        min=0.0
    )
    attach_bone : StringProperty()
    static : BoolProperty()
    mask_array : BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                 False, False, False, False, False, False,
                 False, False, False, False, False)
    )
    hat_category : IntProperty()
    decal_group : StringProperty(default='None')
    body_location : PointerProperty(type=PZ_BodyLocation)
    origin : StringProperty()

# ============================================================================================
# OUTFIT SLOT
# ============================================================================================

class PZ_OutfitItemChoices(PropertyGroup):
    guid : StringProperty()
    name : StringProperty()

class PZ_OutfitItem(PropertyGroup):
    probability : FloatProperty(default = 1.0)
    choices : CollectionProperty(type=PZ_OutfitItemChoices)

class PZ_OutfitSlot(PropertyGroup):
    name : StringProperty()
    search_name : StringProperty()
    guid : StringProperty()
    sex : StringProperty()
    random_top : BoolProperty()
    random_pants : BoolProperty()
    allow_tint : BoolProperty()
    allow_shirt_decal : BoolProperty()
    origin : StringProperty()
    
    outfit_items : CollectionProperty(type=PZ_OutfitItem)

# ============================================================================================
# HAIR STYLE SLOT
# ============================================================================================

class PZ_HairStyleHatStyle(PropertyGroup):
    hat_group : IntProperty()
    style_name : StringProperty()

class PZ_HairStyleSlot(PropertyGroup):
    name : StringProperty()
    model_path : StringProperty()
    texture_type : StringProperty()
    sex : StringProperty()
    level : IntProperty()
    hat_styles : CollectionProperty(type=PZ_HairStyleHatStyle)
    origin : StringProperty()

# ============================================================================================
# MOD DIRECTORY SLOT
# ============================================================================================

class PZ_ModDirectorySlot(PropertyGroup):
    name : StringProperty(
        default = 'Unknown Mod'
    )
    author : StringProperty(
        default = 'Unknown Author'
    )
    mod_dir : StringProperty(
        subtype='DIR_PATH'
    )
    common_dir : StringProperty(
        subtype='DIR_PATH'
    )
    latest_pz_version : FloatProperty(
        default = 42.0
    )

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

# region Methods

'''
These are the various functions that do not warrant their own Operators.
'''

# region Texture Methods

# ============================================================================================
# SKIN TEXTURE UPDATER
# ============================================================================================

def update_skin_texture(self, context):
    prop = context.active_object.pz_human_props
    
    skin_5_fix = prop.skin_color == 4 and prop.zombification != 0
    zombie_3_fix = prop.skin_color == 2 and prop.zombification > 1
    
    s = str(prop.skin_color) if skin_5_fix else str(prop.skin_color + 1)
    z = str(prop.zombification)
    sex = 'Male' if prop.model_sex_index == 0 else 'Female'
    
    target_image = None
    
    if zombie_3_fix and sex == 'Male':
        target_image = bpy.data.images.get("TEX-Male3Zombie1")
    else:
        target_image = bpy.data.images.get("TEX-" + sex + s + 'Zombie' + z)
    
    mat = prop.body_mat
    
    if target_image and mat:
        mat.node_tree.nodes.get('TEX-SkinTexture').image = target_image

# endregion

# region Parenting Methods

# ============================================================================================
# DYNAMIC OBJECT PARENTING
# ============================================================================================

def update_lookpoint_parent_object(self, context):
    prop = context.active_object.pz_human_props
    
    bip01 = bpy.data.objects.get('Bip01')
    lookpoint = bip01.pose.bones.get('CTRL-LookPoint')
    copy_constraint = lookpoint.constraints.get('Copy Location')
    
    copy_constraint.target = prop.lookpoint_parent_object

def update_left_prop_parent_object(self, context):
    prop = context.active_object.pz_human_props
    
    bip01 = bpy.data.objects.get('Bip01')
    lookpoint = bip01.pose.bones.get('CTRL-Prop.L')
    copy_constraint = lookpoint.constraints.get('Copy Location')
    
    copy_constraint.target = prop.left_prop_parent_object

def update_right_prop_parent_object(self, context):
    prop = context.active_object.pz_human_props
    
    bip01 = bpy.data.objects.get('Bip01')
    lookpoint = bip01.pose.bones.get('CTRL-Prop.R')
    copy_constraint = lookpoint.constraints.get('Copy Location')
    
    copy_constraint.target = prop.right_prop_parent_object

# endregion

# region Visibility Methods

# ============================================================================================
# SEX VISIBILITY & RENDER UPDATERS
# ============================================================================================

#-------------------------------------------------------------#
# Clothing Sex Visibility

def update_clothing_sex_visibility(self, context):
    prop = context.active_object.pz_human_props
    mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
    
    instance_str = ' (' + str(prop.rig_instance) + ')'

    male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Clothes' + instance_str)
    female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Clothes' + instance_str)
    
    current_sex = prop.model_sex_index
    
    for i in range(len(mesh_prop_list)):
        mesh_prop = mesh_prop_list[i]
        
        obj = male_collection.objects.get('OBJ-MaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not mesh_prop.slot_hide_viewport
            
        obj = female_collection.objects.get('OBJ-FemaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not mesh_prop.slot_hide_viewport
    
def update_clothing_sex_render(self, context):
    prop = context.active_object.pz_human_props
    mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
    
    instance_str = ' (' + str(prop.rig_instance) + ')'

    male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Clothes' + instance_str)
    female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Clothes' + instance_str)
    
    current_sex = prop.model_sex_index
    
    for i in range(len(mesh_prop_list)):
        mesh_prop = mesh_prop_list[i]
        
        obj = male_collection.objects.get('OBJ-MaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not mesh_prop.slot_hide_render
            
        obj = female_collection.objects.get('OBJ-FemaleClothingMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not mesh_prop.slot_hide_render

#-------------------------------------------------------------#
# Prop Sex Visibility

def update_prop_sex_visibility(self, context):
    prop = context.active_object.pz_human_props
    prop_prop_list = context.active_object.pz_human_prop_mesh_slots
    
    instance_str = ' (' + str(prop.rig_instance) + ')'

    male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Props' + instance_str)
    female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Props' + instance_str)
    
    current_sex = prop.model_sex_index
    
    for i in range(len(prop_prop_list)):
        prop_prop = prop_prop_list[i]
        
        obj = male_collection.objects.get('OBJ-MalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not prop_prop.slot_hide_viewport
            
        obj = female_collection.objects.get('OBJ-FemalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_viewport = obj['sex'] != current_sex or not prop_prop.slot_hide_viewport
    
def update_prop_sex_render(self, context):
    prop = context.active_object.pz_human_props
    prop_prop_list = context.active_object.pz_human_prop_mesh_slots
    
    instance_str = ' (' + str(prop.rig_instance) + ')'

    male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Props' + instance_str)
    female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Props' + instance_str)
    
    current_sex = prop.model_sex_index
    
    for i in range(len(prop_prop_list)):
        prop_prop = prop_prop_list[i]
        
        obj = male_collection.objects.get('OBJ-MalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not prop_prop.slot_hide_render
            
        obj = female_collection.objects.get('OBJ-FemalePropMesh' + str(i) + instance_str)
        if obj:
            obj.hide_render = obj['sex'] != current_sex or not prop_prop.slot_hide_render

#-------------------------------------------------------------#
# Hair Sex Visibility

def update_hair_sex_visibility(self, context):
    prop = context.active_object.pz_human_props
    
    instance_str = ' (' + str(prop.rig_instance) + ')'
    hair_collection = prop.rig_collection.children.get('GEO-PZ_Human' + instance_str).children.get('GEO-PZ_Human_Hair' + instance_str)
    male_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Male' + instance_str)
    female_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Female' + instance_str)
    beard_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Beard' + instance_str)
    
    current_sex = prop.model_sex_index
        
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
    prop = context.active_object.pz_human_props
    
    instance_str = ' (' + str(prop.rig_instance) + ')'
    hair_collection = prop.rig_collection.children.get('GEO-PZ_Human' + instance_str).children.get('GEO-PZ_Human_Hair' + instance_str)
    male_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Male' + instance_str)
    female_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Female' + instance_str)
    beard_collection = hair_collection.children.get('GEO-PZ_Human_Hair_Beard' + instance_str)
    
    current_sex = prop.model_sex_index
        
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

#=================================================================================================================================================
#=================================================================================================================================================

# region Operators

# region Body Texture Operators

# ============================================================================================
# SHADER TREE CONSTRUCTION
# ============================================================================================

class PZ_ConstructBodyTexture(Operator):
    bl_idname = "zomboid.construct_body_texture"
    bl_label = "Construct Body Texture"
    
    #-------------------------------------------------------------#
    # Create Skin with Textures
    
    def reconstruct_body_tex_node(self, context, tex_path, node_index):   
             
        # Get reference to the rig's properties
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        tex_prop = context.active_object.pz_human_body_texture_slots[node_index]
        tex_prop_list = context.active_object.pz_human_body_texture_slots
        
        textures_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\'
            tex_path = tex_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/'
            tex_path = tex_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = textures_dir + tex_path + ".png"
        target = bpy.path.resolve_ncase(target)
        
        if Path(target).is_file():
            
            # Get reference to the human material
            mat = prop.body_mat
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            for node in nodes:
                node.select = False
            
            #------------------#
            
            # Get the texture node, or create it if it does not exist
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.name = "NDE-TexSlot" + str(node_index)
            tex_node.select = True
            
            # Get the texture mix node, or create it if it does not exist
            mix_node = nodes.new(type='ShaderNodeMix')
            mix_node.name = "NDE-TexMix" + str(node_index)
            mix_node.select = True
            
            # Get the color tint node, or create it if it does not exist
            tint_node = nodes.new(type='ShaderNodeMix')
            tint_node.name = "NDE-TexTint" + str(node_index)
            tint_node.select = True
            
            # Get the opacity mult node, or create it if it does not exist
            opacity_node = nodes.new(type='ShaderNodeMath')
            opacity_node.name = "NDE-OpacityMult" + str(node_index)
            opacity_node.select = True
            
            # Get the alpha add node, or create it if it does not exist
            alpha_add_node = nodes.new(type='ShaderNodeMath')
            alpha_add_node.name = "NDE-AlphaAdd" + str(node_index)
            alpha_add_node.select = True
            
            # Create a frame node and group all these nodes inside of it
            frame_node = nodes.get("NDE-GroupFrame" + str(node_index))
            if frame_node is None:
                frame_node = nodes.new(type='NodeFrame')
                frame_node.name = "NDE-GroupFrame" + str(node_index)
                frame_node.label = tex_prop.name
            
            for node in nodes:
                if node.select and node != frame_node:
                    node.parent = frame_node
            
            # Get the emission shader node
            emission_node = nodes.get("NDE-EmissionShader")
            
            # Get the PBR shader node
            pbr_node = nodes.get("NDE-PBRShader")
            
            # Get the mix shader node
            mix_shader_node = nodes.get("NDE-MixShader")
            
            # Get the transparent shader node
            transparent_node = nodes.get("NDE-TransparentShader")
            
            # Get the mix emission and transparent shader node
            emission_alpha_node = nodes.get("NDE-EmissionAlphaMix")
            
            # Get the injury texture node
            injury_node = nodes.get("TEX-InjuryTexture")
            
            # Get the blood mask node
            
            # Get the blood texture node
            
            # Get the blood mix node
            blood_mix_node = nodes.get("NDE-BloodMix")
            
            
            # Get the dirt mask node
            
            # Get the dirt texture node
            
            # Get the dirt mix node
            
            #------------------#
            
            ### Set the mix node properties ###
            mix_node.data_type = 'RGBA'
            
            ### Set the texture node properties ###
            tex_node.image = bpy.data.images.load(str(target))
            
            injury_node.image = bpy.data.images.get('TEX-BodyInjuries')
            
            # Interpolation Driver 
            path = 'nodes["NDE-TexSlot' + str(node_index) +'"].interpolation'
            fcurve = mat.node_tree.driver_add(path)
            driver = fcurve.driver
            driver.type = 'AVERAGE'
            
            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_human_props.texture_interpolation_index"
            
            ### Set the color tint node properties ###
            c = tex_prop.tint_color
            
            tint_node.data_type = 'RGBA'
            tint_node.blend_type = 'MULTIPLY'
            
            # Factor Driver
            path = 'nodes["NDE-TexTint' + str(node_index) +'"].inputs[0].default_value'
            fcurve = mat.node_tree.driver_add(path)
            driver = fcurve.driver
            driver.type = 'AVERAGE'
            
            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_human_body_texture_slots[" + str(node_index) + "].tintable"
            target.use_fallback_value = True
            target.fallback_value = 0.0
            
            # Color Drivers
            for i in range(3):
                path = 'nodes["NDE-TexTint' + str(node_index) +'"].inputs[7].default_value'
                fcurve = mat.node_tree.driver_add(path, i)
                driver = fcurve.driver
                driver.type = 'AVERAGE'
                
                var = driver.variables.new()
                target = var.targets[0]
                target.id = context.active_object
                target.data_path = "pz_human_body_texture_slots[" + str(node_index) + "].tint_color[" + str(i) + "]"
                target.use_fallback_value = True
                target.fallback_value = 1.0
        
            ### Set the opacity mult node properties ###
            opacity_node.operation = 'MULTIPLY'
            
            # Opacity Driver
            path = 'nodes["NDE-OpacityMult' + str(node_index) +'"].inputs[1].default_value'
            fcurve = mat.node_tree.driver_add(path)
            driver = fcurve.driver
            driver.type = 'AVERAGE'
            
            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_human_body_texture_slots[" + str(node_index) + "].opacity"
            target.use_fallback_value = True
            target.fallback_value = 1.0
                
                
            opacity_node.inputs[1].default_value = tex_prop.opacity
            
            ### Set the alpha add node properties ###
            alpha_add_node.operation = 'ADD'
            
            #------------------#
            
            # Connect the color from the texture node to the 1st color in the tint node
            links.new(tex_node.outputs['Color'], tint_node.inputs['A'])
            
            # Connect the alpha from the texture node to the 1st float in the opacity node
            links.new(tex_node.outputs[1], opacity_node.inputs[0])
            
            # Connect the output from the opacity node to the factor of the texture mix node
            links.new(opacity_node.outputs[0], mix_node.inputs[0])
            
            # Connect the output from the opacity node to the 2nd input of the alpha add node
            links.new(opacity_node.outputs[0], alpha_add_node.inputs[1])
            
            # Connect the output from the tint node to the 2nd color of the texture mix node
            links.new(tint_node.outputs['Result'], mix_node.inputs['B'])
            
            skin_node = nodes.get("TEX-SkinTexture")
            output_node = nodes.get("NDE-MaterialOutput")
            use_skin_node = nodes.get("NDE-UseSkin")
            base_alpha_mix_node = nodes.get("NDE-BaseAlphaMix")
            mask_ramp_node = nodes.get("NDE-MaskRamp")
            
            injury_overlay_node = nodes.get("NDE-OverlayBodyInjuries")
            
            # If this is not the first entry in the list, connect the output from the previous iteration to the 1st color of the tex mix node
            if node_index > 0:
                if nodes.get("NDE-DecalMixSlot" + str(node_index - 1)) is not None:
                    prev_output = nodes.get("NDE-DecalMixSlot" + str(node_index - 1))
                    links.new(prev_output.outputs['Result'], mix_node.inputs['A'])
                else:    
                    prev_output = nodes.get("NDE-TexMix" + str(node_index - 1))
                    links.new(prev_output.outputs['Result'], mix_node.inputs['A'])
                
                prev_alpha_add = nodes.get("NDE-AlphaAdd" + str(node_index - 1))
                links.new(prev_alpha_add.outputs['Value'], alpha_add_node.inputs[0])
            elif prop.use_skin_textures and node_index == 0:
                links.new(injury_overlay_node.outputs['Result'], mix_node.inputs['A'])  
                links.new(skin_node.outputs['Alpha'], alpha_add_node.inputs[0]) 

            # If this is the last entry in the list, connect it to the blood mix node
            if node_index == len(tex_prop_list) - 1:
                links.new(mix_node.outputs['Result'], blood_mix_node.inputs['A'])
                links.new(alpha_add_node.outputs['Value'], base_alpha_mix_node.inputs['Factor'])
            
            #------------------#
            
            i = node_index
            
            slot_offset = 1200 * (i)
            
            skin_node.location = (-1000.0, 0.0)
            
            use_skin_node.location = (-600.0, -150.0)
            
            injury_node.location = (-650.0, -400.0)
            
            injury_overlay_node.location = (-200, -150.0)
            
            tex_node.location = (200 + slot_offset, -250.0)
            
            opacity_node.location = (500 + slot_offset, 100.0)
            
            tint_node.location = (500 + slot_offset, -200.0)
            
            mix_node.location = (750 + slot_offset, 0.0)
            
            alpha_add_node.location = (750 + slot_offset, 250.0)
            
            mask_ramp_node.location = (1200 + slot_offset, -800)
            
            base_alpha_mix_node.location = (1500 + slot_offset, -600)
            
            emission_node.location = (1900 + slot_offset, 200.0)
            
            transparent_node.location = (1900 + slot_offset, 300.0)
            
            emission_alpha_node.location = (2200 + slot_offset, 200.0)
            
            pbr_node.location = (2100 + slot_offset, -200.0)
            
            mix_shader_node.location = (2400 + slot_offset, 0.0)
            
            output_node.location = (2600 + slot_offset, 0.0)
            
            #------------------#
            
            ## DECALS ##
            if tex_prop.decal_group != 'None':
                for node in nodes:
                    node.select = False
                
                decals = context.scene.pz_human_decals
                decal = decals[randint(0, len(decals)) - 1]
                
                decal_path = decal.texture_path
                if sys.platform == 'win32':
                    decal_path = decal_path.replace('\\', '\\\\')
                elif sys.platform == 'linux':
                    decal_path = decal_path.replace('\\', '/')
                
                target = textures_dir + decal_path + '.png'
                
                # Create the texture node for the decal texture
                decal_tex_node = nodes.new(type='ShaderNodeTexImage')
                decal_tex_node.name = "NDE-DecalTexSlot" + str(node_index)
                decal_tex_node.select = True
                
                # Create the texture coordinates node for the decal texture
                decal_coordinates_node = nodes.new(type='ShaderNodeTexCoord')
                decal_coordinates_node.name = "NDE-DecalCoordinatesSlot" + str(node_index)
                decal_coordinates_node.select = True
                
                # Create the texture mapping node for the decal texture
                decal_mapping_node = nodes.new(type='ShaderNodeMapping')
                decal_mapping_node.name = "NDE-DecalMappingSlot" + str(node_index)
                decal_mapping_node.select = True
                
                # Create the decal mix node for the decal texture
                decal_mix_node = nodes.new(type='ShaderNodeMix')
                decal_mix_node.name = "NDE-DecalMixSlot" + str(node_index)
                decal_mix_node.select = True
                
                ### Set the decal texture node properties ###
                decal_tex_node.image = bpy.data.images.load(target)
                decal_tex_node.extension = 'CLIP'
                
                # Interpolation Driver 
                path = 'nodes["NDE-DecalTexSlot' + str(node_index) +'"].interpolation'
                fcurve = mat.node_tree.driver_add(path)
                driver = fcurve.driver
                driver.type = 'AVERAGE'
                
                var = driver.variables.new()
                target = var.targets[0]
                target.id = context.active_object
                target.data_path = "pz_human_props.texture_interpolation_index"
                
                ### Set the decal mapping node properties ###
                decal_mapping_node.vector_type = 'TEXTURE'
                
                decal_mapping_node.inputs[1].default_value[0] = 0.43
                decal_mapping_node.inputs[1].default_value[1] = 0.52
                
                decal_mapping_node.inputs[3].default_value[0] = 0.15
                decal_mapping_node.inputs[3].default_value[1] = 0.15
                
                ### Set the decal mix node properties ###
                decal_mix_node.data_type = 'RGBA'
                
                # Connect the UV output from the coordinates node to the vector input of the mapping node
                links.new(decal_coordinates_node.outputs['UV'], decal_mapping_node.inputs['Vector'])
                
                # Connect the vector output from the mapping node to the vector input of the texture node
                links.new(decal_mapping_node.outputs['Vector'], decal_tex_node.inputs['Vector'])
                
                # Connect the output from the shirt texture to the first input of the mix node
                links.new(mix_node.outputs['Result'], decal_mix_node.inputs['A'])
                
                # Connect the output from the decal texture to the respective inputs of the mix node
                links.new(decal_tex_node.outputs['Color'], decal_mix_node.inputs['B'])
                links.new(decal_tex_node.outputs['Alpha'], decal_mix_node.inputs['Factor'])
                
                # If this is the last entry in the list, connect it to the blood mix node
                if node_index == len(tex_prop_list) - 1:
                    links.new(decal_mix_node.outputs['Result'], blood_mix_node.inputs['A'])
                
                #------------------#
                
                decal_coordinates_node.location.x = tex_node.location.x 
                decal_coordinates_node.location.y = tex_node.location.y - 400.0
                
                decal_mapping_node.location.x = tint_node.location.x - 100.0
                decal_mapping_node.location.y = tint_node.location.y - 450.0

                decal_tex_node.location.x  = mix_node.location.x  - 150.0
                decal_tex_node.location.y = mix_node.location.y - 700.0
                
                decal_mix_node.location.x = mix_node.location.x + 200.0
                decal_mix_node.location.y = mix_node.location.y
                
                #------------------#
                
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a texture file at the path: " + target)
            return({'CANCELLED'})
    
    #-------------------------------------------------------------#
    # Skin with no additional textures
    
    def construct_default_skin(self, context):
        prop = context.active_object.pz_human_props

        mat = prop.body_mat
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        emission_node = nodes.get("NDE-EmissionShader")
        pbr_node = nodes.get("NDE-PBRShader")
        skin_node = nodes.get("TEX-SkinTexture")
        use_skin_node = nodes.get("NDE-UseSkin")
        base_alpha_mix_node = nodes.get("NDE-BaseAlphaMix")
        injury_overlay_node = nodes.get("NDE-OverlayBodyInjuries")
        blood_mix_node = nodes.get("NDE-BloodMix")
        dirt_mix_node = nodes.get("NDE-DirtMix")
        
        links.new(skin_node.outputs['Alpha'], base_alpha_mix_node.inputs['Factor'])
        links.new(injury_overlay_node.outputs['Result'], blood_mix_node.inputs['A'])
        links.new(dirt_mix_node.outputs['Result'], emission_node.inputs['Color'])
        links.new(dirt_mix_node.outputs['Result'], pbr_node.inputs['Base Color'])
        
        return({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Execute
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        tex_prop_list = context.active_object.pz_human_body_texture_slots
        
        mat = prop.body_mat
        nodes = mat.node_tree.nodes
        
        for node in nodes:
            if node.get('protected') is None or node.get('protected') == False:
                if node.type == 'TEX_IMAGE' and node.image:
                    image_to_delete = node.image
                    bpy.data.images.remove(image_to_delete)
                nodes.remove(node)
        
        if len(tex_prop_list) == 0:
            self.construct_default_skin(context)
        else:
            for i, tex_prop in enumerate(tex_prop_list):
                self.reconstruct_body_tex_node(context, tex_prop.texture_path, i)
        
        return({'FINISHED'})

# ============================================================================================
# CREATE BODY INJURY TEXTURE
# ============================================================================================

class PZ_HumanRig_CreateBodyInjuryTexture(Operator):
    bl_idname = "zomboid.create_body_injury_texture"
    bl_label = "Create Body Injury Texture"
    bl_description = "Create a combined injury image from the injury textures"
    
    injury_textures = []
    
    def get_injury_textures(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        
        self.injury_textures.clear()
        
        textures_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\BodyDmg\\'
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/BodyDmg/'
        
        injury_props = [prop.upper_torso_injury, prop.lower_torso_injury, prop.left_hand_injury,
                        prop.right_hand_injury, prop.left_forearm_injury, prop.right_forearm_injury,
                        prop.left_upperarm_injury, prop.right_upperarm_injury, prop.head_injury,
                        prop.neck_injury, prop.groin_injury, prop.left_thigh_injury, 
                        prop.right_thigh_injury, prop.left_shin_injury, prop.right_shin_injury,
                        prop.left_foot_injury, prop.right_foot_injury]
        
        body_part_dict = {
            0 : 'chest',
            1 : 'abdomen',
            2 : 'left_hand',
            3 : 'right_hand',
            4 : 'lower_left_arm',
            5 : 'lower_right_arm',
            6 : 'upper_left_arm',
            7 : 'upper_right_arm',
            8 : 'head',
            9 : 'neck',
            10 : 'groin',
            11 : 'left_thigh',
            12 : 'right_thigh',
            13 : 'left_calf',
            14 : 'right_calf',
            15 : 'left_foot',
            16 : 'right_foot'
        }
        
        injury_dict = {
            'SCRATCH' : 'scratches',
            'LACERATION' : 'lacerations',
            'BITE' : 'bites',
            'BANDAGE' : 'bandages',
            'BANDAGEBLOODY' : 'bandages'
        }
        
        sex_dict = {
            'MALE' : 'MaleBody01',
            'FEMALE' : 'FemaleBody01'
        }
        
        index = 0
        for injury in injury_props:
            if injury != 'NONE':
                if injury in ('BANDAGE', 'BANDAGEBLOODY'):
                    tex_name = 'MaleBody01' + '_' + injury_dict[injury] + '_' + body_part_dict[index]
                else:
                    tex_name = sex_dict[prop.model_sex] + '_' + injury_dict[injury] + '_' + body_part_dict[index]
                if injury == 'BANDAGEBLOODY':
                    tex_name = tex_name + '_blood'
                tex_name = textures_dir + tex_name +'.png'
                self.injury_textures.append(tex_name)
            index = index + 1
        
        for injury in context.active_object.pz_human_zombie_injuries:
            tex_name = textures_dir + injury.texture_path.split('\\')[1] + '.png'
            tex_name = bpy.path.resolve_ncase(tex_name)
            self.injury_textures.append(tex_name)

        return ({'FINISHED'})
    
    def generate_injury_texture(self, context):
        prop = context.active_object.pz_human_props

        instance_str = ' (' + str(prop.rig_instance) + ')'
        generated_image = bpy.data.images.get('TEX-BodyInjuries' + instance_str)
        if generated_image is None:
            generated_image = bpy.data.images.new(name='TEX-BodyInjuries' + instance_str, width=256, height=256, alpha=True)
            
        num_pixels = generated_image.size[0] * generated_image.size[1]
        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        
        for tex_path in self.injury_textures:
            injury_texture = bpy.data.images.load(tex_path)
            injury_texture.scale(256, 256)
            injury_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            injury_texture.pixels.foreach_get(injury_pixels)
            
            generated_rgba = generated_pixels.reshape(-1, 4)
            injury_rgba = injury_pixels.reshape(-1, 4)
            
            injury_alpha = injury_rgba[:, 3:4]
            generated_alpha = generated_rgba[:, 3:4]
            
            alpha = generated_alpha + injury_alpha * (1.0 - generated_alpha)
            rgb = (injury_rgba[:, :3] * injury_alpha + generated_rgba[:, :3] * generated_alpha * (1.0 - injury_alpha))
            
            generated_pixels = np.hstack((rgb, alpha)).flatten()
            
            injury_texture.user_clear()
            bpy.data.images.remove(injury_texture)       
        
        generated_image.pixels.foreach_set(generated_pixels)      
        generated_image.update()
        
        return ({'FINISHED'})
    
    def execute(self, context):
        global_prop = context.scene.pz_human_global_props

        if global_prop.pz_directory != '':
            self.get_injury_textures(context)
            self.generate_injury_texture(context)
            return ({'FINISHED'})
        else:
            return({'CANCELLED'})

# ============================================================================================
# CREATE BODY BLOODINESS MASK
# ============================================================================================

class PZ_HumanRig_CreateBodyBloodinessTexture(Operator):

    '''
    This operator will draw the full bloodiness mask texture that combines all of 
    the body part health location masks at a specified intensity from 0.0 to 5.0 for each.
    It draws it to each rig's specific MaskData texture on the green channel using
    Numpy for fast evaluation.
    '''

    bl_idname = "zomboid.create_body_bloodiness_texture"
    bl_label = "Create Body Bloodiness Texture"
    bl_description = "Create a combined blood image from the blood textures"
    
    blood_textures = []
    
    def get_blood_textures(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        
        self.blood_textures.clear()
        
        textures_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\BloodTextures\\'
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/BloodTextures/'
        
        blood_props =  [prop.upper_torso_bloodiness, prop.lower_torso_bloodiness, prop.left_hand_bloodiness,
                        prop.right_hand_bloodiness, prop.left_forearm_bloodiness, prop.right_forearm_bloodiness,
                        prop.left_upperarm_bloodiness, prop.right_upperarm_bloodiness, prop.head_bloodiness,
                        prop.neck_bloodiness, prop.groin_bloodiness, prop.left_thigh_bloodiness, 
                        prop.right_thigh_bloodiness, prop.left_shin_bloodiness, prop.right_shin_bloodiness,
                        prop.left_foot_bloodiness, prop.right_foot_bloodiness, prop.back_bloodiness]
        
        body_part_dict = {
            0 : 'Chest',
            1 : 'Stomach',
            2 : 'HandL',
            3 : 'HandR',
            4 : 'LArmL',
            5 : 'LArmR',
            6 : 'UArmL',
            7 : 'UArmR',
            8 : 'Head',
            9 : 'Neck',
            10 : 'Groin',
            11 : 'ULegL',
            12 : 'ULegR',
            13 : 'LLegL',
            14 : 'LLegR',
            15 : 'FootL',
            16 : 'FootR',
            17 : 'Back'
        }
        
        index = 0
        for blood in blood_props:
            if blood != 0:
                tex_name = 'BloodMask' + body_part_dict[index]
                tex_name = textures_dir + tex_name + '.png'
                self.blood_textures.append((tex_name, blood))
            index = index + 1
        
        return ({'FINISHED'})
    
    def generate_bloodiness_texture(self, context):
        
        prop = context.active_object.pz_human_props

        generated_image = bpy.data.images.get('MASK-MaskData (' + str(prop.rig_instance) +')')
        if generated_image is None:
            generated_image = bpy.data.images.new(name='MASK-MaskData (' + str(prop.rig_instance) +')', width=256, height=256, alpha=True)

        num_pixels = generated_image.size[0] * generated_image.size[1]

        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the red channel
        generated_pixels[0::4] = 0.0

        for tex_path in self.blood_textures:
            blood_texture = bpy.data.images.load(tex_path[0])
            blood_texture.scale(256, 256)

            blood_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            blood_texture.pixels.foreach_get(blood_pixels)

            generated_rgba = generated_pixels.reshape(-1, 4)
            blood_rgba = blood_pixels.reshape(-1, 4)
            
            blood_red = blood_rgba[:, 0:1]
            blood_alpha = blood_rgba[:, 3:4] * tex_path[1]

            prev_red = generated_rgba[:, 0:1]
            prev_green = generated_rgba[:, 1:2]
            prev_blue = generated_rgba[:, 2:3]
            prev_alpha = generated_rgba[:, 3:4]
            
            new_red = prev_red + blood_red * blood_alpha * (1.0 - prev_alpha)
            
            generated_pixels = np.hstack((new_red, prev_green, prev_blue, prev_alpha)).flatten()
            
            blood_texture.user_clear()
            bpy.data.images.remove(blood_texture)       
        
        generated_image.pixels.foreach_set(generated_pixels)      
        generated_image.update()

        return ({'FINISHED'})
    
    def execute(self, context):
        global_prop = context.scene.pz_human_global_props

        if global_prop.pz_directory != '':
            self.get_blood_textures(context)
            self.generate_bloodiness_texture(context)
            return ({'FINISHED'})
        else:
            return({'CANCELLED'})

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
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        
        self.dirt_textures.clear()
        
        textures_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\BloodTextures\\'
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/BloodTextures/'
        
        dirt_props = [prop.upper_torso_dirtiness, prop.lower_torso_dirtiness, prop.left_hand_dirtiness,
                        prop.right_hand_dirtiness, prop.left_forearm_dirtiness, prop.right_forearm_dirtiness,
                        prop.left_upperarm_dirtiness, prop.right_upperarm_dirtiness, prop.head_dirtiness,
                        prop.neck_dirtiness, prop.groin_dirtiness, prop.left_thigh_dirtiness, 
                        prop.right_thigh_dirtiness, prop.left_shin_dirtiness, prop.right_shin_dirtiness,
                        prop.left_foot_dirtiness, prop.right_foot_dirtiness, prop.back_dirtiness]
        
        body_part_dict = {
            0 : 'Chest',
            1 : 'Stomach',
            2 : 'HandL',
            3 : 'HandR',
            4 : 'LArmL',
            5 : 'LArmR',
            6 : 'UArmL',
            7 : 'UArmR',
            8 : 'Head',
            9 : 'Neck',
            10 : 'Groin',
            11 : 'ULegL',
            12 : 'ULegR',
            13 : 'LLegL',
            14 : 'LLegR',
            15 : 'FootL',
            16 : 'FootR',
            17 : 'Back'
        }
        
        index = 0
        for dirt in dirt_props:
            if dirt != 0:
                tex_name = 'BloodMask' + body_part_dict[index]
                tex_name = textures_dir + tex_name + '.png'
                self.dirt_textures.append((tex_name, dirt))
            index = index + 1
        
        return ({'FINISHED'})
    
    def generate_dirtiness_texture(self, context):
        
        prop = context.active_object.pz_human_props

        generated_image = bpy.data.images.get('MASK-MaskData (' + str(prop.rig_instance) +')')
        if generated_image is None:
            generated_image = bpy.data.images.new(name='MASK-MaskData (' + str(prop.rig_instance) +')', width=256, height=256, alpha=True)

        num_pixels = generated_image.size[0] * generated_image.size[1]
        
        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the green channel
        generated_pixels[1::4] = 0.0

        for tex_path in self.dirt_textures:
            dirt_texture = bpy.data.images.load(tex_path[0])
            dirt_texture.scale(256, 256)

            dirt_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            dirt_texture.pixels.foreach_get(dirt_pixels)

            generated_rgba = generated_pixels.reshape(-1, 4)
            dirt_rgba = dirt_pixels.reshape(-1, 4)
            
            dirt_green = dirt_rgba[:, 0:1]
            dirt_alpha = dirt_rgba[:, 3:4] * tex_path[1]

            prev_red = generated_rgba[:, 0:1]
            prev_green = generated_rgba[:, 1:2]
            prev_blue = generated_rgba[:, 2:3]
            prev_alpha = generated_rgba[:, 3:4]
            
            new_green = prev_green + dirt_green * dirt_alpha * (1.0 - prev_alpha)
            
            generated_pixels = np.hstack((prev_red, new_green, prev_blue, prev_alpha)).flatten()
            
            dirt_texture.user_clear()
            bpy.data.images.remove(dirt_texture)       
        
        generated_image.pixels.foreach_set(generated_pixels)      
        generated_image.update()
        
        return ({'FINISHED'})
    
    def execute(self, context):
        global_prop = context.scene.pz_human_global_props

        if global_prop.pz_directory != '':
            self.get_dirt_textures(context)
            self.generate_dirtiness_texture(context)
            return ({'FINISHED'})
        else:
            return({'CANCELLED'})

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
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props

        self.mask_textures.clear()
        
        textures_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\Body\\Masks\\'
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/Body/Masks/'

        mask_dict = {
        0 : "Head",
        1 : "Chest",
        2 : "Crotch",
        3 : "LeftArm",
        4 : "LeftHand",
        5 : "RightArm",
        6 : "RightHand",
        7 : "LeftLeg",
        8 : "LeftFoot",
        9 : "RightLeg",
        10 : "RightFoot",
        11 : "Dress",
        12 : "Chest",
        13 : "Waist",
        14 : "Belt",
        15 : "Crotch",
        16 : "Mask"
        }

        index = 0
        for hide in prop.mask_array:
            if hide:
                tex_name = textures_dir + mask_dict[index] + '.png' 
                self.mask_textures.append(tex_name)
            index = index + 1

        return ({'FINISHED'})

    def generate_mask_texture(self, context):
        prop = context.active_object.pz_human_props

        generated_image = bpy.data.images.get('MASK-MaskData (' + str(prop.rig_instance) +')')
        if generated_image is None:
            generated_image = bpy.data.images.new(name='MASK-MaskData (' + str(prop.rig_instance) +')', width=256, height=256, alpha=True)

        num_pixels = generated_image.size[0] * generated_image.size[1]
        
        generated_pixels = np.zeros(num_pixels * 4, dtype=np.float32)
        generated_image.pixels.foreach_get(generated_pixels)

        generated_image.source = 'GENERATED'

        # Clear the green channel
        generated_pixels[2::4] = 0.0

        for tex_path in self.mask_textures:
            mask_texture = bpy.data.images.load(tex_path)
            mask_texture.scale(256, 256)

            mask_pixels = np.empty(num_pixels * 4, dtype=np.float32)
            mask_texture.pixels.foreach_get(mask_pixels)

            generated_rgba = generated_pixels.reshape(-1, 4)
            mask_rgba = mask_pixels.reshape(-1, 4)
            
            mask_blue = mask_rgba[:, 1:2] + mask_rgba[:, 0:1] + mask_rgba[:, 2:3]
            mask_alpha = mask_rgba[:, 3:4]

            prev_red = generated_rgba[:, 0:1]
            prev_green = generated_rgba[:, 1:2]
            prev_blue = generated_rgba[:, 2:3]
            prev_alpha = generated_rgba[:, 3:4]
            
            new_blue = prev_blue + mask_blue * mask_alpha * (1.0 - prev_alpha)
            
            generated_pixels = np.hstack((prev_red, prev_green, new_blue, prev_alpha)).flatten()
            
            mask_texture.user_clear()
            bpy.data.images.remove(mask_texture)       
        
        generated_image.pixels.foreach_set(generated_pixels)      
        generated_image.update()
        
        return ({'FINISHED'})

    def execute(self, context):
        global_prop = context.scene.pz_human_global_props

        if global_prop.pz_directory != '':
            self.get_mask_textures(context)
            self.generate_mask_texture(context)
            return ({'FINISHED'})
        else:
            return({'CANCELLED'})

# endregion

# region List Operators

# ============================================================================================
# LIST OPERATIONS
# ============================================================================================

#-------------------------------------------------------------#
# Mod Directory Slot List Operations

class PZ_HumanRig_AddModDirectorySlot(Operator):
    bl_idname = "zomboid.add_mod_directory_slot"
    bl_label = "Add Mod Directory Mesh Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_mod_directory_slots",
            active_index_path = "scene.pz_human_global_props.mod_directory_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveModDirectorySlot(Operator):
    bl_idname = "zomboid.remove_mod_directory_slot"
    bl_label = "Remove Mod Directory Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_mod_directory_slots",
            active_index_path = "scene.pz_human_global_props.mod_directory_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Body Texture Slot List Operations

class PZ_HumanRig_AddBodyTextureSlot(Operator):
    bl_idname = "zomboid.add_body_texture_slot"
    bl_label = "Add Texture Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path = "active_object.pz_human_props.body_texture_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveBodyTextureSlot(Operator):
    bl_idname = "zomboid.remove_body_texture_slot"
    bl_label = "Remove Texture Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path = "active_object.pz_human_props.body_texture_slot_active_index"
        )
        
        bpy.ops.zomboid.construct_body_texture()
        
        return ({'FINISHED'})

class PZ_HumanRig_MoveBodyTextureSlotUp(Operator):
    bl_idname = "zomboid.move_body_texture_slot_up"
    bl_label = "Move Texture Slot Up"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_move(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path = "active_object.pz_human_props.body_texture_slot_active_index",
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
            active_index_path = "active_object.pz_human_props.body_texture_slot_active_index",
            direction='DOWN'
        )
        
        bpy.ops.zomboid.construct_body_texture()
        
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Clothing Mesh Slot List Operations

class PZ_HumanRig_AddClothingMeshSlot(Operator):
    bl_idname = "zomboid.add_clothing_mesh_slot"
    bl_label = "Add Clothing Mesh Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_clothing_mesh_slots",
            active_index_path = "active_object.pz_human_props.clothing_mesh_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveClothingMeshSlot(Operator):
    bl_idname = "zomboid.remove_clothing_mesh_slot"
    bl_label = "Remove Clothing Mesh Slot"
    
    def execute(self, context):

        bpy.ops.zomboid.remove_clothing_mesh()
        
        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_clothing_mesh_slots",
            active_index_path = "active_object.pz_human_props.clothing_mesh_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Prop Mesh Slot List Operations

class PZ_HumanRig_AddPropMeshSlot(Operator):
    bl_idname = "zomboid.add_prop_mesh_slot"
    bl_label = "Add Prop Mesh Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="active_object.pz_human_prop_mesh_slots",
            active_index_path = "active_object.pz_human_props.prop_mesh_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemovePropMeshSlot(Operator):
    bl_idname = "zomboid.remove_prop_mesh_slot"
    bl_label = "Remove Prop Mesh Slot"
    
    def execute(self, context):

        bpy.ops.zomboid.remove_prop_mesh()
        
        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_prop_mesh_slots",
            active_index_path = "active_object.pz_human_props.prop_mesh_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Clothing Item Slot List Operations

class PZ_HumanRig_AddClothingItemSlot(Operator):
    bl_idname = "zomboid.add_clothing_item_slot"
    bl_label = "Add Clothing Item Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_clothing_item_slots",
            active_index_path = "scene.pz_human_global_props.clothing_item_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveClothingItemSlot(Operator):
    bl_idname = "zomboid.remove_clothing_item_slot"
    bl_label = "Remove Clothing Item Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_clothing_item_slots",
            active_index_path = "scene.pz_human_global_props.clothing_item_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Outfit Slot List Operations

class PZ_HumanRig_AddOutfitSlot(Operator):
    bl_idname = "zomboid.add_outfit_slot"
    bl_label = "Add Outfit Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_outfit_slots",
            active_index_path = "scene.pz_human_global_props.outfit_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveOutfitSlot(Operator):
    bl_idname = "zomboid.remove_outfit_slot"
    bl_label = "Remove Outfit Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_outfit_slots",
            active_index_path = "scene.pz_human_global_props.outfit_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Hair Style Slot List Operations

class PZ_HumanRig_AddHairStyleSlot(Operator):
    bl_idname = "zomboid.add_hair_style_slot"
    bl_label = "Add Hair Style Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_hair_style_slots",
            active_index_path = "scene.pz_human_global_props.hair_style_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveHairStyleSlot(Operator):
    bl_idname = "zomboid.remove_hair_style_slot"
    bl_label = "Remove Hair Style Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_hair_style_slots",
            active_index_path = "scene.pz_human_global_props.hair_style_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Beard Style Slot List Operations

class PZ_HumanRig_AddBeardStyleSlot(Operator):
    bl_idname = "zomboid.add_beard_style_slot"
    bl_label = "Add Beard Style Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_add(
            list_path="scene.pz_human_beard_styles",
            active_index_path = "scene.pz_human_global_props.beard_style_slot_active_index"
        )
        
        return ({'FINISHED'})
    
class PZ_HumanRig_RemoveBeardStyleSlot(Operator):
    bl_idname = "zomboid.remove_beard_style_slot"
    bl_label = "Remove Beard Style Slot"
    
    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="scene.pz_human_beard_styles",
            active_index_path = "scene.pz_human_global_props.beard_style_slot_active_index"
        )
            
        return ({'FINISHED'})

#-------------------------------------------------------------#
# Zombie Injury List Operations

class PZ_HumanRig_RemoveZombieInjury(Operator):
    bl_idname = "zomboid.remove_zombie_injury"
    bl_label = "Remove Zombie Injury"

    def execute(self, context):
        
        bpy.ops.uilist.entry_remove(
            list_path="object.pz_human_zombie_injuries",
            active_index_path = "object.pz_human_props.zombie_injury_active_index"
        )
        
        bpy.ops.zomboid.create_body_injury_texture()

        return ({'FINISHED'})

# endregion

# region Import Operators

# ============================================================================================
# CLOTHING MESH IMPORTER
# ============================================================================================

class PZ_ImportClothingMesh(Operator):
    bl_idname = "zomboid.import_clothing_mesh"
    bl_label = "Import Clothing Mesh"
    
    #-------------------------------------------------------------#
    # Create Clothing Material
    
    def create_clothing_material(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]

        textures_dir = ''
        tex_path = mesh_prop.texture_path
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\'
            tex_path = tex_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/'
            tex_path = tex_path.replace('\\', '/')
        
        instance_str = ' ( ' + prop.rig_instance + ')'

        # Construct the name of the target file
        target = textures_dir + tex_path + ".png"
        target = bpy.path.resolve_ncase(target)
        
        old_mat = bpy.data.materials.get('MAT-ClothingMaterial' + str(prop.clothing_mesh_slot_active_index) + instance_str)
        if old_mat:
            bpy.data.materials.remove(old_mat, do_unlink=True)
        
        if Path(target).is_file():
            mat = bpy.data.materials.new(name='MAT-ClothingMaterial' + str(prop.clothing_mesh_slot_active_index) + instance_str)
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Get the texture node, or create it if it does not exist
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.name = "NDE-TexSlot"
            tex_node.select = True
            
            # Get the color tint node, or create it if it does not exist
            tint_node = nodes.new(type='ShaderNodeMix')
            tint_node.name = "NDE-TexTint"
            tint_node.select = True
            
            # Create a frame node and group all these nodes inside of it
            frame_node = nodes.get("NDE-GroupFrame")
            if frame_node is None:
                frame_node = nodes.new(type='NodeFrame')
                frame_node.name = "NDE-GroupFrame"
                frame_node.label = str(target)
            
            for node in nodes:
                if node.select and node != frame_node:
                    node.parent = frame_node
            
            # Get the emission shader node
            emission_node = nodes.new(type='ShaderNodeEmission')
            emission_node.name = "NDE-EmissionShader"
            
            # Get the PBR shader node
            pbr_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            pbr_node.name = "NDE-PBRShader"
            
            # Get the mix shader node
            mix_shader_node = nodes.new(type='ShaderNodeMixShader')
            mix_shader_node.name = "NDE-MixShader"
            
            output_node = nodes.get("Material Output")
            
            #------------------#
            
            ### Set the texture node properties ###
            tex_node.image = bpy.data.images.load(str(target))
            
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
            c = mesh_prop.tint_color
            
            tint_node.data_type = 'RGBA'
            tint_node.blend_type = 'MULTIPLY'
            
            # Factor Driver
            path = 'nodes["NDE-TexTint"].inputs[0].default_value'
            fcurve = mat.node_tree.driver_add(path)
            driver = fcurve.driver
            driver.type = 'AVERAGE'
            
            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_human_clothing_mesh_slots[" + str(prop.clothing_mesh_slot_active_index) + "].tintable"
            
            # Color Drivers
            
            for i in range(3):
                path = 'nodes["NDE-TexTint"].inputs[7].default_value'
                fcurve = mat.node_tree.driver_add(path, i)
                driver = fcurve.driver
                driver.type = 'AVERAGE'
                
                var = driver.variables.new()
                target = var.targets[0]
                target.id = context.active_object
                target.data_path = "pz_human_clothing_mesh_slots[" + str(prop.clothing_mesh_slot_active_index) + "].tint_color[" + str(i) + "]"
            
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
            
            #------------------#
            
            # Connect the color from the texture node to the 1st color in the tint node
            links.new(tex_node.outputs['Color'], tint_node.inputs['A'])
            
            # Connect the output from the tint node to the shader nodes
            links.new(tint_node.outputs['Result'], emission_node.inputs['Color'])
            links.new(tint_node.outputs['Result'], pbr_node.inputs['Base Color'])
            
            # Connect the outputs from the tint node to the mix shader nodes
            links.new(emission_node.outputs['Emission'], mix_shader_node.inputs[1])
            links.new(pbr_node.outputs['BSDF'], mix_shader_node.inputs[2])
            
            # Connect the output from the emission node to the material output
            links.new(mix_shader_node.outputs['Shader'], output_node.inputs['Surface'])
            
            #------------------#
            
            tex_node.location = (0.0, 0.0)
            
            tint_node.location = (200.0, 0.0)
            
            emission_node.location = (400.0, 0.0)
            
            output_node.location = (600.0, 0.0)
            
            #------------------#
            
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a texture file named " + target)
            return({'CANCELLED'})
            
    #-------------------------------------------------------------#
    # Import Male Model
    
    def import_male_model(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        models_dir = ''
        model_path = mesh_prop.male_model_path
        
        # Construct the filepath to the 'models_X/Skinned' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            models_dir = global_prop.pz_directory
            model_path = model_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            models_dir = global_prop.pz_directory + 'projectzomboid/'
            model_path = model_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = models_dir + model_path

        match mesh_prop.model_type:
            case 'X':
                target = target + '.x'
            case 'FBX':
                target = target + '.fbx'
            case 'GLB':
                target = target + '.glb'
        
        target = bpy.path.resolve_ncase(target)
        
        if Path(target).is_file():
                
            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            cols_before = set(bpy.data.collections)
            objs_before = set(bpy.context.scene.objects)
            
            match mesh_prop.model_type:
                case 'X':
                    if 'bl_ext.blender_org.io_directx_x' not in bpy.context.preferences.addons.keys():
                        self.report({"ERROR"}, "The .x importer is not enabled or installed")
                        return({'CANCELLED'})
                    
                    bpy.ops.import_scene.directx_x(
                        filepath = str(target),
                        import_textures = False,
                        import_materials = False,
                        import_armature = False
                    )
                    
                case 'FBX':
                    bpy.ops.import_scene.fbx(
                        filepath = str(target),
                        global_scale = 100.0
                    )
                case 'GLB':
                    pass
            
            cols_after = set(bpy.data.collections)
            objs_after = set(bpy.context.scene.objects)
            
            imported_objects = list(objs_after - objs_before)
            imported_collections = list(cols_before - cols_after)
            
            for col in imported_collections:
                pass
            
            male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Clothes' + instance_str)
            
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
                    old_obj = bpy.data.objects.get('OBJ-MaleClothingMesh' + str(prop.clothing_mesh_slot_active_index))
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)
                    
                    #-------------------------
                    
                    # Fix for incorrectly assigned hats that have off rotations
                    if 'WeddingVeil' in obj.name:
                        obj.rotation_euler[0] += math.radians(2)
                    
                    #-------------------------
                    
                    obj.name = 'OBJ-MaleClothingMesh' + str(prop.clothing_mesh_slot_active_index)
                    
                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)
                    
                    if obj.name not in male_collection.objects:
                        male_collection.objects.link(obj)
                       
                    match mesh_prop.model_type:
                        case 'X':
                            obj.rotation_euler[2] += math.pi
                            obj.scale[0] = -1
                            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                        case 'FBX':
                            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                            obj.rotation_euler[0] = -math.pi / 2
                        case 'GLB':
                            pass
                    
                    obj.modifiers.clear()
                    
                    arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                    arm_mod.object = bpy.data.objects.get('Bip01')
                    
                    obj.active_material = bpy.data.materials.get('MAT-ClothingMaterial' + str(prop.clothing_mesh_slot_active_index))
                    
                    obj["sex"] = 0
                    obj.hide_viewport = obj['sex'] != prop.model_sex_index
                    obj.hide_render = obj['sex'] != prop.model_sex_index
                    
                #    obj.parent = bpy.data.objects.get('Bip01')
                        
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in prev_selected_objects:
                obj.select_set(True)
            if prev_active_object is not None:
                context.view_layer.objects.active = prev_active_object
                
            # Restore the context that was before the operation was called
            bpy.ops.object.mode_set(mode=prev_mode)
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a model file at the path: " + target)
            return({'CANCELLED'})
    
    #-------------------------------------------------------------#
    # Import Female Model
    
    def import_female_model(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        models_dir = ''
        model_path = mesh_prop.female_model_path
        
        # Construct the filepath to the 'models_X/Skinned' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            models_dir = global_prop.pz_directory
            model_path = model_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            models_dir = global_prop.pz_directory + 'projectzomboid/'
            model_path = model_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = models_dir + model_path
        
        match mesh_prop.model_type:
            case 'X':
                target = target + '.x'
            case 'FBX':
                target = target + '.fbx'
            case 'GLB':
                target = target + '.glb'
        
        target = bpy.path.resolve_ncase(target)
        
        if Path(target).is_file():
            
            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
        #    cols_before = set(bpy.context.scene.collections)
            objs_before = set(bpy.context.scene.objects)
            
            match mesh_prop.model_type:
                case 'X':
                    if 'bl_ext.blender_org.io_directx_x' not in bpy.context.preferences.addons.keys():
                        self.report({"ERROR"}, "The .x importer is not enabled or installed")
                        return({'CANCELLED'})
                    
                    bpy.ops.import_scene.directx_x(
                        filepath = str(target),
                        import_textures = False,
                        import_materials = False,
                        import_armature = False
                    )
                    
                case 'FBX':
                    bpy.ops.import_scene.fbx(
                        filepath = str(target),
                        global_scale = 100.0
                    )
                case 'GLB':
                    pass
            
            objs_after = set(bpy.context.scene.objects)
            
            imported_objects = list(objs_after - objs_before)
            
            female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Clothes' + instance_str)
            
            for obj in imported_objects:                
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':
                    
                    old_obj = bpy.data.objects.get('OBJ-FemaleClothingMesh' + str(prop.clothing_mesh_slot_active_index))
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)
                    
                    #-------------------------
                    
                    # Fix for incorrectly assigned hats that have off rotations
                    if 'WeddingVeil' in obj.name:
                        obj.rotation_euler[0] += math.radians(2)
                    
                    #-------------------------
                    
                    obj.name = 'OBJ-FemaleClothingMesh' + str(prop.clothing_mesh_slot_active_index)
                    
                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)
                    
                    if obj.name not in female_collection.objects:
                        female_collection.objects.link(obj)
                    
                    match mesh_prop.model_type:
                        case 'X':
                            obj.rotation_euler[2] += math.pi
                            obj.scale[0] = -1
                            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                        case 'FBX':
                            bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                            obj.rotation_euler[0] = -math.pi / 2
                        case 'GLB':
                            pass
                    
                    obj.modifiers.clear()
                    
                    arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                    arm_mod.object = bpy.data.objects.get('Bip01')
                    
                    obj.active_material = bpy.data.materials.get('MAT-ClothingMaterial' + str(prop.clothing_mesh_slot_active_index))
                    
                    obj["sex"] = 1
                    obj.hide_viewport = obj['sex'] != prop.model_sex_index
                    obj.hide_render = obj['sex'] != prop.model_sex_index
                    
                 #   obj.parent = bpy.data.objects.get('Bip01')
                        
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in prev_selected_objects:
                obj.select_set(True)
            if prev_active_object is not None:
                context.view_layer.objects.active = prev_active_object
                
            # Restore the context that was before the operation was called
            bpy.ops.object.mode_set(mode=prev_mode)
        
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a model file at the path: " + target)
            return({'CANCELLED'})
    
    #-------------------------------------------------------------#
    # Check Masks
    
    def check_masks(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]
        
        prop.halt_texture_updates = True
        
        for i in range(len(mesh_prop.mask_array)):
            if mesh_prop.mask_array[i] == True:
                prop.mask_array[i] = True
        
        prop.halt_texture_updates = False
        
        return({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Execute
    
    def execute(self, context):
        self.create_clothing_material(context)
        self.import_male_model(context)
        self.import_female_model(context)
        self.check_masks(context)
        return({'FINISHED'})

# ============================================================================================
# PROP MESH IMPORTER
# ============================================================================================

class PZ_ImportPropMesh(Operator):
    bl_idname = "zomboid.import_prop_mesh"
    bl_label = "Import Prop Mesh"
    
    #-------------------------------------------------------------#
    # Create Clothing Material
    
    def create_prop_material(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_prop_mesh_slots
        mesh_prop = mesh_prop_list[prop.prop_mesh_slot_active_index]
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        textures_dir = ''
        tex_path = mesh_prop.texture_path
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            textures_dir = global_prop.pz_directory + 'media\\textures\\'
            tex_path = tex_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            textures_dir = global_prop.pz_directory + 'projectzomboid/media/textures/'
            tex_path = tex_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = textures_dir + tex_path + ".png"
        target = bpy.path.resolve_ncase(target)
        
        old_mat = bpy.data.materials.get('MAT-PropMaterial' + str(prop.prop_mesh_slot_active_index) + instance_str)
        if old_mat:
            bpy.data.materials.remove(old_mat, do_unlink=True)
        
        if Path(target).is_file():
            mat = bpy.data.materials.new(name='MAT-PropMaterial' + str(prop.prop_mesh_slot_active_index) + instance_str)
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Get the texture node, or create it if it does not exist
            tex_node = nodes.new(type='ShaderNodeTexImage')
            tex_node.name = "NDE-TexSlot"
            tex_node.select = True
            
            # Get the color tint node, or create it if it does not exist
            tint_node = nodes.new(type='ShaderNodeMix')
            tint_node.name = "NDE-TexTint"
            tint_node.select = True
            
            # Create a frame node and group all these nodes inside of it
            frame_node = nodes.get("NDE-GroupFrame")
            if frame_node is None:
                frame_node = nodes.new(type='NodeFrame')
                frame_node.name = "NDE-GroupFrame"
                frame_node.label = str(target)
            
            for node in nodes:
                if node.select and node != frame_node:
                    node.parent = frame_node
            
            # Get the emission shader node
            emission_node = nodes.new(type='ShaderNodeEmission')
            emission_node.name = "NDE-EmissionShader"
            
            # Get the PBR shader node
            pbr_node = nodes.new(type='ShaderNodeBsdfPrincipled')
            pbr_node.name = "NDE-PBRShader"
            
            # Get the mix shader node
            mix_shader_node = nodes.new(type='ShaderNodeMixShader')
            mix_shader_node.name = "NDE-MixShader"
            
            output_node = nodes.get("Material Output")
            
            #------------------#
            
            ### Set the texture node properties ###
            tex_node.image = bpy.data.images.load(str(target))
            
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
            c = mesh_prop.tint_color
            
            tint_node.data_type = 'RGBA'
            tint_node.blend_type = 'MULTIPLY'
            
            # Factor Driver
            path = 'nodes["NDE-TexTint"].inputs[0].default_value'
            fcurve = mat.node_tree.driver_add(path)
            driver = fcurve.driver
            driver.type = 'AVERAGE'
            
            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_human_prop_mesh_slots[" + str(prop.prop_mesh_slot_active_index) + "].tintable"
            
            # Color Drivers
            
            for i in range(3):
                path = 'nodes["NDE-TexTint"].inputs[7].default_value'
                fcurve = mat.node_tree.driver_add(path, i)
                driver = fcurve.driver
                driver.type = 'AVERAGE'
                
                var = driver.variables.new()
                target = var.targets[0]
                target.id = context.active_object
                target.data_path = "pz_human_prop_mesh_slots[" + str(prop.prop_mesh_slot_active_index) + "].tint_color[" + str(i) + "]"
            
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
            
            #------------------#
            
            # Connect the color from the texture node to the 1st color in the tint node
            links.new(tex_node.outputs['Color'], tint_node.inputs['A'])
            
            # Connect the output from the tint node to the shader nodes
            links.new(tint_node.outputs['Result'], emission_node.inputs['Color'])
            links.new(tint_node.outputs['Result'], pbr_node.inputs['Base Color'])
            
            # Connect the outputs from the tint node to the mix shader nodes
            links.new(emission_node.outputs['Emission'], mix_shader_node.inputs[1])
            links.new(pbr_node.outputs['BSDF'], mix_shader_node.inputs[2])
            
            # Connect the output from the emission node to the material output
            links.new(mix_shader_node.outputs['Shader'], output_node.inputs['Surface'])
            
            #------------------#
            
            tex_node.location = (0.0, 0.0)
            
            tint_node.location = (200.0, 0.0)
            
            emission_node.location = (400.0, 0.0)
            
            output_node.location = (600.0, 0.0)
            
            #------------------#
            
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a texture file named " + target)
            return({'CANCELLED'})
        
    
        
    #-------------------------------------------------------------#
    # Import Male Model
    
    def import_male_model(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_prop_mesh_slots
        mesh_prop = mesh_prop_list[prop.prop_mesh_slot_active_index]
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        models_dir = ''
        model_path = mesh_prop.male_model_path
        
        # Construct the filepath to the 'models_X/Skinned' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            models_dir = global_prop.pz_directory
            model_path = model_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            models_dir = global_prop.pz_directory + 'projectzomboid/'
            model_path = model_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = models_dir + model_path

        match mesh_prop.model_type:
            case 'X':
                target = target + '.x'
            case 'FBX':
                target = target + '.fbx'
            case 'GLB':
                target = target + '.glb'
        
        target = bpy.path.resolve_ncase(target)
        
        if Path(target).is_file():
                
            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            objs_before = set(bpy.context.scene.objects)
            
            match mesh_prop.model_type:
                case 'X':
                    if 'bl_ext.blender_org.io_directx_x' not in bpy.context.preferences.addons.keys():
                        self.report({"ERROR"}, "The .x importer is not enabled or installed")
                        return({'CANCELLED'})
                    
                    bpy.ops.import_scene.directx_x(
                        filepath = str(target),
                        import_textures = False,
                        import_materials = False,
                        import_armature = False
                    )
                    
                case 'FBX':
                    bpy.ops.import_scene.fbx(
                        filepath = str(target),
                        global_scale = 100.0
                    )
                case 'GLB':
                    pass
            
            objs_after = set(bpy.context.scene.objects)
            
            imported_objects = list(objs_after - objs_before)
            
            male_collection = bpy.data.collections.get('GEO-PZ_Human_Male_Props' + instance_str)
            
            for obj in imported_objects:                
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':
                    
                    old_obj = bpy.data.objects.get('OBJ-MalePropMesh' + str(prop.prop_mesh_slot_active_index))
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)
                    
                    #-------------------------
                    
                    obj.name = 'OBJ-MalePropMesh' + str(prop.prop_mesh_slot_active_index)
                    
                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)
                    
                    if obj.name not in male_collection.objects:
                        male_collection.objects.link(obj)
                    
                    #-------------------------
                    
                    bip01 = bpy.data.objects.get('Bip01')
                    bone = bip01.pose.bones.get(mesh_prop.attach_bone)
                    
                    obj.parent = bip01
                    obj.parent_type = 'BONE'
                    obj.parent_bone = bone.name
                    
                    obj.matrix_parent_inverse = bone.matrix.inverted()
                    
                    bone_world_matrix = bip01.matrix_world @ bone.matrix
                    obj.matrix_world = bone_world_matrix
                    
                    match mesh_prop.model_type:
                        case 'X':
                            obj.rotation_euler[0] += math.pi
                            obj.scale *= 100
                            
                            # Wrist items are imported upside down and have off rotations, for some reason
                            if bone.name == 'Bip01_L_Forearm':
                                obj.scale[2] *= -1
                                obj.rotation_euler[1] += math.radians(3)
                            if bone.name == 'Bip01_R_Forearm':
                                obj.scale[2] *= -1
                                obj.rotation_euler[1] -= math.radians(3)
                        case 'FBX':
                            obj.rotation_euler[0] = -math.pi / 2
                        case 'GLB':
                            pass
                        
                    #-------------------------
                    
                    obj.modifiers.clear()
                    
                    obj.active_material = bpy.data.materials.get('MAT-PropMaterial' + str(prop.prop_mesh_slot_active_index))
                    
                    obj["sex"] = 0
                    obj.hide_viewport = obj['sex'] != prop.model_sex_index
                    obj.hide_render = obj['sex'] != prop.model_sex_index
                    
                        
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in prev_selected_objects:
                obj.select_set(True)
            if prev_active_object is not None:
                context.view_layer.objects.active = prev_active_object
                
            # Restore the context that was before the operation was called
            bpy.ops.object.mode_set(mode=prev_mode)
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a model file at the path: " + target)
            return({'CANCELLED'})
    
    #-------------------------------------------------------------#
    # Import Female Model
    
    def import_female_model(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        dir_list = context.scene.pz_human_mod_directory_slots
        mesh_prop_list = context.active_object.pz_human_prop_mesh_slots
        mesh_prop = mesh_prop_list[prop.prop_mesh_slot_active_index]
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        models_dir = ''
        model_path = mesh_prop.female_model_path
        
        # Construct the filepath to the 'models_X/Skinned' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            models_dir = global_prop.pz_directory
            model_path = model_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            models_dir = global_prop.pz_directory + 'projectzomboid/'
            model_path = model_path.replace('\\', '/')
        
        # Construct the name of the target file
        target = models_dir + model_path

        match mesh_prop.model_type:
            case 'X':
                target = target + '.x'
            case 'FBX':
                target = target + '.fbx'
            case 'GLB':
                target = target + '.glb'
        
        target = bpy.path.resolve_ncase(target)
        
        if Path(target).is_file():
                
            # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
            prev_mode = context.mode
            if context.active_object is not None:
                prev_active_object = context.active_object
            prev_selected_objects = context.selected_objects
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            objs_before = set(bpy.context.scene.objects)
            
            match mesh_prop.model_type:
                case 'X':
                    if 'bl_ext.blender_org.io_directx_x' not in bpy.context.preferences.addons.keys():
                        self.report({"ERROR"}, "The .x importer is not enabled or installed")
                        return({'CANCELLED'})
                    
                    bpy.ops.import_scene.directx_x(
                        filepath = str(target),
                        import_textures = False,
                        import_materials = False,
                        import_armature = False
                    )
                    
                case 'FBX':
                    bpy.ops.import_scene.fbx(
                        filepath = str(target),
                        global_scale = 100.0
                    )
                case 'GLB':
                    pass
            
            objs_after = set(bpy.context.scene.objects)
            
            imported_objects = list(objs_after - objs_before)
            
            female_collection = bpy.data.collections.get('GEO-PZ_Human_Female_Props' + instance_str)
            
            for obj in imported_objects:                
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':
                    
                    old_obj = bpy.data.objects.get('OBJ-FemalePropMesh' + str(prop.prop_mesh_slot_active_index))
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)
                    
                    obj.name = 'OBJ-FemalePropMesh' + str(prop.prop_mesh_slot_active_index)
                    
                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)
                    
                    if obj.name not in female_collection.objects:
                        female_collection.objects.link(obj)
                    
                    #-------------------------
                    
                    bip01 = bpy.data.objects.get('Bip01')
                    bone = bip01.pose.bones.get(mesh_prop.attach_bone)
                    
                    obj.parent = bip01
                    obj.parent_type = 'BONE'
                    obj.parent_bone = bone.name
                    
                    obj.matrix_parent_inverse = bone.matrix.inverted()
                    
                    bone_world_matrix = bip01.matrix_world @ bone.matrix
                    obj.matrix_world = bone_world_matrix
                    
                    match mesh_prop.model_type:
                        case 'X':
                            obj.rotation_euler[0] += math.pi
                            obj.scale *= 100
                            
                            # Wrist items are imported upside down and have off rotations, for some reason
                            if bone.name == 'Bip01_L_Forearm':
                                obj.scale[2] *= -1
                                obj.rotation_euler[1] -= math.radians(3)
                            if bone.name == 'Bip01_R_Forearm':
                                obj.scale[2] *= -1
                                obj.rotation_euler[1] += math.radians(3)
                        case 'FBX':
                            obj.rotation_euler[0] = -math.pi / 2
                        case 'GLB':
                            pass
                        
                    #-------------------------
                    
                    obj.modifiers.clear()
                    
                    obj.active_material = bpy.data.materials.get('MAT-PropMaterial' + str(prop.prop_mesh_slot_active_index))
                    
                    obj["sex"] = 1
                    obj.hide_viewport = obj['sex'] != prop.model_sex_index
                    obj.hide_render = obj['sex'] != prop.model_sex_index
                    
                        
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            
            for obj in prev_selected_objects:
                obj.select_set(True)
            if prev_active_object is not None:
                context.view_layer.objects.active = prev_active_object
                
            # Restore the context that was before the operation was called
            bpy.ops.object.mode_set(mode=prev_mode)
            return({'FINISHED'})
        else:
            self.report({'ERROR'}, "Could not find a model file at the path: " + target)
            return({'CANCELLED'})
        
    def execute(self, context):
        self.create_prop_material(context)
        self.import_male_model(context)
        self.import_female_model(context)
        
        bpy.ops.zomboid.check_hat_category()
            
        return({'FINISHED'})

# ============================================================================================
# HAIR MESH IMPORTER
# ============================================================================================

class PZ_ImportHairMesh(Operator):
    bl_idname = "zomboid.import_hair_mesh"
    bl_label = "Import Hair Mesh"
    
    hair_type : StringProperty(
        name = 'Hair Type'
    )
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        hair_styles = context.scene.pz_human_hair_style_slots
        beard_styles = context.scene.pz_human_beard_styles
        
        hair_style = None
        match self.hair_type:
            case 'M':
                for hair in hair_styles:
                    if hair.name == prop.current_male_hair_style and hair.sex == 'MALE':
                        hair_style = hair
            case 'F':
                for hair in hair_styles:
                    if hair.name == prop.current_female_hair_style and hair.sex == 'FEMALE':
                        hair_style = hair
            case 'B':
                for beard in beard_styles:
                    if beard.name == prop.current_beard_style:
                        hair_style = beard
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        models_dir = ''
        model_path = hair_style.model_path
        
        # Construct the filepath to the 'models_X/Skinned' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            models_dir = global_prop.pz_directory + '\\media\\models_X\\'
            model_path = model_path.replace('\\', '\\\\')
        elif sys.platform == 'linux':
            models_dir = global_prop.pz_directory + 'projectzomboid/media/models_X/'
            model_path = model_path.replace('\\', '/')
        
        # Construct the name of the target file
        target= models_dir + model_path
    
        target_name = os.path.basename(target)
        directory = os.path.dirname(target)
        directory = bpy.path.resolve_ncase(directory)
        
        if target_name == 'None':
           bpy.ops.zomboid.remove_hair_mesh(hair_type=self.hair_type)
           return ({'FINISHED'})

        extension = ''
        filepath = ''
        for file in os.listdir(directory):
            name, ext = os.path.splitext(file)
            if name.lower() == target_name.lower():
                filepath = os.path.join(directory, file)
                extension = ext
                break

        col = None
        prev_obj = None
        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Male' + instance_str)
                prev_obj = col.objects.get('OBJ-MaleHair' + instance_str)
            case 'F':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Female' + instance_str)
                prev_obj = col.objects.get('OBJ-FemaleHair' + instance_str)
            case 'B':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Beard' + instance_str)
                prev_obj = col.objects.get('OBJ-Beard' + instance_str)
        
        if prev_obj:
            bpy.data.objects.remove(prev_obj, do_unlink=True)
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        if context.active_object is not None:
            prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        objs_before = set(bpy.context.scene.objects)
        
        match extension:
            case '.x' | '.X':
                if 'bl_ext.blender_org.io_directx_x' not in bpy.context.preferences.addons.keys():
                    self.report({"ERROR"}, "The .x importer is not enabled or installed")
                    return({'CANCELLED'})
                
                bpy.ops.import_scene.directx_x(
                        filepath = str(filepath),
                        import_textures = False,
                        import_materials = False,
                        import_armature = False
                    )
                
            case '.fbx':
                bpy.ops.import_scene.fbx(
                    filepath = filepath,
                    global_scale = 100.0
                )
            case '.glb':
                pass
            
        objs_after = set(bpy.context.scene.objects)
        
        imported_objects = list(objs_after - objs_before)

        for obj in imported_objects:                
            if obj.type == 'ARMATURE' or obj.type == 'EMPTY':
                bpy.data.objects.remove(obj, do_unlink=True)
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
                    
                obj.hide_viewport = obj['sex'] != prop.model_sex_index
                obj.hide_render = obj['sex'] != prop.model_sex_index
                match extension:
                    case '.x' | '.X':
                        obj.rotation_euler[2] += math.pi
                        obj.scale[0] = -1
                        obj.location[1] = -.001
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                    case '.fbx':
                        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
                        obj.rotation_euler[0] = -math.pi / 2
                    case '.glb':
                        pass
                
                if self.hair_type == 'M' or self.hair_type == 'F':
                    prop.hair_texture_type = hair_style.texture_type
                
                for collection in obj.users_collection[:]:
                    collection.objects.unlink(obj)
                
                if obj.name not in col.objects:
                    col.objects.link(obj)
                
                obj.modifiers.clear()
                
                arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                arm_mod.object = bpy.data.objects.get('Bip01')
                
                ### Hair Material and Drivers ###
                obj.active_material = bpy.data.materials.get('MAT-Hair')
                
                # Beard Texture Override
                obj['is_beard'] = self.hair_type == 'B'
                
                # Hair Texture Driver
                obj['hair_type'] = 0
                fcurve = obj.driver_add('["hair_type"]')
                driver = fcurve.driver
                
                driver.type = 'AVERAGE'
                
                var = driver.variables.new()
                target = var.targets[0]
                
                target.id = context.active_object
                target.data_path = "pz_human_props.hair_texture_type_index"
                
                # Hair Color Driver
                obj['hair_color'] = [1.0, 0.0, 0.0, 1.0]
                
                for i in range(3):
                    fcurve = obj.driver_add('["hair_color"]', i)
                    driver = fcurve.driver
                    
                    driver.type = 'AVERAGE'
                    
                    var = driver.variables.new()
                    target = var.targets[0]
                    
                    target.id = context.active_object
                    target.data_path = "pz_human_props.hair_color[" + str(i) + "]"
                
            #    obj.parent = bpy.data.objects.get('Bip01')
                    
                
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        for obj in prev_selected_objects:
            obj.select_set(True)
        if prev_active_object is not None:
            context.view_layer.objects.active = prev_active_object
            
        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)
        
        return({'FINISHED'})

# endregion

# region Remove Operators

# ============================================================================================
# CLOTHING MESH REMOVER
# ============================================================================================

class PZ_RemoveClothingMesh(Operator):
    bl_idname = "zomboid.remove_clothing_mesh"
    bl_label = "Remove Clothing Mesh"
    
    #-------------------------------------------------------------#
    # Remove Clothing Material
    
    def remove_clothing_material(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.clothing_mesh_slot_active_index
        
        old_mat = bpy.data.materials.get('MAT-ClothingMaterial' + str(index) + instance_str)
        if old_mat:
            
            drivers = old_mat.node_tree.animation_data.drivers
            for i in range(len(drivers) - 1, -1, -1):
                drivers.remove(drivers[i]) 
            
            bpy.data.materials.remove(old_mat, do_unlink=True)
            
        for i in range(index, len(mesh_prop_list)):
            index_mat = bpy.data.materials.get('MAT-ClothingMaterial' + str(i) + instance_str)
            if index_mat:
                index_mat.name = 'MAT-ClothingMaterial' + str(i - 1) + instance_str
                
                for fcurve in index_mat.node_tree.animation_data.drivers:
                    driver = fcurve.driver
                    target = driver.variables[0].targets[0]
                    
                    old_path = "pz_human_clothing_mesh_slots[" + str(i) + "]"
                    new_path = "pz_human_clothing_mesh_slots[" + str(i - 1) + "]"
                    
                    target.data_path = target.data_path.replace(old_path, new_path)
            
        return ({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Remove Male Clothing Object
    
    def remove_male_clothing_mesh(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.clothing_mesh_slot_active_index
        
        old_obj = bpy.data.objects.get('OBJ-MaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
        for i in range(index, len(mesh_prop_list)):
            index_obj = bpy.data.objects.get('OBJ-MaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-MaleClothingMesh' + str(i - 1) + instance_str
        
        return ({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Remove Female Clothing Object
    
    def remove_female_clothing_mesh(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.clothing_mesh_slot_active_index
        
        old_obj = bpy.data.objects.get('OBJ-FemaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
        for i in range(index, len(mesh_prop_list)):
            index_obj = bpy.data.objects.get('OBJ-FemaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-FemaleClothingMesh' + str(i - 1) + instance_str
        
        return ({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Check Masks
    
    def check_masks(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]
        
        prop.halt_texture_updates = True
        
        for i in range(len(prop.mask_array)):
            test = False
            for j in range(len(mesh_prop_list)):
                if mesh_prop_list[j].name != mesh_prop.name and mesh_prop_list[j].mask_array[i] == True:
                    test = True
                    break
            prop.mask_array[i] = test
            prop.mask_array[i] = prop.mask_array[i]
        
        prop.halt_texture_updates = False
        
        bpy.ops.zomboid.create_mask_texture()
        
        return({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Execute
    
    def execute(self, context):
        self.remove_clothing_material(context)
        self.remove_male_clothing_mesh(context)
        self.remove_female_clothing_mesh(context)
        self.check_masks(context)
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        return ({'FINISHED'})

# ============================================================================================
# PROP MESH REMOVER
# ============================================================================================

class PZ_RemovePropMesh(Operator):
    bl_idname = "zomboid.remove_prop_mesh"
    bl_label = "Remove Prop Mesh"
    
    #-------------------------------------------------------------#
    # Remove Prop Material
    
    def remove_prop_material(self, context):
        prop = context.active_object.pz_human_props
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.prop_mesh_slot_active_index
        
        old_mat = bpy.data.materials.get('MAT-PropMaterial' + str(index) + instance_str)
        if old_mat:
            
            drivers = old_mat.node_tree.animation_data.drivers
            for i in range(len(drivers) - 1, -1, -1):
                drivers.remove(drivers[i]) 
            
            bpy.data.materials.remove(old_mat, do_unlink=True)
            
        for i in range(index, len(prop_prop_list)):
            index_mat = bpy.data.materials.get('MAT-PropMaterial' + str(i) + instance_str)
            if index_mat:
                index_mat.name = 'MAT-PropMaterial' + str(i - 1) + instance_str
                
                for fcurve in index_mat.node_tree.animation_data.drivers:
                    driver = fcurve.driver
                    target = driver.variables[0].targets[0]
                    
                    old_path = "pz_human_prop_mesh_slots[" + str(i) + "]"
                    new_path = "pz_human_prop_mesh_slots[" + str(i - 1) + "]"
                    
                    target.data_path = target.data_path.replace(old_path, new_path)
            
        return ({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Remove Male Prop Object
    
    def remove_male_prop_mesh(self, context):
        prop = context.active_object.pz_human_props
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.prop_mesh_slot_active_index
        
        old_obj = bpy.data.objects.get('OBJ-MalePropMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
        for i in range(index, len(prop_prop_list)):
            index_obj = bpy.data.objects.get('OBJ-MalePropMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-MalePropMesh' + str(i - 1) + instance_str
        
        return ({'FINISHED'})
    
    #-------------------------------------------------------------#
    # Remove Female Prop Object
    
    def remove_female_prop_mesh(self, context):
        prop = context.active_object.pz_human_props
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        instance_str = ' (' + str(prop.rig_instance) + ')'

        index = prop.prop_mesh_slot_active_index
        
        old_obj = bpy.data.objects.get('OBJ-FemalePropMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)
            
        for i in range(index, len(prop_prop_list)):
            index_obj = bpy.data.objects.get('OBJ-FemalePropMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-FemalePropMesh' + str(i - 1) + instance_str
        
        return ({'FINISHED'})

    #-------------------------------------------------------------#
    # Execute
    
    def execute(self, context):
        self.remove_prop_material(context)
        self.remove_male_prop_mesh(context)
        self.remove_female_prop_mesh(context)
        
        bpy.ops.zomboid.check_hat_category(count_self=False)
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        return ({'FINISHED'})

# ============================================================================================
# HAIR MESH REMOVER
# ============================================================================================

class PZ_RemoveHairMesh(Operator):
    bl_idname = "zomboid.remove_hair_mesh"
    bl_label = "Remove Hair Mesh"
    
    hair_type : StringProperty(
        name = 'Hair Type'
    )
    
    def execute(self, context):
        prop = context.active_object.pz_human_props

        instance_str = ' (' + str(prop.rig_instance) + ')'

        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Male' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-MaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'F':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Female' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-FemaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'B':
                col = bpy.data.collections.get('GEO-PZ_Human_Hair_Beard' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-Beard' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
        
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        
        return({'FINISHED'})

# endregion

# region Randomize Operators

## ============================================================================================
## HAIR MESH RANDOMIZER
## ============================================================================================

class PZ_HairRandomizer(Operator):
    bl_idname = "zomboid.randomize_hair_mesh"
    bl_label = "Randomize Hair Mesh"
    
    hair_type : StringProperty(
        name = 'Hair Type'
    )
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        
        match self.hair_type:
            case 'M':
                rnd = randint(0, len(context.scene.pz_human_male_hair_styles) - 1)
                prop.selected_male_hair_style = context.scene.pz_human_male_hair_styles[rnd].name
            case 'F':
                rnd = randint(0, len(context.scene.pz_human_female_hair_styles) - 1)
                prop.selected_female_hair_style = context.scene.pz_human_female_hair_styles[rnd].name
            case 'B':
                rnd = randint(0, len(context.scene.pz_human_beard_styles) - 1)
                prop.selected_beard_style = context.scene.pz_human_beard_styles[rnd].name
        
        return({'FINISHED'})

# ============================================================================================
# HAIR COLOR RANDOMIZER
# ============================================================================================

class PZ_HairColorRandomizer(Operator):
    bl_idname = "zomboid.randomize_hair_color"
    bl_label = "Randomize Hair Color"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        color = (1.0, 1.0, 1.0)
        if prop.natural_hair_color:
            hair_color_array = [
            (0.658, 0.408, 0.060), # Mustard Yellow
            (0.397, 0.265, 0.082), # Coffee
            (0.347, 0.150, 0.024), # Leather
            (0.333, 0.223, 0.093), # Dark Beige
            (0.314, 0.162, 0.072), # Mocha
            (0.298, 0.192, 0.100), # Dull Brown
            (0.159, 0.095, 0.045), # Dark Taupe
            (0.093, 0.056, 0.026), # Dark Brown
            (0.098, 0.036, 0.016), # Chocolate
            (0.040, 0.022, 0.011), # Darker Brown
            (0.034, 0.031, 0.029), # Dark Grey
            (0.011, 0.009, 0.008), # Black
            (0.201, 0.188, 0.162), # Medium Grey
            (0.382, 0.342, 0.216), # Stone
            (0.502, 0.439, 0.338), # Greyish
            (0.381, 0.371, 0.347), # Grey
            (0.515, 0.235, 0.136), # Pinkish Tan
            (0.381, 0.110, 0.061), # Clay
            (0.300, 0.051, 0.051), # Light Maroon
            (0.238, 0.055, 0.029)  # Earth
            ]
            
            rnd = randint(0, len(hair_color_array) - 1)
            color = hair_color_array[rnd]
        else:
            color = (random(), random(), random())
        
        prop.hair_color[0] = color[0]
        prop.hair_color[1] = color[1]
        prop.hair_color[2] = color[2]
        
        return({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY INJURIES
# ============================================================================================           
 
class PZ_HumanRig_RandomizeBodyInjuries(Operator):
    bl_idname = "zomboid.randomize_body_injuries"
    bl_label = "Randomize Body Injuries"
    bl_description = "Randomize the values of all the body intensity options based on a set intensity"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        
        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury", 
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]
        
        prop.halt_texture_updates = True
        
        for injury in injury_props:
            setattr(prop, injury, 'NONE')
        
        options = ['SCRATCH', 'LACERATION', 'BITE']
        chances = [prop.random_scratch_chance, prop.random_laceration_chance, prop.random_bite_chance]
        
        injury_num = 0
        match prop.random_injury_intensity:
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
            if randint(1, 100) <= prop.random_bandage_chance or selected_injury is prop.head_injury:
                if randint(1,100) <= prop.random_bloody_bandage_chance:
                    final_injury = 'BANDAGEBLOODY'
                else:
                    final_injury = 'BANDAGE'
            else:
                final_injury = choices(options, weights=chances)[0]
            
            if selected_injury == 'head_injury' and selected_injury not in ('NONE', 'BANDAGE', 'BANDAGEBLOODY'):
                continue
            
            setattr(prop, selected_injury, final_injury)
            
            injury_props.remove(selected_injury)
        
        bpy.ops.zomboid.create_body_injury_texture()
        
        prop.halt_texture_updates = False
        
        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE ZOMBIE INJURIES
# ============================================================================================           
 
def filter_zombie_injuries(self, context):
            items = []
            items.append(('NONE', 'None', ''))
            for item in context.scene.pz_human_clothing_item_slots:
                if 'ZedDmg' in item.name:
                    entry = (item.name, item.name, '')
                    items.append(entry)
            return items

class PZ_HumanRig_RandomizeZombieInjuries(Operator):
    bl_idname = "zomboid.randomize_zombie_injuries"
    bl_label = "Randomize Zombie Injuries"
    bl_description = "Add a set or random amount of random zombie specific injuries"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props

        injury_choices = filter_zombie_injuries(self, context)

        zombie_injuries = context.active_object.pz_human_zombie_injuries
        
        prop.halt_texture_updates = True
        
        zombie_injuries.clear()
        
        injury_num = 0
        match prop.random_zombie_injury_intensity:
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
            selected_injury = injury_choices[randint(0, len(injury_choices) - 1)]

            if selected_injury[0] == 'NONE':
                injury_choices.remove(selected_injury)
                continue

            new_injury = zombie_injuries.add()
            new_injury.name = selected_injury[0]
            new_injury.texture_path = context.scene.pz_human_clothing_item_slots.get(selected_injury[0]).texture_choices[0].texture_path

            injury_choices.remove(selected_injury)
        
        bpy.ops.zomboid.create_body_injury_texture()
        
        prop.halt_texture_updates = False
        
        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY BLOODINESS
# ============================================================================================

class PZ_HumanRig_RandomizeBodyBloodiness(Operator):
    bl_idname = "zomboid.randomize_body_bloodiness"
    bl_label = "Randomize Body Bloodiness"
    bl_description = "Randomize the values of all the body bloodiness options based on a set intensity"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        
        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                        "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                        "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                        "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness", 
                        "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                        "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]
        
        prop.halt_texture_updates = True
        
        for blood in blood_props:
            setattr(prop, blood, 0)
            bloodiness = 0
            match prop.random_bloodiness_intensity:
                case 'SOME':
                    bloodiness = uniform(0.0, 1.5)
                case 'MODERATE':
                    bloodiness = uniform(1.0, 2.5)
                case 'LOTS':
                    bloodiness = uniform(2.0, 3.5)
                case 'DRENCHED':
                    bloodiness = uniform(3.0, 5.0)
                case 'RANDOM':
                    bloodiness = uniform(0.0, 5.0)

            setattr(prop, blood, bloodiness)
        
        bpy.ops.zomboid.create_body_bloodiness_texture()
        
        prop.halt_texture_updates = False
        
        return ({'FINISHED'})

# ============================================================================================
# RANDOMIZE BODY DIRTINESS
# ============================================================================================

class PZ_HumanRig_RandomizeBodyDirtiness(Operator):
    bl_idname = "zomboid.randomize_body_dirtiness"
    bl_label = "Randomize Body Dirtiness"
    bl_description = "Randomize the values of all the body dirtiness options based on a set intensity"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        
        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                        "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                        "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                        "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness", 
                        "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                        "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]
        
        prop.halt_texture_updates = True
        
        for dirt in dirt_props:
            setattr(prop, dirt, 0)
            dirtiness = 0
            match prop.random_dirtiness_intensity:
                case 'SOME':
                    dirtiness = uniform(0.0, 0.5)
                case 'MODERATE':
                    dirtiness = uniform(0.4, 0.8)
                case 'LOTS':
                    dirtiness = uniform(0.70, 1.2)
                case 'DISGUSTING':
                    dirtiness = uniform(1.1, 2.0)
                case 'RANDOM':
                    dirtiness = uniform(0.0, 2.0)

            setattr(prop, dirt, dirtiness)
        
        bpy.ops.zomboid.create_body_dirtiness_texture()
        
        prop.halt_texture_updates = False
        
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

    def execute(self, context):
        prop = context.active_object.pz_human_props

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                        "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                        "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                        "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness", 
                        "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                        "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]
        
        prop.halt_texture_updates = True
        
        for blood in blood_props:
            setattr(prop, blood, 0)
        
        bpy.ops.zomboid.create_body_bloodiness_texture()

        prop.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE DIRTINESS
# ============================================================================================

class PZ_HumanRig_RemoveBodyDirtiness(Operator):
    bl_idname = "zomboid.remove_body_dirtiness"
    bl_label = "Remove Dirtiness"
    bl_description = "Sets all dirtiness on the body to zero"

    def execute(self, context):
        prop = context.active_object.pz_human_props

        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                        "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                        "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                        "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness", 
                        "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                        "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]
        
        prop.halt_texture_updates = True
        
        for dirt in dirt_props:
            setattr(prop, dirt, 0)
        
        bpy.ops.zomboid.create_body_dirtiness_texture()

        prop.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL BODY INJURIES
# ============================================================================================

class PZ_HumanRig_RemoveAllBodyInjuries(Operator):
    bl_idname = "zomboid.remove_all_body_injuries"
    bl_label = "Remove All Body Injuries"
    bl_description = "Removes all body injuries"

    def execute(self, context):
        prop = context.active_object.pz_human_props

        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury", 
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]
        
        prop.halt_texture_updates = True
        
        for injury in injury_props:
            setattr(prop, injury, 'NONE')
        
        bpy.ops.zomboid.create_body_injury_texture()

        prop.halt_texture_updates = False

        return ({'FINISHED'})

# ============================================================================================
# REMOVE ALL ZOMBIE INJURIES
# ============================================================================================

class PZ_HumanRig_RemoveAllZombieInjuries(Operator):
    bl_idname = "zomboid.remove_all_zombie_injuries"
    bl_label = "Remove All Zombie Injuries"
    bl_description = "Removes all zombie injuries"

    def execute(self, context):
        prop = context.active_object.pz_human_props

        prop.halt_texture_updates = True
        
        context.active_object.pz_human_zombie_injuries.clear()        
        
        bpy.ops.zomboid.create_body_injury_texture()

        prop.halt_texture_updates = False

        return ({'FINISHED'})


# ============================================================================================
# REMOVE ALL BODY DAMAGE
# ============================================================================================

class PZ_HumanRig_RemoveAllBodyDamage(Operator):
    bl_idname = "zomboid.remove_all_body_damage"
    bl_label = "Remove All Body Damage"
    bl_description = "Removes all body damage"

    def execute(self, context):
        
        bpy.ops.zomboid.remove_body_bloodiness()
        bpy.ops.zomboid.remove_body_dirtiness()
        bpy.ops.zomboid.remove_all_body_injuries()
        bpy.ops.zomboid.remove_all_zombie_injuries()

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
    
    def execute(self, context):
        global_prop = context.scene.pz_human_global_props
        dirs = context.scene.pz_human_mod_directory_slots

        dirs.clear()

        pz_dir = Path(global_prop.pz_directory)
        steamapps_dir = pz_dir.parent.parent
        mods_dir = steamapps_dir / 'workshop' / 'content' / '108600'
        
        mod_folders = [item for item in mods_dir.iterdir() if item.is_dir()]

        for mod_path in mod_folders:
            submods_dir = mod_path / 'mods'
            submod_folders = [item for item in submods_dir.iterdir() if item.is_dir()]
            for submod_path in submod_folders:
                # For now, just ignore any mods that don't have a 42 version
                version_folders = [item for item in submod_path.iterdir() if item.is_dir()]

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
                        new_dir.latest_pz_version = round(latest_submod_version_num, 2)

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
                    overwrite_check = context.scene.pz_human_clothing_item_slots.find(os.path.splitext(file.name)[0])
                    if overwrite_check != -1:
                        context.scene.pz_human_clothing_item_slots.remove(overwrite_check)

                    # Create and fill out the clothing item slot
                    item = context.scene.pz_human_clothing_item_slots.add()

                    # Name
                    item.name = os.path.splitext(file.name)[0]

                    # GUID
                    m = root.find('m_GUID') 
                    if m is not None:
                        item.guid = m.text

                    # Models
                    m = root.find('m_MaleModel')
                    if m is not None and m.text is not None:
                        path = m.text
                        start = path.find(':') + 1
                        end = path.find('.')
                        if end == -1:
                            path = path[start:]
                        else:
                            path = path[start:end]
                        if 'media\\models_X' not in path:
                            path = str(Path('media') / 'models_X' / Path(path))
                        item.male_model_path = path
                    else:
                        item.male_model_path = 'None'

                    m = root.find('m_FemaleModel') 
                    if m is not None and m.text is not None:
                        path = m.text
                        start = path.find(':') + 1
                        end = path.find('.')
                        if end == -1:
                            path = path[start:]
                        else:
                            path = path[start:end]
                        if 'media\\models_X' not in path:
                            path = str(Path('media') / 'models_X' / Path(path))
                        item.female_model_path = path
                    else:
                        item.female_model_path = 'None'

                    if item.male_model_path != 'None':
                        match os.path.splitext(item.male_model_path)[1]:
                            case ".x" | ".X":
                                item.model_type = 'X'
                            case ".fbx":
                                item.model_type = 'FBX'
                            case ".glb":
                                item.model_type = 'GLB'
                            case _:
                                item.model_type = 'X'
                        item.is_body_texture = False
                    else:
                        item.model_type = 'NONE'
                        item.is_body_texture = True

                    # Textures
                    base_texture = root.find('m_BaseTextures')
                    textures = root.findall('textureChoices')
                    if base_texture is not None:
                        tex = item.texture_choices.add()
                        tex.texture_path = base_texture.text
                        for t in textures:
                            tex = item.texture_choices.add()
                            tex.texture_path = t.text
                    
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
                            case 'Group04':
                                item.hat_category = 4
                            case 'Group05':
                                item.hat_category = 5
                            case 'nohair': 
                                item.hat_category = 6
                            case 'nohairnobeard':
                                item.hat_category = 7
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
        global_prop = context.scene.pz_human_global_props
        clothing_items = context.scene.pz_human_clothing_item_slots
        
        global_prop.clothing_item_slot_active_index = 0
        clothing_items.clear()
        
        # Get the vanilla clothing item XMLs folder and parse it
        xmls_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xmls_dir = global_prop.pz_directory + '\\media\\clothing\\clothingItems'
        elif sys.platform == 'linux':
            xmls_dir = global_prop.pz_directory + '/projectzomboid/media/clothing/clothingItems'
        
        xmls_dir = Path(xmls_dir)
        
        self.parse_folder(context, xmls_dir, clothing_items, 'Project Zomboid')
        
        for mod in context.scene.pz_human_mod_directory_slots:
            # Find the 'clothing' folder
            first_path = (Path(mod.mod_dir) / 'media' / 'clothing' / 'clothingItems')
            second_path = (Path(mod.mod_dir).parent / 'common' / 'media' / 'clothing' / 'clothingItems')
            first_path = bpy.path.resolve_ncase(str(first_path))
            second_path = bpy.path.resolve_ncase(str(second_path))
            first_path = Path(first_path)
            second_path = Path(second_path)
            if first_path.is_dir():
                self.parse_folder(context, first_path, clothing_items, mod.name)
            elif second_path.is_dir():
                self.parse_folder(context, second_path, clothing_items, mod.name)
        
        self.report({'INFO'}, "Parsed " + str(self.item_count) + " Clothing Item XMLs")
        return ({'FINISHED'})

# ============================================================================================
# OUTFIT XML PARSER
# ============================================================================================

class PZ_HumanRig_ParseOutfitXMLs(Operator):
    bl_idname = "zomboid.parse_outfit_xmls"
    bl_label = "Parse Outfit XMLs"
    bl_description = "Parse all the outfit xmls to get the data needed to import into Blender"
    
    outfit_count = 0

    def parse_xml(self, context, dir, outfits, origin):
        global_prop = context.scene.pz_human_global_props

        # Begin parsing the XML contents of the file
        tree = ET.parse(dir)
        root = tree.getroot()

        female_outfits = root.findall('m_FemaleOutfits')
        male_outfits = root.findall('m_MaleOutfits')
        
        for outfit in female_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = context.scene.pz_human_outfit_slots.find(outfit.find('m_Name').text)
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
                    new_clothing_item.probability = float(clothing_item.find('probability').text)
                    
                # Get first item choice
                choice = new_clothing_item.choices.add()
                
                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    for x in context.scene.pz_human_clothing_item_slots:
                        if x.guid == choice.guid:
                            choice.name = x.name
                            break
                
                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        
                        #TODO: Optimize
                        for x in context.scene.pz_human_clothing_item_slots:
                            if x.guid == choice.guid:
                                choice.name = x.name
                                break
            
            self.outfit_count = self.outfit_count + 1
        for outfit in male_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = context.scene.pz_human_outfit_slots.find(outfit.find('m_Name').text)
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
                    new_clothing_item.probability = float(clothing_item.find('probability').text)
                    
                # Get first item choice
                choice = new_clothing_item.choices.add()

                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    for x in context.scene.pz_human_clothing_item_slots:
                        if x.guid == choice.guid:
                            choice.name = x.name
                            break
                
                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        for x in context.scene.pz_human_clothing_item_slots:
                            if x.guid == choice.guid:
                                choice.name = x.name
                                break
                        
            self.outfit_count = self.outfit_count + 1

    def execute(self, context):
        global_prop = context.scene.pz_human_global_props
        outfits = context.scene.pz_human_outfit_slots
        
        global_prop.outfit_slot_active_index = 0
        outfits.clear()
        
        xml_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xml_dir = global_prop.pz_directory + '\\media\\clothing\\clothing.xml'
        elif sys.platform == 'linux':
            xml_dir = global_prop.pz_directory + '/projectzomboid/media/clothing/clothing.xml'
        
        xml_dir = Path(xml_dir)
        
        self.parse_xml(context, xml_dir, outfits, 'Project Zomboid')
        
        for mod in context.scene.pz_human_mod_directory_slots:
            # Find the 'clothing.xml' file
            first_path = (Path(mod.mod_dir) / 'media' / 'clothing' / 'clothing.xml').resolve()
            second_path = (Path(mod.mod_dir).parent / 'common' / 'media' / 'clothing' / 'clothing.xml').resolve()
            if first_path.is_file():
                self.parse_xml(context, first_path, outfits, mod.name)
            elif second_path.is_file():
                self.parse_xml(context, second_path, outfits, mod.name)

        self.report({'INFO'}, "Parsed " + str(self.outfit_count) + " Outfits")
        return {'FINISHED'}

# ============================================================================================
# HAIR STYLE XML PARSER
# ============================================================================================

class PZ_HumanRig_ParseHairStyleXMLs(Operator):
    bl_idname = "zomboid.parse_hair_style_xmls"
    bl_label = "Parse Hair Style XMLs"
    bl_description = "Parse all the hair style xmls to get the data needed to import into Blender"
    
    def execute(self, context):
        global_prop = context.scene.pz_human_global_props
        hair_styles = context.scene.pz_human_hair_style_slots
        male_styles = context.scene.pz_human_male_hair_styles
        female_styles = context.scene.pz_human_female_hair_styles
        beard_styles = context.scene.pz_human_beard_styles
        
        global_prop.hair_style_slot_active_index = 0
        hair_styles.clear()
        male_styles.clear()
        female_styles.clear()
        beard_styles.clear()
        
        hair_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            hair_dir = global_prop.pz_directory + '\\media\\hairStyles\\hairStyles.xml'
        elif sys.platform == 'linux':
            hair_dir = global_prop.pz_directory + '/projectzomboid/media/hairStyles/hairStyles.xml'
        
        hair_dir = Path(hair_dir)
        
        beard_dir = ''
        
        if sys.platform == 'win32':
            beard_dir = global_prop.pz_directory + '\\media\\hairStyles\\beardStyles.xml'
        elif sys.platform == 'linux':
            beard_dir = global_prop.pz_directory + '/projectzomboid/media/hairStyles/beardStyles.xml'
        
        beard_dir = Path(beard_dir)
        
        # Begin parsing the XML contents of the hair file
        tree = ET.parse(hair_dir)
        root = tree.getroot()
        
        male_hair_styles = root.findall('male')
        female_hair_styles = root.findall('female')
        
        hair_count = 0
        for hair in male_hair_styles:
            bpy.ops.zomboid.add_hair_style_slot()
            item = context.scene.pz_human_hair_style_slots[global_prop.hair_style_slot_active_index]
            
            item.name = hair.find('name').text
            item.sex = 'MALE'
            item.level = int(hair.find('level').text)
    
            match hair.find('texture').text:
                case 'F_Hair_White':
                    item.texture_type = 'NORMAL'
                case 'F_Hair_Braids':
                    item.texture_type = 'BRAIDS'
                case 'F_HairCurly_Short':
                    item.texture_type = 'SHORTCURLY'
                case 'F_HairCurly_Long':
                    item.texture_type = 'LONGCURLY'
            
            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'
            
            for hat_group in hair.findall('alternate'):
                group = item.hat_styles.add()
                match hat_group.get('category'):
                    case 'default':
                        group.hat_group = 0
                    case 'Group01':
                        group.hat_group = 1
                    case 'Group02':
                        group.hat_group = 2
                    case 'Group04':
                        group.hat_group = 4
                    case 'Group05':
                        group.hat_group = 5
                group.style_name = hat_group.get('style')
            
            no_choose = hair.find('noChoose')
            
            if no_choose is not None and no_choose.text == 'true': 
                pass
            else:
                new = male_styles.add()
                new.name = item.name
            
            hair_count = hair_count + 1
            
        for hair in female_hair_styles:
            bpy.ops.zomboid.add_hair_style_slot()
            item = context.scene.pz_human_hair_style_slots[global_prop.hair_style_slot_active_index]
            
            item.name = hair.find('name').text
            item.sex = 'FEMALE'
            item.level = int(hair.find('level').text)
            
            match hair.find('texture').text:
                case 'F_Hair_White':
                    item.texture_type = 'NORMAL'
                case 'F_Hair_Braids':
                    item.texture_type = 'BRAIDS'
                case 'F_HairCurly_Short':
                    item.texture_type = 'SHORTCURLY'
                case 'F_HairCurly_Long':
                    item.texture_type = 'LONGCURLY'
            
            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'
            
            for hat_group in hair.findall('alternate'):
                group = item.hat_styles.add()
                match hat_group.get('category'):
                    case 'default':
                        group.hat_group = 0
                    case 'Group01':
                        group.hat_group = 1
                    case 'Group02':
                        group.hat_group = 2
                    case 'Group04':
                        group.hat_group = 4
                    case 'Group05':
                        group.hat_group = 5
                group.style_name = hat_group.get('style')
            
            no_choose = hair.find('noChoose')
            
            if no_choose is not None and no_choose.text == 'true': 
                pass
            else:
                new = female_styles.add()
                new.name = item.name
            
            hair_count = hair_count + 1
        
        # Begin parsing the XML contents of the beard file
        tree = ET.parse(beard_dir)
        root = tree.getroot()
        
        beard_styles = root.findall('style')
        
        # Add a 'clean' option
        bpy.ops.zomboid.add_beard_style_slot()
        item = context.scene.pz_human_beard_styles[global_prop.beard_style_slot_active_index]
        
        item.name = 'None'
        item.model_path = 'None'
        item.level = 0
        
        beard_count = 0
        for beard in beard_styles:
            bpy.ops.zomboid.add_beard_style_slot()
            item = context.scene.pz_human_beard_styles[global_prop.beard_style_slot_active_index]
            
            item.name = beard.find('name').text
            item.level = int(beard.find('level').text)
            item.model_path = beard.find('model').text
            
            beard_count = beard_count + 1
            
        self.report({'INFO'}, "Parsed " + str(hair_count) + " Hair Styles & " + str(beard_count) + " Beard Styles")
        return ({'FINISHED'})

# ============================================================================================
# DECAL XML PARSER
# ============================================================================================

class PZ_HumanRig_ParseDecalXMLs(Operator):
    bl_idname = "zomboid.parse_decal_xmls"
    bl_label = "Parse Decal XMLs"
    bl_description = "Parse all the clothing xmls to get the data needed to import into Blender"
    
    def parse_decals(self, context):
        global_prop = context.scene.pz_human_global_props
        
        global_prop.decal_slot_active_index = 0
        
        decals = context.scene.pz_human_decals
        decals.clear()
        
        xmls_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xmls_dir = global_prop.pz_directory + '\\media\\clothing\\clothingDecals'
        elif sys.platform == 'linux':
            xmls_dir = global_prop.pz_directory + '/projectzomboid/media/clothing/clothingDecals'
        
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
        global_prop = context.scene.pz_human_global_props
        current_groups = context.scene.pz_human_decal_groups
        
        global_prop.decal_group_slot_active_index = 0
        current_groups.clear()
        
        xmls_dir = ''
        
        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xml_dir = global_prop.pz_directory + 'media\\clothing\\clothingDecals.xml'
        elif sys.platform == 'linux':
            xml_dir = global_prop.pz_directory + 'projectzomboid/media/clothing/clothingDecals.xml'
        
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
        global_prop = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations
        
        body_locations.clear()
        
        global_prop.body_location_active_index = 0
        
        file_dir = ''
        
        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = global_prop.pz_directory + 'media\\lua\\shared\\NPCs\\BodyLocations.lua'
        elif sys.platform == 'linux':
            file_dir = global_prop.pz_directory + 'projectzomboid/media/lua/shared/NPCs/BodyLocations.lua'
            
        with open(file_dir, 'r', encoding='utf-8') as file:
            for line in file:
                lua_line = line.strip()
                
                # Line creates a new body location
                if 'getOrCreateLocation' in lua_line:
                    pattern=r'\.(.*?)\)'
                    body_location = body_locations.add()
                    body_location.name = re.findall(pattern, lua_line)[0]
                
                elif 'setExclusive' in lua_line:
                    pattern=r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.exclusive_locations.add()
                            hide_loc.name = matches[0]
                            break
                
                elif 'setHideModel' in lua_line:
                    pattern=r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.hide_locations.add()
                            hide_loc.name = matches[0]
                            break
                
                elif 'setAltModel' in lua_line:
                    pattern=r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.alt_locations.add()
                            hide_loc.name = matches[0]
                            break
        
        return ({'FINISHED'}) 
    
    def parse_clothing_txt(self, context):
        global_prop = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations
        clothing_items = context.scene.pz_human_clothing_item_slots
        
        file_dir = ''
        
        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = global_prop.pz_directory + 'media\\scripts\\generated\\items\\clothing.txt'
        elif sys.platform == 'linux':
            file_dir = global_prop.pz_directory + 'projectzomboid/media/scripts/generated/items/clothing.txt'
        
        in_main_portion = False
        in_item_block = False
        
        current_clothing_item = ''
        current_body_location = ''
        
        with open(file_dir, 'r', encoding='utf-8') as file:
            #TODO: Replace with albion's more sophisticated parser
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
                        current_body_location = txt_line.split(':')[1].split(',')[0].upper()
                        #print(current_body_location)

                    if 'ClothingItem' in txt_line:
                        current_clothing_item = txt_line.split('= ')[1].split(',')[0]
                        #print(current_clothing_item)
                    
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
# PARSE ALL ASSETS
# ============================================================================================

class PZ_HumanRig_ParseAllXMLs(Operator):
    bl_idname = "zomboid.parse_all_xmls"
    bl_label = "Parse All Assets"
    bl_description = "Parse all the relevant xmls to get the data needed to import into Blender"
    
    def execute(self, context):
        bpy.ops.zomboid.parse_body_location_lua()
        bpy.ops.zomboid.parse_clothing_xmls()
        bpy.ops.zomboid.parse_outfit_xmls()
        bpy.ops.zomboid.parse_hair_style_xmls()
        bpy.ops.zomboid.parse_decal_xmls()
        
        return ({'FINISHED'}) 

# ============================================================================================
# CLEAR ALL ASSETS
# ============================================================================================

class PZ_HumanRig_ClearAllXMLs(Operator):
    bl_idname = "zomboid.clear_all_xmls"
    bl_label = "Clear All Assets"
    bl_description = "Clear all the parsed asset entries"
    
    def execute(self, context):
        
        bpy.context.scene.pz_human_global_props.clothing_item_slot_active_index = -1
        bpy.context.scene.pz_human_global_props.outfit_slot_active_index = -1
        bpy.context.scene.pz_human_global_props.hair_style_slot_active_index = -1
        bpy.context.scene.pz_human_global_props.beard_style_slot_active_index = -1
        bpy.context.scene.pz_human_global_props.decal_slot_active_index = -1
        bpy.context.scene.pz_human_global_props.body_location_active_index = -1
        
        bpy.context.scene.pz_human_clothing_item_slots.clear()
        bpy.context.scene.pz_human_outfit_slots.clear()
        bpy.context.scene.pz_human_hair_style_slots.clear()
        bpy.context.scene.pz_human_male_hair_styles.clear()
        bpy.context.scene.pz_human_female_hair_styles.clear()
        bpy.context.scene.pz_human_beard_styles.clear()
        bpy.context.scene.pz_human_decal_groups.clear()
        bpy.context.scene.pz_human_body_locations.clear()
        
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
    
    def select_guids(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        
        outfit_name = prop.selected_outfit.split()[0]
        outfit_sex = ''
        if '(Male)' in prop.selected_outfit:
            outfit_sex = 'MALE'
        elif '(Female)' in prop.selected_outfit:
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
        
        return ({'ERROR'})
    
    def add_clothing_items(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        body_texture_prop_list = context.active_object.pz_human_body_texture_slots
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        # Select the model sex
        if '(Male)' in prop.selected_outfit:
            prop.model_sex = 'MALE'
            
            if prop.random_hair_style:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='M')
            if randint(1, 100) <= prop.random_beard_chance:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='B')
            else:
                prop.beard_style = 'None'
        elif '(Female)' in prop.selected_outfit:
            prop.model_sex = 'FEMALE'
            
            if prop.random_hair_style:
                bpy.ops.zomboid.randomize_hair_mesh(hair_type='F')
            
        # Select random body textures, if enabled
        if prop.random_skin_color:
            prop.skin_color = randint(0, 4)
        if prop.random_zombie:
            prop.zombification = randint(1, 3)
        else:
            prop.zombification = 0
        
        # Select random hair color, if enabled
        if prop.random_hair_color:
            bpy.ops.zomboid.randomize_hair_color()
        
        # Randomize injuries, if enabled
        if prop.randomize_injuries:
            bpy.ops.zomboid.randomize_body_injuries()
            bpy.ops.zomboid.randomize_zombie_injuries()
            bpy.ops.zomboid.randomize_body_bloodiness()
            bpy.ops.zomboid.randomize_body_dirtiness()
        
        if self.random_top:
            match randint(1, 6):
                case 1:
                    # Standard Default T-Shirt
                    bpy.ops.zomboid.add_clothing_item(guid='e4ec9087-006d-41dc-81f4-585b6d2e958c', generate_mask=False)
                case 2:
                    # Tintable Default T-Shirt 
                    bpy.ops.zomboid.add_clothing_item(guid='19af00e4-ed4d-49bc-a893-a4a3376fe6da', generate_mask=False)
                case 3:
                    # Standard Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(guid='d0616b36-b727-4c08-9274-020cb2e72bf8', generate_mask=False)
                case 4:
                    # Tintable Default T-Shirt w/ Decal
                    bpy.ops.zomboid.add_clothing_item(guid='53b95680-245b-4439-8ba7-5aa6d938e465', generate_mask=False)
                case 5:
                    # Standard Default Vest
                    bpy.ops.zomboid.add_clothing_item(guid='903c06ea-78e7-4f42-a3da-768be61f216f', generate_mask=False)
                case 6:
                    # Tintable Default Vest 
                    bpy.ops.zomboid.add_clothing_item(guid='a700a956-32c2-49a6-bd5f-5a2895073f19', generate_mask=False)
        
        if self.random_pants:
            match randint(1, 3):
                case 1:
                    # Standard Default Trousers
                    bpy.ops.zomboid.add_clothing_item(guid='e4b71599-604d-4cc7-9ce4-7723a7e37d8a', generate_mask=False)
                case 2:
                    # Hue-able Default Trousers
                    bpy.ops.zomboid.add_clothing_item(guid='5b07d45e-84c9-4ddf-ad6e-4bc2f27cace7', generate_mask=False)
                case 3:
                    # Tintable Default Trousers
                    bpy.ops.zomboid.add_clothing_item(guid='1e2ed52f-9ee7-464b-9581-a450f2fbb403', generate_mask=False)
        
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
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        outfits = context.scene.pz_human_outfit_slots
        
        rnd = randint(0, len(outfits)-1)
        prop.selected_outfit = outfits[rnd].search_name
        
        bpy.ops.zomboid.apply_outfit()
        
        return({'FINISHED'})

# ============================================================================================
# ADD CLOTHING ITEM TO MODEL
# ============================================================================================

class PZ_HumanRig_AddClothingItem(Operator):
    bl_idname = "zomboid.add_clothing_item"
    bl_label = "Add Clothing Item"
    bl_description = "Adds a clothing item onto the model"
    
    guid : StringProperty()
    generate_mask : BoolProperty(
        default=True
    )
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        global_prop = context.scene.pz_human_global_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        body_texture_prop_list = context.active_object.pz_human_body_texture_slots
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        item = None
        for clothing_item in context.scene.pz_human_clothing_item_slots:
            if clothing_item.guid == self.guid:
                item = clothing_item
        
        if item is not None:
            
            # Body Texture
            if item.is_body_texture:
                bpy.ops.zomboid.add_body_texture_slot()
                tex_prop = body_texture_prop_list[prop.body_texture_slot_active_index]
                
                rnd = randint(0, len(item.texture_choices) - 1)
                tex_prop.name = item.name
                tex_prop.decal_group = item.decal_group
                tex_prop.texture_path = item.texture_choices[rnd].texture_path
            
            # Clothing Mesh
            elif item.static == False and item.attach_bone == 'None':
                bpy.ops.zomboid.add_clothing_mesh_slot()
                mesh_prop = mesh_prop_list[prop.clothing_mesh_slot_active_index]
                
                mesh_prop.male_model_path = item.male_model_path
                mesh_prop.female_model_path = item.female_model_path
                
                rnd = randint(0, len(item.texture_choices) - 1)
                mesh_prop.texture_path = item.texture_choices[rnd].texture_path
                mesh_prop.name = item.name
                
                for i in range(len(item.mask_array)):
                    if item.mask_array[i] == True:
                        mesh_prop.mask_array[i] = True
                
                mesh_prop.hat_category = item.hat_category
                
                bpy.ops.zomboid.import_clothing_mesh()
            
            # Prop Mesh
            else:
                bpy.ops.zomboid.add_prop_mesh_slot()
                prop_prop = prop_prop_list[prop.prop_mesh_slot_active_index]
                
                prop_prop.male_model_path = item.male_model_path
                prop_prop.female_model_path = item.female_model_path
                
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
            return ({'ERROR'})
    
# ============================================================================================
# REMOVE ALL CLOTHING ITEMS
# ============================================================================================

class PZ_HumanRig_RemoveAllClothingItems(Operator):
    bl_idname = "zomboid.remove_all_clothing_items"
    bl_label = "Remove All Clothing Items"
    bl_description = "Removes all clothing items from the model"
    
    def execute(self, context):
        prop = context.active_object.pz_human_props
        mesh_prop_list = context.active_object.pz_human_clothing_mesh_slots
        body_texture_prop_list = context.active_object.pz_human_body_texture_slots
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        
        # Remove all existing clothing meshes
        prop.clothing_mesh_slot_active_index = len(mesh_prop_list) - 1
        for i in range(len(mesh_prop_list)):
            bpy.ops.zomboid.remove_clothing_mesh_slot()
        prop.clothing_mesh_slot_active_index = -1
            
        # Remove all existing body textures
        prop.body_texture_slot_active_index = len(body_texture_prop_list) - 1
        for i in range(len(body_texture_prop_list)):
            bpy.ops.zomboid.remove_body_texture_slot()
        prop.body_texture_slot_active_index = -1
            
        # Remove all existing prop meshes
        prop.prop_mesh_slot_active_index = len(prop_prop_list) - 1
        for i in range(len(prop_prop_list)):
            bpy.ops.zomboid.remove_prop_mesh_slot()
        prop.prop_mesh_slot_active_index = -1
        
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
        prop = context.active_object.pz_human_props
        prop_prop_list = context.active_object.pz_human_prop_mesh_slots
        clothing_prop_list = context.active_object.pz_human_clothing_mesh_slots
        
        # If there are no props or clothing meshes, set the hair style to the selected one
        if prop.prop_mesh_slot_active_index == -1 and prop.clothing_mesh_slot_active_index == -1:
            if prop.current_male_hair_style != prop.selected_male_hair_style:
                prop.current_male_hair_style = prop.selected_male_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
            if prop.current_female_hair_style != prop.selected_female_hair_style:
                prop.current_female_hair_style = prop.selected_female_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
            if prop.current_beard_style != prop.selected_beard_style:
                prop.current_beard_style = prop.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            prop.current_hat_category = -1
            
            return ({'FINISHED'})
        
        test = False
        if prop.prop_mesh_slot_active_index != -1:
            prop_prop = prop_prop_list[prop.prop_mesh_slot_active_index]
    
            for i in range(len(prop_prop_list)):
                if prop_prop_list[i].hat_category != -1: # Found a prop mesh that has a hat category
                    if (prop_prop_list[i].name == prop_prop.name and not self.count_self):
                        continue
                    test = True
                    if prop_prop_list[i].hat_category > prop.current_hat_category:
                        prop.current_hat_category = prop_prop_list[i].hat_category
        
        if prop.clothing_mesh_slot_active_index != -1:
            clothing_prop = clothing_prop_list[prop.clothing_mesh_slot_active_index]
        
            for i in range(len(clothing_prop_list)):
                if clothing_prop_list[i].hat_category != -1: # Found a prop mesh that has a hat category
                    if (clothing_prop_list[i].name == clothing_prop.name and not self.count_self):
                        continue
                    test = True
                    if clothing_prop_list[i].hat_category > prop.current_hat_category:
                        prop.current_hat_category = clothing_prop_list[i].hat_category
        
        if test:
            if prop.current_hat_category >= 6:
                prop.current_male_hair_style = 'Bald'
                prop.current_female_hair_style = 'Bald'
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
                if prop.current_hat_category == 7:
                    prop.current_beard_style = 'None'
                    bpy.ops.zomboid.import_hair_mesh(hair_type='B')
                else:
                    prop.current_breard_style = prop.selected_beard_style
                    bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            else:
                prop.current_breard_style = prop.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')
                
                for hair in context.scene.pz_human_hair_style_slots:
                    if hair.name == prop.selected_male_hair_style and hair.sex == 'MALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == prop.current_hat_category:
                                if prop.current_male_hair_style != hat_style.style_name:
                                    prop.current_male_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_mesh(hair_type='M')
                                break
                            
                    if hair.name == prop.selected_female_hair_style and hair.sex == 'FEMALE':
                        for hat_style in hair.hat_styles:
                            if hat_style.hat_group == prop.current_hat_category:
                                if prop.current_female_hair_style != hat_style.style_name:
                                    prop.current_female_hair_style = hat_style.style_name
                                    bpy.ops.zomboid.import_hair_mesh(hair_type='F')
                                break
        else:
            if prop.current_male_hair_style != prop.selected_male_hair_style:
                prop.current_male_hair_style = prop.selected_male_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='M')
            if prop.current_female_hair_style != prop.selected_female_hair_style:
                prop.current_female_hair_style = prop.selected_female_hair_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='F')
            if prop.current_beard_style != prop.selected_beard_style:
                prop.current_beard_style = prop.selected_beard_style
                bpy.ops.zomboid.import_hair_mesh(hair_type='B')
            prop.current_hat_category = -1
        
        
        return ({'FINISHED'})

# endregion

# region Instancing Operators

class PZ_HumanRig_DuplicateRig(Operator):
    bl_idname = "zomboid.duplicate_rig"
    bl_label = "Duplicate Rig"
    bl_description = "Creates a new instance of the rig that copies all of the selected rigs attributes" 

    def recursively_duplicate_collection(self, context, source_collection, parent_collection=None):


        return ({'FINISHED'})

    def execute(self, context):
        prop = context.active_object.pz_human_props

        self.recursively_duplicate_collection(context, prop.rig_collection, context.collection)



        return ({'FINISHED'})

# endregion

# region Export Operators

# ============================================================================================
# GLB EXPORTER
# ============================================================================================

class PZ_HumanRig_Export(Operator):
    bl_idname = "zomboid.export_glb"
    bl_label = "Select Folder"
    bl_description = "Export your animations as GLB files that are adjusted for Project Zomboid"
    
    filter_glob : StringProperty(
        default='.glb',
        options={'HIDDEN'}
    )
    
    filename_ext = ""

# ------------------------------------------------------------------------#
#  Main Function

    def export_anim(self, action):        
        context = bpy.context
        
        # Force set the animation to export at 30 FPS, which is what Project Zomboid evaluates animations at
        context.scene.render.fps = 30
        
        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects
        
        # Get references to the objects that will be exported
        dummy01 = bpy.data.objects.get('Dummy01')
        bip01 = bpy.data.objects.get('Bip01')
        mesh = bpy.data.objects.get('GEO-MaleBody')
        translation_data = bpy.data.objects.get('Translation_Data')
        
        # Get reference to the rig's properties
        prop = context.active_object.pz_human_props
        
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
        bip01_track.name = action.name                                                     # NLA track will have the same name as the action 
        translation_data_track = translation_data.animation_data.nla_tracks.new()                    
        translation_data_track.name = action.name
                
        bip01.animation_data.action = action
        anim_length = int(action.frame_range[0]) - 1                                       # Subtract 1 frame from the frame range to avoid an empty frame
        bip01_strip = bip01_track.strips.new(action.name, anim_length, action)
                
        translation_data.animation_data.action = action
        translation_data_strip = translation_data_track.strips.new(action.name, anim_length, action)
        translation_data_strip.frame_end = bip01_strip.frame_end
        
        # Call the Blender gltf exporter with specific settings tailored for our setup and Project Zomboid
        bpy.ops.export_scene.gltf( 
            filepath= prop.file_output_path + '/' + action.name +'.glb',
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
        translation_data.animation_data.nla_tracks.remove(translation_data_track)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)
        
        for obj in prev_selected_objects:
            obj.select_set(True)
        context.view_layer.objects.active = prev_active_object
        
        return {'FINISHED'}
    
# ------------------------------------------------------------------------#
#  Execute
    
    def execute(self, context): 
        
        # Get reference to the rig's properties
        prop = context.active_object.pz_human_props
        
        if len(prop.file_output_path) > 0: 
            if prop.batch_export:         
                for action in bpy.data.actions:
                    if prop.action_filter in action.name:
                        self.export_anim(action)
            else:
                if bpy.data.objects.get('Bip01').animation_data.action is not None:
                    self.export_anim(bpy.data.objects.get('Bip01').animation_data.action)
                else:
                    print("Bip01 has no active action selected.")
        else:
            self.report({"WARNING"}, "Declare a filepath to export to")
                    
        return {'FINISHED'}

# endregion

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

# region Rig Properties

'''
This is the main PropertyGroup attatched to each instance of the rig. It contains all
of the attributes relating to animation, visuals, etc.
'''

class PZ_HumanRigProperties(PropertyGroup):

# ============================================================================================
# IMPORTANT OBJECTS
# ============================================================================================

    rig_collection : PointerProperty(type=Collection)
    male_body_object : PointerProperty(type=Object)
    translation_data_empty : PointerProperty(type=Object)
    dummy01_empty : PointerProperty(type=Object)
    mask_data : PointerProperty(type=Image)
    injury_tex : PointerProperty(type=Image)
    body_mat : PointerProperty(type=Material)

# ============================================================================================
# INSTANCING
# ============================================================================================

    rig_instance : IntProperty(default=0)

# ============================================================================================
# HEAD ROTATION
# ============================================================================================

    head_lookpoint : FloatProperty(
        name="Use LookPoint", 
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 will have the head rotate with CTRL-Head, 1 will make the head rotate towards CTRL-LookPoint"
        )

# ============================================================================================
# IK/FK SWITCHING
# ============================================================================================

    arm_ik_l : FloatProperty(
        name="Left Arm IK", 
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
        )
    arm_ik_r : FloatProperty(
        name="Right Arm IK", 
        default=0.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
        )
    leg_ik_l : FloatProperty(
        name="Left Leg IK", 
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
        )
    leg_ik_r : FloatProperty(
        name="Right Leg IK", 
        default=1.0,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
        description="0 for FK, 1 for IK"
        )

# ============================================================================================
# CONSTRAINTS
# ============================================================================================

    fk_constrain : BoolProperty(
        name="Limit FK Rotations",
        default=True,
        description="When true, FK controls have rotation constraints, not letting limbs bend beyond what they can realistically bend. Disable if you need to make an animation for breaking bones"
    )
    
    root_is_ik_floor : BoolProperty(
        name="Root is IK Floor",
        default=True,
        description="When true, the leg IK controls cannot go below CTRL-Root"
    )
    
# ------------------------------------------------------------------------#
#  Lookpoint Parenting
    
    def update_lookpoint_parent_index(self, context) :
        self.lookpoint_parent_index = context.active_object.pz_human_props['left_prop_parent']
    
    lookpoint_parent : EnumProperty(
        name="LookPoint Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Lookpoint is not child of anything", 0),
            ('ROOT', "Root", "Lookpoint is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Lookpoint is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Lookpoint is the child of CTRL-Chest", 3),
            ('OBJECT', "Object", "Copies the location of a selected object", 4)
        ],
        default='ROOT',
        update=update_lookpoint_parent_index
    )
    
    lookpoint_parent_index : IntProperty(
        default=1
    )
    
    def update_lookpoint_parent_object(self, context):
        update_lookpoint_parent_object(self, context)
    
    lookpoint_parent_object : PointerProperty(
        name = "LookPoint Parent Object",
        type = Object,
        update = update_lookpoint_parent_object
    )

# ------------------------------------------------------------------------#
#  Left Prop Parenting
    
    def update_left_prop_parent_index(self, context):
        self.left_prop_parent_index = context.active_object.pz_human_props['left_prop_parent']
    
    left_prop_parent : EnumProperty(
        name="Left Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Left Prop is not child of anything", 0),
            ('ROOT', "Root", "Left Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Left Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_left_prop_parent_index
    )
    
    left_prop_parent_index : IntProperty(
        default=2
    )
    
    def update_left_prop_parent_object(self, context):
       # update_left_prop_parent_object(self, context)
       pass
    
    left_prop_parent_object : PointerProperty(
        name = "Left Prop Parent Object",
        type = Object,
        update = update_left_prop_parent_object
    )

# ------------------------------------------------------------------------#
#  Right Prop Parenting
    
    def update_right_prop_parent_index(self, context):
        self.right_prop_parent_index = context.active_object.pz_human_props['right_prop_parent']
    
    right_prop_parent : EnumProperty(
        name="Right Prop Parent",
        description="What the lookpoint is parented to",
        items=[
            ('NONE', "None", "Right Prop is not child of anything", 0),
            ('ROOT', "Root", "Right Prop is the child of CTRL-Root", 1),
            ('HAND', "Hand", "Right Prop is the child of the hand", 2),
            ('OBJECT', "Object", "Copies the location of a selected object", 3)
        ],
        default='HAND',
        update=update_right_prop_parent_index
    )
    
    right_prop_parent_index : IntProperty(
        default=2
    )
    
    def update_right_prop_parent_object(self, context):
     #   update_right_prop_parent_object(self, context)
        pass
    
    right_prop_parent_object : PointerProperty(
        name = "Right Prop Parent Object",
        type = Object,
        update = update_right_prop_parent_object
    )

# ------------------------------------------------------------------------#
#  Backpack Parenting
    
    def update_backpack_parent_index(self, context):
        self.backpack_parent_index = context.active_object.pz_human_props['backpack_parent']
    
    backpack_parent : EnumProperty(
        name="Backpack Parent",
        description="What the backpack is parented to",
        items=[
            ('NONE', "None", "Backpack is not child of anything", 0),
            ('ROOT', "Root", "Backpack is the child of CTRL-Root", 1),
            ('SPINE', "Spine", "Backpack is the child of the spine", 2)
        ],
        default='SPINE',
        update=update_backpack_parent_index
    )
    
    backpack_parent_index : IntProperty(
        default=2
    )

# ------------------------------------------------------------------------#
#  Dress Parenting
    
    def update_dress_parent_index(self, context):
        self.dress_parent_index = context.active_object.pz_human_props['dress_parent']
    
    dress_parent : EnumProperty(
        name="Dress Parent",
        description="What the dress is parented to",
        items=[
            ('NONE', "None", "Dress is not child of anything", 0),
            ('ROOT', "Root", "Dress is the child of CTRL-Root", 1),
            ('LEGS', "Legs", "Dress bones are calculated between the legs", 2)
        ],
        default='LEGS',
        update=update_dress_parent_index
    )
    
    dress_parent_index : IntProperty(
        default=2
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Control Parenting
    
    def update_right_arm_ik_control_parent_index(self, context):
        self.right_arm_ik_control_parent_index = context.active_object.pz_human_props['right_arm_ik_control_parent']
    
    right_arm_ik_control_parent : EnumProperty(
        name="Right Arm IK Control Parent",
        description="What the right arm IK control is parented to",
        items=[
            ('NONE', "None", "Right arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Right arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Right arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_right_arm_ik_control_parent_index
    )
    
    right_arm_ik_control_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Right Arm IK Pole Parenting
    
    def update_right_arm_ik_pole_parent_index(self, context):
        self.right_arm_ik_pole_parent_index = context.active_object.pz_human_props['right_arm_ik_pole_parent']
    
    right_arm_ik_pole_parent : EnumProperty(
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
        update=update_right_arm_ik_pole_parent_index
    )
    
    right_arm_ik_pole_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Control Parenting
    
    def update_left_arm_ik_control_parent_index(self, context):
        self.left_arm_ik_control_parent_index = context.active_object.pz_human_props['left_arm_ik_control_parent']
    
    left_arm_ik_control_parent : EnumProperty(
        name="Left Arm IK Control Parent",
        description="What the left arm IK control is parented to",
        items=[
            ('NONE', "None", "Left arm IK control is not child of anything", 0),
            ('ROOT', "Root", "Left arm IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left arm IK control is the child of CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Left arm IK control is the child of CTRL-Chest", 3)
        ],
        default='ROOT',
        update=update_left_arm_ik_control_parent_index
    )
    
    left_arm_ik_control_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Left Arm IK Pole Parenting
    
    def update_left_arm_ik_pole_parent_index(self, context):
        self.left_arm_ik_pole_parent_index = context.active_object.pz_human_props['left_arm_ik_pole_parent']
    
    left_arm_ik_pole_parent : EnumProperty(
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
        update=update_left_arm_ik_pole_parent_index
    )
    
    left_arm_ik_pole_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Control Parenting
    
    def update_right_leg_ik_control_parent_index(self, context):
        self.right_leg_ik_control_parent_index = context.active_object.pz_human_props['right_leg_ik_control_parent']
    
    right_leg_ik_control_parent : EnumProperty(
        name="Right Leg IK Control Parent",
        description="What the right leg IK control is parented to",
        items=[
            ('NONE', "None", "Right leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Right leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Right leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_right_leg_ik_control_parent_index
    )
    
    right_leg_ik_control_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Right Leg IK Pole Parenting
    
    def update_right_leg_ik_pole_parent_index(self, context):
        self.right_leg_ik_pole_parent_index = context.active_object.pz_human_props['right_leg_ik_pole_parent']
    
    right_leg_ik_pole_parent : EnumProperty(
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
        update=update_right_leg_ik_pole_parent_index
    )
    
    right_leg_ik_pole_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Control Parenting
    
    def update_left_leg_ik_control_parent_index(self, context):
        self.left_leg_ik_control_parent_index = context.active_object.pz_human_props['left_leg_ik_control_parent']
    
    left_leg_ik_control_parent : EnumProperty(
        name="Left Leg IK Control Parent",
        description="What the left leg IK control is parented to",
        items=[
            ('NONE', "None", "Left leg IK control is not child of anything", 0),
            ('ROOT', "Root", "Left leg IK control is the child of CTRL-Root", 1),
            ('PELVIS', "Pelvis", "Left leg IK control is the child of CTRL-Pelvis", 2)
        ],
        default='ROOT',
        update=update_left_leg_ik_control_parent_index
    )
    
    left_leg_ik_control_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Left Leg IK Pole Parenting
    
    def update_left_leg_ik_pole_parent_index(self, context):
        self.left_leg_ik_pole_parent_index = context.active_object.pz_human_props['left_leg_ik_pole_parent']
    
    left_leg_ik_pole_parent : EnumProperty(
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
        update=update_left_leg_ik_pole_parent_index
    )
    
    left_leg_ik_pole_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  All IK Control Parent
    
    def update_all_ik_control_parent_index(self, context):
        self.all_ik_control_parent_index = context.active_object.pz_human_props['all_ik_control_parent']
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
    
    all_ik_control_parent : EnumProperty(
        name="Set Parent For All IK Controls: ",
        description="Sets the parent for all IK controls instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Controls are not parented to anything", 0),
            ('ROOT', "Root", "IK Controls are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Controls are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Controls are parented to CTRL-Chest, Leg IK Controls are parented to CTRL-Pelvis", 3)
        ],
        default='ROOT',
        update=update_all_ik_control_parent_index
    )
    
    all_ik_control_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  All IK Pole Parent
    
    def update_all_ik_pole_parent_index(self, context):
        self.all_ik_pole_parent_index = context.active_object.pz_human_props['all_ik_pole_parent']
        
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
            
    all_ik_pole_parent : EnumProperty(
        name="Set Parent For All IK Poles: ",
        description="Sets the parent for all IK poles instead of having to choose each one individually. Tries to match the corresponding limbs as best as it can (legs cannot be parented to the chest, and will be parented to the pelvis instead when 'Chest' is selected)",
        items=[
            ('NONE', "None", "IK Poles are not parented to anything", 0),
            ('ROOT', "Root", "IK Poles are parented to CTRL-Root", 1),
            ('PELVIS', "Pelvis", "IK Poles are parented to CTRL-Pelvis", 2),
            ('CHEST', "Chest", "Arm IK Poles are parented to CTRL-Chest, Leg IK Poles are parented to CTRL-Pelvis", 3),
            ('CONTROL', "Control", "IK Poles are parented to their corresponding IK controls", 4),
            ('JOINT', "Joint", "IK Poles are parented to the calculated position between the start and end of their corresponding limb", 5)
        ],
        default='ROOT',
        update=update_all_ik_pole_parent_index
    )
    
    all_ik_pole_parent_index : IntProperty(
        default=1
    )

# ------------------------------------------------------------------------#
#  Auto Wrist Twist

    auto_wrist_twist : BoolProperty(
        name="Auto Wrist Twist",
        description="If true, the forearm will slightly twitst to follow the hand's X rotation, which can mitigate candywrapping",
        default=True
    )

    wrist_twist_amount : FloatProperty(
        name="Wrist Twist Amount",
        description="How strongly the forearm follows the hand's X rotation. Can cause issues at higher levels",
        default = 0.25,
        min = 0.0,
        max = 1.0
    )

# ============================================================================================
# MODEL
# ============================================================================================

    def update_selected_clothing_item(self, context):
        if self.selected_clothing_item != '':
            item = None
            for clothing_item in context.scene.pz_human_clothing_item_slots:
                if clothing_item.name == self.selected_clothing_item:
                    bpy.ops.zomboid.add_clothing_item(guid=clothing_item.guid)
                    break
            self.selected_clothing_item = ''

    selected_clothing_item : StringProperty(
        name='Add Clothing Item',
        update=update_selected_clothing_item
    )

# ------------------------------------------------------------------------#
#  Body Mesh
    
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
        update_skin_texture(self, context)

        bpy.ops.zomboid.create_body_injury_texture()
    
    def update_body_visibility(self, context):
        prop = context.active_object.pz_human_props
        instance_str = ' (' + str(prop.rig_instance) + ')'

        col = bpy.data.collections.get('GEO-PZ_Human_Bodies' + instance_str)
        if col:
            col.hide_viewport = not self.show_body
            col.hide_render = not self.show_body
    
    model_sex : EnumProperty(
        name="Model Sex",
        description="Which human model to use",
        items=[
            ('MALE', "Male", "The male model", 0),
            ('FEMALE', "Female", "The female model", 1),
        ],
        default='MALE',
        update=update_sex_index
    )
    
    model_sex_index : IntProperty()
    
    show_body : BoolProperty(
        name="Body Enabled",
        default=True,
        description="Show the body of the character",
        update=update_body_visibility
    )
    
    show_dress : BoolProperty(
        name="Show Dress",
        default=True,
        description="Show the dress model for the respective sex"
    ) 
    use_skeleton : BoolProperty(
        name="Show Skeleton",
        default=False,
        description="Use the skeleton model for the selected sex"
    ) 

# ------------------------------------------------------------------------#
#  Masking
    
    def update_mask_array(self, context):
        prop = context.active_object.pz_human_props
        if not prop.halt_texture_updates:
            bpy.ops.zomboid.create_mask_texture()
    
    mask_array : BoolVectorProperty(
        name='Mask Array',
        description='Array of toggles for each mesh mask',
        size=17,
        default=(False, False, False, False, False, False,
                False, False, False, False, False, False,
                False, False, False, False, False),
        update=update_mask_array
    )

# ------------------------------------------------------------------------#
#  Body Injuries
    
    def update_body_injury(self, context):
        prop = context.active_object.pz_human_props
        if not prop.halt_texture_updates:
            bpy.ops.zomboid.create_body_injury_texture()

    upper_torso_injury : EnumProperty( # 0
        name='Upper Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    lower_torso_injury : EnumProperty( # 1
        name='Lower Torso Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_hand_injury : EnumProperty( # 2
        name='Left Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_hand_injury : EnumProperty( # 3
        name='Right Hand Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_forearm_injury : EnumProperty( # 4
        name='Left Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_forearm_injury : EnumProperty( # 5
        name='Right Forearm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_upperarm_injury : EnumProperty( # 6
        name='Left Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_upperarm_injury : EnumProperty( # 7
        name='Right Upperarm Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    head_injury : EnumProperty( # 8
        name='Head Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('BANDAGE', "Bandage", "Bandage injury texture", 1),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 2)
        ],
        default='NONE',
        update=update_body_injury
    )
    neck_injury : EnumProperty( # 9
        name='Neck Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    groin_injury : EnumProperty( # 10
        name='Groin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_thigh_injury : EnumProperty( # 11
        name='Left Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_thigh_injury : EnumProperty( # 12
        name='Right Thigh Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_shin_injury : EnumProperty( # 13
        name='Left Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_shin_injury : EnumProperty( # 14
        name='Right Shin Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    left_foot_injury : EnumProperty( # 15
        name='Left Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )
    right_foot_injury : EnumProperty( # 16
        name='Right Foot Injury',
        items=[
            ('NONE', "None", "No injury texture", 0),
            ('SCRATCH', "Scratch", "Scratch injury texture", 1),
            ('LACERATION', "Laceration", "Laceration injury texture", 2),
            ('BITE', "Bite", "Bite injury texture", 3),
            ('BANDAGE', "Bandage", "Bandage injury texture", 4),
            ('BANDAGEBLOODY', "Bandage (Bloody)", "Bloody Bandage injury texture", 5)
        ],
        default='NONE',
        update=update_body_injury
    )

    

    def update_selected_zombie_injury(self, context):
        if self.selected_zombie_injury != 'NONE':
            new_injury = context.active_object.pz_human_zombie_injuries.add()
            new_injury.name = self.selected_zombie_injury
            new_injury.texture_path = context.scene.pz_human_clothing_item_slots.get(self.selected_zombie_injury).texture_choices[0].texture_path
            self.selected_zombie_injury = 'NONE'
            bpy.ops.zomboid.create_body_injury_texture()


    selected_zombie_injury : EnumProperty(
        name = 'Add Zombie Injury',
        items = filter_zombie_injuries,
        update = update_selected_zombie_injury
    )

# ------------------------------------------------------------------------#
#  Bloodiness

    def update_bloodiness_texture(self, context):
        prop = context.active_object.pz_human_props
        if not prop.halt_texture_updates:
            bpy.ops.zomboid.create_body_bloodiness_texture()

    upper_torso_bloodiness : FloatProperty( 
        name='Upper Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    lower_torso_bloodiness : FloatProperty( 
        name='Lower Torso Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_hand_bloodiness : FloatProperty( 
        name='Left Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_hand_bloodiness : FloatProperty( 
        name='Right Hand Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_forearm_bloodiness : FloatProperty( 
        name='Left Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_forearm_bloodiness : FloatProperty( 
        name='Right Forearm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_upperarm_bloodiness : FloatProperty( 
        name='Left Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_upperarm_bloodiness : FloatProperty( 
        name='Right Upperarm Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    head_bloodiness : FloatProperty( 
        name='Head Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    neck_bloodiness : FloatProperty( 
        name='Neck Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    groin_bloodiness : FloatProperty( 
        name='Groin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_thigh_bloodiness : FloatProperty( 
        name='Left Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_thigh_bloodiness : FloatProperty( 
        name='Right Thigh Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_shin_bloodiness : FloatProperty( 
        name='Left Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_shin_bloodiness : FloatProperty( 
        name='Right Shin Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    left_foot_bloodiness : FloatProperty( 
        name='Left Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    right_foot_bloodiness : FloatProperty( 
        name='Right Foot Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )
    back_bloodiness : FloatProperty( 
        name='Back Bloodiness',
        default=0.0,
        min=0.0,
        max=5.0,
        subtype='FACTOR',
        update=update_bloodiness_texture
    )

# ------------------------------------------------------------------------#
#  Dirtiness

    def update_dirtiness_texture(self, context):
        prop = context.active_object.pz_human_props
        if not prop.halt_texture_updates:
            bpy.ops.zomboid.create_body_dirtiness_texture()

    upper_torso_dirtiness : FloatProperty( 
        name='Upper Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    lower_torso_dirtiness : FloatProperty( 
        name='Lower Torso Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_hand_dirtiness : FloatProperty( 
        name='Left Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_hand_dirtiness : FloatProperty( 
        name='Right Hand Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_forearm_dirtiness : FloatProperty( 
        name='Left Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_forearm_dirtiness : FloatProperty( 
        name='Right Forearm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_upperarm_dirtiness : FloatProperty( 
        name='Left Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_upperarm_dirtiness : FloatProperty( 
        name='Right Upperarm Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    head_dirtiness : FloatProperty( 
        name='Head Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    neck_dirtiness : FloatProperty( 
        name='Neck Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    groin_dirtiness : FloatProperty( 
        name='Groin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_thigh_dirtiness : FloatProperty( 
        name='Left Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_thigh_dirtiness : FloatProperty( 
        name='Right Thigh Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_shin_dirtiness : FloatProperty( 
        name='Left Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_shin_dirtiness : FloatProperty( 
        name='Right Shin Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    left_foot_dirtiness : FloatProperty( 
        name='Left Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    right_foot_dirtiness : FloatProperty( 
        name='Right Foot Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )
    back_dirtiness : FloatProperty( 
        name='Back Dirtiness',
        default=0.0,
        min=0.0,
        max=2.0,
        subtype='FACTOR',
        update=update_dirtiness_texture
    )

# ------------------------------------------------------------------------#
#  Body Textures
    
    # Skin ---------------------------------------
    
    skin_color : IntProperty(
        name="Skin Color",
        default=0,
        min=0,
        max=4,
        description="Which skin color texture set to use",
        update=update_skin_texture
    )
    
    zombification : IntProperty(
        name="Zombification",
        default=0,
        min=0,
        max=3,
        description="Level of zombification texture to use",
        update=update_skin_texture
    )
    
    skeleton_type : IntProperty(
        name="Skeleton Type",
        default=0,
        min=0,
        max=2,
        description="Which skeleton texture to use"
    )

# ------------------------------------------------------------------------#
#  Hair Mesh
    
    current_hat_category : IntProperty(
        default = -1
    )
    
    # Male Hair ---------------------------------------
    
    def update_male_hair_style(self, context):
        if self.selected_male_hair_style == '':
            self.selected_male_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()
        
    selected_male_hair_style : StringProperty(
        name="Male Hair",
        update=update_male_hair_style
    )
    
    current_male_hair_style : StringProperty()

    # Beard ---------------------------------------
    
    def update_beard_style(self, context):
        if self.selected_beard_style == '':
            self.selected_beard_style = 'None'
        else:
            bpy.ops.zomboid.check_hat_category()
    
    selected_beard_style : StringProperty(
        name="Beard",
        update=update_beard_style
    )
    
    current_beard_style : StringProperty()
    
    # Female Hair ---------------------------------------
    
    def update_female_hair_style(self, context):
        if self.selected_female_hair_style == '':
            self.selected_female_hair_style = 'Bald'
        else:
            bpy.ops.zomboid.check_hat_category()
    
    selected_female_hair_style : StringProperty(
        name="Female Hair",
        update=update_female_hair_style
    )
    
    current_female_hair_style : StringProperty()
    
    # ---------------------------------------------------
    
    def update_hair_visibility(self, context):
        col = bpy.data.collections.get('GEO-PZ_Human_Hair')
        if col:
            col.hide_viewport = not self.show_hair
            col.hide_render = not self.show_hair
    
    show_hair : BoolProperty(
        name="Hair Enabled",
        default=True,
        description="Show the hair of the character",
        update=update_hair_visibility
    )

# ------------------------------------------------------------------------#
#  Hair Texture
    
    def update_hair_texture_type_index(self, context):
        self.hair_texture_type_index = context.active_object.pz_human_props['hair_texture_type']
    
    hair_texture_type : EnumProperty(
        name="Hair Texture",
        description="Which hair texture to use",
        items=[
            ('NORMAL', "Normal", "Normal hair texture", 0),
            ('BRAIDS', "Braids", "Braids hair texture", 1),
            ('SHORTCURLY', "Short Curly", "Short curly hair texture", 2),
            ('LONGCURLY', "Long Curly", "Long curly hair texture", 3),
        ],
        default='NORMAL',
        update=update_hair_texture_type_index
    )
    
    hair_texture_type_index : IntProperty()
    
    hair_color : FloatVectorProperty(
        name="Hair Color",
        subtype='COLOR',
        default = (0.25, 0.15, 0.05),
        min=0,
        max=1
    )

# ============================================================================================
# RANDOMNESS
# ============================================================================================
    
    random_zombie : BoolProperty(
        name='Zombie',
        default=False
    )
    
    random_skin_color : BoolProperty(
        name='Random Skin Color',
        default=True
    )
    
    random_hair_style : BoolProperty(
        name='Random Hair Style',
        default=True
    )
    
    random_hair_color : BoolProperty(
        name='Random Hair Color',
        default=True
    )
    natural_hair_color : BoolProperty(
        name='Natural Hair Color',
        default=True
    )
    random_beard_chance : IntProperty(
        name='Random Beard Chance',
        default=50,
        min=0,
        max=100,
        subtype='PERCENTAGE'
    )
    randomize_injuries : BoolProperty(
        name='Randomize Injuries',
        description='Randomly apply injuries on the body',
        default=False
    )
    random_injury_intensity : EnumProperty(
        name='Random Injury Intensity',
        description='How many injuries should appear on the body',
        items= [
            ('NONE', "None", "No injury textures", 0),
            ('MINOR', "Minor", "1-2 injury textures", 1),
            ('MODERATE', "Moderate", "3-4 injury textures", 2),
            ('SERIOUS', "Serious", "5-6 injury textures", 3),
            ('SEVERE', "Severe", "7-10 injury textures", 4),
            ('INSANE', "Insane", "11-16 injury textures", 5),
            ('RANDOM', "Random", "0-16 injury textures", 6)
        ],
        default='MODERATE'
    )
    random_zombie_injury_intensity : EnumProperty(
        name='Random Zombie Injury Intensity',
        description='How many zombie injuries should appear on the body',
        items= [
            ('NONE', "None", "No injury textures", 0),
            ('INTACT', "Intact", "1-3 injury textures", 1),
            ('DAMAGED', "Damaged", "3-5 injury textures", 2),
            ('HACKED APART', "Hacked Apart", "5-15 injury textures", 3),
            ('MUTILATED', "Mutilated", "20-40 injury textures", 4),
            ('RENDED APART', "Rended Apart", "40-73 injury textures", 5),
            ('RANDOM', "Random", "0-73 injury textures", 6)
        ],
        default='DAMAGED'
    )
    random_scratch_chance : FloatProperty(
        name='Random Scratch Chance',
        description='Weighted chance injury will be a scratch (chances are automatically evened out to add up to 100%)',
        default=65,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0
    )
    random_laceration_chance : FloatProperty(
        name='Random Laceration Chance',
        description='Weighted chance injury will be a laceration (chances are automatically evened out to add up to 100%)',
        default=30,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0
    )
    random_bite_chance : FloatProperty(
        name='Random Bite Chance',
        description='Weighted chance injury will be a bite (chances are automatically evened out to add up to 100%)',
        default=5,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0
    )
    random_bandage_chance : FloatProperty(
        name='Random Bandage Chance',
        description='Weighted chance injury will be covered with a bandage',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0
    )
    random_bloody_bandage_chance : FloatProperty(
        name='Random Bloody Bandage Chance',
        description='Weighted chance a bandage will be bloody',
        default=35,
        subtype='PERCENTAGE',
        min=0.0,
        max=100.0
    )
    random_bloodiness_intensity : EnumProperty(
        name='Random Bloodiness Intensity',
        description='How much blood should appear on the body',
        items= [
            ('NONE', "None", "No bloodiness", 0),
            ('SOME', "Some", "A bit of bloodiness", 1),
            ('MODERATE', "Moderate", "Quite a bit of bloodiness", 2),
            ('LOTS', "Lots", "A lot of bloodiness", 3),
            ('DRENCHED', "Drenched", "Absolutely soaked in blood", 4),
            ('RANDOM', "Random", "Random amount of blood for each body part", 5)
        ],
        default='MODERATE'
    )
    random_dirtiness_intensity : EnumProperty(
        name='Random Dirtiness Intensity',
        description='How much dirt should appear on the body',
        items= [
            ('NONE', "None", "No dirt", 0),
            ('SOME', "Some", "A bit of dirt", 1),
            ('MODERATE', "Moderate", "Quite a bit of dirt", 2),
            ('LOTS', "Lots", "A lot of dirt", 3),
            ('DISGUSTING', "Disgusting", "Absolutely covered in dirt", 4),
            ('RANDOM', "Random", "Random amount of dirt for each body part", 5)
        ],
        default='MODERATE'
    )
    
# ============================================================================================
# SHADING
# ============================================================================================

    def update_shading_type_index(self, context):
        self.shading_type_index = context.active_object.pz_human_props['shading_type']
    
    shading_type : EnumProperty(
        name="Shading Type",
        description="What type of shading to use",
        items=[
            ('EMISSION', "Emission", "The model will be unshaded, which is more akin to what it will look like in Project Zomboid", 0),
            ('PBR', "PBR", "The model will have shading, which is good for more high graphical fidelity renders", 1),
            ('CUSTOM', "Custom", "The model will use a specified shading node group using the generated color and alpha from the main material. Make sure the group has 'Color' as the first input, 'Alpha' as the second, and 'Shader' as the only output", 2)
        ],
        default='EMISSION',
        update=update_shading_type_index
    )
    
    shading_type_index : IntProperty()

# ------------------------------------------------------------------------#
#  Emission

    emission_strength : FloatProperty(
        name = "Emission Strength",
        description = "How strong the emission shader is. Can be used to indicate if the character is in a darker area",
        default = 1.0,
        min = 0.0, 
        max = 5.0
    )

# ------------------------------------------------------------------------#
#  PBR

    roughness : FloatProperty(
        name = "Roughness",
        description = "How 'rough' the model is. Lower values mean it is more reflective",
        default = 0.9,
        min = 0.0,
        max = 1.0
    )
    
    metallic : FloatProperty(
        name = "Metallic",
        description = "How 'metal' the model is",
        default = 0.0,
        min = 0.0,
        max = 1.0
    )

# ------------------------------------------------------------------------#
#  Custom

    def update_custom_shading_group_name(self, context):
        mat = self.body_mat
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        selected_group = bpy.data.node_groups.get(self.custom_shading_group_name)

        if selected_group.bl_idname != 'ShaderNodeTree':
            return

        custom_shader_switch_node = nodes.get('NDE-CustomShaderSwitch')
        alpha_mix_node = nodes.get('NDE-BaseAlphaMix')
        dirt_mix_node = nodes.get('NDE-DirtMix')
        group_node = nodes.get('NDE-CustomShadingGroup')

        group_node.node_tree = selected_group

        # Ensure that the node is correctly linked

       # if any(input.identifier == 'Color' for input in group_node.inputs):
        if group_node.inputs.get('Color') is not None:
            links.new(dirt_mix_node.outputs['Result'], group_node.inputs['Color'])

      #  if any(input.identifier == 'Alplha' for input in group_node.inputs):
        if group_node.inputs.get('Alpha') is not None:
            links.new(alpha_mix_node.outputs['Result'], group_node.inputs['Alpha'])

       # if any(output.identifier == 'Shader' for output in group_node.outputs):
        if group_node.outputs.get('Shader') is not None:
            links.new(group_node.outputs['Shader'], custom_shader_switch_node.inputs[2])        

    custom_shading_group_name: StringProperty(
        name = "Custom Group Name",
        description = "The name of the custom shading node group to use",
        default = 'SHD-Placeholder',
        update = update_custom_shading_group_name
    )

# ------------------------------------------------------------------------#
#  Texture Interpolation
    
    def update_texture_interpolation_index(self, context):
        self.texture_interpolation_index = context.active_object.pz_human_props['texture_interpolation']
    
    texture_interpolation : EnumProperty(
        name="Texture Interpolation",
        description="Whether the textures have a more pixel-y look or a smoothed one",
        items=[
            ('LINEAR', "Linear", "Textures will be smoothed", 0),
            ('CLOSEST', "Closest", "Textures will be pixelated", 1)
        ],
        default='CLOSEST',
        update=update_texture_interpolation_index
    )
    
    texture_interpolation_index : IntProperty(
        default=1
    )

# ============================================================================================
# COMPOSITING
# ============================================================================================

# ------------------------------------------------------------------------#
#  Outline

    use_outline : BoolProperty(
        name='Outline',
        description='Use the Compositor to create an outline around the model. Intended for still shots',
        default=False
    )
    
    outline_size : IntProperty(
        name='Outline Size',
        description='How many pixels wide the outline is',
        default=4,
        min=1,
        max=8
    )
    
    outline_color : FloatVectorProperty(
        name="Outline Color",
        subtype='COLOR',
        default = (1.00, 1.00, 1.00),
        min=0,
        max=1
    )

# ============================================================================================
# CONTROLS
# ============================================================================================

# ------------------------------------------------------------------------#
#  Misc. Widget Settings

    widgets_size : FloatProperty(
        name="Widget Size", 
        default=2.5,
        min=1.0,
        max=10.0,
        subtype="PIXEL",
        description="The size of the control widgets"
    )
    auto_hide_controls : BoolProperty(
        name="Auto Hide Controls",
        default=True,
        description="When true, control bones that can not contribute to the end result are automatically hidden"
    )

# ------------------------------------------------------------------------#
#  Control Toggles

    # FK Toggles
    
    toggle_left_arm_fk_controls : BoolProperty(
        name="Arm FK.L",
        default=True,
        description="Show the left arm FK controls"
    )
    toggle_right_arm_fk_controls : BoolProperty(
        name="Arm FK.R",
        default=True,
        description="Show the right arm FK controls"
    )
    toggle_left_leg_fk_controls : BoolProperty(
        name="Leg FK.L",
        default=True,
        description="Show the left arm FK controls"
    )
    toggle_right_leg_fk_controls : BoolProperty(
        name="Leg FK.R",
        default=True,
        description="Show the right arm FK controls"
    )
    
    # IK Toggles
    
    toggle_left_arm_ik_controls : BoolProperty(
        name="Arm IK.L",
        default=True,
        description="Show the left arm IK controls"
    )
    toggle_right_arm_ik_controls : BoolProperty(
        name="Arm IK.R",
        default=True,
        description="Show the right arm IK controls"
    )
    toggle_left_leg_ik_controls : BoolProperty(
        name="Leg IK.L",
        default=True,
        description="Show the left arm IK controls"
    )
    toggle_right_leg_ik_controls : BoolProperty(
        name="Leg IK.R",
        default=True,
        description="Show the right arm IK controls"
    )
    
    # Root Toggles
    
    toggle_root_controls : BoolProperty(
        name="Root",
        default=True,
        description="Show the root controls"
    )
    toggle_translation_data_controls : BoolProperty(
        name="Translation Data",
        default=True,
        description="Show the translation data controls"
    )
    
    # Head Toggles
    
    toggle_look_point_controls : BoolProperty(
        name="Look Point",
        default=True,
        description="Show the look point controls"
    )
    toggle_head_controls : BoolProperty(
        name="Head",
        default=True,
        description="Show the head controls"
    )
    
    # Hand Toggles
    
    toggle_left_hand_controls : BoolProperty(
        name="Hand.L",
        default=True,
        description="Show the left hand controls"
    )
    toggle_right_hand_controls : BoolProperty(
        name="Hand.R",
        default=True,
        description="Show the right hand controls"
    )
    
    # Finger Toggles
    
    toggle_left_finger_controls : BoolProperty(
        name="Fingers.L",
        default=True,
        description="Show the left fingers controls"
    )
    toggle_right_finger_controls : BoolProperty(
        name="Fingers.R",
        default=True,
        description="Show the right fingers controls"
    )
    
    # Prop Toggles
    
    toggle_left_prop_controls : BoolProperty(
        name="Prop.L",
        default=True,
        description="Show the left prop controls"
    )
    toggle_right_prop_controls : BoolProperty(
        name="Prop.R",
        default=True,
        description="Show the right prop controls"
    )
    toggle_backpack_controls : BoolProperty(
        name="Backpack",
        default=True,
        description="Show the backpack controls"
    )
    toggle_dress_controls : BoolProperty(
        name="Dress",
        default=True,
        description="Show the dress controls"
    )
    
    # Feet Toggles
    
    toggle_left_foot_controls : BoolProperty(
        name="Foot.L",
        default=True,
        description="Show the left foot controls"
    )
    toggle_right_foot_controls : BoolProperty(
        name="Foot.R",
        default=True,
        description="Show the right foot controls"
    )
    
    # Shoulder Toggles
    
    toggle_left_shoulder_controls : BoolProperty(
        name="Shoulder.L",
        default=True,
        description="Show the left shoulder controls"
    )
    toggle_right_shoulder_controls : BoolProperty(
        name="Shoulder.R",
        default=True,
        description="Show the right shoulder controls"
    )
    
    # Torso Toggles
    
    toggle_pelvis_controls : BoolProperty(
        name="Pelvis",
        default=True,
        description="Show the pelvis controls"
    )
    toggle_spine_controls : BoolProperty(
        name="Spine",
        default=True,
        description="Show the spine controls"
    )
    toggle_chest_controls : BoolProperty(
        name="Chest",
        default=True,
        description="Show the chest controls"
    )
    
# ============================================================================================
# EXPORT
# ============================================================================================

    file_output_path : StringProperty(
        name="Output Directory",
        default="",
        description="The folder in which your animations will be stored. Most of the time, it should be in the 'anims_X' folder in your mod's media folder",
        subtype= 'DIR_PATH'
    )
    batch_export : BoolProperty(
        name="Batch Export",
        default=True,
        description="If true, every individual action on Bip01 that has the substring from the Action Filter will be exported as a .glb file to the directory. If false, only export the active action on Bip01"
    )
    action_filter : StringProperty(
        name="Action Filter",
        default="Bob_",
        description="If an action contains this substring, it will be exported as a .glb"
    )

# ============================================================================================
# TESTING
# ============================================================================================
    
    # def update_body_texture_slots(self, context):
    #     return update_body_texture_slots(self, context)
    
    body_texture_slot_active_index : IntProperty(
        name = "Active Body Texture Slot"
    )
    
    clothing_mesh_slot_active_index : IntProperty(
        name = "Active Clothing Mesh Slot"
    )
    
    prop_mesh_slot_active_index : IntProperty(
        name = "Active Clothing Mesh Slot"
    )
    
    zombie_injury_active_index : IntProperty(
        name = "Active Zombie Injury"
    )

    def update_clothing_visibility(self, context):
        col = bpy.data.collections.get('GEO-PZ_Human_Clothes')
        if col:
            col.hide_viewport = not self.show_clothing
            col.hide_render = not self.show_clothing
    
    show_clothing : BoolProperty(
        name = "Clothing Enabled",
        default = True,
        update = update_clothing_visibility
    )
    
    def update_prop_visibility(self, context):
        col = bpy.data.collections.get('GEO-PZ_Human_Props')
        if col:
            col.hide_viewport = not self.show_props
            col.hide_render = not self.show_props
    
    show_props : BoolProperty(
        name = "Props Enabled",
        default = True,
        update = update_prop_visibility
    )
    
    use_skin_textures : BoolProperty(
        name="Use Skin Textures",
        default=True,
        description="Use the vanilla skin textures as the base"
    )
    
    selected_outfit : StringProperty(
        name='Selected Outfit'
    )
   
# ============================================================================================
# DEBUG
# ============================================================================================
    
    debug_toggle : BoolProperty(
        name='Debug',
        default=False
    )
    halt_texture_updates : BoolProperty(
        default=False
    )

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

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

    pz_directory : StringProperty(
        name="Project Zomboid Directory",
        default="",
        description="The location of your Project Zomboid install, most commonly found in the 'common' folder in the Steam directory",
        subtype= 'DIR_PATH'
    )
    mod_directory : StringProperty(
        name="Mod Directory",
        default="",
        description="The location of your custom mod, which will be used if a texture name cannot be found in the vanilla directory",
        subtype= 'DIR_PATH'
    )
    mod_directory_slot_active_index : IntProperty()

# ============================================================================================
# LISTS
# ============================================================================================

    clothing_item_slot_active_index : IntProperty()
    outfit_slot_active_index : IntProperty()
    hair_style_slot_active_index : IntProperty()
    beard_style_slot_active_index : IntProperty()
    decal_slot_active_index : IntProperty()
    body_location_active_index : IntProperty()

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

# region UI

# region Scene Rigs UI

class PZ_HumanRig_SceneRigsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_scene_rigs_panel"
    bl_label = "Zomboid Human Scene Rigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    
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
    
    @classmethod
    def poll(cls, context):
        try:
            return context.active_object.get("rig_id") == "ZOMBOID_Human"
        except:
            return False
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        layout.label(text='Rig Instance: ' + str(prop.rig_instance))
        layout.prop(prop, 'debug_toggle')

        layout.operator('zomboid.duplicate_rig')
        
        if prop.debug_toggle:
            layout.prop(prop, 'rig_collection')
            layout.prop(prop, 'male_body_object')
            layout.prop(prop, 'translation_data_empty')
            layout.prop(prop, 'dummy01_empty')
            
            layout.separator()

            layout.prop(prop, 'body_mat')
            layout.prop(prop, 'mask_data')
            layout.prop(prop, 'injury_tex')

            layout.separator()
            
            layout.prop(prop, 'current_male_hair_style')
            layout.prop(prop, 'current_beard_style')
            layout.prop(prop, 'current_female_hair_style')
            layout.prop(prop, 'current_hat_category')

# ============================================================================================
# CONSTRAINTS PANEL
# ============================================================================================

class PZ_HumanRig_ConstraintsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_constraints_panel"
    bl_label = "Constraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        main_column = layout.column()
        
        subpanel, panel_area = main_column.panel("head_rotation_subpanel", default_closed=False)
        subpanel.label(text='Head Rotation')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            column.use_property_split = True
            
            column.prop(prop, "head_lookpoint")
            column.prop(prop, "lookpoint_parent")
            if prop.lookpoint_parent_index == 4:
                column.prop(prop, "lookpoint_parent_object")
        
        main_column.separator(factor=2.0, type='LINE')
        
        subpanel, panel_area = main_column.panel("ik_fk_subpanel", default_closed=False)
        subpanel.label(text='Inverse Kinematics')
        
        if panel_area:
            box = panel_area.box()
            
            main_row = box.row()
            
            left_column = main_row.column()
            left_column.use_property_split = True
            
            sub_box = left_column.box()
            
            sub_box.label(text="Left Arm")
            sub_box.prop(prop, "arm_ik_l", text='IK')
            sub_box.prop(prop, "left_arm_ik_control_parent", text='Control Parent')
            sub_box.prop(prop, "left_arm_ik_pole_parent", text='Pole Parent')
            sub_box.separator(factor=0.5)
            
            left_column.separator()
            
            sub_box = left_column.box()
            
            sub_box.label(text="Left Leg")
            sub_box.prop(prop, "leg_ik_l", text='IK')
            sub_box.prop(prop, "left_leg_ik_control_parent", text='Control Parent')
            sub_box.prop(prop, "left_leg_ik_pole_parent", text='Pole Parent')
            sub_box.separator(factor=0.5)

            right_column = main_row.column()
            right_column.use_property_split = True
            
            sub_box = right_column.box()
            
            sub_box.label(text="Right Arm")
            sub_box.prop(prop, "arm_ik_r", text='IK')
            sub_box.prop(prop, "right_arm_ik_control_parent", text='Control Parent')
            sub_box.prop(prop, "right_arm_ik_pole_parent", text='Pole Parent')
            sub_box.separator(factor=0.5)
            
            right_column.separator()
            
            sub_box = right_column.box()
            
            sub_box.label(text="Right Leg")
            sub_box.prop(prop, "leg_ik_r", text='IK')
            sub_box.prop(prop, "right_leg_ik_control_parent", text='Control Parent')
            sub_box.prop(prop, "right_leg_ik_pole_parent", text='Pole Parent')
            sub_box.separator(factor=0.5)
            
            box.separator()
            column = box.column()
            column.prop(prop, 'all_ik_control_parent')
            column.prop(prop, 'all_ik_pole_parent')
        
        main_column.separator(factor=2.0, type='LINE')
        
        subpanel, panel_area = main_column.panel("dress_prop_backpack_subpanel", default_closed=False)
        subpanel.label(text='Props & Dress')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            left_column = row.column()
            left_column.use_property_split = True
            left_column.prop(prop, 'left_prop_parent')
            if prop.left_prop_parent_index == 3:
                left_column.prop(prop, 'left_prop_parent_object')
            
            right_column = row.column()
            right_column.use_property_split = True
            right_column.prop(prop, 'right_prop_parent')
            if prop.right_prop_parent_index == 3:
                right_column.prop(prop, 'right_prop_parent_object')
            
            column.separator(factor=2.0, type='LINE')
            
            row = column.row()
            row.use_property_split = True
            row.prop(prop, 'backpack_parent')
            
            column.separator(factor=2.0, type='LINE')
            
            row = column.row()
            row.use_property_split = True
            row.prop(prop, 'dress_parent')
        
        main_column.separator(factor=2.0, type='LINE')
        
        subpanel, panel_area = main_column.panel("wrist_twist_subpanel", default_closed=False)
        subpanel.label(text='Auto Wrist Twist')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            row.prop(prop, 'auto_wrist_twist')
            if prop.auto_wrist_twist:
                row.prop(prop, 'wrist_twist_amount')
            
# ============================================================================================
# CONTROLS PANEL
# ============================================================================================

class PZ_HumanRig_ControlsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_controls_panel"
    bl_label = "Controls"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        column = layout.column()
        
        row = column.row()
        
        row.prop(prop, "widgets_size")
        row.prop(prop, "auto_hide_controls")
        
        column.separator(factor=2.5, type="LINE")
        
        row = column.row()
        row.prop(prop, "toggle_root_controls", toggle=True)
        
        row = column.row()
        row.prop(prop, "toggle_translation_data_controls", toggle=True)
        
        column.separator()
        
        row = column.row()
        row.prop(prop, "toggle_left_hand_controls", toggle=True)
        row.prop(prop, "toggle_right_hand_controls", toggle=True)
        
        row = column.row()
        row.prop(prop, "toggle_left_finger_controls", toggle=True)
        row.prop(prop, "toggle_right_finger_controls", toggle=True)
        
        column.separator()
        
        row = column.row()
        row.prop(prop, "toggle_left_prop_controls", toggle=True)
        row.prop(prop, "toggle_right_prop_controls", toggle=True)
        
        row = column.row()
        row.prop(prop, "toggle_backpack_controls", toggle=True)
        
        row = column.row()
        row.prop(prop, "toggle_dress_controls", toggle=True)
        
        column.separator()
        
        row = column.row()
        row.prop(prop, "toggle_left_foot_controls", toggle=True)
        row.prop(prop, "toggle_right_foot_controls", toggle=True)
        
        column.separator()
        
        row = column.row()
        row.prop(prop, "toggle_left_shoulder_controls", toggle=True)
        row.prop(prop, "toggle_right_shoulder_controls", toggle=True)
        
        column.separator()
        
        row = column.row()
        row.prop(prop, "toggle_pelvis_controls", toggle=True)
        row.prop(prop, "toggle_spine_controls", toggle=True)
        row.prop(prop, "toggle_chest_controls", toggle=True)
        
        if not prop.auto_hide_controls:
            
            column.separator()
            
            # Head Control Toggles
            row = column.row()
            row.prop(prop, "toggle_head_controls", toggle=True)
            row = column.row()
            row.prop(prop, "toggle_look_point_controls", toggle=True)
            
            column.separator()
            
            # FK Arm Control Toggles
            row = column.row()
            row.prop(prop, "toggle_left_arm_fk_controls", toggle=True)
            row.prop(prop, "toggle_right_arm_fk_controls", toggle=True)
            
            # FK Leg Control Toggles
            row = column.row()
            row.prop(prop, "toggle_left_leg_fk_controls", toggle=True)
            row.prop(prop, "toggle_right_leg_fk_controls", toggle=True)
            
            column.separator()
            
            # IK Arm Control Toggles
            row = column.row()
            row.prop(prop, "toggle_left_arm_ik_controls", toggle=True)
            row.prop(prop, "toggle_right_arm_ik_controls", toggle=True)
            
            # IK Leg Control Toggles
            row = column.row()
            row.prop(prop, "toggle_left_leg_ik_controls", toggle=True)
            row.prop(prop, "toggle_right_leg_ik_controls", toggle=True)

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
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        main_column = layout.column()
        
        column = main_column.column()
        
        row = column.row()
        row.scale_y = 1.5
        row.prop(prop, "model_sex", expand=True)
        
        column.separator(factor=2)
        
        row = column.row()
        row.prop_search(prop, 'selected_clothing_item', context.scene, 'pz_human_clothing_item_slots')
        
        row = column.row()
        row.operator('zomboid.remove_all_clothing_items')
        
        column.separator(factor=2)
        
        subpanel, panel_area = column.panel("body_model_subpanel", default_closed=False)
        subpanel.label(text='Body')
        
        subpanel.prop(prop, "show_body")
        
        if prop.show_body and panel_area:
            box = panel_area.box()
            column = box.column()
        
            column.label(text="Body Mesh")
            column.separator(factor=0.5)    
            
            row = column.row()
            row.prop(prop, "use_skeleton")
            if not prop.use_skeleton:
                row.prop(prop, "show_dress")
            
            if not prop.use_skeleton:
            
                column.separator(factor=3, type='LINE')    
                column.label(text="Body Masks")
                column.separator(factor=0.5)    
                
                subcolumn = column.column(align=True)
                
                row = subcolumn.row(align=True)
                for index in range(6):
                    row.prop(prop, "mask_array", text=str(index), index=index, toggle=True)
                
                row = subcolumn.row(align=True)
                for index in range(6, 12):
                    row.prop(prop, "mask_array", text=str(index), index=index, toggle=True)
                    
                row = subcolumn.row(align=True)
                for index in range(12, 17):
                    row.prop(prop, "mask_array", text=str(index), index=index, toggle=True)    
                
                subcolumn.separator()
                
                column.separator(factor=3, type='LINE')    
                column.label(text="Body Damage")
                column.separator(factor=0.5) 
                
                box = column.box()
                
                body_injury_subpanel, body_injury_panel_area = box.panel("body_injury_subpanel", default_closed=False)
                body_injury_subpanel.label(text='Body Injuries')
                
                if body_injury_panel_area:
                    sub_col = body_injury_panel_area.column()
                    sub_col.prop(prop, 'upper_torso_injury')
                    sub_col.prop(prop, 'lower_torso_injury')
                    sub_col.prop(prop, 'left_hand_injury')
                    sub_col.prop(prop, 'right_hand_injury')
                    sub_col.prop(prop, 'left_forearm_injury')
                    sub_col.prop(prop, 'right_forearm_injury')
                    sub_col.prop(prop, 'left_upperarm_injury')
                    sub_col.prop(prop, 'right_upperarm_injury')
                    sub_col.prop(prop, 'head_injury')
                    sub_col.prop(prop, 'neck_injury')
                    sub_col.prop(prop, 'groin_injury')
                    sub_col.prop(prop, 'left_thigh_injury')
                    sub_col.prop(prop, 'right_thigh_injury')
                    sub_col.prop(prop, 'left_shin_injury')
                    sub_col.prop(prop, 'right_shin_injury')
                    sub_col.prop(prop, 'left_foot_injury')
                    sub_col.prop(prop, 'right_foot_injury')

                    sub_box = sub_col.box()
                    
                    sub_box.prop(prop, 'random_scratch_chance')
                    sub_box.prop(prop, 'random_laceration_chance')
                    sub_box.prop(prop, 'random_bite_chance')
                    sub_box.prop(prop, 'random_bandage_chance')
                    sub_box.prop(prop, 'random_bloody_bandage_chance')
                    row = sub_box.row()
                    row.prop(prop, 'random_injury_intensity')
                    row.operator('zomboid.randomize_body_injuries')

                    sub_col.operator('zomboid.remove_all_body_injuries')
                

                zombie_injury_subpanel, zombie_injury_panel_area = box.panel("zombie_injury_subpanel", default_closed=False)
                zombie_injury_subpanel.label(text='Zombie Injuries')
                
                if zombie_injury_panel_area:
                    sub_col = zombie_injury_panel_area.column()
                    sub_col.prop(prop, 'selected_zombie_injury')
                    sub_col.template_list("PZ_UL_ZombieInjuryList", "pz_zombie_injury_list", context.object, "pz_human_zombie_injuries", context.object.pz_human_props, "zombie_injury_active_index")
                    if prop.zombie_injury_active_index != -1:
                        sub_col.operator('zomboid.remove_zombie_injury')
                    row = sub_col.row()
                    row.prop(prop, 'random_zombie_injury_intensity')
                    row.operator('zomboid.randomize_zombie_injuries')
                    sub_col.operator('zomboid.remove_all_zombie_injuries')

                bloodiness_subpanel, bloodiness_panel_area = box.panel("bloodiness_subpanel", default_closed=False)
                bloodiness_subpanel.label(text='Bloodiness')
                
                if bloodiness_panel_area:
                    sub_col = bloodiness_panel_area.column()
                    sub_col.prop(prop, 'upper_torso_bloodiness')
                    sub_col.prop(prop, 'lower_torso_bloodiness')
                    sub_col.prop(prop, 'left_hand_bloodiness')
                    sub_col.prop(prop, 'right_hand_bloodiness')
                    sub_col.prop(prop, 'left_forearm_bloodiness')
                    sub_col.prop(prop, 'right_forearm_bloodiness')
                    sub_col.prop(prop, 'left_upperarm_bloodiness')
                    sub_col.prop(prop, 'right_upperarm_bloodiness')
                    sub_col.prop(prop, 'head_bloodiness')
                    sub_col.prop(prop, 'neck_bloodiness')
                    sub_col.prop(prop, 'groin_bloodiness')
                    sub_col.prop(prop, 'left_thigh_bloodiness')
                    sub_col.prop(prop, 'right_thigh_bloodiness')
                    sub_col.prop(prop, 'left_shin_bloodiness')
                    sub_col.prop(prop, 'right_shin_bloodiness')
                    sub_col.prop(prop, 'left_foot_bloodiness')
                    sub_col.prop(prop, 'right_foot_bloodiness')
                    sub_col.prop(prop, 'back_bloodiness')
                    row = sub_col.row()
                    row.prop(prop, 'random_bloodiness_intensity')
                    row.operator('zomboid.randomize_body_bloodiness')
                    sub_col.operator('zomboid.remove_body_bloodiness')
                
                dirtiness_subpanel, dirtiness_panel_area = box.panel("dirtiness_subpanel", default_closed=False)
                dirtiness_subpanel.label(text='Dirtiness')
                
                if dirtiness_panel_area:
                    sub_col = dirtiness_panel_area.column()
                    sub_col.prop(prop, 'upper_torso_dirtiness')
                    sub_col.prop(prop, 'lower_torso_dirtiness')
                    sub_col.prop(prop, 'left_hand_dirtiness')
                    sub_col.prop(prop, 'right_hand_dirtiness')
                    sub_col.prop(prop, 'left_forearm_dirtiness')
                    sub_col.prop(prop, 'right_forearm_dirtiness')
                    sub_col.prop(prop, 'left_upperarm_dirtiness')
                    sub_col.prop(prop, 'right_upperarm_dirtiness')
                    sub_col.prop(prop, 'head_dirtiness')
                    sub_col.prop(prop, 'neck_dirtiness')
                    sub_col.prop(prop, 'groin_dirtiness')
                    sub_col.prop(prop, 'left_thigh_dirtiness')
                    sub_col.prop(prop, 'right_thigh_dirtiness')
                    sub_col.prop(prop, 'left_shin_dirtiness')
                    sub_col.prop(prop, 'right_shin_dirtiness')
                    sub_col.prop(prop, 'left_foot_dirtiness')
                    sub_col.prop(prop, 'right_foot_dirtiness')
                    sub_col.prop(prop, 'back_dirtiness')
                    row = sub_col.row()
                    row.prop(prop, 'random_dirtiness_intensity')
                    row.operator('zomboid.randomize_body_dirtiness')
                    sub_col.operator('zomboid.remove_body_dirtiness')

                box.operator('zomboid.remove_all_body_damage')

            column.separator(factor=3, type='LINE')    
            column.label(text="Body Textures")
            column.separator(factor=0.5)    
            
            box = column.box()
            column = box.column()
            row = column.row()
        
            if not prop.use_skeleton:
                row.prop(prop, "use_skin_textures")
            
                row = column.row()
                
                if prop.use_skin_textures:
                    row.prop(prop, "skin_color")
                    row.prop(prop, "zombification")
                
                column.separator(factor=2)
                
                row = column.row()
                
                row.label(text="Body Clothing Textures")
                
                row = column.row(align=True)
                
                row.template_list("PZ_UL_BodyTextureList", "pz_body_texture_list", context.object, "pz_human_body_texture_slots", context.object.pz_human_props, "body_texture_slot_active_index")
                
                side_column = row.column(align=True)
                
                if prop.body_texture_slot_active_index != -1:
                    side_column.operator("zomboid.remove_body_texture_slot", text="", icon="REMOVE")
                    
                    column.separator()
                    
                    side_column.operator("zomboid.move_body_texture_slot_up", icon="TRIA_UP", text="")
                    side_column.operator("zomboid.move_body_texture_slot_down", icon="TRIA_DOWN", text="")
  
                
                column.separator(factor=1.5)
                row = column.row()
        
                if prop.body_texture_slot_active_index != -1:
                    row.label(text="Current Slot Properties")
                    tex_prop = context.active_object.pz_human_body_texture_slots[prop.body_texture_slot_active_index]
                    
                    box = column.box()
                    column = box.column()
                    
                    row = column.row()
                    row.prop(tex_prop, "tintable")
                    if tex_prop.tintable:
                        row.prop(tex_prop, "tint_color")
                    
                    row = column.row()
                    row.prop(tex_prop, "opacity")
                    
            else:
                row.prop(prop, "skeleton_type")
        
        main_column.separator(factor=1.5, type='LINE')
        
        subpanel, panel_area = main_column.panel("clothing_model_subpanel", default_closed=True)
        subpanel.label(text='Clothes')
        
        subpanel.prop(prop, "show_clothing")
        
        if panel_area and prop.show_clothing:
            box = panel_area.box()
            column = box.column()
            
            row = column.row()
            row.label(text="Clothing Models")
            column.separator(factor=0.5)    
            
            row = column.row(align=True)
            side_column = row.column(align=True)
            
            side_column.template_list("PZ_UL_ClothingMeshList", "pz_clothing_mesh_list", context.object, "pz_human_clothing_mesh_slots", context.object.pz_human_props, "clothing_mesh_slot_active_index")
            
            side_column = row.column(align=True)
            
            if prop.clothing_mesh_slot_active_index != -1:
                side_column.operator("zomboid.remove_clothing_mesh_slot", text="", icon="REMOVE")
            
            column.separator(factor=1.5)
            row = column.row()
            
            if prop.clothing_mesh_slot_active_index != -1:
                row.label(text="Current Slot Properties")
                mesh_prop = context.active_object.pz_human_clothing_mesh_slots[prop.clothing_mesh_slot_active_index]
                
                box = column.box()
                column = box.column()
                
                row = column.row()
                row.prop(mesh_prop, "tintable")
                if mesh_prop.tintable:
                    row.prop(mesh_prop, "tint_color")
        
        main_column.separator(factor=1.5, type='LINE')
        
        subpanel, panel_area = main_column.panel("prop_model_subpanel", default_closed=True)
        subpanel.label(text='Props')
        
        subpanel.prop(prop, "show_props")
        
        if panel_area and prop.show_hair:
            box = panel_area.box()
            column = box.column()
            
            row = column.row()
            row.label(text="Prop Models")
            column.separator(factor=0.5)    
            
            row = column.row(align=True)
            side_column = row.column(align=True)
            
            side_column.template_list("PZ_UL_PropMeshList", "pz_prop_mesh_list", context.object, "pz_human_prop_mesh_slots", context.object.pz_human_props, "prop_mesh_slot_active_index")
            
            side_column = row.column(align=True)
            
            if prop.prop_mesh_slot_active_index != -1:
                side_column.operator("zomboid.remove_prop_mesh_slot", text="", icon="REMOVE")
            
            column.separator(factor=1.5)
            row = column.row()
            
            if prop.prop_mesh_slot_active_index != -1:
                row.label(text="Current Slot Properties")
                mesh_prop = context.active_object.pz_human_prop_mesh_slots[prop.prop_mesh_slot_active_index]
                
                box = column.box()
                column = box.column()
                
                row = column.row()
                row.prop(mesh_prop, "tintable")
                if mesh_prop.tintable:
                    row.prop(mesh_prop, "tint_color")
        
        main_column.separator(factor=1.5, type='LINE')
        
        subpanel, panel_area = main_column.panel("hair_model_subpanel", default_closed=True)
        subpanel.label(text='Hair')
        
        subpanel.prop(prop, "show_hair")
        
        if panel_area and prop.show_hair:
            box = panel_area.box()
            column = box.column()
            
            row = column.row()
            
            row.prop(prop, 'hair_color')
            row.operator('zomboid.randomize_hair_color', text='', icon='FILE_REFRESH')
            row.prop(prop, 'hair_texture_type')
            
            column.separator(factor=1.5, type='LINE')
            
            row = column.row(align=True)
            
            if prop.model_sex_index == 0:
                row.prop_search(prop, 'selected_male_hair_style', context.scene, 'pz_human_male_hair_styles')
                row.operator('zomboid.randomize_hair_mesh', text='', icon='FILE_REFRESH').hair_type = 'M'
                
                column.separator()
                
                row = column.row(align=True)
                row.prop_search(prop, 'selected_beard_style', context.scene, 'pz_human_beard_styles')
                row.operator('zomboid.randomize_hair_mesh', text='', icon='FILE_REFRESH').hair_type = 'B'
            else:
                row.prop_search(prop, 'selected_female_hair_style', context.scene, 'pz_human_female_hair_styles')
                row.operator('zomboid.randomize_hair_mesh', text='', icon='FILE_REFRESH').hair_type = 'F'
        
        main_column.separator(factor=1.5)
        
        main_column.separator(factor=3.0)
        
        subpanel, panel_area = main_column.panel("presets_subpanel", default_closed=False)
        subpanel.label(text='Outfits')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            row.prop_search(prop, 'selected_outfit', context.scene, 'pz_human_outfit_slots', item_search_property='search_name')
            
            row = column.row()
            
            row.prop(prop, 'random_zombie')
            row.prop(prop, 'random_skin_color')
            
            row = column.row()
            
            row.prop(prop, 'random_hair_style')
            row.prop(prop, 'random_hair_color')
            
            row = column.row()
            
            row.prop(prop, 'natural_hair_color')
            
            row = column.row()
            
            row.prop(prop, 'random_beard_chance', slider=True)
            
            row = column.row()
            row.prop(prop, 'randomize_injuries')
            
            if prop.randomize_injuries:
                box=column.box()
                
                box.prop(prop, 'random_bloodiness_intensity')
                box.prop(prop, 'random_dirtiness_intensity')
                
                box.separator()
                
                box.prop(prop, 'random_injury_intensity')
                box.prop(prop, 'random_zombie_injury_intensity')

                box.separator()

                box.prop(prop, 'random_scratch_chance')
                box.prop(prop, 'random_laceration_chance')
                box.prop(prop, 'random_bite_chance')

                box.separator()
                
                box.prop(prop, 'random_bandage_chance')
                box.prop(prop, 'random_bloody_bandage_chance')
            
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
#            row.prop(prop, "use_outline")
#            if prop.use_outline:
#                column.separator()
#                row = column.row()
#                row.prop(prop, "outline_size")
#                row.prop(prop, "outline_color")

# ============================================================================================
# SHADING PANEL
# ============================================================================================

class PZ_HumanRig_ShadingPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_shading_panel"
    bl_label = "Shading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        column = layout.column()
        row = column.row()
        row.scale_y = 1.5
        row.prop(prop, "shading_type", expand=True)
        
        column.separator()
        
        row = column.row()

        match prop.shading_type_index:
            case 0:
                row.prop(prop, 'emission_strength')
            case 1:
                row.prop(prop, 'roughness')
                row.prop(prop, 'metallic')
            case 2:
                row.prop_search(prop, 'custom_shading_group_name', bpy.data, 'node_groups')

                selected_group = bpy.data.node_groups.get(prop.custom_shading_group_name)

                if selected_group.bl_idname != 'ShaderNodeTree':
                    column.label(text='Selected group is not a Shader Node group')
                else:
                    inputs = 0
                    outputs = 0
                    for item in list(selected_group.interface.items_tree):
                        if item.in_out == 'INPUT':
                            if inputs > 1:
                                column.label(text='Inputs after the second input will not be read')
                            if inputs == 0:
                                if item.name != 'Color':
                                    column.label(text='The first input is not named \'Color\'')
                                if item.socket_type != 'NodeSocketColor':
                                    column.label(text='The first input is not a Color type')
                            elif inputs == 1:
                                if item.name != 'Alpha':
                                    column.label(text='The first input is not named \'Alpha\'')
                                if item.socket_type != 'NodeSocketFloat':
                                    column.label(text='The first input is not a Float type')
                            inputs = inputs + 1
                        elif item.in_out == 'OUTPUT':
                            if outputs > 0:
                                column.label(text='Outputs after the first output will not be evaluated')
                            if outputs == 0:
                                if item.name != 'Shader':
                                    column.label(text='The first output is not named \'Shader\'')
                                if item.socket_type != 'NodeSocketShader':
                                    column.label(text='The first output is not a Shader type')

        column.separator()
        
        row = column.row()
        row.prop(prop, 'texture_interpolation')
            
# ============================================================================================
# EXPORT PANEL
# ============================================================================================

class PZ_HumanRig_ExportPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_export_panel"
    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "VIEW3D_PT_pz_human_rig_main_panel"
    
    def draw(self, context):
        layout = self.layout
        prop = context.active_object.pz_human_props
        
        column = layout.column()
        
        row = column.row()
        row.prop(prop, "file_output_path")
        
        row = column.row()
        row.alignment = 'LEFT'
        row.prop(prop, "batch_export")
        
        if prop.batch_export:
            row.prop(prop, "action_filter")
        
        row = column.row()
        row.operator("zomboid.export_glb_button")

#-------------------------------------------------------------#
# Export Button

class PZ_HumanRig_ExportButton(Operator):
    bl_idname = "zomboid.export_glb_button"
    bl_label = "Export GLBs for Project Zomboid"
    
    def execute(self, context):
        bpy.ops.zomboid.export_glb('INVOKE_DEFAULT')
        return {'FINISHED'}

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
    
    def draw(self, context):
        layout = self.layout

# ============================================================================================
# DIRECTORIES PANEL
# ============================================================================================

class PZ_UL_ModDirectoryList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name)

class PZ_HumanRig_DirectoriesPanel(Panel):
    bl_idname = "PROPERTIES_PT_pz_human_rig_directories_panel"
    bl_label = "Directories"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = "PROPERTIES_PT_pz_human_rig_global_panel"
    
    def draw(self, context):
        layout = self.layout
        global_prop = context.scene.pz_human_global_props
        
        column = layout.column()
        
        column.prop(global_prop, "pz_directory")
      
        column.separator()
                
        
        column.label(text="Mod Directories")
        
        row = column.row()

        row.operator('zomboid.get_all_mod_directories')
        row.operator('zomboid.remove_all_mod_directories')

        row = column.row(align=True)
        
        row.template_list("PZ_UL_ModDirectoryList", "pz_mod_directory_list", context.scene, "pz_human_mod_directory_slots", context.scene.pz_human_global_props, "mod_directory_slot_active_index")
        
        side_column = row.column(align=True)

        side_column.operator("zomboid.add_mod_directory_slot", text="", icon="ADD")
        
        if global_prop.mod_directory_slot_active_index != -1:
            side_column.operator("zomboid.remove_mod_directory_slot", text="", icon="REMOVE")
            
            dir_prop = context.scene.pz_human_mod_directory_slots[global_prop.mod_directory_slot_active_index]

            box = column.box()
            
            box.label(text = 'Mod Author:                                            ' + dir_prop.author)
            box.label(text = 'Latest PZ Version:                                   ' + str(round(dir_prop.latest_pz_version, 2)))
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

class PZ_HumanRig_AssetsPanel(Panel):
    bl_idname = "PROPERTIES_PT_pz_human_rig_assets_panel"
    bl_label = "Assets"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_parent_id = "PROPERTIES_PT_pz_human_rig_global_panel"
    
    def draw(self, context):
        layout = self.layout
        global_prop = context.scene.pz_human_global_props
        
        main_column = layout.column()
        
        main_column.operator('zomboid.parse_all_xmls')
        main_column.operator('zomboid.clear_all_xmls')
        
        subpanel, panel_area = main_column.panel("clothing_items_subpanel", default_closed=True)
        subpanel.label(text='Clothing Items')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            row.operator("zomboid.parse_clothing_xmls")
            
            row = column.row(align=True)
            
            row.template_list("PZ_UL_ClothingItemList", "pz_clothing_item_list", context.scene, "pz_human_clothing_item_slots", context.scene.pz_human_global_props, "clothing_item_slot_active_index")
                
            column.separator()
            
            row = column.row()
            
            if global_prop.clothing_item_slot_active_index != -1:
                row.label(text="Clothing Item Properties")
                item_prop = context.scene.pz_human_clothing_item_slots[global_prop.clothing_item_slot_active_index]
                
                box = column.box()
                split = box.split()
                sub_column = split.column()
                
                sub_column.label(text="GUID:                             " + item_prop.guid)
                sub_column.label(text="Male Model Path:         " + item_prop.male_model_path)
                sub_column.label(text="Female Model Path:     " + item_prop.female_model_path)
                sub_column.label(text="Model Type:                  " + item_prop.model_type)
                sub_column.label(text="Tintable:                        " + str(item_prop.tintable))
                sub_column.label(text="Body Location:             " + item_prop.body_location.name)
                
                sub_column = split.column()
                
                sub_column.label(text="Static:                                         " + str(item_prop.static))
                sub_column.label(text="Attach Bone:                             " + item_prop.attach_bone)
                sub_column.label(text="Is Body Texture:                       " + str(item_prop.is_body_texture))
                sub_column.label(text="Hat Category:                           " + str(item_prop.hat_category))
                sub_column.label(text="Decal Group:                             " + str(item_prop.decal_group))
                sub_column.label(text="Origin:                                        " + item_prop.origin)
                
                
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
                    
                
        subpanel, panel_area = main_column.panel("outfits_subpanel", default_closed=True)
        subpanel.label(text='Outfits')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            row.operator("zomboid.parse_outfit_xmls")
            
            row = column.row(align=True)
            
            row.template_list("PZ_UL_OutfitList", "pz_outfit_list", context.scene, "pz_human_outfit_slots", context.scene.pz_human_global_props, "outfit_slot_active_index")
                
            column.separator()
            
            row = column.row()
            
            if global_prop.outfit_slot_active_index != -1:
                row.label(text="Outfit Properties")
                item_prop = context.scene.pz_human_outfit_slots[global_prop.outfit_slot_active_index]
                
                box = column.box()
                split = box.split()
                column = split.column()
                
                column.label(text="GUID:                             " + item_prop.guid)
                column.label(text="Random Top:                " + str(item_prop.random_top))
                column.label(text="Random Pants:             " + str(item_prop.random_pants))
                column.label(text="Origin:                            " + str(item_prop.origin))
                
                for outfit_item in item_prop.outfit_items:
                    column.separator(factor=2.0)
                    column.label(text=str(round(outfit_item.probability * 100, 2)) + '% chance for one of the following:')
                    for choice in outfit_item.choices:
                        column.label(text='- ' + choice.name)
                    
                    
        subpanel, panel_area = main_column.panel("hair_styles_subpanel", default_closed=True)
        subpanel.label(text='Hair Styles')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            row = column.row()
            
            row.operator("zomboid.parse_hair_style_xmls")
            
            row = column.row(align=True)
            
            row.template_list("PZ_UL_HairStyleList", "pz_hair_style_list", context.scene, "pz_human_hair_style_slots", context.scene.pz_human_global_props, "hair_style_slot_active_index")
            
            column.separator()
            
            row = column.row()
            
            if global_prop.hair_style_slot_active_index != -1:
                row.label(text="Hair Properties")
                item_prop = context.scene.pz_human_hair_style_slots[global_prop.hair_style_slot_active_index]
                
                box = column.box()
                split = box.split()
                sub_column = split.column()
                
                sub_column.label(text='Model Path:        ' + item_prop.model_path)
                sub_column.label(text='Texture Type:      ' + item_prop.texture_type)
                sub_column.label(text='Hair Level:           ' + str(item_prop.level))
                
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
                
                
        
        subpanel, panel_area = main_column.panel("beard_styles_subpanel", default_closed=True)
        subpanel.label(text='Beard Styles')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()

            row = column.row(align=True)
            
            row.template_list("PZ_UL_BeardStyleList", "pz_beard_style_list", context.scene, "pz_human_beard_styles", context.scene.pz_human_global_props, "beard_style_slot_active_index")
            
            column.separator()
            
            row = column.row()
            
            if global_prop.beard_style_slot_active_index != -1:
                row.label(text="Beard Properties")
                item_prop = context.scene.pz_human_beard_styles[global_prop.beard_style_slot_active_index]
                
                box = column.box()
                split = box.split()
                column = split.column()
                
                column.label(text='Model Path:        ' + item_prop.model_path)
                column.label(text='Beard Level:           ' + str(item_prop.level))
        
        
        
        subpanel, panel_area = main_column.panel("decals_subpanel", default_closed=True)
        subpanel.label(text='Decals')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            
            row = column.row()
            
            row.operator("zomboid.parse_decal_xmls")
            
            row = column.row(align=True)
            
            row.template_list("PZ_UL_DecalsList", "pz_decals_list", context.scene, "pz_human_decals", context.scene.pz_human_global_props, "decal_slot_active_index")
            
            column.separator()
            
            row=column.row()
            
            if global_prop.decal_slot_active_index != -1:
                row.label(text="Decal Properties")
                item_prop = context.scene.pz_human_decals[global_prop.decal_slot_active_index]
                
                box = column.box()
                split = box.split()
                column = split.column()
                              
                column.label(text='Texture Path:         ' + item_prop.texture_path)
                column.label(text='X Position:             ' + str(item_prop.x_pos))
                column.label(text='Y Position:             ' + str(item_prop.y_pos))
                column.label(text='Width:                    ' + str(item_prop.width))
                column.label(text='Height:                   ' + str(item_prop.height))
        
        subpanel, panel_area = main_column.panel("body_locations_subpanel", default_closed=True)
        subpanel.label(text='Body Locations')
        
        if panel_area:
            box = panel_area.box()
            column = box.column()
            
            row = column.row()
            
            row.template_list("PZ_UL_BodyLocationList", "pz_body_location_list", context.scene, "pz_human_body_locations", context.scene.pz_human_global_props, "body_location_active_index")
            
            column.separator()
            
            row=column.row()
            
            if global_prop.body_location_active_index != -1:
                row.label(text="Body Location Properties")
                item_prop = context.scene.pz_human_body_locations[global_prop.body_location_active_index]
                
                box = column.box()
                split = box.split()
                column = split.column()
                
                if len(item_prop.properties.hide_locations) > 0:
                    column.label(text='Body Location will be hidden if any of these locations are used:')
                    column.separator(factor=0.5)
                    
                    for loc in item_prop.properties.hide_locations:
                        column.label(text=loc.name)
                    
                    column.separator()
                
                if len(item_prop.properties.alt_locations) > 0:
                    column.label(text='Body Location will use an alternate model if any of these locations are used:')
                    column.separator(factor=0.5)
                    
                    for loc in item_prop.properties.alt_locations:
                        column.label(text=loc.name)
                    
                    column.separator()
                
                if len(item_prop.properties.exclusive_locations) > 0:
                    column.label(text='Body Location cannot be equpped if any of these locations are used (will be hidden in Blender):')
                    column.separator(factor=0.5)
                    
                    for loc in item_prop.properties.exclusive_locations:
                        column.label(text=loc.name)
                    
                    column.separator()

# endregion

# endregion

#=================================================================================================================================================
#=================================================================================================================================================

# region Registering

'''
This is the area that registers all of the custom classes for the rig into Blender.
There are a lot of classes, so it's a bit of a mess. Note that order matters.
'''

object_classes = [PZ_BodyLocationRef, PZ_BodyLocationProperties, PZ_BodyLocation,
                  PZ_ShirtDecal, PZ_ShirtDecalGroup, PZ_ZombieInjury,
                  PZ_BodyTextureSlot, PZ_ClothingMeshSlot, PZ_PropMeshSlot,
                  PZ_ClothingItemTextureChoices, PZ_ClothingItemSlot,
                  PZ_OutfitItemChoices, PZ_OutfitItem, PZ_OutfitSlot,
                  PZ_HairStyleHatStyle, PZ_HairStyleSlot,
                  PZ_ModDirectorySlot, PZ_HumanRigObject]

operator_classes = [PZ_ConstructBodyTexture, PZ_HumanRig_CreateBodyInjuryTexture,
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
                    PZ_HumanRig_ParseClothingXMLs, PZ_HumanRig_ParseOutfitXMLs,
                    PZ_HumanRig_ParseHairStyleXMLs, PZ_HumanRig_ParseDecalXMLs,
                    PZ_HumanRig_ParseBodyLocationLua, PZ_HumanRig_ParseAllXMLs,PZ_HumanRig_ClearAllXMLs,
                    PZ_HumanRig_ApplyOutfit, PZ_HumanRig_ApplyRandomOutfit, PZ_HumanRig_AddClothingItem,
                    PZ_HumanRig_RemoveAllClothingItems, PZ_CheckHatCategory, PZ_HumanRig_Export,
                    PZ_HumanRig_DuplicateRig
                    ]

property_classes = [PZ_HumanRigProperties, PZ_HumanRigGlobalProperties]

scene_rig_ui_classes = [PZ_HumanRig_SceneRigsPanel]

rig_ui_classes = [PZ_UL_BodyTextureList, PZ_UL_ClothingMeshList, PZ_UL_PropMeshList,
                  PZ_UL_ZombieInjuryList, PZ_HumanRig_ExportButton,
                  PZ_HumanRig_MainPanel, PZ_HumanRig_ConstraintsPanel, PZ_HumanRig_ControlsPanel,
                  PZ_HumanRig_ModelPanel, PZ_HumanRig_ShadingPanel, PZ_HumanRig_ExportPanel,
                 ]

scene_ui_classes = [PZ_UL_ModDirectoryList, PZ_UL_ClothingItemList, PZ_UL_OutfitList,
                    PZ_UL_HairStyleList, PZ_UL_BeardStyleList, PZ_UL_DecalsList,
                    PZ_UL_BodyLocationList, PZ_HumanRig_GlobalPanel,
                    PZ_HumanRig_DirectoriesPanel, PZ_HumanRig_AssetsPanel]

classes = object_classes + operator_classes + property_classes + scene_rig_ui_classes + rig_ui_classes + scene_ui_classes

def initialize_rigs():
    # TODO make this work on all rigs

    rigs = bpy.context.scene.pz_human_rigs

    # # TEMP FOR TESTING
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
                # Initialize the major data objects on the rig
                prop = obj.pz_human_props

                new_rig = rigs.add()
                new_rig.obj = obj

                prop.rig_instance = len(rigs) - 1

                instance_str = ' (' + str(prop.rig_instance) + ')'
                prop.rig_collection = bpy.data.collections.get('CH-PZ_Human' + instance_str)
                prop.male_body_object = bpy.data.objects.get('OBJ-MaleBody' + instance_str)
                prop.translation_data_empty = bpy.data.objects.get('OBJ-TranslationData' + instance_str)
                prop.dummy01_empty = bpy.data.objects.get('OBJ-Dummy01' + instance_str)

                # TODO: Create new material and mask data if it does not exist

                prop.mask_data = bpy.data.images.get('MASK-MaskData' + instance_str)
                prop.injury_tex = bpy.data.images.get('TEX-BodyInjuries' + instance_str)
                prop.body_mat = bpy.data.materials.get('MAT-HumanBody' + instance_str)

                new_rig.name = 'PZ Human Rig ' + str(obj.pz_human_props.rig_instance)

    for rig in rigs:
        prop = rig.obj.pz_human_props

        mask = prop.mask_data
        rig_obj = rig.obj

        # Force a reload of the generated textures
        if mask is not None and rig_obj is not None:
            bpy.context.view_layer.objects.active = rig_obj
            rig_obj.select_set(True)

            mask.reload()

            bpy.ops.zomboid.create_body_bloodiness_texture()

            mask.reload()

            bpy.ops.zomboid.create_body_bloodiness_texture()
            bpy.ops.zomboid.create_body_dirtiness_texture()
            bpy.ops.zomboid.create_mask_texture()

def register():

    # Register our classes
    for cls in classes:
        bpy.utils.register_class(cls)

    #-------------------------------------------

    # Store our scene properties on the scene
    Scene.pz_human_global_props = PointerProperty(
        type=PZ_HumanRigGlobalProperties,
        name="PZ Human Rig Global Properties"
        )
    
    # Store our scene collections on the scene
    Scene.pz_human_rigs = CollectionProperty(type=PZ_HumanRigObject)
    Scene.pz_human_mod_directory_slots = CollectionProperty(type=PZ_ModDirectorySlot)
    Scene.pz_human_clothing_item_slots = CollectionProperty(type=PZ_ClothingItemSlot)
    Scene.pz_human_outfit_slots = CollectionProperty(type=PZ_OutfitSlot)
    Scene.pz_human_hair_style_slots = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_male_hair_styles = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_female_hair_styles = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_beard_styles = CollectionProperty(type=PZ_HairStyleSlot)
    Scene.pz_human_decal_groups = CollectionProperty(type=PZ_ShirtDecalGroup)
    Scene.pz_human_decals = CollectionProperty(type=PZ_ShirtDecal)
    Scene.pz_human_body_locations = CollectionProperty(type=PZ_BodyLocation)

    #-------------------------------------------

    # Filter method so we only get Zomboid Human rigs
    def poll_bip01(self, object):
        return object.type == 'ARMATURE' and object.name == 'Bip01'
    
    # Store our rig properties on the Zomboid rig object
    Object.pz_human_props = PointerProperty(
        type=PZ_HumanRigProperties,
        name="PZ Human Rig Properties",
        poll=poll_bip01
        )

    # Store the rig collections on the rig object
    Object.pz_human_body_texture_slots = CollectionProperty(type=PZ_BodyTextureSlot)
    Object.pz_human_clothing_mesh_slots = CollectionProperty(type=PZ_ClothingMeshSlot)
    Object.pz_human_prop_mesh_slots = CollectionProperty(type=PZ_PropMeshSlot)
    Object.pz_human_zombie_injuries = CollectionProperty(type=PZ_ZombieInjury)

    initialize_rigs()

def unregister():

    # Unregister our classes
    for cls in classes:
        bpy.utils.unregister_class(cls)

    #-------------------------------------------

    # Remove properties and collections from the rig objects
    del Object.pz_human_props
    del Object.pz_human_body_texture_slots
    del Object.pz_human_clothing_mesh_slots
    del Object.pz_human_prop_mesh_slots
    del Object.pz_human_zombie_injuries

    #-------------------------------------------

    # Remove properties and collections from the scene
    del Scene.pz_human_rigs
    del Scene.pz_human_mod_directory_slots
    del Scene.pz_human_clothing_item_slots
    del Scene.pz_human_outfit_slots
    del Scene.pz_human_hair_style_slots
    del Scene.pz_human_male_hair_styles
    del Scene.pz_human_female_hair_styles
    del Scene.pz_human_beard_styles
    del Scene.pz_human_decal_groups
    del Scene.pz_human_decals
    del Scene.pz_human_body_locations

if __name__ == "__main__":
    register()

# endregion