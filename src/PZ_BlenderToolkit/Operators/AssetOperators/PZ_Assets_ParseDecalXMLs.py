# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy 
import os
import sys
import xml.etree.ElementTree as ET

from bpy.types import Operator 
from pathlib import Path

class PZ_Assets_ParseDecalXMLs(Operator):
    bl_idname = "zomboid.parse_decal_xmls"
    bl_label = "Parse Decal XMLs"
    bl_description = "Parse all the decal xmls to get the data needed to import shirt decals into Blender"

    def parse_decals(self, context):
        g = context.scene.pz_scene_properties

        g.decal_reference_active_index = 0

        decals = context.scene.pz_human_decals
        decals.clear()

        xmls_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xmls_dir = g.pz_directory + '\\media\\clothing\\clothingDecals'
        elif sys.platform == 'linux':
            xmls_dir = g.pz_directory + '/projectzomboid/media/clothing/clothingDecals'

        xmls_dir = Path(xmls_dir)

        item_count = 0
        for file in xmls_dir.glob("*.xml"):
            if file.is_file():
                decal = decals.add()

                # Parse the file name
                decal.name = os.path.splitext(file.name)[0]

                # Begin parsing the XML contents of the file
                tree = ET.parse(file)
                root = tree.getroot()

                decal.texture_path = root.find('texture').text
                decal.x = int(root.find('x').text)
                decal.y = int(root.find('y').text)
                decal.width = int(root.find('width').text)
                decal.height = int(root.find('height').text)

                item_count += 1

        return ({'FINISHED'})

    def parse_decal_groups(self, context):
        g = context.scene.pz_scene_properties
        current_groups = context.scene.pz_human_decal_groups

        g.decal_group_slot_active_index = 0
        current_groups.clear()

        xmls_dir = ''

        # Construct the filepath to the 'textures' folder in the PZ directory
        # Linux has an additional 'projectzomboid' subfolder
        if sys.platform == 'win32':
            xml_dir = g.pz_directory + 'media\\clothing\\clothingDecals.xml'
        elif sys.platform == 'linux':
            xml_dir = g.pz_directory + 'projectzomboid/media/clothing/clothingDecals.xml'

        decal_count = 0

        # Begin parsing the XML contents of the hair file
        tree = ET.parse(xml_dir)
        root = tree.getroot()

        decal_groups = root.findall('group')
        for decal_group in decal_groups:
            new_group = context.scene.pz_human_decal_groups.add()
            new_group.name = decal_group.find('name').text

            decals = decal_group.findall('decal')
            for decal in decals:
                new_decal = new_group.decals.add()
                new_decal.name = decal.text

        return ({'FINISHED'})

    def execute(self, context):
        self.parse_decals(context)
        self.parse_decal_groups(context)

        return ({'FINISHED'})