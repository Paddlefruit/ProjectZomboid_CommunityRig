# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty
from ......Utility.PZ_MaterialMethods import remove_model_material

class PZ_RemoveClothingMesh(Operator):
    bl_idname = "zomboid.remove_clothing_model"
    bl_label = "Remove Clothing Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    stop_texture_updates: BoolProperty(
        default=True
    )

    # -------------------------------------------------------------#
    # Remove Clothing Material

    def remove_clothing_material(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_model_active_index

        old_mat = bpy.data.materials.get(
            'MAT-ClothingMaterial' + str(index) + instance_str)
        if old_mat:

            drivers = old_mat.node_tree.animation_data.drivers
            for i in range(len(drivers) - 1, -1, -1):
                drivers.remove(drivers[i])

            bpy.data.materials.remove(old_mat, do_unlink=True)

        for i in range(index, len(m_list)):
            index_mat = bpy.data.materials.get(
                'MAT-ClothingMaterial' + str(i) + instance_str)
            if index_mat:
                index_mat.name = 'MAT-ClothingMaterial' + \
                    str(i - 1) + instance_str

                for fcurve in index_mat.node_tree.animation_data.drivers:
                    driver = fcurve.driver
                    target = driver.variables[0].targets[0]

                    old_path = "pz_clothing_models[" + str(i) + "]"
                    new_path = "pz_clothing_models[" + str(i - 1) + "]"

                    target.data_path = target.data_path.replace(
                        old_path, new_path)

        return ({'FINISHED'})

    # -------------------------------------------------------------#
    # Remove Male Clothing Object

    def remove_male_clothing_mesh(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_model_active_index

        old_obj = bpy.data.objects.get(
            'OBJ-MaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(m_list)):
            index_obj = bpy.data.objects.get(
                'OBJ-MaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-MaleClothingMesh' + str(i - 1) + instance_str

        return ({'FINISHED'})

    # -------------------------------------------------------------#
    # Remove Female Clothing Object

    def remove_female_clothing_mesh(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models

        instance_str = ' (' + str(p.rig_instance) + ')'

        index = p.clothing_model_active_index

        old_obj = bpy.data.objects.get(
            'OBJ-FemaleClothingMesh' + str(index) + instance_str)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        for i in range(index, len(m_list)):
            index_obj = bpy.data.objects.get(
                'OBJ-FemaleClothingMesh' + str(i) + instance_str)
            if index_obj:
                index_obj.name = 'OBJ-FemaleClothingMesh' + str(i - 1) + instance_str

        return ({'FINISHED'})

    def check_masks(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models
        m = m_list[p.clothing_model_active_index]

        if self.stop_texture_updates:
            p.stop_texture_updates = True

        for i in range(len(p.visibility_mask_array)):
            test = False
            for j in range(len(m_list)):
                if m_list[j].name != m.name and m_list[j].visibility_mask_array[i] == True:
                    test = True
                    break
            p.visibility_mask_array[i] = test
            p.visibility_mask_array[i] = p.visibility_mask_array[i]

        if self.stop_texture_updates:
            p.stop_texture_updates = False
            bpy.ops.zomboid.create_visibility_mask()

        return ({'FINISHED'})

    def execute(self, context):
        p = context.active_object.pz_human_props
        m_list = context.active_object.pz_clothing_models

        remove_model_material(context, 'CLOTHING')
        self.remove_male_clothing_mesh(context)
        self.remove_female_clothing_mesh(context)

        self.check_masks(context)

        bpy.ops.zomboid.check_hat_category(count_self=False)

        m_list.remove(p.clothing_model_active_index)
        p.clothing_model_active_index -= 1

        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True)

        return ({'FINISHED'})