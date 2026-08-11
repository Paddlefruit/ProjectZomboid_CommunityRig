# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from bpy.types import Operator

from random import uniform, randint, choices

from .....Utility.PZ_FilterMethods import filter_zombie_injuries

class PZ_HumanRig_RandomizeBodyDamage(Operator):
    bl_idname = "zomboid.randomize_body_damage"
    bl_label = "Randomize Body Damage"
    bl_description = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        model_properties = context.active_object.pz_model_properties
        injury_properties = context.active_object.pz_injury_properties
        random_properties = context.active_object.pz_random_properties

        # Randomize Bloodiness Properties
        if random_properties.randomize_bloodiness:

            blood_props = ["upper_torso_bloodiness", "lower_torso_bloodiness", "left_hand_bloodiness",
                        "right_hand_bloodiness", "left_forearm_bloodiness", "right_forearm_bloodiness",
                        "left_upperarm_bloodiness", "right_upperarm_bloodiness", "head_bloodiness",
                        "neck_bloodiness", "groin_bloodiness", "left_thigh_bloodiness",
                        "right_thigh_bloodiness", "left_shin_bloodiness", "right_shin_bloodiness",
                        "left_foot_bloodiness", "right_foot_bloodiness", "back_bloodiness"]

            model_properties.stop_texture_updates = True

            for blood in blood_props:
                if randint(1, 100) <= random_properties.part_bloodiness_chance:
                    setattr(injury_properties, blood, uniform(random_properties.min_random_bloodiness, random_properties.max_random_bloodiness))

            bpy.ops.zomboid.create_bloodiness_mask()

            model_properties.stop_texture_updates = False


        # Randomize Dirtiness Properties
        if random_properties.randomize_dirtiness:
                
            dirt_props = ["upper_torso_dirtiness", "lower_torso_dirtiness", "left_hand_dirtiness",
                                "right_hand_dirtiness", "left_forearm_dirtiness", "right_forearm_dirtiness",
                                "left_upperarm_dirtiness", "right_upperarm_dirtiness", "head_dirtiness",
                                "neck_dirtiness", "groin_dirtiness", "left_thigh_dirtiness",
                                "right_thigh_dirtiness", "left_shin_dirtiness", "right_shin_dirtiness",
                                "left_foot_dirtiness", "right_foot_dirtiness", "back_dirtiness"]
            
            model_properties.stop_texture_updates = True

            for dirt in dirt_props:
                if randint(1, 100) <= random_properties.part_dirtiness_chance:
                    setattr(injury_properties, dirt, uniform(random_properties.min_random_dirtiness, random_properties.max_random_dirtiness))

            bpy.ops.zomboid.create_dirtiness_mask()

            model_properties.stop_texture_updates = False

        # Randomize Body Injuries
        if random_properties.randomize_body_injuries:
            injury_props = ["upper_torso_injury", "lower_torso_injury", "left_hand_injury",
                            "right_hand_injury", "left_forearm_injury", "right_forearm_injury",
                            "left_upperarm_injury", "right_upperarm_injury", "head_injury",
                            "neck_injury", "groin_injury", "left_thigh_injury",
                            "right_thigh_injury", "left_shin_injury", "right_shin_injury",
                            "left_foot_injury", "right_foot_injury"]

            model_properties.stop_texture_updates = True

            for injury in injury_props:
                setattr(injury_properties, injury, 'NONE')

            options = ['SCRATCH', 'LACERATION', 'BITE']
            chances = [random_properties.random_scratch_chance,
                        random_properties.random_laceration_chance, 
                        random_properties.random_bite_chance]

            injury_num = randint(random_properties.min_random_body_injuries, random_properties.max_random_body_injuries)

            for i in range(1, injury_num):
                selected_injury = injury_props[randint(0, len(injury_props) - 1)]
                final_injury = ''
                if randint(1, 100) <= random_properties.random_bandage_chance or selected_injury is injury_properties.head_injury:
                    if randint(1, 100) <= random_properties.random_bloody_bandage_chance:
                        final_injury = 'BANDAGEBLOODY'
                    else:
                        final_injury = 'BANDAGE'
                else:
                    final_injury = choices(options, weights=chances)[0]

                if selected_injury == 'head_injury' and selected_injury not in ('NONE', 'BANDAGE', 'BANDAGEBLOODY'):
                    continue

                setattr(injury_properties, selected_injury, final_injury)

                injury_props.remove(selected_injury)

            bpy.ops.zomboid.create_body_texture()

            model_properties.stop_texture_updates = False

        # Randomize Zombie Injuries
        if random_properties.randomize_zombie_injuries:
            injury_choices = filter_zombie_injuries(self, context)
            
            zombie_injuries = context.active_object.pz_zombie_injuries

            model_properties.stop_texture_updates = True

            zombie_injuries.clear()

            injury_num = randint(random_properties.min_random_zombie_injuries, random_properties.max_random_zombie_injuries)

            for i in range(1, injury_num):
                if injury_choices:
                    selected_injury = injury_choices[randint(0, len(injury_choices) - 1)]

                    if selected_injury[0] == 'NONE':
                        injury_choices.remove(selected_injury)
                        continue

                    new_injury = zombie_injuries.add()
                    new_injury.name = selected_injury[0]
                    new_injury.texture_path = addon_data.pz_zombie_injury_references.get(selected_injury[0]).texture_path

                    injury_choices.remove(selected_injury)

            bpy.ops.zomboid.create_body_texture()

            model_properties.stop_texture_updates = False

        return ({'FINISHED'})