# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class PZ_RemoveHairMesh(Operator):
    bl_idname = "zomboid.remove_hair_model"
    bl_label = "Remove Hair Mesh"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        object_pointers = context.active_object.pz_object_pointers

        match self.hair_type:
            case 'M':
                if object_pointers.male_hair_object:
                    data = object_pointers.male_hair_object.data
                    bpy.data.objects.remove(object_pointers.male_hair_object, do_unlink=True)
                    if data:
                        bpy.data.meshes.remove(data, do_unlink=True)

                if object_pointers.male_hair_material:
                    bpy.data.materials.remove(object_pointers.male_hair_material, do_unlink=True)

                if object_pointers.male_hair_image:
                    bpy.data.images.remove(object_pointers.male_hair_image, do_unlink=True)
            case 'F':
                if object_pointers.female_hair_object:
                    data = object_pointers.female_hair_object.data
                    bpy.data.objects.remove(object_pointers.female_hair_object, do_unlink=True)
                    if data:
                        bpy.data.meshes.remove(data, do_unlink=True)

                    if object_pointers.female_hair_material:
                        bpy.data.materials.remove(object_pointers.female_hair_material, do_unlink=True)
    
                    if object_pointers.female_hair_image:
                        bpy.data.images.remove(object_pointers.female_hair_image, do_unlink=True)
            case 'B':
                if object_pointers.beard_object:
                    data = object_pointers.beard_object.data
                    bpy.data.objects.remove(object_pointers.beard_object, do_unlink=True)
                    if data:
                        bpy.data.meshes.remove(data, do_unlink=True)

                    if object_pointers.beard_material:
                        bpy.data.materials.remove(object_pointers.beard_material, do_unlink=True)
    
                    if object_pointers.beard_image:
                        bpy.data.images.remove(object_pointers.beard_image, do_unlink=True)

      #  bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})