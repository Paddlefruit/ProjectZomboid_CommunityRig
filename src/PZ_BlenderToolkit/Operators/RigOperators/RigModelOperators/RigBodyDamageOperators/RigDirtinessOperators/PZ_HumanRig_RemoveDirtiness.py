# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveBodyDirtiness(Operator):
    bl_idname = "zomboid.remove_body_dirtiness"
    bl_label = "Remove Dirtiness"
    bl_description = "Sets all dirtiness on the body to zero"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties

        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                      "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                      "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                      "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness",
                      "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                      "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]

        if self.stop_texture_updates:
            model_properties.stop_texture_updates = True

        for dirt in dirt_props:
            setattr(injury_properties, dirt, 0)

        if self.stop_texture_updates:
            bpy.ops.zomboid.create_dirtiness_mask()
            model_properties.stop_texture_updates = False

        return ({'FINISHED'})