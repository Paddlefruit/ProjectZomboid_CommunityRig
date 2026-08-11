# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Collection, Object
from bpy.props import IntProperty, PointerProperty, EnumProperty, BoolProperty, StringProperty


class PZ_SceneProperties(PropertyGroup):

    # These properties and methods relate to the storage of human rig objects in the scene

    def update_human_rig_active_index(self, context):
        if self.human_rig_active_index == -1:
            return
        selected_rig = context.scene.pz_human_rigs[self.human_rig_active_index]
        if selected_rig:
            if context.active_object:
                if context.active_object.mode == 'OBJECT':
                    bpy.ops.object.select_all(action='DESELECT')
                    selected_rig.rig_object.select_set(True)
                    context.view_layer.objects.active = selected_rig.rig_object
                elif context.active_object.mode == 'POSE':
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    selected_rig.rig_object.select_set(True)
                    context.view_layer.objects.active = selected_rig.rig_object
                    bpy.ops.object.mode_set(mode='POSE')
            else:
                context.view_layer.objects.active = selected_rig.rig_object
                context.view_layer.objects.active = selected_rig.rig_object

    human_rig_active_index: IntProperty(
           default=-1,
           update=update_human_rig_active_index
    )

    # The collection that newly created rigs will be added to
    rig_parent_collection: PointerProperty(
        name='Parent Collection',
        description='The collection that the new rig will be added to. If left blank, it will be added to the Scene collection',
        type=Collection
    )

    # The enum that describes which position in the world the rig will be created at
    rig_creation_location: EnumProperty(
        name='Creation Location',
        description='The position/transform in the world that the rig will be created at',
        items=[
            ('WORLDORIGIN', 'World Origin', 'The rig will be created at (0, 0, 0)', 0),
            ('CURSOR', '3D Cursor', 'The rig will be created using the transforms of the 3D Cursor', 1),
            ('OBJECT', 'Object', 'The rig will be created using the transforms of an explicitly selected object', 2)
        ],
        default='WORLDORIGIN'
    )

    # The boolean that toggles if you want to use the 3D cursors rotation on rig created
    use_3d_cursor_rotation: BoolProperty(
        name='Use 3D Cursor Rotation',
        default=False
    )

    # The object whos transforms will be copied upon rig creation, if selected
    rig_creation_location_object: PointerProperty(
        name='Creation Object',
        type=Object
    )

    # The initial outfit to be applied to newly created rigs
    initial_outfit: StringProperty(
        name='Initial Outfit',
        description='The outfit that this rig will be created with'
    )

