# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.types import Operator
from pathlib import Path

from ....Utility.PZ_AssetMethods import directx_import_available
from ....Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportAccessoryModel(Operator):
    bl_idname = "zomboid.import_accessory_model"
    bl_label = "Import Accessory Model"

    def import_accessory_model(self, context, model_path, model_type, attach_bone, sex):
        p = context.active_object.pz_human_props
        #model_props = context.active_object.pz_model_props

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

            sex_collection_name = 'COL-PZ_Human_Male_Accessories' if sex == 'MALE' else 'COL-PZ_Human_Female_Accessories'
            accessory_collection = bpy.data.collections.get(
                sex_collection_name + instance_str)

            for obj in imported_objects:
                if obj.type == 'ARMATURE':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'EMPTY':
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif obj.type == 'MESH':

                    sex_name = 'OBJ-MaleAccessoryMesh' if sex == 'MALE' else 'OBJ-FemaleAccessoryMesh'
                    obj_name = sex_name + \
                        str(p.accessory_model_active_index) + instance_str

                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    obj.name = obj_name

                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)

                    if obj.name not in accessory_collection.objects:
                        accessory_collection.objects.link(obj)

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
                            obj.data.materials.clear()
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0
                        case '.glb':
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0

                    obj.modifiers.clear()

                    obj.active_material = bpy.data.materials.get(
                        'MAT-AccessoryMaterial' + str(p.accessory_model_active_index) + instance_str)

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
        m_list = context.active_object.pz_accessory_models
        m = m_list[p.accessory_model_active_index]

        create_model_material(context, m.texture_path, 'ACCESSORY')

        self.import_accessory_model(context, m.male_model_path,
                               m.model_type, m.attach_bone, 'MALE')
        self.import_accessory_model(context, m.female_model_path,
                               m.model_type, m.attach_bone, 'FEMALE')

        bpy.ops.zomboid.check_hat_category()

        return ({'FINISHED'})