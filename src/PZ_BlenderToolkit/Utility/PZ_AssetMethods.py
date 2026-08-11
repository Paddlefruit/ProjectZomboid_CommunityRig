# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import functools
from pathlib import Path

def directx_import_available():
    checks = ['bl_ext.blender_org.io_directx_x',
              'bl_ext.user_default.io_directx_x'
              ]
    for check in checks:
        if check in bpy.context.preferences.addons.keys():
            return True
    return False

@functools.lru_cache(maxsize=256)
def get_zomboid_asset_folders(context, parent_path):
    addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
    mods = addon_data.pz_mod_directories

    results = []

    vanilla_results = [dir for dir in Path(addon_data.pz_directory).rglob(
        parent_path, case_sensitive=False) if dir.is_dir()]
    for path in vanilla_results:
        results.append((path, 'Project Zomboid'))

    for mod in mods:
        if mod.active:
            candidate_paths = [
                Path(mod.mod_dir),
                Path(mod.mod_dir).parent / 'common'
            ]
            for path in candidate_paths:
                modded_results = [dir for dir in path.rglob(
                    parent_path, case_sensitive=False) if dir.is_dir()]
                for path in modded_results:
                    results.append((path, mod.name))
    return results

def get_zomboid_asset(context, item_path, allowed_types=[]):
    item_path = item_path.replace('\\', '/')
    parent_name = Path(item_path).parent.name
    asset_name = Path(item_path).stem

    for folder, mod_name in get_zomboid_asset_folders(context, parent_name):
        for file in folder.glob(f"{asset_name}.*", case_sensitive=False):
            if file.is_file():
                if len(allowed_types) > 0:
                    if file.suffix.lower() in allowed_types:
                        return file, file.suffix.lower()
                else:
                    return file, file.suffix.lower()

    if 'bk/' not in item_path:
        print('Could not find ' + item_path)
        
    return (None, None)