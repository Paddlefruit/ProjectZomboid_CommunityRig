# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import os
import bpy 
import xml.etree.ElementTree as ET

from pathlib import Path
from bpy.types import Operator 

from ...Utility.PZ_AssetMethods import get_zomboid_asset, get_file_all_sources, parse_path

class PZ_Assets_ParseHairStyleXMLs(Operator):
    bl_idname = "zomboid.parse_hair_style_xmls"
    bl_label = "Parse Hair Style XMLs"
    bl_description = "Parse all the hair style xmls to get the data needed to import hair models into Blender"

    hair_count = 0
    beard_count = 0

    def parse_hair_xml(self, context, dir, hair_styles, male_styles, female_styles, origin):

        tree = ET.parse(dir)
        root = tree.getroot()

        male_hair_styles = root.findall('male')
        female_hair_styles = root.findall('female')

        for hair in male_hair_styles:
            m = hair.find('name')
            if m is not None and m.text is not None:
                overwrite_index = hair_styles.find(m.text)
                if overwrite_index != -1:
                    if hair_styles.get(m.text).sex == 'MALE':
                        hair_styles.remove(overwrite_index)
                        male_styles.remove(male_styles.find(m.text))

            item = hair_styles.add()

            item.name = hair.find('name').text
            item.sex = 'MALE'

            m = hair.find('level')
            if m is not None and m.text is not None:
                item.level = int(hair.find('level').text)
            else:
                item.level = 0

            texture = hair.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, Path('media/textures') / parse_path(texture.text), allowed_types=[".png"])
                assert x[0] is not None
                item.texture_path = os.fspath(x[0])

            model = hair.find('model')
            if model is not None and model.text:
                x = get_zomboid_asset(context, Path('media/models_X/') / parse_path(model.text), allowed_types=[".fbx", ".x", ".glb"])
                assert x[0] is not None
                item.model_path = os.fspath(x[0])
                item.model_type = x[1]
            else:
                item.model_path = 'None'
                item.model_type = 'N/A'

            for hat_group in hair.findall('alternate'):
                x = -1
                match hat_group.get('category'):
                    case 'default':
                        x = 0
                    case 'Group01':
                        x = 1
                    case 'Group02':
                        x = 2
                    case 'Group03':
                        x = 3
                    case 'Group04':
                        x = 4
                    case 'Group05':
                        x = 5
                    case 'Group06':
                        x = 6
                    case 'Group07':
                        x = 7
                if x != -1:
                    group = item.hat_styles.add()
                    group.hat_group = x
                    group.style_name = hat_group.get('style')

            no_choose = hair.find('noChoose')

            if no_choose is not None and no_choose.text == 'true':
                pass
            else:
                new = male_styles.add()
                new.name = item.name

            item.origin = origin

            self.hair_count = self.hair_count + 1

        for hair in female_hair_styles:
            m = hair.find('name')
            if m is not None and m.text is not None:
                overwrite_index = hair_styles.find(m.text)
                if overwrite_index != -1:
                    if hair_styles.get(m.text).sex == 'FEMALE':
                        hair_styles.remove(overwrite_index)
                        female_styles.remove(female_styles.find(m.text))

            item = hair_styles.add()

            item.name = hair.find('name').text
            item.sex = 'FEMALE'

            m = hair.find('level')
            if m is not None and m.text is not None:
                item.level = int(hair.find('level').text)
            else:
                item.level = 0

            texture = hair.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, Path('media/textures') / parse_path(texture.text), allowed_types=[".png"])
                assert x[0] is not None
                item.texture_path = os.fspath(x[0])

            model = hair.find('model')
            if model is not None and model.text:
                x = get_zomboid_asset(context, Path('media/models_X') / parse_path(model.text), allowed_types=[".x", ".fbx", ".glb"])
                assert x[0] is not None
                item.model_path = os.fspath(x[0])
                item.model_type = x[1]
            else:
                item.model_path = 'None'
                item.model_type = 'N/A'

            for hat_group in hair.findall('alternate'):
                x = -1
                match hat_group.get('category'):
                    case 'default':
                        x = 0
                    case 'Group01':
                        x = 1
                    case 'Group02':
                        x = 2
                    case 'Group03':
                        x = 3
                    case 'Group04':
                        x = 4
                    case 'Group05':
                        x = 5
                    case 'Group06':
                        x = 6
                    case 'Group07':
                        x = 7
                if x != -1:
                    group = item.hat_styles.add()
                    group.hat_group = x
                    group.style_name = hat_group.get('style')

            no_choose = hair.find('noChoose')

            if no_choose is not None and no_choose.text == 'true':
                pass
            else:
                new = female_styles.add()
                new.name = item.name

            item.origin = origin

            self.hair_count = self.hair_count + 1

    def parse_beard_xml(self, context, dir, beard_styles, origin):

        tree = ET.parse(dir)
        root = tree.getroot()

        new_beard_styles = root.findall('style')

        for beard in new_beard_styles:
            item = beard_styles.add()

            item.name = beard.find('name').text

            m = beard.find('level')
            if m is not None and m.text is not None:
                item.level = int(beard.find('level').text)
            else:
                item.level = 0

            texture = beard.find('texture')
            if texture is not None:
                x = get_zomboid_asset(context, Path('media/textures') / parse_path(texture.text), allowed_types=[".png"])
                assert x[0] is not None
                item.texture_path = os.fspath(x[0])

            model = beard.find('model')
            if model is not None and model.text:
                x = get_zomboid_asset(context, Path('media/models_X') / parse_path(model.text), allowed_types=[".x", ".fbx", ".glb"])
                assert x[0] is not None
                item.model_path = os.fspath(x[0])
                item.model_type = x[1]
            else:
                item.model_path = 'None'
                item.model_type = 'N/A'

            self.beard_count = self.beard_count + 1

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        hair_styles = addon_data.pz_hair_style_references
        male_styles = addon_data.pz_male_hair_style_references
        female_styles = addon_data.pz_female_hair_style_references
        beard_styles = addon_data.pz_beard_style_references

        addon_data.hair_style_reference_active_index = 0
        hair_styles.clear()
        male_styles.clear()
        female_styles.clear()
        beard_styles.clear()

        # Add a 'clean' beard option
        item = beard_styles.add()
        item.name = 'None'
        item.model_path = 'None'
        item.level = 0

        for file, mod_name in get_file_all_sources("media/hairStyles/hairStyles.xml"):
            self.parse_hair_xml(context, os.fspath(file), hair_styles, male_styles, female_styles, mod_name)
        
        for file, mod_name in get_file_all_sources("media/hairStyles/beardStyles.xml"):
            self.parse_beard_xml(context, os.fspath(file), beard_styles, mod_name)

        self.report({'INFO'}, "Parsed " + str(self.hair_count) +
                    " Hair Styles & " + str(self.beard_count) + " Beard Styles")
        return ({'FINISHED'})