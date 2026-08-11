# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from pathlib import Path

def resolve_image_users(img_name):
    target_img = bpy.data.images.get(img_name)
    real_img = bpy.data.images.get(img_name.split('.001')[0])

    if real_img:
        # Loop through all materials and nodes to see if this image is used there, and replace it if so
        for mat in bpy.data.materials:
            if mat.use_nodes and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image == target_img:
                        node.image = real_img

    bpy.data.images.remove(target_img)

def create_model_material(context, texture_path, category, hair_type=None):

    # Get all data
    main_properties = context.active_object.pz_main_properties
    model_properties = context.active_object.pz_model_properties
    object_pointers = context.active_object.pz_object_pointers

    instance_str = main_properties.get_instance_str(context)

    # Get the path to the materials Blend file
    mat_blend_path = Path(__file__).parent.parent / 'Assets' / 'Blend' / 'PZ_Materials.blend'


    mat_name = ''
    match category:
        case 'ACCESSORY':
            mat_name = 'MAT-AccessoryMaterial' + str(model_properties.equipped_clothing_item_active_index) + instance_str
        case 'CLOTHING':
            mat_name = 'MAT-ClothingMaterial' + str(model_properties.equipped_clothing_item_active_index) + instance_str
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
        # case 'ATTACHMENT':
        #     mat_name = 'MAT-AttachmentMaterial' + str(model_properties.attachment_active_index) + instance_str
                

    old_mat = bpy.data.materials.get(mat_name)
    if old_mat:
        bpy.data.materials.remove(old_mat, do_unlink=True)

    # Get the boilerplace material from the blend file
    boilerplate_mat_name = 'MAT-PZMaterialBoilerplate'
    with bpy.data.libraries.load(str(mat_blend_path)) as (data_from, data_to):
        if boilerplate_mat_name in data_from.materials:
            data_to.materials.append(boilerplate_mat_name)

    boilerplate_mat = bpy.data.materials.get(boilerplate_mat_name)
    mat = boilerplate_mat.copy()
    bpy.data.materials.remove(boilerplate_mat)

    mat.name = mat_name

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Get the existing nodes

    tex_node = nodes.get('NDE-TexSlot')
    mask_node = nodes.get('NDE-MaskData')
    blood_tex_node = nodes.get('NDE-BloodTex')
    dirt_tex_node = nodes.get('NDE-DirtTex')
    tint_node = nodes.get('NDE-TexTint')
    emission_node = nodes.get('NDE-EmissionShader')
    pbr_node = nodes.get('NDE-PBRShader')
    custom_shader_node = nodes.get('NDE-CustomShader')
    mix_custom_shader_node = nodes.get('NDE-MixCustomShader')
    dirt_mix_node = nodes.get('NDE-DirtMix')
    alpha_mix_node = nodes.get('NDE-AlphaMix')

    ## Set the texture node properties and drivers ##

    # Main Texture
    if category != 'BODY':
        tex_node.image = bpy.data.images.load(texture_path)
    else:
        if object_pointers.body_image_texture:
            tex_node.image = object_pointers.body_image_texture

    if object_pointers.mask_data_image:
        mask_node.image = object_pointers.mask_data_image

    # Dirt Overlay
    dirt_image_name = 'TEX-GrimeOverlay'
    with bpy.data.libraries.load(str(mat_blend_path)) as (data_from, data_to):
        if dirt_image_name in data_from.images:
            data_to.images.append(dirt_image_name)
    dirt_tex_node.image = bpy.data.images.get(dirt_image_name)

    # Blood Overlay
    blood_image_name = 'TEX-BloodOverlay'
    with bpy.data.libraries.load(str(mat_blend_path)) as (data_from, data_to):
        if blood_image_name in data_from.images:
            data_to.images.append(blood_image_name)
    blood_tex_node.image = bpy.data.images.get(blood_image_name)

    # Interpolation Driver
    path = 'nodes["NDE-TexSlot"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.texture_interpolation_index"

    context.active_object.update_tag()
    mat.node_tree.update_tag()

    ### Set the color tint node properties ###
    tint_node.data_type = 'RGBA'
    tint_node.blend_type = 'MULTIPLY'

    # Color Drivers

    if category == 'CLOTHING' or category == 'ACCESSORY':
        for i in range(3):
            path = 'nodes["NDE-TexTint"].inputs[7].default_value'
            fcurve = mat.node_tree.driver_add(path, i)
            driver = fcurve.driver
            driver.type = 'AVERAGE'

            var = driver.variables.new()
            target = var.targets[0]
            target.id = context.active_object
            target.data_path = "pz_equipped_clothing_items[" + str(model_properties.equipped_clothing_item_active_index) + "].tint_color[" + str(i) + "]"

            context.active_object.update_tag()
            mat.node_tree.update_tag()
            
    elif category == 'HAIR':
        for i in range(3):
            path = 'nodes["NDE-TexTint"].inputs[7].default_value'
            fcurve = mat.node_tree.driver_add(path, i)
            driver = fcurve.driver
            driver.type = 'SCRIPTED'

            driver.expression = 'max(color / (zomb + 1), 0.01) if toggle and zomb > 0 else color'

            color_var = driver.variables.new()
            color_var.name = 'color'
            color_target = color_var.targets[0]
            color_target.id = context.active_object
            color_target.data_path = "pz_model_properties.hair_color[" + str(i) + "]"

            do_darken_var = driver.variables.new()
            do_darken_var.name = 'toggle'
            do_darken_target = do_darken_var.targets[0]
            do_darken_target.id = context.active_object
            do_darken_target.data_path = "pz_model_properties.darken_zombie_hair"

            is_zombie_var = driver.variables.new()
            is_zombie_var.name = 'zomb'
            is_zombie_target = is_zombie_var.targets[0]
            is_zombie_target.id = context.active_object
            is_zombie_target.data_path = "pz_model_properties.zombification_index"
            context.active_object.update_tag()
            mat.node_tree.update_tag()


    ### Set the mix shader node properties ###

    # Factor Driver
    path = 'nodes["NDE-MixShader"].inputs[0].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.shading_type_index"

    context.active_object.update_tag()
    mat.node_tree.update_tag()

    ### Set the emission node properties ###

    # Strength Driver
    path = 'nodes["NDE-EmissionShader"].inputs[1].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.emission_strength"

    context.active_object.update_tag()
    mat.node_tree.update_tag()

    ### Set the PBR node properties ###

    # Roughness Driver
    path = 'nodes["NDE-PBRShader"].inputs[2].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.roughness"

    context.active_object.update_tag()
    mat.node_tree.update_tag()

    # Metallic Driver
    path = 'nodes["NDE-PBRShader"].inputs[1].default_value'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.metallic"

    context.active_object.update_tag()
    mat.node_tree.update_tag()

    ### Set the custom shader node properties ###
    selected_group = bpy.data.node_groups.get(context.active_object.pz_shading_properties.custom_shading_group_name)
    
    if selected_group:
        custom_shader_node.node_tree = selected_group

        if custom_shader_node.inputs.get('Color') is not None:
            links.new(dirt_mix_node.outputs['Result'], custom_shader_node.inputs['Color'])

        if custom_shader_node.outputs.get('Shader') is not None:
            links.new(custom_shader_node.outputs['Shader'], mix_custom_shader_node.inputs[2])

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
    target.data_path = "pz_shading_properties.shading_type_index"

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
    target.data_path = "pz_shading_properties.texture_interpolation_index"

    # Blood Overlay
    path = 'nodes["NDE-BloodTex"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.texture_interpolation_index"

    # Dirt Overlay
    path = 'nodes["NDE-DirtTex"].interpolation'
    fcurve = mat.node_tree.driver_add(path)
    driver = fcurve.driver
    driver.type = 'AVERAGE'

    var = driver.variables.new()
    target = var.targets[0]
    target.id = context.active_object
    target.data_path = "pz_shading_properties.texture_interpolation_index"

    # Skip overlay links if this is an accessory or hair

    if category == 'ACCESSORY' or category == 'HAIR':
        links.new(tint_node.outputs['Result'], emission_node.inputs['Color'])
        links.new(tint_node.outputs['Result'], pbr_node.inputs['Base Color'])
        if custom_shader_node.inputs.get('Color') is not None:
            links.new(tint_node.outputs['Result'], custom_shader_node.inputs['Color'])
    
    if category != 'BODY':
        for link in links:
            if link.from_node == alpha_mix_node:
                links.remove(link)

    return (mat, tex_node.image)


def remove_model_material(context, category):
    pass
    # p = context.active_object.pz_human_props
    # instance_str = ' (' + str(p.rig_instance) + ')'

    # index = -1
    # a_list = None

    # mat_name = ''
    # match category:
    #     case 'ACCESSORY':
    #         mat_name = 'MAT-AccessoryMaterial' + str(index) + instance_str
    #         a_list = context.active_object.pz_accessory_models
    #         index = p.accessory_model_active_index
    #     case 'CLOTHING':
    #         mat_name = 'MAT-ClothingMaterial' + str(index) + instance_str
    #         a_list = context.active_object.pz_clothing_models
    #         index = p.clothing_model_active_index

    # old_mat = bpy.data.materials.get(mat_name)
    # if old_mat:

    #     drivers = old_mat.node_tree.animation_data.drivers
    #     for i in range(len(drivers) - 1, -1, -1):
    #         drivers.remove(drivers[i])

    #     bpy.data.materials.remove(old_mat, do_unlink=True)

    # for i in range(index, len(a_list)):
    #     index_mat = bpy.data.materials.get(mat_name)
    #     if index_mat:
    #         match category:
    #             case 'ACCESSORY':
    #                 index_mat.name = 'MAT-AccessoryMaterial' + str(i - 1) + instance_str
    #             case 'CLOTHING':
    #                 index_mat.name = 'MAT-ClothingMaterial' + str(i - 1) + instance_str

    #         for fcurve in index_mat.node_tree.animation_data.drivers:
    #             driver = fcurve.driver
    #             target = driver.variables[0].targets[0]

    #             match category:
    #                 case 'ACCESSORY':
    #                     old_path = "pz_accessory_models[" + str(i) + "]"
    #                     new_path = "pz_accessory_models[" + str(i - 1) + "]"
    #                 case 'CLOTHING':
    #                     old_path = "pz_clothing_models[" + str(i) + "]"
    #                     new_path = "pz_clothing_models[" + str(i - 1) + "]"

    #             target.data_path = target.data_path.replace(old_path, new_path)