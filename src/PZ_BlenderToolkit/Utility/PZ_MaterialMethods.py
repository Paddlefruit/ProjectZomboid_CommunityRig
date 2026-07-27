# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

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