# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy
import re

from bpy.types import Operator
from ...Utility.PZ_AssetMethods import get_zomboid_asset

class PZ_Assets_ParseBodyLocationLua(Operator):
    bl_idname = "zomboid.parse_body_location_lua"
    bl_label = "Parse Body Location Lua"
    bl_description = "Get all of the data pertaining to BodyLocations from Project Zomboid"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        body_locations = addon_data.pz_body_locations

        body_locations.clear()
        addon_data.body_location_active_index = -1

        file, _ = get_zomboid_asset(context, "media/lua/shared/NPCs/BodyLocations.lua")
        
        if file is not None:
            with open(file, 'r', encoding='utf-8') as file:

                counter = 0
                
                for line in file:
                    lua_line = line.strip()

                    # Line creates a new body location
                    if 'getOrCreateLocation' in lua_line:
                        pattern = r'\.(.*?)\)'
                        body_location = body_locations.add()
                        body_location.name = re.findall(pattern, lua_line)[0]
                        body_location.order = counter
                        counter += 1

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