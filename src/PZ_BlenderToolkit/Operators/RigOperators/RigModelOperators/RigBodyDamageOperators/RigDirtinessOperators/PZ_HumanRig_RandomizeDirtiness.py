# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

from random import uniform

class PZ_HumanRig_RandomizeDirtiness(Operator):
    bl_idname = "zomboid.randomize_dirtiness"
    bl_label = "Randomize Dirtiness"
    bl_description = "Randomize the values of all the body dirtiness options based on a set intensity"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties
        random_properties = context.active_object.pz_random_properties

        dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                      "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                      "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                      "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness",
                      "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                      "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]

        model_properties.stop_texture_updates = True

        for dirt in dirt_props:
            setattr(injury_properties, dirt, 0)
            dirtiness = 0
            match random_properties.random_dirtiness_intensity:
                case 'SOME':
                    dirtiness = uniform(0.0, 0.5)
                case 'MODERATE':
                    dirtiness = uniform(0.0, 0.8)
                case 'LOTS':
                    dirtiness = uniform(0.0, 1.2)
                case 'DISGUSTING':
                    dirtiness = uniform(0.0, 2.0)

            setattr(injury_properties, dirt, dirtiness)

        bpy.ops.zomboid.create_dirtiness_mask()

        model_properties.stop_texture_updates = False

        return ({'FINISHED'})