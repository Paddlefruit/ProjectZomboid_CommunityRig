# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy # type: ignore
from bpy.types import Scene, Object
from bpy.props import CollectionProperty, PointerProperty

from . import auto_load
from .PropertyGroups.PZ_HumanRig_Objects import *
from .PropertyGroups.PZ_Scene_Properties import *
from .PropertyGroups.PZ_HumanRig_Properties import PZ_HumanRigProperties

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

    Scene.pz_human_global_props = PointerProperty(
        type=PZ_Scene_Properties,
        name="PZ Human Rig Global Properties"
    )

    Scene.pz_human_rigs = CollectionProperty(type=PZ_HumanRigObject)

    # -------------------------------------------

    # Filter method so we only get Zomboid Human rigs
    def poll_bip01(self, object):
        return object.type == 'ARMATURE' and object.name == 'Bip01'

    # Store our rig properties on the Zomboid rig object
    Object.pz_human_props = PointerProperty(
        type=PZ_HumanRigProperties,
        name="PZ Human Rig Properties",
        poll=poll_bip01,
        override={"LIBRARY_OVERRIDABLE"}
    )

    # Store the rig collections on the rig object
    Object.pz_human_body_texture_slots = CollectionProperty(
        type=PZ_BodyTextureSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_clothing_mesh_slots = CollectionProperty(
        type=PZ_ClothingMeshSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_prop_mesh_slots = CollectionProperty(
        type=PZ_PropMeshSlot,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )
    Object.pz_human_zombie_injuries = CollectionProperty(
        type=PZ_ZombieInjury,
        override={"LIBRARY_OVERRIDABLE", "USE_INSERTION"}
    )

  #  initialize_rigs()

def unregister():
    auto_load.unregister()

    # Remove properties and collections from the rig objects
    del Object.pz_human_props
    del Object.pz_human_body_texture_slots
    del Object.pz_human_clothing_mesh_slots
    del Object.pz_human_prop_mesh_slots
    del Object.pz_human_zombie_injuries

    # -------------------------------------------

    # Remove properties and collections from the scene
    del Scene.pz_human_rigs
 