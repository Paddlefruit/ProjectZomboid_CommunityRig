# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

class PZ_HumanRig_RemoveAttachment(Operator):
    bl_idname = "zomboid.remove_attachment"
    bl_label = "Remove Attachment"
    bl_description = "Removes an attachment from the model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get all data
        p = context.active_object.pz_human_props
        rig_attachments = context.active_object.pz_attachments
        attachment_to_remove = rig_attachments[p.attachment_active_index]

        # Delete the attachment model object
        obj_to_remove = bpy.data.objects.get(attachment_to_remove.object_name)
        if obj_to_remove:
            bpy.data.objects.remove(obj_to_remove, do_unlink=True)

        # Delete the attachment model material
        mat_to_remove = bpy.data.materials.get(attachment_to_remove.material_name)
        if mat_to_remove:
            bpy.data.materials.remove(mat_to_remove, do_unlink=True)

        # Remove this attachment data from the rig
        rig_attachments.remove(p.attachment_active_index)
        p.attachment_active_index -= 1

        return ({'FINISHED'})
