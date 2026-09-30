# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from mathutils import Matrix
from ..Utility.PZ_AssetMethods import ADDON_ROOT

def switch_body_model(self, context):
    model_properties = context.active_object.pz_model_properties
    object_pointers = context.active_object.pz_object_pointers
    main_properties = context.active_object.pz_main_properties

    models_blend_path = ADDON_ROOT / 'Assets' / 'Blend' / 'CH-PZ_HumanRig_BaseModels.blend'

    # Remove the previous body
    if object_pointers.body_object:
        data = object_pointers.body_object.data
        bpy.data.objects.remove(object_pointers.body_object, do_unlink=True)
        if data:
            bpy.data.meshes.remove(data, do_unlink=True)

    # Get the name of the body object from the models blend file
    obj_name = ''
    match model_properties.human_subtype:
        case 'HUMAN' | 'MANNEQUIN':
            obj_name = 'MaleBody_BASE' if model_properties.model_sex == 'MALE' else 'FemaleBody_BASE'
        case 'SKELETON':
            obj_name = 'MaleSkeleton_BASE' if model_properties.model_sex == 'MALE' else 'FemaleSkeleton_BASE'
        case 'SCARECROW':
            obj_name = 'Scarecrow_BASE'

    with bpy.data.libraries.load(str(models_blend_path)) as (data_from, data_to):
        if obj_name in data_from.objects:
            data_to.objects.append(obj_name)

    # Get the imported object, link it to the models collection
    new_body = bpy.data.objects.get(obj_name)
    object_pointers.model_collection.objects.link(new_body)
    object_pointers.body_object = new_body

    # Rename the imported object and its data
    new_body.name = 'OBJ-Body' + main_properties.get_instance_str(context)
    new_body.data.name = 'GEO-Body' + main_properties.get_instance_str(context)

    # Parent the imported object to the rig
    new_body.parent = object_pointers.rig_object
    new_body.matrix_parent_inverse = object_pointers.rig_object.matrix_world.inverted()

    # Offset the object based on the difference between the rig position and world origin
    new_body.location += object_pointers.rig_object.location / 100

    # Rotate the body to the rig object
    new_body.rotation_euler = object_pointers.rig_object.rotation_euler

    # Scale the body to the rig object
    new_body.scale = object_pointers.rig_object.scale

    # Add the armature modifier to the object, set it to the rig
    arm_modifier = new_body.modifiers.new(name='Armature', type='ARMATURE')
    arm_modifier.object = object_pointers.rig_object

    # Run the update_hide_dress to activate or deactivate the mask modifier
    update_hide_dress(self, context)

    # Set the material on the object
    new_body.active_material = object_pointers.body_material

    # Set initial selection properties
    new_body.hide_select = not model_properties.models_selectable

def switch_clothing_model_sex(self, context):
    model_properties = context.active_object.pz_model_properties
    equipped_clothing = context.active_object.pz_equipped_clothing_items

    for index, item in enumerate(equipped_clothing):
        if item.model_object:
            data = item.model_object.data
            bpy.data.objects.remove(item.model_object, do_unlink=True)
            if data:
                bpy.data.meshes.remove(data, do_unlink=True)

        model_properties.equipped_clothing_item_active_index = index
        if item.data.clothing_type == 'CLOTHINGMODEL':
            bpy.ops.zomboid.import_clothing_model(replace_material=False)
        elif item.data.clothing_type == 'ACCESSORY':
            bpy.ops.zomboid.import_accessory_model(replace_material=False)


def switch_hair_model_sex(self, context):
    object_pointers = context.active_object.pz_object_pointers
    model_properties = context.active_object.pz_model_properties
    
    if object_pointers.hair_object:
        data = object_pointers.hair_object.data
        bpy.data.objects.remove(object_pointers.hair_object, do_unlink=True)
        if data:
            bpy.data.meshes.remove(data, do_unlink=True)

    if object_pointers.beard_object:
        data = object_pointers.beard_object.data
        bpy.data.objects.remove(object_pointers.beard_object, do_unlink=True)
        if data:
            bpy.data.meshes.remove(data, do_unlink=True)

    # Bandaid fix for spaghetti
    model_properties.current_male_hair_style = 'switch'
    model_properties.current_female_hair_style = 'switch'
    model_properties.current_beard_style = 'switch'

    bpy.ops.zomboid.check_hat_category()

def update_hide_dress(self, context):
    object_pointers = context.active_object.pz_object_pointers
    model_properties = context.active_object.pz_model_properties
    if 'Hide Dress' in object_pointers.body_object.modifiers:
        object_pointers.body_object.modifiers['Hide Dress'].show_viewport = model_properties.hide_dress
        object_pointers.body_object.modifiers['Hide Dress'].show_render = model_properties.hide_dress

def update_lookpoint_parent_object(self, context):
    control_properties = context.active_object.pz_control_properties

    lookpoint = context.active_object.pose.bones.get('CTRL-LookPoint')
    copy_constraint = lookpoint.constraints.get('Copy Location')

    copy_constraint.target = control_properties.lookpoint_parent_object

def update_left_prop_parent_object(self, context):
    control_properties = context.active_object.pz_control_properties

    prop = context.active_object.pose.bones.get('CTRL-Prop.L')
    copy_constraint = prop.constraints.get('Copy Location')

    copy_constraint.target = control_properties.left_prop_parent_object

def update_right_prop_parent_object(self, context):
    control_properties = context.active_object.pz_control_properties

    prop = context.active_object.pose.bones.get('CTRL-Prop.R')
    copy_constraint = prop.constraints.get('Copy Location')

    copy_constraint.target = control_properties.right_prop_parent_object

def update_model_selectability(self, context):
    object_pointers = context.active_object.pz_object_pointers
    model_properties = context.active_object.pz_model_properties
    equipped_clothing = context.active_object.pz_equipped_clothing_items

    # The specific non-clothing models
    rig_models = [
        object_pointers.body_object,
        object_pointers.hair_object,
        object_pointers.beard_object
    ]

    # The clothing models on equipped clothing items
    male_clothing_models = [obj.male_model_object for obj in equipped_clothing if obj.data.clothing_type != 'BODYTEXTURE' and obj.male_model_object]
    female_clothing_models = [obj.female_model_object for obj in equipped_clothing if obj.data.clothing_type != 'BODYTEXTURE' and obj.female_model_object]

    # The whole collection
    model_objects = rig_models + male_clothing_models + female_clothing_models

    for model in model_objects:
        if model:
            model.hide_select = not model_properties.models_selectable