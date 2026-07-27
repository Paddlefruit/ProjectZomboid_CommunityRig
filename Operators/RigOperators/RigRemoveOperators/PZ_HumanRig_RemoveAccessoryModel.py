# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from ....Utility.PZ_MaterialMethods import remove_model_material

class PZ_RemovePropMesh(Operator):
    bl_idname = "zomboid.remove_accessory_model"
    bl_label = "Remove Prop Mesh"

    def remove_accessory_model(self, context, sex):
        p = context.active_object.pz_human_props
        a_list = context.active_object.pz_human_prop_mesh_slots

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.prop_mesh_slot_active_index

        obj_name = 'OBJ-MalePropMesh' if sex == 'MALE' else 'OBJ-FemalePropMesh'
        orig_obj_name = obj_name + str(index) + instance_str

        old_obj = bpy.data.objects.get(orig_obj_name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(a_list)):
            index_obj = bpy.data.objects.get(obj_name + str(i) + instance_str)
            if index_obj:
                index_obj.name = obj_name + str(i - 1) + instance_str

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        a_list = context.active_object.pz_human_prop_mesh_slots

        remove_model_material(context, 'PROP')

        self.remove_accessory_model(context, 'MALE')
        self.remove_accessory_model(context, 'FEMALE')

        bpy.ops.zomboid.check_hat_category(count_self=False)

        a_list.remove(p.prop_mesh_slot_active_index)
        p.prop_mesh_slot_active_index -= 1

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})