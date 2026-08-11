# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

from random import uniform

class PZ_HumanRig_RandomizeBloodiness(Operator):
    bl_idname = "zomboid.randomize_bloodiness"
    bl_label = "Randomize Bloodiness"
    bl_description = "Randomize the values of all the body bloodiness options based on a set intensity"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties
        random_properties = context.active_object.pz_random_properties

        blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                       "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                       "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                       "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                       "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                       "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

        model_properties.stop_texture_updates = True

        for blood in blood_props:
            setattr(injury_properties, blood, 0)
            bloodiness = 0
            match random_properties.random_bloodiness_intensity:
                case 'SOME':
                    bloodiness = uniform(0.0, 1.5)
                case 'MODERATE':
                    bloodiness = uniform(0.0, 2.5)
                case 'LOTS':
                    bloodiness = uniform(0.0, 3.5)
                case 'DRENCHED':
                    bloodiness = uniform(0.0, 5.0)

            setattr(injury_properties, blood, bloodiness)

        bpy.ops.zomboid.create_bloodiness_mask()

        model_properties.stop_texture_updates = False

        return ({'FINISHED'})