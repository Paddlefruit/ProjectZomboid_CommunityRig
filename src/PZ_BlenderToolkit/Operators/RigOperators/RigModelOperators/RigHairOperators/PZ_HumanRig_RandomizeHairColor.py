# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
from bpy.types import Operator
from random import random, randint

class PZ_RandomizeHairColor(Operator):
    bl_idname = "zomboid.randomize_hair_color"
    bl_label = "Randomize Hair Color"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        p = context.active_object.pz_human_props
        color = (1.0, 1.0, 1.0)
        if p.natural_hair_color:
            hair_color_array = [
                (0.658, 0.408, 0.060),  # Mustard Yellow
                (0.397, 0.265, 0.082),  # Coffee
                (0.347, 0.150, 0.024),  # Leather
                (0.333, 0.223, 0.093),  # Dark Beige
                (0.314, 0.162, 0.072),  # Mocha
                (0.298, 0.192, 0.100),  # Dull Brown
                (0.159, 0.095, 0.045),  # Dark Taupe
                (0.093, 0.056, 0.026),  # Dark Brown
                (0.098, 0.036, 0.016),  # Chocolate
                (0.040, 0.022, 0.011),  # Darker Brown
                (0.034, 0.031, 0.029),  # Dark Grey
                (0.011, 0.009, 0.008),  # Black
                (0.201, 0.188, 0.162),  # Medium Grey
                (0.382, 0.342, 0.216),  # Stone
                (0.502, 0.439, 0.338),  # Greyish
                (0.381, 0.371, 0.347),  # Grey
                (0.515, 0.235, 0.136),  # Pinkish Tan
                (0.381, 0.110, 0.061),  # Clay
                (0.300, 0.051, 0.051),  # Light Maroon
                (0.238, 0.055, 0.029)  # Earth
            ]

            rnd = randint(0, len(hair_color_array) - 1)
            color = hair_color_array[rnd]
        else:
            color = (random(), random(), random())

        p.hair_color[0] = color[0]
        p.hair_color[1] = color[1]
        p.hair_color[2] = color[2]

        # Call a tag update on the hair color drivers
        instance_str = ' (' + str(p.rig_instance) + ')'
        context.active_object.update_tag()
        hair_mats = ('MAT-MaleHair' + instance_str, 'MAT-FemaleHair' + instance_str, 'MAT-Beard' + instance_str)
        for hair_mat in hair_mats:
            mat = bpy.data.materials.get(hair_mat)
            if mat:
                mat.node_tree.update_tag()

        # Redraw the viewport
        for area in context.window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return ({'FINISHED'})