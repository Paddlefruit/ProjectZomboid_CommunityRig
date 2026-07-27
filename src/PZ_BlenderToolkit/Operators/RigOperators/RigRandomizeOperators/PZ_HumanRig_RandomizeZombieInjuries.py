# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from random import randint

from ....Utility.PZ_FilterMethods import filter_zombie_injuries

class PZ_HumanRig_RandomizeZombieInjuries(Operator):
    bl_idname = "zomboid.randomize_zombie_injuries"
    bl_label = "Randomize Zombie Injuries"
    bl_description = "Add a set or random amount of random zombie specific injuries"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props

        injury_choices = filter_zombie_injuries(self, context)

        zombie_injuries = context.active_object.pz_human_zombie_injuries

        p.halt_texture_updates = True

        zombie_injuries.clear()

        injury_num = 0
        match p.random_zombie_injury_intensity:
            case 'INTACT':
                injury_num = randint(1, 3)
            case 'DAMAGED':
                injury_num = randint(3, 5)
            case 'HACKED APART':
                injury_num = randint(5, 15)
            case 'MUTILATED':
                injury_num = randint(20, 40)
            case 'RENDED APART':
                injury_num = randint(40, 73)
            case 'RANDOM':
                injury_num = randint(0, 73)

        for i in range(1, injury_num):
            selected_injury = injury_choices[randint(
                0, len(injury_choices) - 1)]

            if selected_injury[0] == 'NONE':
                injury_choices.remove(selected_injury)
                continue

            new_injury = zombie_injuries.add()
            new_injury.name = selected_injury[0]
            new_injury.texture_path = addon_prefs.pz_human_zombie_injuries.get(
                selected_injury[0]).texture_path

            injury_choices.remove(selected_injury)

        bpy.ops.zomboid.create_body_texture()

        p.halt_texture_updates = False

        return ({'FINISHED'})