# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty

class PZ_HumanRig_RemoveAllBodyInjuries(Operator):
    bl_idname = "zomboid.remove_all_body_injuries"
    bl_label = "Remove All Body Injuries"
    bl_description = "Removes all body injuries"
    bl_options = {'REGISTER', 'UNDO'}

    halt_texture_updates: BoolProperty(
        default=True
    )

    def execute(self, context):
        p = context.active_object.pz_human_props

        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury",
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]

        if self.halt_texture_updates:
            p.halt_texture_updates = True

        for injury in injury_props:
            setattr(p, injury, 'NONE')

        if self.halt_texture_updates:
            bpy.ops.zomboid.create_body_texture()
            p.halt_texture_updates = False

        return ({'FINISHED'})