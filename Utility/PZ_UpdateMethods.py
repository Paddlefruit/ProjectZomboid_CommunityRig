# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

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