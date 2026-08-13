# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Scene, Object, WindowManager
from bpy.props import CollectionProperty, PointerProperty
from bpy.utils import previews
from pathlib import Path

from . import auto_load

from .PropertyGroups.General.PZ_ClothingItem import PZ_EquippedClothingItem
from .PropertyGroups.General.PZ_Injuries import PZ_ZombieInjury
from .PropertyGroups.General.PZ_BodyLocation import PZ_BodyLocation
from .PropertyGroups.General.PZ_HumanRig import PZ_HumanRig
from .PropertyGroups.PZ_SceneProperties import *

from .PropertyGroups.RigProperties.PZ_HumanRig_ObjectPointers import PZ_HumanRig_ObjectPointers
from .PropertyGroups.RigProperties.PZ_HumanRig_MainProperties import PZ_HumanRigMainProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_AnimationProperties import PZ_HumanRigAnimationProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_ControlProperties import PZ_HumanRigControlProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_ExportProperties import PZ_HumanRigExportProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_ModelProperties import PZ_HumanRigModelProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_InjuryProperties import PZ_HumanRigInjuryProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_ShadingProperties import PZ_HumanRigShadingProperties
from .PropertyGroups.RigProperties.PZ_HumanRig_RandomProperties import PZ_HumanRigRandomProperties

bl_info = {
    "name": "Project Zomboid Blender Toolkit",
    "description": "A Blender Add-On relating to several aspects of creating Project Zomboid content in Blender",
    "author": "Paddlefruit",
    "version": (1, 0, 0),
    "blender": (5, 2, 0)
}

def register():
    auto_load.init()
    auto_load.register()

    # Store our scene props on the Scene
    Scene.pz_scene_properties = PointerProperty(
        type=PZ_SceneProperties,
        name="PZ Human Rig Global Properties"
    )

    # The collection of human rig objects in the scene
    Scene.pz_human_rigs = CollectionProperty(
        type=PZ_HumanRig
    )

    #################################################

    # Filter method so we only get Zomboid Human rigs
    def poll_bip01(self, object):
        return object.type == 'ARMATURE' and object.name == 'Bip01'

    # Store the property group of object pointers on all human rig objects
    Object.pz_object_pointers = PointerProperty(
        type=PZ_HumanRig_ObjectPointers,
        poll=poll_bip01
    )

    # Store the property group of main properties on all human rig objects
    Object.pz_main_properties = PointerProperty(
        type=PZ_HumanRigMainProperties,
        poll=poll_bip01
    )

    # Store the property group of model properties on all human rig objects
    Object.pz_model_properties = PointerProperty(
        type=PZ_HumanRigModelProperties,
        poll=poll_bip01
    )

    # Store the property group of model properties on all human rig objects
    Object.pz_random_properties = PointerProperty(
        type=PZ_HumanRigRandomProperties,
        poll=poll_bip01
    )

    # Store the property group of injury properties on all human rig objects
    Object.pz_injury_properties = PointerProperty(
        type=PZ_HumanRigInjuryProperties,
        poll=poll_bip01
    )

    # Store the property group of shading properties on all human rig objects
    Object.pz_shading_properties = PointerProperty(
        type=PZ_HumanRigShadingProperties,
        poll=poll_bip01
    )

    # Store the property group of animation properties on all human rig objects
    Object.pz_animation_properties = PointerProperty(
        type=PZ_HumanRigAnimationProperties,
        poll=poll_bip01
    )

    # Store the property group of control properties on all human rig objects
    Object.pz_control_properties = PointerProperty(
        type=PZ_HumanRigControlProperties,
        poll=poll_bip01
    )

    # Store the property group of export properties on all human rig objects
    Object.pz_export_properties = PointerProperty(
        type=PZ_HumanRigExportProperties,
        poll=poll_bip01
    )

    #################################################

    # The collection of equipped clothing item objects on the rig
    Object.pz_equipped_clothing_items = CollectionProperty(
        type=PZ_EquippedClothingItem
    )

    # The collection of current zombie injuries on the rig
    Object.pz_zombie_injuries = CollectionProperty(
        type=PZ_ZombieInjury
    )

    # Object.pz_attachments = CollectionProperty(
    #     type=PZ_Attachment
    # )

    # The collection of used body locations on the rig
    Object.pz_used_body_locations = CollectionProperty(
        type=PZ_BodyLocation
    )

    #################################################

    # Add our custom icons to Blender
    custom_icons = previews.new()

    # Get the icon paths
    random_icon_path = Path(__file__).parent / 'Assets' / 'Icons' / 'ICON-Random.svg'

    # Load the icons
    custom_icons.load('pz_random_icon', str(random_icon_path), 'IMAGE')

    # Store the icons in the WindowManager
    WindowManager.pz_icons = custom_icons

def unregister():
    auto_load.unregister()

    del Object.pz_object_pointers
    del Object.pz_main_properties
    del Object.pz_model_properties
    del Object.pz_injury_properties
    del Object.pz_shading_properties
    del Object.pz_animation_properties
    del Object.pz_control_properties
    del Object.pz_export_properties

    del Object.pz_equipped_clothing_items
    del Object.pz_zombie_injuries
    del Object.pz_used_body_locations

    del Scene.pz_human_rigs

    # Remove our custom icons from the WindowManager
    icons = getattr(bpy.types.WindowManager, 'pz_icons', None)
    if icons:
        previews.remove(icons)
        del WindowManager.pz_icons
