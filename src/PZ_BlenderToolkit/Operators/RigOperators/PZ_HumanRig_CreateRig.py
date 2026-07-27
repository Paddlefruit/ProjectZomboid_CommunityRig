# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from pathlib import Path
from bpy.types import Operator

class PZ_HumanRig_CreateRig(Operator):
    bl_idname = "zomboid.create_rig"
    bl_label = "Create Rig"
    bl_description = "Creates a new instance of the rig and adds it to the scene"

    def execute(self, context):
        scene_props = context.scene.pz_human_global_props
        rigs = context.scene.pz_human_rigs

        # Get the path to the PZ_HumanRig Blend file and append it to this file
        rig_blend_path = Path(__file__).parent.parent.parent / 'Assets' / 'PZ_HumanRig.blend'
        rig_col_name = 'CH-PZ_Human ([INSTANCE])'

        with bpy.data.libraries.load(str(rig_blend_path)) as (data_from, data_to):
            if rig_col_name in data_from.collections:
                data_to.collections.append(rig_col_name)

        appended_collection = bpy.data.collections.get(rig_col_name)
        if appended_collection:
            if scene_props.rig_parent_collection:
                scene_props.rig_parent_collection.children.link(appended_collection)
            else:
                bpy.context.scene.collection.children.link(appended_collection)

        # Add this rig to the list of rigs in the scene
        new_rig = rigs.add()
        new_rig.obj = bpy.data.objects.get('OBJ-HumanRig ([INSTANCE])')
        bpy.context.view_layer.objects.active = new_rig.obj

        # Get the property group on the rig and start modifying it
        rig_props = new_rig.obj.pz_human_props
        rig_props.rig_instance = 1

        # Check if the import duplicated textures, and remove those duplicates if so
        

        return ({'FINISHED'})