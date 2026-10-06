# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import os
import bpy
import re

import bpy
from bpy.types import Operator

from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders, scan_path


class PZ_Assets_GetInjuries(Operator):
    bl_idname = "zomboid.get_injuries"
    bl_label = "Get Injuries"
    bl_description = "Get all the references to the injury textures so Blender can pull them later"

    body_parts = ['chest', 'abdomen', 'left_hand', 'right_hand', 'lower_left_arm',
                  'lower_right_arm', 'upper_left_arm', 'upper_right_arm', 'head',
                  'neck', 'groin', 'left_thigh', 'right_thigh',
                  'left_calf', 'right_calf', 'left_foot', 'right_foot']

    body_part_pattern = r"(?:" + "|".join(re.escape(part)
                                          for part in body_parts) + r")"
    body_part_regex = re.compile(body_part_pattern)

    injury_types = ['scratches', 'lacerations', 'bites', 'bandages']

    injury_type_pattern = r"(?:" + "|".join(re.escape(injury)
                                            for injury in injury_types) + r")"
    injury_type_regex = re.compile(injury_type_pattern)

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        body_injuries = addon_data.pz_body_injury_references
        zombie_injuries = addon_data.pz_zombie_injury_references

        body_injuries.clear()
        zombie_injuries.clear()

        for folder, _ in get_zomboid_asset_folders(context, "media/textures/BodyDmg"):
            for file in scan_path(folder, max_depth=-1):
                file_name = os.path.basename(file)
                _, file_stem = os.path.splitext(file_name)
                if os.path.isfile(file) and file_stem == '.png':
                    if file_name.startswith("M_ZedDmg"):
                        injury = zombie_injuries.add()
                        injury.name = file_name
                        injury.texture_path = os.fspath(file)
                        continue

                injury = body_injuries.add()

                injury.sex = 'FEMALE' if 'FemaleBody' in file_name else 'MALE'

                # TODO(aoqia): Replace regex with string operations
                body_part = self.body_part_regex.search(file_name)
                if body_part is not None:
                    injury.body_part = body_part.group()

                damage_type = self.injury_type_regex.search(file_name)
                if damage_type is not None:
                    match damage_type.group():
                        case 'scratches':
                            injury.damage_type = 'SCRATCH'
                        case 'lacerations':
                            injury.damage_type = 'LACERATION'
                        case 'bites':
                            injury.damage_type = 'BITE'
                        case 'bandages':
                            if '_blood' in file_name:
                                injury.damage_type = 'BANDAGEBLOODY'
                            else:
                                injury.damage_type = 'BANDAGE'
                injury.texture_path = os.fspath(file)

        return ({'FINISHED'})
