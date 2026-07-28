# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import StringProperty

class PZ_RemoveHairMesh(Operator):
    bl_idname = "zomboid.remove_hair_mesh"
    bl_label = "Remove Hair Mesh"

    hair_type: StringProperty(
        name='Hair Type'
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        instance_str = ' (' + str(p.rig_instance) + ')'

        match self.hair_type:
            case 'M':
                col = bpy.data.collections.get(
                    'COL-PZ_Human_Hair_Male' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-MaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'F':
                col = bpy.data.collections.get(
                    'COL-PZ_Human_Hair_Female' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-FemaleHair' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)
            case 'B':
                col = bpy.data.collections.get(
                    'COL-PZ_Human_Hair_Beard' + instance_str)
                if col:
                    obj = col.objects.get('OBJ-Beard' + instance_str)
                    if obj:
                        bpy.data.objects.remove(obj, do_unlink=True)

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})