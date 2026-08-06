# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

def update_selected_attachment_point(self, context):
    p = context.active_object.pz_human_props
    attachments = context.active_object.pz_attachments
    bpy.ops.zomboid.move_attachment(attachment_point=attachments[p.attachment_active_index].selected_point)

class PZ_AttachmentPoint(PropertyGroup):
    sex: StringProperty()
    bone_name: StringProperty()
    offset: FloatVectorProperty()
    rotation: FloatVectorProperty()

class PZ_AttachmentTransformGroup(PropertyGroup):
    attachment_point: StringProperty()
    offset: FloatVectorProperty()
    rotation: FloatVectorProperty()
    scale: FloatProperty(default=1.0)

class PZ_Attachment(PropertyGroup):
    model_path: StringProperty()
    model_type: StringProperty()
    texture_path: StringProperty()
    override_groups: CollectionProperty(type=PZ_AttachmentTransformGroup)
    selected_point: StringProperty(
        name='Attachment Point',
        update=update_selected_attachment_point
    )
    object_name: StringProperty()
    material_name: StringProperty()
    image_name: StringProperty()