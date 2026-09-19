# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import os
import bpy 
import xml.etree.ElementTree as ET

from bpy.types import Operator 
from pathlib import Path

from ...Utility.PZ_AssetMethods import get_file_all_sources

class PZ_Assets_ParseOutfitXMLs(Operator):
    bl_idname = "zomboid.parse_outfit_xmls"
    bl_label = "Parse Outfit XMLs"
    bl_description = "Parse all the outfit xmls to get the data needed to import outfits into Blender"

    outfit_count = 0

    def parse_xml(self, context, dir, outfits, origin, lookup):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        
        # Begin parsing the XML contents of the file
        tree = ET.parse(dir)
        root = tree.getroot()

        female_outfits = root.findall('m_FemaleOutfits')
        male_outfits = root.findall('m_MaleOutfits')

        for outfit in female_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = addon_data.pz_outfit_references.find(
                outfit.find('m_Name').text)
            if overwrite_index != -1:
                if addon_data.pz_outfit_references.get(outfit.find('m_Name').text).sex == 'FEMALE':
                    addon_data.pz_outfit_references.remove(overwrite_index)
                    female_outfits.remove(outfit)

            item = outfits.add()

            item.name = outfit.find('m_Name').text
            item.search_name = item.name + ' (Female)'
            item.sex = 'FEMALE'
            item.guid = outfit.find('m_Guid').text
            item.origin = origin

            if outfit.find('m_Top') is not None and outfit.find('m_Top').text != 'true':
                item.random_top = False
            else:
                item.random_top = True

            if outfit.find('m_Pants') is not None and outfit.find('m_Pants').text != 'true':
                item.random_pants = False
            else:
                item.random_pants = True

            clothing_items = outfit.findall('m_items')
            for clothing_item in clothing_items:
                new_clothing_item = item.outfit_items.add()

                # Get item probability
                if clothing_item.find('probability') is not None:
                    new_clothing_item.probability = float(
                        clothing_item.find('probability').text)

                # Get first item choice
                choice = new_clothing_item.choices.add()

                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    if choice.guid in lookup:
                        choice.name = lookup[choice.guid]

                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        if choice.guid in lookup:
                            choice.name = lookup[choice.guid]

            self.outfit_count = self.outfit_count + 1
        for outfit in male_outfits:
            # If there is an outfit item with the same name and sex as the outfit we are about to evaluate, remove it and overwrite it
            overwrite_index = addon_data.pz_outfit_references.find(
                outfit.find('m_Name').text)
            if overwrite_index != -1:
                if addon_data.pz_outfit_references.get(outfit.find('m_Name').text).sex == 'MALE':
                    addon_data.pz_outfit_references.remove(overwrite_index)
                    male_outfits.remove(outfit)

            item = outfits.add()

            item.name = outfit.find('m_Name').text
            item.search_name = item.name + ' (Male)'
            item.sex = 'MALE'
            item.guid = outfit.find('m_Guid').text
            item.origin = origin

            if outfit.find('m_Top') is not None and outfit.find('m_Top').text != 'true':
                item.random_top = False
            else:
                item.random_top = True

            if outfit.find('m_Pants') is not None and outfit.find('m_Pants').text != 'true':
                item.random_pants = False
            else:
                item.random_pants = True

            clothing_items = outfit.findall('m_items')
            for clothing_item in clothing_items:
                new_clothing_item = item.outfit_items.add()

                # Get item probability
                if clothing_item.find('probability') is not None:
                    new_clothing_item.probability = float(
                        clothing_item.find('probability').text)

                # Get first item choice
                choice = new_clothing_item.choices.add()

                m = clothing_item.find('itemGUID')
                if m is not None and m.text is not None:
                    choice.guid = clothing_item.find('itemGUID').text
                    if choice.guid in lookup:
                        choice.name = lookup[choice.guid]

                # Get all subitem choices
                subitems = clothing_item.findall('subItems')
                if len(subitems) > 0:
                    for subitem in subitems:
                        choice = new_clothing_item.choices.add()
                        choice.guid = subitem.find('itemGUID').text
                        if choice.guid in lookup:
                            choice.name = lookup[choice.guid]

            self.outfit_count = self.outfit_count + 1

    def execute(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        outfits = addon_data.pz_outfit_references

        addon_data.outfit_reference_active_index = 0
        outfits.clear()

        clothing_lookup = {
            clothing.guid : clothing.name for clothing in addon_data.pz_clothing_item_references
        }

        for file, mod_name in get_file_all_sources('media/clothing/clothing.xml'):
            self.parse_xml(context, os.fspath(file), outfits, mod_name, clothing_lookup)

        self.report({'INFO'}, "Parsed " + str(self.outfit_count) + " Outfits")
        return {'FINISHED'}