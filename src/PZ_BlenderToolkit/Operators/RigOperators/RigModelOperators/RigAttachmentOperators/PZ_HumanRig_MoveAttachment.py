# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.props import StringProperty
from bpy.types import Operator

import math
from mathutils import Matrix, Vector, Euler

class PZ_HumanRig_MoveAttachment(Operator):
    bl_idname = "zomboid.move_attachment"
    bl_label = "Move Attachment"
    bl_description = "Moves an attachment to a specified attachment point"

    attachment_point: StringProperty()

    def execute(self, context):
        # Get all general data
        addon_data = context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        known_attachment_points = addon_data.pz_attachment_points
        rig_attachments = context.active_object.pz_attachments
        current_attachment = rig_attachments[p.attachment_active_index]

        # Get the attachment model object
        attachment_obj = bpy.data.objects.get(current_attachment.object_name)

        # Get the attachment point from the add on data
        attachment_point = None
        for item in known_attachment_points:
            if item.name == self.attachment_point:
                if item.sex == p.model_sex:
                    attachment_point = item
                    break
        if not attachment_point:
            return({'CANCELLED'})

        # Unparent the attachment model object and reset its transforms
        attachment_obj.parent = None
        attachment_obj.matrix_basis = Matrix.Identity(4)

        # Get the rig object
        rig_obj = context.active_object

        # Get the bone that the attachment point uses
        attachment_bone = rig_obj.pose.bones.get(attachment_point.bone_name)

        # Parent the attachment model object to it's new calculated position
        attachment_obj.parent = rig_obj
        attachment_obj.parent_type = 'BONE'
        attachment_obj.parent_bone = attachment_bone.name

        offset_transform = Vector((attachment_point.offset[0], attachment_point.offset[1], attachment_point.offset[2]))
        offset_rotation = Euler((math.radians(attachment_point.rotation[0]), math.radians(attachment_point.rotation[1]), math.radians(attachment_point.rotation[2])))
        offset_scale = Vector((1.0, 1.0, 1.0))
        offset_matrix = Matrix.LocRotScale(offset_transform, offset_rotation, offset_scale)

        attachment_obj.matrix_parent_inverse = attachment_bone.matrix.inverted()
        bone_world_matrix = rig_obj.matrix_world @ attachment_bone.matrix
        attachment_obj.matrix_world = bone_world_matrix @ offset_matrix

        attachment_obj.scale *= 100
        
        return({'FINISHED'})