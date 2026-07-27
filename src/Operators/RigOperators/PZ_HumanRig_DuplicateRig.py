# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

class PZ_HumanRig_DuplicateRig(Operator):
    bl_idname = "zomboid.duplicate_rig"
    bl_label = "Duplicate Rig"
    bl_description = "Creates a new instance of the rig that copies all of the selected rigs attributes"

    def recursively_duplicate_collection(self, context, source_collection, parent_collection=None):

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        rigs = context.scene.pz_human_rigs

        # Create the new rig object
        new_rig = rigs.add()

        # Recursively create the new rig objects
        self.recursively_duplicate_collection(
            context, p.rig_collection, context.collection)

        return ({'FINISHED'})