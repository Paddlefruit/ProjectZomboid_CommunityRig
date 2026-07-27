# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
import xml.etree.ElementTree as ET

from bpy.types import Operator 

from ...Utility.PZ_AssetMethods import get_zomboid_asset, get_zomboid_asset_folders

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
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'

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
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            if hair.find('model').text:
                item.model_path = hair.find('model').text
            else:
                item.model_path = 'None'

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
                x = get_zomboid_asset(context, 'textures/' + texture.text)
                item.texture_path = str(x[0])

            item.model_path = beard.find('model').text

            self.beard_count = self.beard_count + 1

    def execute(self, context):
        addon_prefs = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        hair_styles = addon_prefs.pz_human_hair_style_slots
        male_styles = addon_prefs.pz_human_male_hair_styles
        female_styles = addon_prefs.pz_human_female_hair_styles
        beard_styles = addon_prefs.pz_human_beard_styles

        addon_prefs.hair_style_slot_active_index = 0
        hair_styles.clear()
        male_styles.clear()
        female_styles.clear()
        beard_styles.clear()

        # Add a 'clean' beard option
        item = beard_styles.add()
        item.name = 'None'
        item.model_path = 'None'
        item.level = 0

        for folder, mod_name in get_zomboid_asset_folders(context, 'hairStyles'):
            if (folder / 'hairStyles.xml').is_file():
                self.parse_hair_xml(context, str(folder / 'hairStyles.xml'), hair_styles, male_styles, female_styles, mod_name)
            if (folder / 'beardStyles.xml').is_file():
                self.parse_beard_xml(context, str(folder / 'beardStyles.xml'), beard_styles, mod_name)

        self.report({'INFO'}, "Parsed " + str(self.hair_count) +
                    " Hair Styles & " + str(self.beard_count) + " Beard Styles")
        return ({'FINISHED'})