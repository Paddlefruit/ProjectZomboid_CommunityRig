# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import re
from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatProperty, IntProperty, FloatVectorProperty, BoolVectorProperty

from ...Utility.PZ_UpdateMethods import *
from ...Utility.PZ_FilterMethods import filter_zombie_injuries

'''
This property group contains general properties that the
rig uses
'''

class PZ_HumanRigMainProperties(PropertyGroup):

    # Automatically update rig instance
    def update_rig_instance(self, context):
        object_pointers = context.active_object.pz_object_pointers

        instance_str = context.active_object.pz_main_properties.get_instance_str(context)

        old_instance_pattern = r' \([0-9]+\)| \(\[INSTANCE\]\)'
        
        # Check if this instance number is already used. If so, increment by one and return.
        for rig in context.scene.pz_human_rigs:
            if rig.rig_object != context.active_object:
                if self.rig_instance == rig.rig_object.pz_main_properties.rig_instance:
                    self.rig_instance += 1
                    return

        # Recursively go through the rig collection and change all '({old rig instance})'
        # to '({new rig instance})'

        object_pointers.rig_collection.name = re.sub(old_instance_pattern, instance_str, object_pointers.rig_collection.name)
        for obj in object_pointers.rig_collection.objects:
            obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
            if obj.data and isinstance(obj.data, bpy.types.ID):
                obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
        for col in object_pointers.rig_collection.children_recursive:
            col.name = re.sub(old_instance_pattern, instance_str, col.name)
            for obj in col.objects:
                obj.name = re.sub(old_instance_pattern, instance_str, obj.name)
                if obj.data and isinstance(obj.data, bpy.types.ID):
                    obj.data.name = re.sub(old_instance_pattern, instance_str, obj.data.name)
                if obj.active_material:
                    obj.active_material.name = re.sub(old_instance_pattern, instance_str, obj.active_material.name)
        
        if object_pointers.mask_data_image:
            object_pointers.mask_data_image.name = re.sub(old_instance_pattern, instance_str, object_pointers.mask_data_image.name)
        if object_pointers.body_texture_image:
            object_pointers.body_texture_image.name = re.sub(old_instance_pattern, instance_str, object_pointers.body_texture_image.name)

    # The unique ID that this rig uses
    rig_instance: IntProperty(
        default=0,
        min=0,
        update=update_rig_instance
    )

    # The string that uses this ID across all areas of the rig
    def get_instance_str(self, context):
        main_properties = context.active_object.pz_main_properties
        return ' (' + str(main_properties.rig_instance) + ')'

    rig_name : StringProperty(
        name='Name',
        description='The identifier used for this rig instance',
        default='Human'
    )