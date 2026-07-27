# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 

from bpy.types import Operator
from pathlib import Path

class PZ_Assets_GetModDirectories(Operator):
    bl_idname = "zomboid.get_mod_directories"
    bl_label = "Get Mod Directories"
    bl_description = "Automatically grabs all installed mods and populates the directories folder for you. It does this by traversing upwards twice from the Project Zomboid directory into \'steamapps\', then goes into the workshop/common/108600 folder where your mods are installed"

    @classmethod
    def poll(cls, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        return addon_prefs.pz_directory != ''

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        dirs = addon_prefs.pz_human_mod_directory_slots

        dirs.clear()

        pz_dir = Path(addon_prefs.pz_directory)
        steamapps_dir = pz_dir.parent.parent
        mods_dir = steamapps_dir / 'workshop' / 'content' / '108600'

        mod_folders = [item for item in mods_dir.iterdir() if item.is_dir()]

        for mod_path in mod_folders:
            submods_dir = mod_path / 'mods'
            submod_folders = [
                item for item in submods_dir.iterdir() if item.is_dir()]
            for submod_path in submod_folders:
                # For now, just ignore any mods that don't have a 42 version
                version_folders = [
                    item for item in submod_path.iterdir() if item.is_dir()]

                latest_submod_version_folder = None
                latest_submod_version_num = 0.0
                for folder in version_folders:
                    try:
                        if float(folder.name) > latest_submod_version_num:
                            latest_submod_version_folder = folder
                            latest_submod_version_num = float(folder.name)
                    except ValueError:
                        continue
                if latest_submod_version_folder is not None:
                    mod_name = ''
                    mod_author = ''
                    try:
                        with open(latest_submod_version_folder / 'mod.info', 'r') as file:
                            for line in file:
                                info_line = line.strip()

                                if ('name=') in info_line:
                                    mod_name = info_line.split('name=')[1]
                                elif ('author=') in info_line:
                                    mod_author = info_line.split('author=')[1]

                        new_dir = dirs.add()
                        if mod_name != '':
                            new_dir.name = mod_name
                        if mod_author != '':
                            new_dir.author = mod_author
                        new_dir.mod_dir = str(latest_submod_version_folder)
                        new_dir.latest_pz_version = round(
                            latest_submod_version_num, 2)

                    except FileNotFoundError:
                        pass

        return ({'FINISHED'})