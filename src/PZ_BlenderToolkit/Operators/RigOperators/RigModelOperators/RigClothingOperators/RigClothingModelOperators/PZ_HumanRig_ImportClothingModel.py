# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import BoolProperty
from bpy.types import Operator
from pathlib import Path
from random import randint
from mathutils import Vector, Matrix

from ......Utility.PZ_AssetMethods import directx_import_available
from ......Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportClothingModel(Operator):
    bl_idname = "zomboid.import_clothing_model"
    bl_label = "Import Clothing Model"

    stop_texture_updates: BoolProperty(
        default=True
    )

    replace_material: BoolProperty(
        default=True
    )

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
        if self.replace_material:
            current_clothing_item.material, current_clothing_item.image = create_model_material(context, texture_path, 'CLOTHING')
        
        # Rename the image name
        current_clothing_item.image.name = 'TEX-Clothing' + str(model_properties.equipped_clothing_item_active_index) + instance_str

        # Method that will be run for both sex's models
        def import_clothing_model(model_path: str, model_type: str):
            print(model_type)
            if Path(model_path).is_file():

                # Store object mode that was used
                prev_mode = context.active_object.mode

               # with bpy.context.temp_override(active_object=context.active_object):

                # Get a list of all objects before the import
                objs_before = set(bpy.context.scene.objects)
                mats_before = set(bpy.data.materials)

                # Run the import method for the respective model type
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
                        rig_object = context.active_object
                        current_mode = context.active_object.mode
                        bpy.ops.import_scene.fbx(
                            filepath=model_path,
                            global_scale=100.0
                        )
                        bpy.ops.object.select_all(action='DESELECT')
                        for obj in context.selected_objects:
                            obj.select_set(True)
                        if rig_object:
                            context.view_layer.objects.active = rig_object
                            bpy.ops.object.mode_set(mode=current_mode)
                    case '.glb':
                        rig_object = context.active_object
                        current_mode = context.active_object.mode
                        bpy.ops.import_scene.gltf(
                            filepath=model_path,
                            disable_bone_shape=True
                        )
                        bpy.ops.object.select_all(action='DESELECT')
                        for obj in context.selected_objects:
                            obj.select_set(True)
                        if rig_object:
                            context.view_layer.objects.active = rig_object
                            bpy.ops.object.mode_set(mode=current_mode)

                # Get a list of all added objects to the scene
                objs_after = set(bpy.context.scene.objects)
                mats_after = set(bpy.data.materials)

                imported_objects = list(objs_after - objs_before)
                imported_materials = list(mats_after - mats_before)

                for mat in imported_materials:
                    bpy.data.materials.remove(mat)

                # Method that checks edge cases where a model file has two meshes instead of one
                def check_multi_model(wanted_model_name, delete_model_name):
                    x = None
                    y = None
                    for obj in imported_objects:
                        if obj.name == wanted_model_name:
                            x = obj
                        elif obj.name == delete_model_name:
                            y = obj
                    if x is not None and y is not None:
                        data = y.data
                        imported_objects.remove(y)
                        bpy.data.objects.remove(y, do_unlink=True)
                        if data:
                            bpy.data.meshes.remove(data, do_unlink=True)

                check_multi_model('Bob_Trousers', 'Bob_LongShorts')
                check_multi_model('F_HydrationBackpack', 'F_ALICE_PackODD')

                # Loop through all added objects, delete unneeded ones, and isolate the model object
                model_obj = None
                armature_obj = None
                objs_to_remove = []
                for obj in imported_objects:
                    match obj.type:
                        case 'ARMATURE':
                            armature_obj = obj
                            objs_to_remove.append(obj)
                        case 'EMPTY':
                            objs_to_remove.append(obj)
                        case 'MESH':
                            model_obj = obj

                origin_difference = Vector((0.0, 0.0, 0.0))
                if model_obj:
                    if armature_obj:
                        origin_difference = armature_obj.location - model_obj.location
                else:
                    return ({'CANCELLED'})

                # Delete unwanted object
                for obj_to_remove in objs_to_remove:
                    bpy.data.objects.remove(obj_to_remove, do_unlink=True)

                # Create the name for the new object
                obj_name = 'OBJ-Clothing' + str(model_properties.equipped_clothing_item_active_index) + instance_str

                # Remove pre-existing object with this name, if it exists
                old_obj = bpy.data.objects.get(obj_name)
                if old_obj:
                    bpy.data.objects.remove(old_obj, do_unlink=True)


                # Apply scale of model object at the data level
                matrx = model_obj.matrix_local
                loc, rot, scale = matrx.decompose()
                matrix_scale = Matrix.LocRotScale(None, None, scale)
                model_obj.data.transform(matrix_scale)
                model_obj.scale = (1.0, 1.0, 1.0)

                
                # Rename the new object
                model_obj.name = obj_name

                # Rename the mesh data on the model object
                data = model_obj.data
                if data:
                    data.name = 'GEO-Clothing' + str(model_properties.equipped_clothing_item_active_index) + instance_str

                # Unlink this object from any collections it may have been linked to in the import process
                for collection in model_obj.users_collection[:]:
                    collection.objects.unlink(model_obj)

                # Get the rig's model collection and add to it
                attachment_collection = object_pointers.model_collection
                attachment_collection.objects.link(model_obj)

                # Set the parent of the model object to the rig object
                model_obj.parent = context.active_object

                # Apply additional transformations based on the model type
                match model_type:
                    case '.x':
                        model_obj.rotation_euler[2] += math.pi
                        model_obj.scale[0] *= -1
                        model_obj.scale *= 100
                    case '.fbx':
                        model_obj.rotation_euler[0] += math.pi / 2
                        model_obj.scale[0] = 100.0
                        model_obj.scale[1] = 100.0
                        model_obj.scale[2] = 100.0
                        model_obj.data.materials.clear()
                    case '.glb':
                        model_obj.rotation_mode = 'XYZ'
                        model_obj.rotation_euler[0] += math.pi / 2
                        model_obj.scale[0] = 100.0
                        model_obj.scale[1] = 100.0
                        model_obj.scale[2] = 100.0
                        model_obj.data.materials.clear()


                # Translate model by the difference of origins
                model_obj.location -= origin_difference * 100
                model_obj.location.xyz = model_obj.location.xzy
                model_obj.location.y *= -1

                # Remove any modifiers from the model object
                model_obj.modifiers.clear()

                # Apply the material that was created to the model
                model_obj.active_material = current_clothing_item.material

                # Add an Armature modifier to the model object
                armature_mod = model_obj.modifiers.new(name="Armature", type='ARMATURE')
                armature_mod.object = context.active_object

                # Set initial selection properties
                model_obj.hide_select = not model_properties.models_selectable

                print(model_obj)
                return model_obj
            return None

        # Call the import method for the current sex
        if model_properties.model_sex == 'MALE':
            if current_clothing_item.use_alt_model:
                if current_clothing_item.data.male_alt_model_path != '':
                    current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.male_alt_model_path, current_clothing_item.data.male_model_type)
                else:
                    current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.male_model_path, current_clothing_item.data.male_model_type)
            else:
                current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.male_model_path, current_clothing_item.data.male_model_type)
        else:
            if current_clothing_item.use_alt_model:
                if current_clothing_item.data.female_alt_model_path != '':
                    current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.female_alt_model_path, current_clothing_item.data.female_model_type)
                else:
                    current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.female_model_path, current_clothing_item.data.female_model_type)
            else:
                current_clothing_item.model_object = import_clothing_model(current_clothing_item.data.female_model_path, current_clothing_item.data.female_model_type)

        # Temporarily pause texture updates if indicated
        if self.stop_texture_updates:
            model_properties.stop_texture_updates = True

        # Add the masks from this clothing item to the main rig masks array
        for i in range(len(current_clothing_item.data.visibility_mask_array)):
            if current_clothing_item.data.visibility_mask_array[i] == True:
                model_properties.visibility_mask_array[i] = True

        # Resume texture updates
        if self.stop_texture_updates:
            model_properties.stop_texture_updates = False

        return ({'FINISHED'})
                