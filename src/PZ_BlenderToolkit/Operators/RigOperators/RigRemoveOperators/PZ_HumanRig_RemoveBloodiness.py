# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveBodyBloodiness(Operator):
    bl_idname = "zomboid.remove_body_bloodiness"
    bl_label = "Remove Bloodiness"
    bl_description = "Sets all bloodiness on the body to zero"
    bl_options = {'REGISTER', 'UNDO'}

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                       "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                       "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                       "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                       "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                       "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for blood in blood_props:
            setattr(p, blood, 0)

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_bloodiness_mask()
            p.halt_texture_updates = False

        return ({'FINISHED'})