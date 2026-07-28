# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy
import re
import sys

from bpy.types import Operator
from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders

class PZ_Assets_ParseBodyLocationTxt(Operator):
    bl_idname = "zomboid.parse_body_location_txt"
    bl_label = "Parse Body Location Txt"
    bl_description = "Get all of the data pertaining to BodyLocations from Project Zomboid"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        body_locations = addon_prefs.pz_human_body_locations
        clothing_items = addon_prefs.pz_human_clothing_item_slots

        for folder, origin in get_zomboid_asset_folders(context, 'items'):
            if (folder / 'clothing.txt').is_file():
                in_main_portion = False
                in_item_block = False

                current_clothing_item = ''
                current_body_location = ''

                with open(str((folder / 'clothing.txt')), 'r', encoding='utf-8') as file:
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
                                print(current_body_location)

                            if 'ClothingItem' in txt_line:
                                current_clothing_item = txt_line.split('= ')[
                                    1].split(',')[0]
                                print(current_clothing_item)

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