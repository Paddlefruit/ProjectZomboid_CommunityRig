# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

from random import randint, choices

class PZ_HumanRig_RandomizeBodyInjuries(Operator):
    bl_idname = "zomboid.randomize_body_injuries"
    bl_label = "Randomize Body Injuries"
    bl_description = "Randomize the values of all the body intensity options based on a set intensity"

    def execute(self, context):
        p = context.active_object.pz_human_props

        injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                        "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                        "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                        "neck_injury", "groin_injury", "left_thigh_injury",
                        "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                        "left_foot_injury", "right_foot_injury"]

        p.halt_texture_updates = True

        for injury in injury_props:
            setattr(p, injury, 'NONE')

        options = ['SCRATCH', 'LACERATION', 'BITE']
        chances = [p.random_scratch_chance,
                   p.random_laceration_chance, p.random_bite_chance]

        injury_num = 0
        match p.random_injury_intensity:
            case 'MINOR':
                injury_num = randint(1, 2)
            case 'MODERATE':
                injury_num = randint(3, 4)
            case 'SERIOUS':
                injury_num = randint(5, 6)
            case 'SEVERE':
                injury_num = randint(7, 10)
            case 'INSANE':
                injury_num = randint(11, 16)
            case 'RANDOM':
                injury_num = randint(0, 16)

        for i in range(1, injury_num):
            selected_injury = injury_props[randint(0, len(injury_props) - 1)]
            final_injury = ''
            if randint(1, 100) <= p.random_bandage_chance or selected_injury is p.head_injury:
                if randint(1, 100) <= p.random_bloody_bandage_chance:
                    final_injury = 'BANDAGEBLOODY'
                else:
                    final_injury = 'BANDAGE'
            else:
                final_injury = choices(options, weights=chances)[0]

            if selected_injury == 'head_injury' and selected_injury not in ('NONE', 'BANDAGE', 'BANDAGEBLOODY'):
                continue

            setattr(p, selected_injury, final_injury)

            injury_props.remove(selected_injury)

        bpy.ops.zomboid.create_body_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})