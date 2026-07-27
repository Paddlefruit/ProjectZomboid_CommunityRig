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

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py" and file != "auto_load.py":
                rel_path = os.path.relpath(os.path.join(root, file), directory)
                module_dots = rel_path.replace(os.sep, ".").removesuffix(".py")

                full_module_name = f"{__package__}.{module_dots}"
                module = importlib.import_module(full_module_name)
                imported_modules.append(module)

    return imported_modules

def get_classes_to_register(module_list):
    classes = []
    addon_pref_obj = None

    blender_bases = (Operator, Panel, UIList, PropertyGroup, AddonPreferences)

    # Order it so that classes are grabbed from the top to the bottom of each python file
    # Load the AddonPreferences class last
    for module in module_list:
        file_classes = []
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__ and issubclass(obj, blender_bases):
                if issubclass(obj, AddonPreferences):
                    addon_pref_obj = obj
                    continue
                line_no = inspect.getsourcelines(obj)[1]
                file_classes.append((line_no, obj))

            file_classes.sort(key=lambda x: x[0])

        for _, obj in file_classes:
            if obj not in classes:
                print(obj)
                classes.append(obj)
                
    classes.append(addon_pref_obj)
    return classes

def inspect_package_name(directory):
    return os.path.dirname(directory)

def register():
    for cls in ordered_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in ordered_classes:
        bpy.utils.unregister_class(cls)