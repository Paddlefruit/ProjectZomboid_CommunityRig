# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import BoolProperty
from bpy.types import Operator
from pathlib import Path
from random import randint

from ......Utility.PZ_AssetMethods import directx_import_available
from ......Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportClothingModel(Operator):
    bl_idname = "zomboid.import_clothing_model"
    bl_label = "Import Clothing Model"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):

        # Get all data
        addon_prefs = context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        current_clothing_item = context.active_object.pz_equipped_clothing_items[p.equipped_clothing_item_active_index]

        instance_str = ' (' + str(p.rig_instance) + ')'

        # Select a random texture from all available texture choices
        texture_path = current_clothing_item.get_texture_path()

        # Create the attachment material, and assign it to the clothing item data
        current_clothing_item.material, current_clothing_item.image = create_model_material(context, texture_path, 'CLOTHING')

        # Method that will be run for both sex's models
        def import_clothing_model(sex: str, model_path: str):
            if Path(model_path).is_file():
                with bpy.context.temp_override(active_object=context.active_object):

                    # Get a list of all objects before the import
                    objs_before = set(bpy.context.scene.objects)

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
                    imported_objects = list(objs_after - objs_before)

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
                            imported_objects.remove(y)
                            bpy.data.objects.remove(y, do_unlink=True)

                    check_multi_model('Bob_Trousers', 'Bob_LongShorts')
                    check_multi_model('F_HydrationBackpack', 'F_ALICE_PackODD')

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
                    sex_name = 'OBJ-MaleClothingModel' if sex == 'MALE' else 'OBJ-FemaleClothingModel'
                    obj_name = sex_name + str(p.equipped_clothing_item_active_index) + instance_str

                    # Remove pre-existing object with this name, if it exists
                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    # Rename the new object
                    model_obj.name = obj_name

                    # Unlink this object from any collections it may have been linked to in the import process
                    for collection in model_obj.users_collection[:]:
                        collection.objects.unlink(model_obj)

                    # Get the rig's clothing collection for the respective sex, and add the model object to it
                    sex_collection_name = 'COL-PZ_Human_Male_Clothes' if sex == 'MALE' else 'COL-PZ_Human_Female_Clothes'
                    attachment_collection = bpy.data.collections.get(sex_collection_name + instance_str)
                    attachment_collection.objects.link(model_obj)

                    # Apply the material that was created to the model
                    model_obj.active_material = current_clothing_item.material

                    # Set the parent of the model object to the rig object
                    model_obj.parent = context.active_object

                    # Apply additional transformations based on the model type
                    match current_clothing_item.data.model_type:
                        case '.x':
                            model_obj.rotation_euler[2] += math.pi
                            model_obj.scale[0] *= -1
                            model_obj.scale *= 100
                        case '.fbx':
                            model_obj.scale[0] = 100.0
                            model_obj.scale[1] = 100.0
                            model_obj.scale[2] = 100.0
                            model_obj.data.materials.clear()
                            model_obj.rotation_euler[0] += math.pi / 2
                        case '.glb':
                            model_obj.scale[0] = 1.0
                            model_obj.scale[1] = 1.0
                            model_obj.scale[2] = 1.0

                    # Remove any modifiers from the model object
                    model_obj.modifiers.clear()

                    # Add an Armature modifier to the model object
                    armature_mod = model_obj.modifiers.new(name="Armature", type='ARMATURE')
                    armature_mod.object = context.active_object

                    # Add a custom property to indicate which sex this model is
                    model_obj["sex"] = 0 if sex == 'MALE' else 1

                    # Set initial view paramaters for the model based on the current sex
                    model_obj.hide_viewport = model_obj['sex'] != p.model_sex_index
                    model_obj.hide_render = model_obj['sex'] != p.model_sex_index

                    return model_obj

        # Call the import method for both the male and female model
        if current_clothing_item.use_alt_model:
            if current_clothing_item.data.male_alt_model_path != '' and current_clothing_item.data.female_alt_model_path != '':
                current_clothing_item.male_model_object = import_clothing_model('MALE', current_clothing_item.data.male_alt_model_path)
                current_clothing_item.female_model_object = import_clothing_model('FEMALE', current_clothing_item.data.female_alt_model_path)
            else:
                current_clothing_item.male_model_object = import_clothing_model('MALE', current_clothing_item.data.male_model_path)
                current_clothing_item.female_model_object = import_clothing_model('FEMALE', current_clothing_item.data.female_model_path)
        else:
            current_clothing_item.male_model_object = import_clothing_model('MALE', current_clothing_item.data.male_model_path)
            current_clothing_item.female_model_object = import_clothing_model('FEMALE', current_clothing_item.data.female_model_path)

        # Temporarily pause texture updates if indicated
        if self.halt_texture_updates:
            p.halt_texture_updates = True

        # Add the masks from this clothing item to the main rig masks array
        for i in range(len(current_clothing_item.data.mask_array)):
            if current_clothing_item.data.mask_array[i] == True:
                p.mask_array[i] = True

        # Resume texture updates
        if self.halt_texture_updates:
            p.halt_texture_updates = False

        return ({'FINISHED'})
                