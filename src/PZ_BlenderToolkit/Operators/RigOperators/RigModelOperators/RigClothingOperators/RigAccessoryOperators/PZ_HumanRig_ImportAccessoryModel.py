# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.types import Operator
from pathlib import Path
from random import randint

from ......Utility.PZ_AssetMethods import directx_import_available
from ......Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportAccessoryModel(Operator):
    bl_idname = "zomboid.import_accessory_model"
    bl_label = "Import Accessory Model"

    def execute(self, context):

        # Get all data
        object_pointers = context.active_object.pz_object_pointers
        main_properties = context.active_object.pz_main_properties
        model_properties = context.active_object.pz_model_properties

        current_clothing_item = context.active_object.pz_equipped_clothing_items[model_properties.equipped_clothing_item_active_index]

        instance_str = main_properties.get_instance_str(context)

        # Select a random texture from all available texture choices
        texture_path = current_clothing_item.get_texture_path()

        # Create the attachment material, and assign it to the clothing item data
        current_clothing_item.material, current_clothing_item.image = create_model_material(context, texture_path, 'ACCESSORY')

        # Rename the image name
        current_clothing_item.image.name = 'TEX-Attachment' + str(model_properties.equipped_clothing_item_active_index) + instance_str
    
        # Method that will be run for both sex's models
        def import_accessory_model(sex: str, model_path: str):
            if Path(model_path).is_file():
                with bpy.context.temp_override(active_object=context.active_object):

                    # Get a list of all objects before the import
                    objs_before = set(bpy.context.scene.objects)
                    mats_before = set(bpy.data.materials)

                    # Run the import method for the respective model type
                    match current_clothing_item.data.model_type:
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

                    # Get a list of all added objects to the scene
                    objs_after = set(bpy.context.scene.objects)
                    mats_after = set(bpy.data.materials)

                    imported_objects = list(objs_after - objs_before)
                    imported_materials = list(mats_after - mats_before)

                    for mat in imported_materials:
                        bpy.data.materials.remove(mat)

                    # Loop through all added objects, delete unneeded ones, and isolate the model object
                    model_obj = None
                    for obj in imported_objects:
                        match obj.type:
                            case 'ARMATURE':
                                bpy.data.objects.remove(obj, do_unlink=True)
                            case 'EMPTY':
                                bpy.data.objects.remove(obj, do_unlink=True)
                            case 'MESH':
                                model_obj = obj

                    if not model_obj:
                        return ({'CANCELLED'})

                    # Create the name for the new object
                    sex_name = 'OBJ-MaleAccessory' if sex == 'MALE' else 'OBJ-FemaleAccessory'
                    obj_name = sex_name + str(model_properties.equipped_clothing_item_active_index) + instance_str

                    # Remove pre-existing object with this name, if it exists
                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    # Rename the new object
                    model_obj.name = obj_name

                    # Rename the mesh data on the model object
                    data = model_obj.data
                    if data:
                        sex_name = 'GEO-MaleAccessory' if sex == 'MALE' else 'GEO-FemaleAccessory'
                        data.name = sex_name + str(model_properties.equipped_clothing_item_active_index) + instance_str

                    # Unlink this object from any collections it may have been linked to in the import process
                    for collection in model_obj.users_collection[:]:
                        collection.objects.unlink(model_obj)

                    # Get the rig's model collection and add to it
                    attachment_collection = object_pointers.model_collection
                    attachment_collection.objects.link(model_obj)

                    # Apply the material that was created to the model
                    model_obj.active_material = current_clothing_item.material

                    # Set the parent of the model object to the specific bone on the rig
                    bone = context.active_object.pose.bones.get(current_clothing_item.data.attach_bone)

                    model_obj.parent = context.active_object
                    model_obj.parent_type = 'BONE'
                    model_obj.parent_bone = bone.name

                    model_obj.matrix_parent_inverse = bone.matrix.inverted()
                    bone_world_matrix = context.active_object.matrix_world @ bone.matrix
                    model_obj.matrix_world = bone_world_matrix

                    # Apply additional transformations based on the model type
                    match current_clothing_item.data.model_type:
                        case '.x':
                            model_obj.rotation_euler[0] += math.pi
                            model_obj.scale *= 100

                            # Wrist items are imported upside down and have off rotations, for some reason
                            if sex == 'MALE':
                                if bone.name == 'Bip01_L_Forearm':
                                    model_obj.scale[2] *= -1
                                    model_obj.rotation_euler[1] += math.radians(3)
                                if bone.name == 'Bip01_R_Forearm':
                                    model_obj.scale[2] *= -1
                                    model_obj.rotation_euler[1] -= math.radians(3)
                            elif sex == 'FEMALE':
                                if bone.name == 'Bip01_L_Forearm':
                                    model_obj.scale[2] *= -1
                                    model_obj.rotation_euler[1] -= math.radians(3)
                                if bone.name == 'Bip01_R_Forearm':
                                    model_obj.scale[2] *= -1
                                    model_obj.rotation_euler[1] += math.radians(3)
                        
                            #  flip_uvs(obj)

                        case '.fbx':
                            model_obj.data.materials.clear()
                            model_obj.scale[0] = 1.0
                            model_obj.scale[1] = 1.0
                            model_obj.scale[2] = 1.0
                        case '.glb':
                            model_obj.scale[0] = 1.0
                            model_obj.scale[1] = 1.0
                            model_obj.scale[2] = 1.0

                    # Remove any modifiers from the model object
                    model_obj.modifiers.clear()

                    # Add a custom property to indicate which sex this model is
                    model_obj["sex"] = 0 if sex == 'MALE' else 1

                    # Set initial view paramaters for the model based on the current sex
                    model_obj.hide_viewport = model_obj['sex'] != model_properties.model_sex_index
                    model_obj.hide_render = model_obj['sex'] != model_properties.model_sex_index

                    return model_obj

        # Call the import method for both the male and female model
        if current_clothing_item.use_alt_model:
            if current_clothing_item.data.male_alt_model_path != '' and current_clothing_item.data.female_alt_model_path != '':
                current_clothing_item.male_model_object = import_accessory_model('MALE', current_clothing_item.data.male_alt_model_path)
                current_clothing_item.female_model_object = import_accessory_model('FEMALE', current_clothing_item.data.female_alt_model_path)
            else:
                current_clothing_item.male_model_object = import_accessory_model('MALE', current_clothing_item.data.male_model_path)
                current_clothing_item.female_model_object = import_accessory_model('FEMALE', current_clothing_item.data.female_model_path)
        else:
            current_clothing_item.male_model_object = import_accessory_model('MALE', current_clothing_item.data.male_model_path)
            current_clothing_item.female_model_object = import_accessory_model('FEMALE', current_clothing_item.data.female_model_path)

        return ({'FINISHED'})