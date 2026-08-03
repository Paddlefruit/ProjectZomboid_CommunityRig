# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator

class PZ_HumanRig_RemoveBodyTexture(Operator):
    bl_idname = "zomboid.remove_body_texture"
    bl_label = "Remove Texture Slot"

    def execute(self, context):

        bpy.ops.uilist.entry_remove(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index"
        )

        bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})


class PZ_HumanRig_MoveBodyTextureUp(Operator):
    bl_idname = "zomboid.move_body_texture_up"
    bl_label = "Move Texture Slot Up"

    def execute(self, context):

        bpy.ops.uilist.entry_move(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index",
            direction='UP'
        )

        bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})


class PZ_HumanRig_MoveBodyTextureDown(Operator):
    bl_idname = "zomboid.move_body_texture_down"
    bl_label = "Move Texture Slot Down"

    def execute(self, context):

        bpy.ops.uilist.entry_move(
            list_path="active_object.pz_human_body_texture_slots",
            active_index_path="active_object.pz_human_props.body_texture_slot_active_index",
            direction='DOWN'
        )

        bpy.ops.zomboid.create_body_texture()

        return ({'FINISHED'})