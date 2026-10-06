# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
import os
import re
import xml.etree.ElementTree as ET

from bpy.types import Operator
from pathlib import Path

import bpy
from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders, scan_path


class PZ_Assets_GetSkinTextures(Operator):
    bl_idname = "zomboid.get_skin_textures"
    bl_label = "Get Skin & Stubble Textures"
    bl_description = "Get all the references to the skin and stubble textures so Blender can pull them later"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        skin_textures = addon_data.pz_skin_texture_references
        stubble_textures = addon_data.pz_stubble_texture_references
        visibility_masks = addon_data.pz_visibility_mask_references
        overlay_masks = addon_data.pz_overlay_mask_references

        skin_textures.clear()
        stubble_textures.clear()
        visibility_masks.clear()
        overlay_masks.clear()

        #TODO Find a way to find the texture names without being predetermined, and optimize

        human_skin_tex_names = [
            'MaleBody01',
            'MaleBody01a',
            'MaleBody02',
            'MaleBody02a',
            'MaleBody03',
            'MaleBody03a',
            'MaleBody04',
            'MaleBody04a',
            'MaleBody05',
            'MaleBody05a',
            'FemaleBody01',
            'FemaleBody02',
            'FemaleBody03',
            'FemaleBody04',
            'FemaleBody05',
        ]

        zombie_skin_tex_names = [
            'M_ZedBody01_level1',
            'M_ZedBody01_level2',
            'M_ZedBody01_level3',
            'M_ZedBody02_level1',
            'M_ZedBody02_level2',
            'M_ZedBody02_level3',
            'M_ZedBody03_level1',
            'M_ZedBody03_level2',
            'M_ZedBody03_level3',
            'M_ZedBody04_level1',
            'M_ZedBody04_level2',
            'M_ZedBody04_level3',
            'M_ZedBody05_level1',
            'M_ZedBody05_level2',
            'M_ZedBody05_level3',

            'F_ZedBody01_level1',
            'F_ZedBody01_level2',
            'F_ZedBody01_level3',
            'F_ZedBody02_level1',
            'F_ZedBody02_level2',
            'F_ZedBody02_level3',
            'F_ZedBody03_level1',
            'F_ZedBody03_level2',
            'F_ZedBody03_level3',
            'F_ZedBody04_level1',
            'F_ZedBody04_level2',
            'F_ZedBody04_level3',
            'F_ZedBody05_level1',
            'F_ZedBody05_level2',
            'F_ZedBody05_level3',
        ]

        mannequin_tex_names = [
            'M_Mannequin_Black',
            'M_Mannequin_White'
        ]

        scarecrow_tex_names = [
            'Male_Scarecrow'
        ]

        skeleton_tex_names = [
            'Skeleton',
            'SkeletonBurned',
            'SkeletonMuscle'
        ]

        tone_pattern = r'(?<=Body)(\d+)'
        tone_regex = re.compile(tone_pattern)

        zombification_pattern = r'(?<=level)(\d+)'
        zombification_regex = re.compile(zombification_pattern)

        overlay_mask_pattern = r'(?<=BloodMask).*'
        overlay_mask_regex = re.compile(overlay_mask_pattern)

        for folder, mod_name in get_zomboid_asset_folders(context, "media/textures/Body"):
            # Skin Textures
            for path in scan_path(folder):
                path_name = os.path.basename(path)
                path_root, path_stem = os.path.splitext(path_name)
                if os.path.isfile(path):
                    if path_root in human_skin_tex_names + zombie_skin_tex_names + mannequin_tex_names + scarecrow_tex_names + skeleton_tex_names:    
                        overwrite_check = skin_textures.find(path_root)
                        if overwrite_check != -1:
                            if addon_data.allow_overwriting:
                                skin_textures.remove(overwrite_check)
                            else:
                                continue
                        
                        item = skin_textures.add()

                        item.name = path_stem
                        item.texture_path = os.fspath(path)
                        item.origin = mod_name

                        if path_stem in human_skin_tex_names:
                            item.body_type = 'HUMAN'
                            item.sex = 'FEMALE' if 'FemaleBody' in path_stem else 'MALE'
                            item.skin_tone = int(tone_regex.search(path_stem).group())
                            item.chest_hair = path_stem.endswith('a')
                            continue

                        if path_stem in zombie_skin_tex_names:
                            item.body_type = 'ZOMBIE'
                            item.zombification = int(zombification_regex.search(path_stem).group())
                            item.sex = 'FEMALE' if 'F_' in path_stem else 'MALE'
                            item.skin_tone = int(tone_regex.search(path_stem).group())
                            continue
                            
                        if path_stem in mannequin_tex_names:
                            item.body_type = 'MANNEQUIN'
                            item.sex = 'FEMALE' if 'F_' in path_stem else 'MALE'
                            continue

                        if path_stem in skeleton_tex_names:
                            item.body_type = 'SKELETON'
                            continue

                        if path_stem in scarecrow_tex_names:
                            item.body_type = 'SCARECROW'
                            continue
                
                elif os.path.isdir(path):
                    # Stubble Textures
                    if path_name.lower() == 'stubble':
                        for subfile in scan_path(path):
                            subfile_name = os.path.basename(subfile)
                            subfile_root, subfile_stem = os.path.splitext(subfile_name)
                            overwrite_check = stubble_textures.find(subfile_root)
                            if overwrite_check != -1:
                                if addon_data.allow_overwriting:
                                    stubble_textures.remove(overwrite_check)
                                else:
                                    continue
                            
                            item = stubble_textures.add()
                            
                            item.texture_path = os.fspath(subfile)
                            item.name = subfile_stem
                            item.sex = 'FEMALE' if 'F_' in subfile_stem else 'MALE'
                            item.stubble_type = 'BEARD' if 'Beard' in subfile_stem else 'HAIR'
                            item.origin = mod_name
                    
                    # Visibility Masks
                    if path_name.lower() == 'masks':
                        for subfile in scan_path(path):
                            subfile_name = os.path.basename(subfile)
                            subfile_root, subfile_stem = os.path.splitext(subfile_name)
                            overwrite_check = visibility_masks.find(subfile_stem)
                            if overwrite_check != -1:
                                if addon_data.allow_overwriting:
                                    visibility_masks.remove(overwrite_check)
                                else:
                                    continue

                            item = visibility_masks.add()
                            
                            item.name = 'FullBody' if subfile_stem == 'Mask' else subfile_stem
                            item.texture_path = os.fspath(subfile)

            # Overlay Masks
            folder_parent = os.path.dirname(folder)
            blood_textures = os.path.join(folder_parent, 'BloodTextures')
            if os.path.isdir(blood_textures):
                for path in scan_path(blood_textures):
                    path_name = os.path.basename(path)
                    path_root, path_stem = os.path.splitext(path_name)
                    # No need for overwriting
                    if 'BloodMask' in path_stem:
                        item = overlay_masks.add()
                        
                        item.name = overlay_mask_regex.search(path_stem).group()
                        item.texture_path = os.fspath(path)

        return ({'FINISHED'})
