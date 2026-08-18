# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import os
import bpy

from pathlib import Path
from bpy.types import Operator
from ...Utility.PZ_AssetMethods import get_zomboid_asset, parse_path

class PZ_Assets_GetAttachmentPoints(Operator):
    bl_idname = "zomboid.get_attachments"
    bl_label = "Get Attachments"
    bl_description = "Get all of the data pertaining to attachments (weapons, held food, etc.) from Project Zomboid"

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        attachments = addon_data.pz_attachments

        attachments.clear()

        def parse_file(path):
            if path.is_file():
                in_main_portion = False
                in_model_block = False
                in_attachment_block = False

                current_item = ''
                current_attachment_point = ''
                current_model_path = ''
                current_texture_path = ''

                offset_vals = [0, 0, 0]
                rotation_vals = [0, 0, 0]
                scale_val = 1

                attachment_stack = []

                with path.open('r', encoding='utf-8') as file:
                    # TODO: Replace with albion's more sophisticated parser
                    for line in file:
                        txt_line = line.strip()

                        if not in_main_portion and '{' in txt_line:
                            in_main_portion = True
                            continue

                        if 'model' in txt_line:
                            current_item = txt_line.split('model ')[1]

                        if in_main_portion and not in_model_block:
                            if '{' in txt_line:
                                in_model_block = True
                                continue
                            if '}' in txt_line:
                                in_main_portion = False
                                continue

                        if in_model_block and not in_attachment_block:
                            if 'mesh =' in txt_line:
                                current_model_path = txt_line.split('= ')[1].split(',')[0]
                            if 'texture =' in txt_line:
                                current_texture_path = txt_line.split('= ')[1].split(',')[0]
                            if 'attachment' in txt_line:
                                current_attachment_point = txt_line.split('attachment ')[1]
                            if '{' in txt_line:
                                in_attachment_block = True
                                continue
                            if '}' in txt_line:
                                in_model_block = False

                                for item in attachment_stack:
                                    if item['attachment_point'] == 'world':
                                        attachment_stack.remove(item)

                                if len(attachment_stack) > 0:
                                    new_attachment = attachments.add()

                                    new_attachment.name = current_item

                                    x = get_zomboid_asset(context, Path('media/models_X') / parse_path(current_model_path), allowed_types=['.x', '.fbx', '.glb'])
                                    assert x[0] is not None
                                    print(x)
                                    new_attachment.model_path = os.fspath(x[0])
                                    new_attachment.model_type = x[1]

                                    if current_texture_path == '':
                                        new_attachment.texture_path = os.fspath(get_zomboid_asset(context, Path('media/textures') / parse_path(current_model_path), allowed_types=['.png'])[0])
                                    else:
                                        new_attachment.texture_path = os.fspath(get_zomboid_asset(context, Path('media/textures') / parse_path(current_texture_path), allowed_types=['.png'])[0])

                                    # for item in attachment_stack:
                                    #     new_attachment_group = new_attachment.attachment_groups.add()
                                    #     new_attachment_group.attachment_point = item['attachment_point']
                                    #     new_attachment_group.offset = item['offset']
                                    #     new_attachment_group.rotation = item['rotate']
                                    #     new_attachment_group.scale = item['scale']

                                    attachment_stack.clear()
                                    current_model_path = ''
                                    current_texture_path = ''
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
                            if 'scale' in txt_line:
                                scale_val = float(txt_line.split('= ')[1].split(',')[0])
                                continue
                            if '}' in txt_line:
                                in_attachment_block = False

                                attachment_stack.append({
                                    'attachment_point' : current_attachment_point,
                                    'offset' : offset_vals,
                                    'rotate' : rotation_vals,
                                    'scale' : scale_val
                                })

                                current_attachment_point = ''
                                offset_vals = [0, 0, 0]
                                rotation_vals = [0, 0, 0]
                                scale_val = 1

                                continue

        parse_file(get_zomboid_asset(context, Path("media/scripts/generated/models_weapons.txt"))[0])

        return ({'FINISHED'})