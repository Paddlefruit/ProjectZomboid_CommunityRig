# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.props import StringProperty
from bpy.types import Operator

class PZ_HumanRig_AddAttachment(Operator):
    bl_idname = "zomboid.add_attachment"
    bl_label = "Add Attachment"
    bl_description = "Adds an attachment onto the model"

    attachment_name: StringProperty()

    def execute(self, context):
        addon_prefs = context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        known_attachments = addon_prefs.pz_human_attachments
        known_attachment_points = addon_prefs.pz_human_attachment_points
        rig_attachments = context.active_object.pz_attachments

        # Get the matching attachment from the add on collection
        if self.attachment_name:
            matching_attachment = known_attachments.get(self.attachment_name)
        else:
            return ({'CANCELLED'})

        # Add that attachments data onto the rig
        if matching_attachment:
            new_attachment = rig_attachments.add()
            p.attachment_active_index += 1

            new_attachment.name = matching_attachment.name
            new_attachment.model_path = matching_attachment.model_path
            new_attachment.model_type = matching_attachment.model_type
            new_attachment.texture_path = matching_attachment.texture_path

            for group in matching_attachment.override_groups:
                new_group = new_attachment.override_groups.add()

                new_group.attachment_point = group.attachment_point
                new_group.offset = group.offset
                new_group.rotation = group.rotation
                new_group.scale = group.scale
            
            bpy.ops.zomboid.import_attachment_model()
            bpy.ops.zomboid.move_attachment(attachment_point='Bip01_Prop2')

            return({'FINISHED'})
        else:
            return ({'CANCELLED'})

