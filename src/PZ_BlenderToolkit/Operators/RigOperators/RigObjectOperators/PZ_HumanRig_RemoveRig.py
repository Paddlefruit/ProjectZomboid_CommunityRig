# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator, Collection

class PZ_HumanRig_RemoveRig(Operator):
    bl_idname = "zomboid.remove_rig"
    bl_label = "Remove Rig"
    bl_description = "Removes this instance of the rig from the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Get all data
        rigs = context.scene.pz_human_rigs
        rig_to_remove = rigs[context.scene.pz_scene_properties.human_rig_active_index]
        
        object_pointers = rig_to_remove.rig_object.pz_object_pointers

        # Begin removing everything
        with bpy.context.temp_override(active_object=object_pointers.rig_object):
            bpy.ops.zomboid.reset_model()

        bpy.data.images.remove(object_pointers.mask_data_image, do_unlink=True)
        bpy.data.images.remove(object_pointers.body_texture_image, do_unlink=True)
        bpy.data.materials.remove(object_pointers.body_material, do_unlink=True)

        # Remove all objects and collections recursively
        def remove_collection_recursive(col : Collection):
            if not col:
                return
            for subcol in col.children[:]:
                remove_collection_recursive(subcol)
            for obj in col.objects[:]:
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(col, do_unlink=True)

        remove_collection_recursive(object_pointers.rig_collection)

        rigs.remove(context.scene.pz_scene_properties.human_rig_active_index)
        context.scene.pz_scene_properties.human_rig_active_index -= 1
        
        return ({'FINISHED'})