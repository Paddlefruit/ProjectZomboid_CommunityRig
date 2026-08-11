# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Panel, UIList

# The UI List of rigs in the scene
class PZ_UL_RigList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.rig_object.pz_main_properties.rig_name)
        row.label(text=str(item.rig_object.pz_main_properties.rig_instance))

class PZ_HumanRig_SceneRigsPanel(Panel):
    bl_idname = "VIEW3D_PT_pz_human_rig_scene_rigs_panel"
    bl_label = "Scene Rigs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zomboid"

    def draw(self, context):
        addon_data = bpy.context.preferences.addons['PZ_BlenderToolkit'].preferences
        human_rigs = context.scene.pz_human_rigs
        scene_properties = context.scene.pz_scene_properties

        # Get the initial layout
        layout = self.layout

        # The list of rigs in the current scene
        layout.label(text='Rigs in Scene')
        layout.template_list("PZ_UL_RigList", "pz_human_rigs_list", context.scene, "pz_human_rigs", scene_properties, "human_rig_active_index")

        # A subbox detailing the properties of the selected rig in the list
        if scene_properties.human_rig_active_index != -1:
            current_rig = human_rigs[scene_properties.human_rig_active_index]
            main_properties = current_rig.rig_object.pz_main_properties
            object_pointers = current_rig.rig_object.pz_object_pointers

            layout.operator('zomboid.remove_rig')

            layout.label(text='Rig Properties')
            subbox = layout.box()
            subbox.prop(main_properties, 'rig_name')
            
            # Show more options if debug is enabled
            if addon_data.debug:

                subbox.prop(main_properties, 'rig_instance')
                
                # The subpanel containing the main directories
                subpanel, subpanel_area = subbox.panel("object_pointers_subpanel", default_closed=True)
                subpanel.label(text='Object Pointers')

                if subpanel_area:
                    subpanel_area.separator(factor=0.5)
                    subpanel_area.prop(object_pointers, 'rig_collection')
                    subpanel_area.prop(object_pointers, 'model_collection')
                    subpanel_area.separator(factor=0.5)
                    subpanel_area.prop(object_pointers, 'rig_object')
                    subpanel_area.prop(object_pointers, 'dummy01_object')
                    subpanel_area.prop(object_pointers, 'translation_data_object')
                    subpanel_area.prop(object_pointers, 'male_body_object')
                    subpanel_area.prop(object_pointers, 'female_body_object')
                    subpanel_area.prop(object_pointers, 'male_skeleton_object')
                    subpanel_area.prop(object_pointers, 'female_skeleton_object')
                    subpanel_area.prop(object_pointers, 'male_dress_object')
                    subpanel_area.prop(object_pointers, 'female_dress_object')
                    subpanel_area.prop(object_pointers, 'male_hair_object')
                    subpanel_area.prop(object_pointers, 'female_hair_object')
                    subpanel_area.prop(object_pointers, 'beard_object')
                    subpanel_area.separator(factor=0.5)
                    subpanel_area.prop(object_pointers, 'body_texture_image')
                    subpanel_area.prop(object_pointers, 'mask_data_image')
                    subpanel_area.prop(object_pointers, 'male_hair_image')
                    subpanel_area.prop(object_pointers, 'female_hair_image')
                    subpanel_area.prop(object_pointers, 'beard_image')
                    subpanel_area.separator(factor=0.5)
                    subpanel_area.prop(object_pointers, 'body_material')
                    subpanel_area.prop(object_pointers, 'male_hair_material')
                    subpanel_area.prop(object_pointers, 'female_hair_material')
                    subpanel_area.prop(object_pointers, 'beard_material')

            layout.separator(type='LINE')

        # Subbox with all details pertaining to rig creation
        layout.label(text='Creation Settings')
        subbox = layout.box()
        subbox.prop(scene_properties, 'rig_parent_collection')
        subbox.prop(scene_properties, 'rig_creation_location')
        if scene_properties.rig_creation_location == 'CURSOR':
            subbox.prop(scene_properties, 'use_3d_cursor_rotation')
        if scene_properties.rig_creation_location == 'OBJECT':
            subbox.prop(scene_properties, 'rig_creation_location_object')
        subbox.prop_search(scene_properties, 'initial_outfit', addon_data, 'pz_outfit_references', item_search_property='search_name')

        op = subbox.operator('zomboid.create_rig')
        op.rig_creation_location = scene_properties.rig_creation_location
        op.use_3d_cursor_rotation = scene_properties.use_3d_cursor_rotation
        if scene_properties.rig_creation_location_object:
            op.rig_creation_location_object = scene_properties.rig_creation_location_object.name
        if scene_properties.initial_outfit:
            op.initial_outfit = scene_properties.initial_outfit