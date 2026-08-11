# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

def update_clothing_sex_viewport(self, context):
    model_properties = context.active_object.pz_model_properties
    equipped_clothing = context.active_object.pz_equipped_clothing_items

    for item in equipped_clothing:
        if item.male_model_object:
            item.male_model_object.hide_viewport = model_properties.model_sex != 'MALE'
        if item.female_model_object:
            item.female_model_object.hide_viewport = model_properties.model_sex != 'FEMALE'

def update_clothing_sex_render(self, context):
    model_properties = context.active_object.pz_model_properties
    equipped_clothing = context.active_object.pz_equipped_clothing_items
    
    for item in equipped_clothing:
        if item.male_model_object:
            item.male_model_object.hide_render = model_properties.model_sex != 'MALE'
        if item.female_model_object:
            item.female_model_object.hide_render = model_properties.model_sex != 'FEMALE'

def update_hair_sex_viewport(self, context):
    model_properties = context.active_object.pz_model_properties
    object_pointers = context.active_object.pz_object_pointers

    if object_pointers.male_hair_object:
        object_pointers.male_hair_object.hide_viewport = model_properties.model_sex != 'MALE'
    if object_pointers.female_hair_object:
        object_pointers.female_hair_object.hide_viewport = model_properties.model_sex != 'FEMALE'
    if object_pointers.beard_object:
        object_pointers.beard_object.hide_viewport = model_properties.model_sex != 'MALE'

def update_hair_sex_render(self, context):
    model_properties = context.active_object.pz_model_properties
    object_pointers = context.active_object.pz_object_pointers

    if object_pointers.male_hair_object:
        object_pointers.male_hair_object.hide_render = model_properties.model_sex != 'MALE'
    if object_pointers.female_hair_object:
        object_pointers.female_hair_object.hide_render = model_properties.model_sex != 'FEMALE'
    if object_pointers.beard_object:
        object_pointers.beard_object.hide_render = model_properties.model_sex != 'MALE'

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