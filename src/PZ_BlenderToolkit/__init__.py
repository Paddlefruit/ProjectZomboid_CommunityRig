# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Scene, Object
from bpy.props import CollectionProperty, PointerProperty

from . import auto_load
from .PropertyGroups.General.PZ_ClothingItem import PZ_EquippedClothingItem
from .PropertyGroups.General.PZ_Injuries import PZ_ZombieInjury
from .PropertyGroups.General.PZ_BodyLocation import PZ_BodyLocation
from .PropertyGroups.General.PZ_HumanRig import PZ_HumanRig
from .PropertyGroups.PZ_SceneProperties import *
from .PropertyGroups.RigProperties.PZ_HumanRig_Properties import *

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
    Scene.pz_human_global_props = PointerProperty(
        type=PZ_SceneProperties,
        name="PZ Human Rig Global Properties"
    )

    Scene.pz_human_rigs = CollectionProperty(type=PZ_HumanRig)

    # -------------------------------------------

    # Filter method so we only get Zomboid Human rigs
    def poll_bip01(self, object):
        return object.type == 'ARMATURE' and object.name == 'Bip01'

    # Store our rig properties on the Zomboid rig object
    Object.pz_human_props = PointerProperty(
        type=PZ_HumanRigProperties,
        name="PZ Human Rig Properties",
        poll=poll_bip01
    )

    # # Store our property groups on the Rig objects
    # Object.pz_model_props = PointerProperty(
    #     type=PZ_HumanRigModelProperties,
    #     name="PZ Human Rig Properties",
    #     poll=poll_bip01
    # )

    

    # Object.pz_body_clothing_textures = CollectionProperty(
    #     type=PZ_BodyTextureSlot
    # )
    # Object.pz_clothing_models = CollectionProperty(
    #     type=PZ_ClothingMeshSlot
    # )
    # Object.pz_accessory_models = CollectionProperty(
    #     type=PZ_PropMeshSlot
    # )
    Object.pz_equipped_clothing_items = CollectionProperty(
        type=PZ_EquippedClothingItem
    )
    Object.pz_zombie_injuries = CollectionProperty(
        type=PZ_ZombieInjury
    )
    # Object.pz_attachments = CollectionProperty(
    #     type=PZ_Attachment
    # )
    Object.pz_used_body_locations = CollectionProperty(
        type=PZ_BodyLocation
    )

def unregister():
    auto_load.unregister()

    # Remove properties and collections from the rig objects
    del Object.pz_human_props

    del Object.pz_equipped_clothing_items
    del Object.pz_zombie_injuries

    del Object.pz_used_body_locations

    # -------------------------------------------

    # Remove properties and collections from the scene
    del Scene.pz_human_rigs
 