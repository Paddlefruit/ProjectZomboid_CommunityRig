# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from bpy.types import Operator
from ...Utility.PZ_AssetMethods import get_zomboid_asset_folders

class PZ_Assets_GetAttachmentPoints(Operator):
    bl_idname = "zomboid.get_attachment_points"
    bl_label = "Get Attachment Points"
    bl_description = "Get all of the data pertaining to attachment locations on the body from Project Zomboid"

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        attachment_points = addon_prefs.pz_human_attachment_points

        attachment_points.clear()

        def parse_file(path):
            if path.is_file():
                in_main_portion = False
                in_model_block = False
                in_attachment_block = False

                current_model = ''
                current_attachment = ''

                offset_vals = [0, 0, 0]
                rotation_vals = [0, 0, 0]
                bone_name = ''

                with open(str(path), 'r', encoding='utf-8') as file:
                    # TODO: Replace with albion's more sophisticated parser
                    for line in file:
                        txt_line = line.strip()

                        if not in_main_portion and '{' in txt_line:
                            in_main_portion = True
                            continue

                        if 'model' in txt_line:
                            current_model = txt_line.split('model ')[1]
                        
                        if in_main_portion and not in_model_block:
                            if '{' in txt_line:
                                in_model_block = True
                                continue
                            if '}' in txt_line:
                                in_main_portion = False
                                continue

                        if in_model_block and not in_attachment_block:
                            if 'attachment' in txt_line:
                                current_attachment = txt_line.split('attachment ')[1]
                            if '{' in txt_line:
                                in_attachment_block = True
                                continue
                            if '}' in txt_line:
                                in_model_block = False
                                current_model = ''
                                continue

                        if in_attachment_block:
                            if 'offset' in txt_line:
                                offset_text = txt_line.split('= ')[1].split(',')[0].split()
                                for index, val in enumerate(offset_text):
                                    offset_vals[index] = float(val)
                                continue
                            if 'rotate' in txt_line:
                                rotation_text = txt_line.split('= ')[1].split(',')[0].split()
                                for index, val in enumerate(rotation_text):
                                    rotation_vals[index] = float(val)
                                continue
                            if 'bone' in txt_line:
                                bone_name = txt_line.split('= ')[1].split(',')[0]
                                continue

                            if  '}' in txt_line:
                                in_attachment_block = False

                                new_attachment_point = attachment_points.add()

                                new_attachment_point.name = current_attachment
                                new_attachment_point.bone_name = bone_name

                                if current_model == 'FemaleBody':
                                    new_attachment_point.sex = 'FEMALE'
                                elif current_model == 'MaleBody':
                                    new_attachment_point.sex = 'MALE'

                                new_attachment_point.offset = offset_vals
                                new_attachment_point.rotation = rotation_vals

                                current_attachment = ''
                                offset_vals = [0, 0, 0]
                                rotation_vals = [0, 0, 0]
                                bone_name = ''

                                continue

        for folder, origin in get_zomboid_asset_folders(context, 'generated'):
            parse_file(folder / 'models_characters.txt')

        return ({'FINISHED'})