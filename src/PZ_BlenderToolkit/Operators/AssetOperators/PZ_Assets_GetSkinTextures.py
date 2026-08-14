# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
import os
import re
import xml.etree.ElementTree as ET

from bpy.types import Operator
from pathlib import Path

from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders

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

        for folder, mod_name in get_zomboid_asset_folders(context, 'media/textures/Body'):
            # Skin Textures
            for file in folder.iterdir():
                if file.is_file():
                    if file.stem in human_skin_tex_names + zombie_skin_tex_names + mannequin_tex_names + scarecrow_tex_names + skeleton_tex_names:    
                        overwrite_check = skin_textures.find(file.stem)
                        if overwrite_check != -1:
                            if addon_data.allow_overwriting:
                                skin_textures.remove(overwrite_check)
                            else:
                                continue
                        
                        item = skin_textures.add()

                        item.name = file.stem
                        item.texture_path = str(file)
                        item.origin = mod_name

                        if file.stem in human_skin_tex_names:
                            item.body_type = 'HUMAN'
                            item.sex = 'FEMALE' if 'FemaleBody' in file.stem else 'MALE'
                            item.skin_tone = int(tone_regex.search(file.stem).group())
                            item.chest_hair = file.stem.endswith('a')
                            continue

                        if file.stem in zombie_skin_tex_names:
                            item.body_type = 'ZOMBIE'
                            item.zombification = int(zombification_regex.search(file.stem).group())
                            item.sex = 'FEMALE' if 'F_' in file.stem else 'MALE'
                            item.skin_tone = int(tone_regex.search(file.stem).group())
                            continue
                            
                        if file.stem in mannequin_tex_names:
                            item.body_type = 'MANNEQUIN'
                            item.sex = 'FEMALE' if 'F_' in file.stem else 'MALE'
                            continue

                        if file.stem in skeleton_tex_names:
                            item.body_type = 'SKELETON'
                            continue

                        if file.stem in scarecrow_tex_names:
                            item.body_type = 'SCARECROW'
                            continue
                
                if file.is_dir():

                    # Stubble Textures
                    if file.name.lower() == 'stubble':
                        for subfile in file.iterdir():
                            overwrite_check = stubble_textures.find(subfile.stem)
                            if overwrite_check != -1:
                                if addon_data.allow_overwriting:
                                    stubble_textures.remove(overwrite_check)
                                else:
                                    continue
                            
                            item = stubble_textures.add()
                            
                            item.texture_path = os.fspath(subfile)
                            item.name = subfile.stem
                            item.sex = 'FEMALE' if 'F_' in subfile.stem else 'MALE'
                            item.stubble_type = 'BEARD' if 'Beard' in subfile.stem else 'HAIR'
                            item.origin = mod_name
                    
                    # Visibility Masks
                    if file.name.lower() == 'masks':
                        for subfile in file.iterdir():
                            overwrite_check = visibility_masks.find(subfile.stem)
                            if overwrite_check != -1:
                                if addon_data.allow_overwriting:
                                    visibility_masks.remove(overwrite_check)
                                else:
                                    continue

                            item = visibility_masks.add()
                            
                            item.name = 'FullBody' if subfile.stem == 'Mask' else subfile.stem
                            item.texture_path = os.fspath(subfile)

            # Overlay Masks
            if (folder.parent / 'BloodTextures').is_dir():

                for file in (folder.parent / 'BloodTextures').iterdir():
                    # No need for overwriting
                    if 'BloodMask' in file.stem:
                        item = overlay_masks.add()
                        
                        item.name = overlay_mask_regex.search(file.stem).group()
                        item.texture_path = os.fspath(file)

        return ({'FINISHED'})