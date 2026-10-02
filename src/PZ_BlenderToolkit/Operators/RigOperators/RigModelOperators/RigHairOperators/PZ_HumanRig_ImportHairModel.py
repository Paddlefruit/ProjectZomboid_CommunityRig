# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.props import StringProperty
from bpy.types import Operator
from pathlib import Path
from mathutils import Vector

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
                    prev_obj = object_pointers.hair_object
                case 'F':
                    prev_obj = object_pointers.hair_object
                case 'B':
                    prev_obj = object_pointers.beard_object

            if prev_obj:
                bpy.data.objects.remove(prev_obj, do_unlink=True)

            # Store object mode that was used
            prev_mode = context.active_object.mode

           # with context.temp_override(active_object=context.active_object, selected_objects=context.selected_objects):

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
                    rig_object = context.active_object
                    current_mode = context.active_object.mode
                    bpy.ops.import_scene.fbx(
                        filepath=str(model_path),
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
                        filepath=str(model_path),
                        disable_bone_shape=True,
                        import_select_created_objects=False
                    )
                    bpy.ops.object.select_all(action='DESELECT')
                    for obj in context.selected_objects:
                        obj.select_set(True)
                    if rig_object:
                        context.view_layer.objects.active = rig_object
                        bpy.ops.object.mode_set(mode=current_mode)

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
                            obj.name = 'OBJ-Hair' + instance_str
                            if obj.data:
                                obj.data.name = 'GEO-Hair' + instance_str
                        case 'F':
                            obj.name = 'OBJ-Hair' + instance_str
                            if obj.data:
                                obj.data.name = 'GEO-Hair' + instance_str
                        case 'B':
                            obj.name = 'OBJ-Beard' + instance_str
                            if obj.data:
                                obj.data.name = 'GEO-Beard' + instance_str

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
                            obj.rotation_mode = 'XYZ'
                        case '.glb':
                            obj.scale[0] = 100.0
                            obj.scale[1] = 100.0
                            obj.scale[2] = 100.0
                            obj.rotation_mode = 'XYZ'

                    # Check the local height of the bounding box to see if it is rotated correctly
                    
                    # # Check one of the box verticies and see if it's below the object origin. If it is, there is likely an inccorect rotation
                    # for i in range(4):
                    #     bound_box = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                    #     min_bound_z = min(corner.z for corner in bound_box)

                    #     print(min_bound_z)
                    #     print(obj.matrix_world.translation.z)

                    #     if min_bound_z <= obj.matrix_world.translation.z:
                    #         obj.rotation_euler[0] += math.pi/2
                    #     else:
                    #         break
                    for i in range(3):
                        if Vector(obj.bound_box[0]).z <= 0.3:
                            obj.rotation_mode = 'XYZ'
                            obj.rotation_euler[0] += math.pi/2
                        else:
                            break


                    # Check the scale of the bounding box to see if it is scaled by a magnitude too small or a magnitude too large
                    dims = obj.dimensions
                    box_volume = dims.x * dims.y * dims.z

                    if box_volume < 0.0001:
                        obj.scale *= 100
                    elif box_volume > 0.01:
                        obj.scale /= 100


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
                            object_pointers.hair_object = obj
                        case 'F':
                            object_pointers.hair_object = obj
                        case 'B':
                            object_pointers.beard_object = obj

                    if hair_style.texture_path:
                        match self.hair_type:
                            case 'M':
                                object_pointers.hair_material, object_pointers.hair_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                object_pointers.hair_image.name = 'TEX-Hair' + instance_str
                                obj.active_material = object_pointers.hair_material
                            case 'F':
                                object_pointers.hair_material, object_pointers.hair_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                object_pointers.hair_image.name = 'TEX-Hair' + instance_str
                                obj.active_material = object_pointers.hair_material
                            case 'B':
                                object_pointers.beard_material, object_pointers.beard_image = create_model_material(context, hair_style.texture_path, 'HAIR', hair_type=self.hair_type)
                                object_pointers.beard_image.name = 'TEX-Beard' + instance_str
                                obj.active_material = object_pointers.beard_material

            for obj in objs_to_remove:
                bpy.data.objects.remove(obj, do_unlink=True)

            # Restore pose mode if it was used
            if context.active_object:
                bpy.ops.object.mode_set(mode=prev_mode)

            return ({'FINISHED'})
        return({'CANCELLED'})