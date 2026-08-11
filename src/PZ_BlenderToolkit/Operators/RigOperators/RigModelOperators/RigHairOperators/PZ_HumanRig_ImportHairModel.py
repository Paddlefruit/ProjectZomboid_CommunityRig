# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import StringProperty
from bpy.types import Operator
from pathlib import Path

from .....Utility.PZ_AssetMethods import directx_import_available
from .....Utility.PZ_MaterialMethods import create_model_material

class PZ_ImportHairModel(Operator):
    bl_idname = "zomboid.import_hair_model"
    bl_label = "Import Hair Model"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        main_properties = context.active_object.pz_main_properties
        model_properties = context.active_object.pz_model_properties
        object_pointers = context.active_object.pz_object_pointers

        hair_styles = addon_data.pz_hair_style_references
        beard_styles = addon_data.pz_beard_style_references

        hair_style = None
        match self.hair_type:
            case 'M':
                for hair in hair_styles:
                    if hair.name == model_properties.current_male_hair_style and hair.sex == 'MALE':
                        hair_style = hair
            case 'F':
                for hair in hair_styles:
                    if hair.name == model_properties.current_female_hair_style and hair.sex == 'FEMALE':
                        hair_style = hair
            case 'B':
                for beard in beard_styles:
                    if beard.name == model_properties.current_beard_style:
                        hair_style = beard

        if hair_style:

            instance_str = main_properties.get_instance_str(context)

            model_path = hair_style.model_path
            extension = hair_style.model_type

            prev_obj = None
            match self.hair_type:
                case 'M':
                    prev_obj = object_pointers.male_hair_object
                case 'F':
                    prev_obj = object_pointers.female_hair_object
                case 'B':
                    prev_obj = object_pointers.beard_object

            if prev_obj:
                bpy.data.objects.remove(prev_obj, do_unlink=True)

            with context.temp_override(active_object=context.active_object):

                bpy.ops.object.mode_set(mode='OBJECT')

                objs_before = set(bpy.context.scene.objects)
                mats_before = set(bpy.data.materials)

                match extension:
                    case '.x' | '.X':
                        if not directx_import_available():
                            self.report(
                                {"ERROR"}, "The .x importer is not enabled or installed")
                            return ({'CANCELLED'})

                        bpy.ops.import_scene.directx_x(
                            filepath=str(model_path),
                            import_textures=False,
                            import_materials=False,
                            import_armature=False,
                            import_animation=False,
                            use_import_collection=False
                        )

                    case '.fbx':
                        bpy.ops.import_scene.fbx(
                            filepath=str(model_path),
                            global_scale=100.0
                        )
                    case '.glb':
                        bpy.ops.import_scene.gltf(
                            filepath=str(model_path),
                            disable_bone_shape=True
                        )

                objs_after = set(bpy.context.scene.objects)
                mats_after = set(bpy.data.materials)

                imported_objects = list(objs_after - objs_before)
                imported_materials = list(mats_after - mats_before)

                for mat in imported_materials:
                    bpy.data.materials.remove(mat)

                objs_to_remove = []
                for obj in imported_objects:
                    if obj.type == 'ARMATURE' or obj.type == 'EMPTY':
                        objs_to_remove.append(obj)
                    elif obj.type == 'MESH':
                        match self.hair_type:
                            case 'M':
                                obj.name = 'OBJ-MaleHair' + instance_str
                                if obj.data:
                                    obj.data.name = 'GEO-MaleHair' + instance_str
                                obj["sex"] = 0
                            case 'F':
                                obj.name = 'OBJ-FemaleHair' + instance_str
                                if obj.data:
                                    obj.data.name = 'GEO-FemaleHair' + instance_str
                                obj["sex"] = 1
                            case 'B':
                                obj.name = 'OBJ-Beard' + instance_str
                                if obj.data:
                                    obj.data.name = 'GEO-Beard' + instance_str
                                obj["sex"] = 0

                        obj.hide_viewport = obj['sex'] != model_properties.model_sex_index
                        obj.hide_render = obj['sex'] != model_properties.model_sex_index

                        obj.parent = context.active_object

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

                        col = object_pointers.model_collection

                        if obj.name not in col.objects:
                            col.objects.link(obj)

                        obj.modifiers.clear()

                        arm_mod = obj.modifiers.new(name="Armature", type='ARMATURE')
                        arm_mod.object = context.active_object

                        match self.hair_type:
                            case 'M':
                                object_pointers.male_hair_object = obj
                            case 'F':
                                object_pointers.female_hair_object = obj
                            case 'B':
                                object_pointers.beard_object = obj

                        if hair_style.texture_path:
                            match self.hair_type:
                                case 'M':
                                    object_pointers.male_hair_material, object_pointers.male_hair_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                    object_pointers.male_hair_image.name = 'TEX-MaleHair' + instance_str
                                    obj.active_material = object_pointers.male_hair_material
                                case 'F':
                                    object_pointers.female_hair_material, object_pointers.female_hair_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                    object_pointers.female_hair_image.name = 'TEX-FemaleHair' + instance_str
                                    obj.active_material = object_pointers.female_hair_material
                                case 'B':
                                    object_pointers.beard_material, object_pointers.beard_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                    object_pointers.beard_image.name = 'TEX-Beard' + instance_str
                                    obj.active_material = object_pointers.beard_material

                for obj in objs_to_remove:
                    bpy.data.objects.remove(obj, do_unlink=True)

            return ({'FINISHED'})
        return({'CANCELLED'})