# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveBodyBloodiness(Operator):
    bl_idname = "zomboid.remove_body_bloodiness"
    bl_label = "Remove Bloodiness"
    bl_description = "Sets all bloodiness on the body to zero"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                       "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                       "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                       "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                       "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                       "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

        if self.stop_texture_updates:
            model_properties.stop_texture_updates = True

        for blood in blood_props:
            setattr(injury_properties, blood, 0)

        if self.stop_texture_updates:
            bpy.ops.zomboid.create_bloodiness_mask()
            model_properties.stop_texture_updates = False

        return ({'FINISHED'})