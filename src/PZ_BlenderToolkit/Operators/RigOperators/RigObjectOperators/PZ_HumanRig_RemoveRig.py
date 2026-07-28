# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator, Collection

class PZ_HumanRig_RemoveRig(Operator):
    bl_idname = "zomboid.remove_rig"
    bl_label = "Remove Rig"
    bl_description = "Removes this instance of the rig from the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        rigs = context.scene.pz_human_rigs
        rig_to_remove = rigs[context.scene.pz_human_global_props.human_rig_active_index]
        rig_obj = rig_to_remove.obj
        rig_col = rig_obj.pz_human_props.rig_collection

        with bpy.context.temp_override(active_object=rig_obj):
            bpy.ops.zomboid.reset_model()

        bpy.data.images.remove(rig_obj.pz_human_props.mask_tex, do_unlink=True)
        bpy.data.images.remove(rig_obj.pz_human_props.body_tex, do_unlink=True)
        bpy.data.materials.remove(rig_obj.pz_human_props.body_mat, do_unlink=True)

        def remove_collection_recursive(col : Collection):
            if not col:
                return
            for subcol in col.children[:]:
                remove_collection_recursive(subcol)
            for obj in col.objects[:]:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col, do_unlink=True)

        remove_collection_recursive(rig_col)

        rigs.remove(context.scene.pz_human_global_props.human_rig_active_index)
        context.scene.pz_human_global_props.human_rig_active_index -= 1
        
        return ({'FINISHED'})