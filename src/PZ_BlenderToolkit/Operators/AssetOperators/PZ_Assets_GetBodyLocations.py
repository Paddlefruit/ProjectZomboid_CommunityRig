# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy
import re
import sys

from bpy.types import Operator

class PZ_Assets_GetBodyLocations(Operator):
    bl_idname = "zomboid.get_body_locations"
    bl_label = "Get Body Locations"
    bl_description = "Get all of the data pertaining to BodyLocations from Project Zomboid"

    def parse_body_locations_lua(self, context):
        g = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations

        body_locations.clear()

        g.body_location_active_index = 0

        file_dir = ''

        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = g.pz_directory + 'media\\lua\\shared\\NPCs\\BodyLocations.lua'
        elif sys.platform == 'linux':
            file_dir = g.pz_directory + 'projectzomboid/media/lua/shared/NPCs/BodyLocations.lua'

        with open(file_dir, 'r', encoding='utf-8') as file:
            for line in file:
                lua_line = line.strip()

                # Line creates a new body location
                if 'getOrCreateLocation' in lua_line:
                    pattern = r'\.(.*?)\)'
                    body_location = body_locations.add()
                    body_location.name = re.findall(pattern, lua_line)[0]

                elif 'setExclusive' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.exclusive_locations.add()
                            hide_loc.name = matches[0]
                            break

                elif 'setHideModel' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.hide_locations.add()
                            hide_loc.name = matches[0]
                            break

                elif 'setAltModel' in lua_line:
                    pattern = r'ItemBodyLocation\.([A-Z_]+)'
                    matches = re.findall(pattern, lua_line)
                    for loc in body_locations:
                        if loc.name == matches[1]:
                            hide_loc = loc.properties.alt_locations.add()
                            hide_loc.name = matches[0]
                            break

        return ({'FINISHED'})

    def parse_clothing_txt(self, context):
        g = context.scene.pz_human_global_props
        body_locations = context.scene.pz_human_body_locations
        clothing_items = context.scene.pz_human_clothing_item_slots

        file_dir = ''

        # Construct the filepath to the 'BodyLocations.lua' file in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            file_dir = g.pz_directory + 'media\\scripts\\generated\\items\\clothing.txt'
        elif sys.platform == 'linux':
            file_dir = g.pz_directory + 'projectzomboid/media/scripts/generated/items/clothing.txt'

        in_main_portion = False
        in_item_block = False

        current_clothing_item = ''
        current_body_location = ''

        with open(file_dir, 'r', encoding='utf-8') as file:
            # TODO: Replace with albion's more sophisticated parser
            for line in file:
                txt_line = line.strip()

                if not in_main_portion and '{' in txt_line:
                    in_main_portion = True
                    continue

                if in_main_portion and not in_item_block:
                    if 'item' in txt_line:
                        current_clothing_item = txt_line.split('item ')[1]
                        continue
                    if '{' in txt_line:
                        in_item_block = True
                        continue
                    if '}' in txt_line:
                        in_main_portion = False
                        continue

                if in_main_portion and in_item_block:
                    if 'BodyLocation' in txt_line:
                        current_body_location = txt_line.split(
                            ':')[1].split(',')[0].upper()
                        # print(current_body_location)

                    if 'ClothingItem' in txt_line:
                        current_clothing_item = txt_line.split('= ')[
                            1].split(',')[0]
                        # print(current_clothing_item)

                    if '}' in txt_line:
                        in_item_block = False

                        for clothing_item in clothing_items:
                            if clothing_item.name == current_clothing_item:
                                for body_location in body_locations:
                                    if body_location.name == current_body_location:

                                        current_clothing_item = ''
                                        current_body_location = ''
                                    break
                                break

                        continue

        return ({'FINISHED'})

    def execute(self, context):
        self.parse_body_locations_lua(context)
        self.parse_clothing_txt(context)

        return ({'FINISHED'})