# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import StringProperty
from bpy.types import Operator
from pathlib import Path

from ....Utility.PZ_AssetMethods import directx_import_available, get_zomboid_asset
from ....Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportHairModel(Operator):
    bl_idname = "zomboid.import_hair_model"
    bl_label = "Import Hair Model"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        hair_styles = addon_prefs.pz_human_hair_style_slots
        beard_styles = addon_prefs.pz_human_beard_styles

        hair_style = None
        match self.hair_type:
            case 'M':
                for hair in hair_styles:
                    if hair.name == p.current_male_hair_style and hair.sex == 'MALE':
                        hair_style = hair
            case 'F':
                for hair in hair_styles:
                    if hair.name == p.current_female_hair_style and hair.sex == 'FEMALE':
                        hair_style = hair
            case 'B':
                for beard in beard_styles:
                    if beard.name == p.current_beard_style:
                        hair_style = beard

        instance_str = ' (' + str(p.rig_instance) + ')'

        model_path = hair_style.model_path

        filepath = None
        extension = None

        if Path(model_path).name != 'None':
            filepath, extension = get_zomboid_asset(context, model_path)
        else:
            bpy.ops.zomboid.remove_hair_mesh(hair_type=self.hair_type)
            return ({'FINISHED'})
        if filepath is None:
            return ({'CANCELLED'})

        col = None
        prev_obj = None
        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Male' + instance_str)
                prev_obj = col.objects.get('OBJ-MaleHair' + instance_str)
            case 'F':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Female' + instance_str)
                prev_obj = col.objects.get('OBJ-FemaleHair' + instance_str)
            case 'B':
                col = bpy.data.collections.get(
                    'GEO-PZ_Human_Hair_Beard' + instance_str)
                prev_obj = col.objects.get('OBJ-Beard' + instance_str)

        if prev_obj:
            bpy.data.objects.remove(prev_obj, do_unlink=True)
            bpy.ops.outliner.orphans_purge(
                do_local_ids=True, do_linked_ids=True, do_recursive=True)

        create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)

        # Store the current context (current mode, selected objects, and active object) to restore later when operation is finished
        prev_mode = context.mode
        if context.active_object is not None:
            prev_active_object = context.active_object
        prev_selected_objects = context.selected_objects

        bpy.ops.object.mode_set(mode='OBJECT')

        objs_before = set(bpy.context.scene.objects)

        match extension:
            case '.x' | '.X':
                if not directx_import_available():
                    self.report(
                        {"ERROR"}, "The .x importer is not enabled or installed")
                    return ({'CANCELLED'})

                bpy.ops.import_scene.directx_x(
                    filepath=str(filepath),
                    import_textures=False,
                    import_materials=False,
                    import_armature=False,
                    import_animation=False,
                    use_import_collection=False
                )

            case '.fbx':
                bpy.ops.import_scene.fbx(
                    filepath=str(filepath),
                    global_scale=100.0
                )
            case '.glb':
                bpy.ops.import_scene.gltf(
                    filepath=str(filepath),
                    disable_bone_shape=True
                )

        objs_after = set(bpy.context.scene.objects)

        imported_objects = list(objs_after - objs_before)

        objs_to_remove = []
        for obj in imported_objects:
            if obj.type == 'ARMATURE' or obj.type == 'EMPTY':
                objs_to_remove.append(obj)
            elif obj.type == 'MESH':
                match self.hair_type:
                    case 'M':
                        obj.name = 'OBJ-MaleHair' + instance_str
                        obj["sex"] = 0
                    case 'F':
                        obj.name = 'OBJ-FemaleHair' + instance_str
                        obj["sex"] = 1
                    case 'B':
                        obj.name = 'OBJ-Beard' + instance_str
                        obj["sex"] = 0

                obj.hide_viewport = obj['sex'] != p.model_sex_index
                obj.hide_render = obj['sex'] != p.model_sex_index

                # matrix_world = obj.matrix_world.copy()
                # obj.parent = prev_active_object
                # obj.matrix_world = matrix_world

                # obj.location = prev_active_object.location
                # obj.rotation_euler = prev_active_object.rotation_euler

                bip01 = prev_active_object
                obj.parent = bip01

                match extension:
                    case '.x' | '.X':
                        obj.rotation_euler[2] += math.pi
                        obj.scale[0] *= -1
                        obj.scale *= 100
                        if self.hair_type == 'B':
                            obj.location[1] -= 0.125
                    case '.fbx':
                        obj.data.materials.clear()
                        obj.scale[0] = 1.0
                        obj.scale[1] = 1.0
                        obj.scale[2] = 1.0
                    case '.glb':
                        obj.scale[0] = 100.0
                        obj.scale[1] = 100.0
                        obj.scale[2] = 100.0

                for collection in obj.users_collection[:]:
                    collection.objects.unlink(obj)

                if obj.name not in col.objects:
                    col.objects.link(obj)

                obj.modifiers.clear()

                arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                arm_mod.object = prev_active_object
                
                match self.hair_type:
                    case 'M':
                        obj.active_material = bpy.data.materials.get('MAT-MaleHair' + instance_str)
                    case 'F':
                        obj.active_material = bpy.data.materials.get('MAT-FemaleHair' + instance_str)
                    case 'B':
                        obj.active_material = bpy.data.materials.get('MAT-Beard' + instance_str)

        for obj in objs_to_remove:
            bpy.data.objects.remove(obj, do_unlink=True)

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        for obj in prev_selected_objects:
            obj.select_set(True)
        if prev_active_object is not None:
            context.view_layer.objects.active = prev_active_object

        # Restore the context that was before the operation was called
        bpy.ops.object.mode_set(mode=prev_mode)

        return ({'FINISHED'})