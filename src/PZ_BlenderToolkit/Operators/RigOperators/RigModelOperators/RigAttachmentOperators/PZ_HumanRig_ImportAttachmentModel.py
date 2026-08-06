# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import math

from bpy.types import Operator

from .....Utility.PZ_MaterialMethods import create_model_material
from .....Utility.PZ_AssetMethods import directx_import_available

class PZ_HumanRig_ImportAttachmentModel(Operator):
    bl_idname = "zomboid.import_attachment_model"
    bl_label = "Import Attachment Model"
    bl_description = "Imports the attachment model"

    def execute(self, context):
        
        # Get all data
        addon_prefs = context.preferences.addons['PZ_BlenderToolkit'].preferences
        p = context.active_object.pz_human_props
        current_attachment = context.active_object.pz_attachments[p.attachment_active_index]
        instance_str = ' (' + str(p.rig_instance) + ')'

        with bpy.context.temp_override():

            # Get a list of all objects before the import
            objs_before = set(bpy.context.scene.objects)

            # Run the import method for the respective model type
            match current_attachment.model_type:
                case '.x':
                    if not directx_import_available():
                        self.report(
                            {"ERROR"}, "The .x importer is not enabled or installed")
                        return ({'CANCELLED'})

                    bpy.ops.import_scene.directx_x(
                        filepath=current_attachment.model_path,
                        import_textures=False,
                        import_materials=False,
                        import_armature=False,
                        import_animation=False,
                        use_import_collection=False
                    )

                case '.fbx':
                    bpy.ops.import_scene.fbx(
                        filepath=current_attachment.model_path,
                        global_scale=100.0
                    )
                case '.glb':
                    bpy.ops.import_scene.gltf(
                        filepath=current_attachment.model_path,
                        disable_bone_shape=True
                    )

            # Get a list of all added objects to the scene
            objs_after = set(bpy.context.scene.objects)
            imported_objects = list(objs_after - objs_before)

            # Loop through all added objects, delete unneeded ones, and isolate the model object
            model_obj = None
            for obj in imported_objects:
                match obj.type:
                    case 'ARMATURE':
                        bpy.data.objects.remove(obj, do_unlink=True)
                    case 'EMPTY':
                        bpy.data.objects.remove(obj, do_unlink=True)
                    case 'MESH':
                        model_obj = obj

            if not model_obj:
                return ({'CANCELLED'})

            # Check if there is an object that uses the name that this object should have, and remove it if so
            obj_name = 'OBJ-AttachmentMesh' + str(p.attachment_active_index) + instance_str

            old_obj = bpy.data.objects.get(obj_name)
            if old_obj:
                bpy.data.objects.remove(old_obj, do_unlink=True)

            # Rename the new object
            model_obj.name = obj_name

            # Unlink this object from any collections it may have been linked to in the import process
            for collection in model_obj.users_collection[:]:
                collection.objects.unlink(model_obj)

            # Get the rig's attachment collection, and add the model object to it
            attachment_collection = bpy.data.collections.get('COL-PZ_Human_Attachments' + instance_str)
            attachment_collection.objects.link(model_obj)

            # Create the attachment material, and assign it to this attachment data
            current_attachment.material_name = create_model_material(context, current_attachment.texture_path, 'ATTACHMENT').name

            # Apply the material that was created to the model
            model_obj.active_material = bpy.data.materials.get(current_attachment.material_name)

            # Apply additional transform adjustments based on the model type
            match current_attachment.model_type:
                case '.x':
                    # obj.rotation_euler[0] += math.pi
                    # obj.scale *= 100
                    pass
                case '.fbx':
                    obj.data.materials.clear()
                    obj.scale[0] = 1.0
                    obj.scale[1] = 1.0
                    obj.scale[2] = 1.0
                case '.glb':
                    obj.scale[0] = 1.0
                    obj.scale[1] = 1.0
                    obj.scale[2] = 1.0

            # Assign this object to the attachment data on the rig
            current_attachment.object_name = model_obj.name

        return ({'FINISHED'})


