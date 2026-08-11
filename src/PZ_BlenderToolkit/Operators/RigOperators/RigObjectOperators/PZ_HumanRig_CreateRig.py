# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy

from pathlib import Path
from bpy.types import Operator, Object
from bpy.props import StringProperty, BoolProperty
from ....Utility.PZ_MaterialMethods import resolve_image_users

class PZ_HumanRig_CreateRig(Operator):
    bl_idname = "zomboid.create_rig"
    bl_label = "Create Rig"
    bl_description = "Creates a new instance of the rig and adds it to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    rig_creation_location: StringProperty()
    rig_creation_location_object: StringProperty()
    use_3d_cursor_rotation: BoolProperty()
    initial_outfit: StringProperty()

    def execute(self, context):
        scene_props = context.scene.pz_scene_properties
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences

        rigs = context.scene.pz_human_rigs

        # Get the path to the PZ_HumanRig Blend file
        rig_blend_path = Path(__file__).parent.parent.parent.parent / 'Assets' / 'Blend' / 'CH-PZ_HumanRig.blend'
        rig_col_name = 'CH-PZ_Human ([INSTANCE])'

        # Capture all images in data before
        images_before = set(bpy.data.images)

        # Append the rig collection to this file
        with bpy.data.libraries.load(str(rig_blend_path)) as (data_from, data_to):
            if rig_col_name in data_from.collections:
                data_to.collections.append(rig_col_name)

        appended_collection = bpy.data.collections.get(rig_col_name)
        if appended_collection:
            if scene_props.rig_parent_collection:
                scene_props.rig_parent_collection.children.link(appended_collection)
            else:
                bpy.context.scene.collection.children.link(appended_collection)

        # Check if the import duplicated textures, and remove those duplicates if so
        images_after = set(bpy.data.images)
        images_to_check = images_after - images_before

        for img in images_to_check:
            if '.001' in img.name:
                resolve_image_users(img.name)

        # Add this rig to the list of rigs in the scene
        new_rig = rigs.add()
        new_rig.rig_object = bpy.data.objects.get('OBJ-HumanRig ([INSTANCE])')
        bpy.context.view_layer.objects.active = new_rig.rig_object

        # Get the object pointers property group and hook all of the available data up
        object_pointers = new_rig.rig_object.pz_object_pointers

        object_pointers.rig_object = new_rig.rig_object
        object_pointers.dummy01_object = bpy.data.objects.get('OBJ-Dummy01 ([INSTANCE])')
        object_pointers.translation_data_object = bpy.data.objects.get('OBJ-TranslationData ([INSTANCE])')
        object_pointers.male_body_object = bpy.data.objects.get('OBJ-MaleBody ([INSTANCE])')
        object_pointers.female_body_object = bpy.data.objects.get('OBJ-FemaleBody ([INSTANCE])')
        object_pointers.male_skeleton_object = bpy.data.objects.get('OBJ-MaleSkeleton ([INSTANCE])')
        object_pointers.female_skeleton_object = bpy.data.objects.get('OBJ-FemaleSkeleton ([INSTANCE])')
        object_pointers.male_dress_object = bpy.data.objects.get('OBJ-MaleDress ([INSTANCE])')
        object_pointers.female_dress_object = bpy.data.objects.get('OBJ-FemaleDress ([INSTANCE])')

        object_pointers.body_material = bpy.data.materials.get('MAT-HumanBody ([INSTANCE])')

        object_pointers.body_texture_image = bpy.data.images.get('TEX-BodyTexture ([INSTANCE])')
        object_pointers.mask_data_image = bpy.data.images.get('MASK-MaskData ([INSTANCE])')

        object_pointers.rig_collection = bpy.data.collections.get('CH-PZ_Human ([INSTANCE])')
        object_pointers.model_collection = bpy.data.collections.get('COL-PZ_Human_Models ([INSTANCE])')

        # Get the main property group on the rig and modify the rig instance
        main_properties = new_rig.rig_object.pz_main_properties
        main_properties.rig_instance = 1

        match self.rig_creation_location:
            case 'CURSOR':
                cursor = context.scene.cursor
                object_pointers.rig_object.location = cursor.location * 100
                if self.use_3d_cursor_rotation:
                    object_pointers.rig_object.rotation_euler = cursor.rotation_euler
            case 'OBJECT':
                if self.rig_creation_location_object:
                    loc_object = bpy.data.objects.get(self.rig_creation_location_object)
                    if loc_object:
                        if loc_object.location:
                            object_pointers.rig_object.location = loc_object.location * 100
                        if loc_object.rotation_euler:
                            object_pointers.rig_object.rotation_euler = loc_object.rotation_euler

        # Deselect all objects, and select the newly created rig
        for obj in context.selected_objects:
            obj.select_set(False)
        object_pointers.rig_object.select_set(True)
        context.view_layer.objects.active = object_pointers.rig_object

        # Apply an initial outfit if indicated
        if addon_data.references_obtained:
            if self.initial_outfit:
                object_pointers.rig_object.pz_model_properties.selected_outfit = self.initial_outfit
                bpy.ops.zomboid.apply_outfit()

        return ({'FINISHED'})