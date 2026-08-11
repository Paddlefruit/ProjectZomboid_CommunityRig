# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy
import os
import xml.etree.ElementTree as ET

from bpy.types import Operator 
from pathlib import Path

from ...Utility.PZ_AssetMethods import get_zomboid_asset, get_zomboid_asset_folders

class PZ_Assets_ParseClothingXMLs(Operator):
    bl_idname = "zomboid.parse_clothing_xmls"
    bl_label = "Parse Clothing XMLs"
    bl_description = "Parse all the clothing xmls to get the data needed to import clothing items into Blender"

    item_count = 0

    def parse_folder(self, context, dir, clothing_items, origin):
        for file in dir.glob("*.xml"):
            if file.is_file():
                try:
                    # Begin parsing the XML contents of the file
                    tree = ET.parse(file)
                    root = tree.getroot()

                    has_model = False
                    has_attach_bone = False
                    is_static = False

                    # If there is an existing clothing item with the same name as the file we are about to evaluate, remove it and overwrite it
                    overwrite_check = clothing_items.find(
                        os.path.splitext(file.name)[0])
                    if overwrite_check != -1:
                        clothing_items.remove(
                            overwrite_check)

                    # Create and fill out the clothing item slot
                    item = clothing_items.add()

                    # Name
                    item.name = os.path.splitext(file.name)[0]

                    # GUID
                    m = root.find('m_GUID')
                    if m is not None:
                        item.guid = m.text

                    # Models
                    def get_model(xml_id):
                        m = root.find(xml_id)
                        if m is not None and m.text is not None and m.text != 'null':
                            path = m.text
                            start = path.find(':') + 1
                            end = path.find('.')
                            if end == -1:
                                path = path[start:]
                            else:
                                path = path[start:end]
                            if 'media\\models_X' not in path:
                                path = str(Path('media') /
                                           'models_X' / Path(path))
                            x, y = get_zomboid_asset(context, path)
                            if y is not None:
                                return (str(x), y, False)
                            else:
                                return ('', 'N/A', True)
                        else:
                            return ('', 'N/A', True)

                    item.male_model_path, item.model_type, item.is_body_texture = get_model('m_MaleModel')
                    item.male_alt_model_path = get_model('m_AltMaleModel')[0]
                    item.female_model_path, item.model_type, item.is_body_texture = get_model('m_FemaleModel')
                    item.female_alt_model_path = get_model('m_AltFemaleModel')[0]

                    if item.male_model_path != '' or item.female_model_path != '':
                        has_model = True

                    # Attach Bone
                    m = root.find('m_AttachBone')
                    if m is not None and m.text is not None:
                        has_attach_bone = True
                        item.attach_bone = m.text

                    # Static
                    m = root.find('m_Static')
                    if m is not None and m.text == 'true':
                        is_static = True

                    # Clothing Type
                    if not has_model:
                        item.clothing_type = 'BODYTEXTURE'
                    elif not is_static and not has_attach_bone or is_static and not has_attach_bone:
                        item.clothing_type = 'CLOTHINGMODEL'
                    else:
                        item.clothing_type = 'ACCESSORY'

                    # Textures
                    base_texture = root.find('m_BaseTextures')
                    textures = root.findall('textureChoices')
                    if base_texture is not None:
                        tex = item.texture_choices.add()
                        x = get_zomboid_asset(context, base_texture.text)
                        tex.texture_path = str(x[0])
                    for t in textures:
                        tex = item.texture_choices.add()
                        x = get_zomboid_asset(context, t.text)
                        tex.texture_path = str(x[0])

                    # Tintable
                    m = root.find('m_AllowRandomTint')
                    if m is not None and m.text == 'true':
                        item.tintable = True
                    else:
                        item.tintable = False

                    # Masks
                    masks = root.findall('m_Masks')
                    for m in masks:
                        item.visibility_mask_array[int(m.text)] = True

                    # Hat Category
                    m = root.find('m_HatCategory')
                    if m is not None:
                        match m.text:
                            case 'default':
                                item.hat_category = 0
                            case 'Group01':
                                item.hat_category = 1
                            case 'Group02':
                                item.hat_category = 2
                            case 'Group03':
                                item.hat_category = 3
                            case 'Group04':
                                item.hat_category = 4
                            case 'Group05':
                                item.hat_category = 5
                            case 'Group06':
                                item.hat_category = 6
                            case 'Group07':
                                item.hat_category = 7
                            case 'nohair':
                                item.hat_category = 8
                            case 'nohairnobeard':
                                item.hat_category = 9
                    else:
                        item.hat_category = -1

                    # Decal Group
                    m = root.find('m_DecalGroup')
                    if m is not None:
                        item.decal_group = m.text

                    # Origin
                    item.origin = origin

                    self.item_count = self.item_count + 1
                except ET.ParseError:
                    continue

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        clothing_items = addon_data.pz_clothing_item_references
        for folder in get_zomboid_asset_folders(context, 'clothingItems'):
            self.parse_folder(context, folder[0], clothing_items, folder[1])

        self.report({'INFO'}, "Parsed " + str(self.item_count) + " Clothing Item XMLs")

        return ({'FINISHED'})