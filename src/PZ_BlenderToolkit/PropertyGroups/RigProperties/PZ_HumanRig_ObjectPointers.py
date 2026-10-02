# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import PropertyGroup, Object, Material, Image, Collection
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty, BoolVectorProperty, EnumProperty

from ...Utility.PZ_UpdateMethods import *

class PZ_HumanRig_ObjectPointers(PropertyGroup):

    ### COLLECTION POINTERS ###

    # The pointer property that points to the main rig collection
    rig_collection: PointerProperty(
        type=Collection
    )

    # The pointer property that points to the collection of models this rig uses
    model_collection: PointerProperty(
        type=Collection
    )

    ### OBJECT POINTERS ###

    # The pointer property that points to the actual rig object
    rig_object: PointerProperty(
        type=Object
    )

    # The pointer property that points to the Dummy01 object
    dummy01_object: PointerProperty(
        type=Object
    )

    translation_data_object: PointerProperty(
        type=Object
    )

    body_object: PointerProperty(
        type=Object
    )

    # The pointer that points to the hair object
    hair_object: PointerProperty(
        type=Object
    )

    # The pointer that points to the beard object
    beard_object: PointerProperty(
        type=Object
    )

    ### IMAGE POINTERS ###

    # The pointer that points to the body texture image
    body_texture_image: PointerProperty(
        type=Image
    )

    # The pointer that points to the mask data image
    mask_data_image: PointerProperty(
        type=Image
    )

    # The pointers that point to the relevant hair images
    hair_image: PointerProperty(
        type=Image
    )
    beard_image: PointerProperty(
        type=Image
    )

    ### MATERIAL POINTERS ###

    # The pointer that points to the body material
    body_material: PointerProperty(
        type=Material
    )

    # The pointers that point to the relevant hair materials
    hair_material: PointerProperty(
        type=Material
    )
    beard_material: PointerProperty(
        type=Material
    )
