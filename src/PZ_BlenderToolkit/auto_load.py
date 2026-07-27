# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false

import bpy
import os
import sys
import importlib
import inspect

from bpy.types import Operator, Panel, UIList, PropertyGroup, AddonPreferences

modules = []
ordered_classes = []

def init():
    global modules, ordered_classes

    current_dir = os.path.dirname(__file__)
    modules = get_all_submodules(current_dir)
    ordered_classes = get_classes_to_register(modules)

def get_all_submodules(directory):
    imported_modules = []

    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for file in sorted(files):
            if file.endswith(".py") and file != "__init__.py" and file != "auto_load.py":
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                module_dots = rel_path.replace(os.sep, ".").removesuffix(".py")

                full_module_name = f"{__package__}.{module_dots}"
                module = importlib.import_module(full_module_name)
                imported_modules.append(module)

    return imported_modules

def get_classes_to_register(module_list):
    classes = []

    blender_bases = (Operator, Panel, UIList, PropertyGroup, AddonPreferences)

    # Order it so that classes are grabbed from the top to the bottom of each python file
    # Load the AddonPreferences class last
    for module in module_list:
        file_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__ and issubclass(obj, blender_bases):
                line_no = inspect.getsourcelines(obj)[1]
                file_classes.append((line_no, obj))

            file_classes.sort(key=lambda x: x[0])

        for _, obj in file_classes:
            if obj not in classes:
                classes.append(obj)

    def get_registration_order(cls):
        if issubclass(cls, PropertyGroup):
            return 0
        if issubclass(cls, (Operator, UIList)):
            return 1
        if issubclass(cls, Panel):
            print(str(cls) + '   ' + str(hasattr(cls, 'bl_parent_id')))
            if hasattr(cls, 'bl_parent_id'):
                return 3
            return 2
        if issubclass(cls, AddonPreferences):
            return 4
        return 5

    classes.sort(key=get_registration_order)
    return classes

def inspect_package_name(directory):
    return os.path.dirname(directory)

def register():
    for cls in ordered_classes:
        print(cls)
        bpy.utils.register_class(cls)

def unregister():
    for cls in ordered_classes:
        bpy.utils.unregister_class(cls)