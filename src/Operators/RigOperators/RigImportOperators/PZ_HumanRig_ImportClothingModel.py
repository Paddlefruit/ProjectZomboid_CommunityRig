# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import BoolProperty
from bpy.types import Operator
from pathlib import Path

from ....Utility.PZ_AssetMethods import directx_import_available
from ....Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportClothingModel(Operator):
    bl_idname = "zomboid.import_clothing_model"
    bl_label = "Import Clothing Model"

    halt_texture_updates: BoolProperty(
        default=True
    )

    def import_clothing_model(self, context, model_path, model_type, sex):
        p = context.active_object.pz_human_props

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

            objs_after = set(bpy.context.scene.objects)

            imported_objects = list(objs_after - objs_before)

            sex_collection_name = 'GEO-PZ_Human_Male_Clothes' if sex == 'MALE' else 'GEO-PZ_Human_Female_Clothes'
            clothing_collection = bpy.data.collections.get(
                sex_collection_name + instance_str)

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

                    sex_name = 'OBJ-MaleClothingMesh' if sex == 'MALE' else 'OBJ-FemaleClothingMesh'
                    obj_name = sex_name + \
                        str(p.clothing_mesh_slot_active_index) + instance_str

                    old_obj = bpy.data.objects.get(obj_name)
                    if old_obj:
                        bpy.data.objects.remove(old_obj, do_unlink=True)

                    # -------------------------

                    # Fix for incorrectly assigned hats that have off rotations
                    if 'WeddingVeil' in obj.name:
                        obj.rotation_euler[0] += math.radians(2)

                    # -------------------------

                    obj.name = obj_name

                    for collection in obj.users_collection[:]:
                        collection.objects.unlink(obj)

                    if obj.name not in clothing_collection.objects:
                        clothing_collection.objects.link(obj)

                    # matrix_world = obj.matrix_world.copy()
                    # obj.parent = prev_active_object
                    # obj.matrix_world = matrix_world

                    bip01 = prev_active_object
                    obj.parent = bip01

                    match model_type:
                        case '.x':
                            obj.rotation_euler[2] += math.pi
                            obj.scale[0] *= -1
                            obj.scale *= 100
                        case '.fbx':
                            obj.scale[0] = 100.0
                            obj.scale[1] = 100.0
                            obj.scale[2] = 100.0
                            obj.data.materials.clear()
                            obj.rotation_euler[0] += math.pi / 2
                        case '.glb':
                            obj.scale[0] = 1.0
                            obj.scale[1] = 1.0
                            obj.scale[2] = 1.0

                    obj.modifiers.clear()

                    arm_mod = obj.modifiers.new(
                        name="Armature", type='ARMATURE')
                    arm_mod.object = prev_active_object

                    obj.active_material = bpy.data.materials.get(
                        'MAT-ClothingMaterial' + str(p.clothing_mesh_slot_active_index) + instance_str)

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
            print("Could not find a model file at the path: " + model_path)
            return ({'CANCELLED'})

    def add_masks(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        m = m_list[p.clothing_mesh_slot_active_index]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for i in range(len(m.mask_array)):
            if m.mask_array[i] == True:
                p.mask_array[i] = True

        if self.halt_texture_updates:
            p.halt_texture_updates = False

        return ({'FINISHED'})

    def execute(self, context):

        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_human_clothing_mesh_slots
        m = m_list[p.clothing_mesh_slot_active_index]

        create_model_material(context, m.texture_path, 'CLOTHING')

        self.import_clothing_model(
            context, m.male_model_path, m.model_type, 'MALE')
        self.import_clothing_model(
            context, m.female_model_path, m.model_type, 'FEMALE')

        self.add_masks(context)

        bpy.ops.zomboid.check_hat_category()

        return ({'FINISHED'})