# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty


class PZ_Scene_Properties(PropertyGroup):

    def update_human_rig_active_index(self, context):
        if self.human_rig_active_index == -1:
            return
        selected_rig = context.scene.pz_human_rigs[self.human_rig_active_index]
        if selected_rig:
            if context.active_object.mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')
                selected_rig.obj.select_set(True)
                context.view_layer.objects.active = selected_rig.obj
            elif context.active_object.mode == 'POSE':
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                selected_rig.obj.select_set(True)
                context.view_layer.objects.active = selected_rig.obj
                bpy.ops.object.mode_set(mode='POSE')
            

    human_rig_active_index: IntProperty(
           default=-1,
           update=update_human_rig_active_index
    )
