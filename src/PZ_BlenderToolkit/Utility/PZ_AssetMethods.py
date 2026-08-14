# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import os
import bpy
import functools

from pathlib import Path
from typing import NewType
from collections.abc import Iterable
from dataclasses import dataclass

from PZ_BlenderToolkit.PropertyGroups.General.PZ_ModDirectory import PZ_ModDirectory

def directx_import_available():
    checks = ['bl_ext.blender_org.io_directx_x',
              'bl_ext.user_default.io_directx_x'
              ]
    for check in checks:
        if check in bpy.context.preferences.addons.keys():
            return True
    return False

VirtualPath = NewType("VirtualPath", str)
"""Sanitised path best created through sanitise_path()"""

cache_globs: list[str] = [
    "media/lua/shared/NPCs/BodyLocations.lua",
    "media/scripts/generated/items/clothing.txt",
    "media/scripts/generated/items/container.txt",
    "media/clothing/**",
    "media/textures/**",
    "media/models_X/**",
]
"""Glob patterns of files to add to the cache."""

asset_cache: dict[VirtualPath, Path] = {}
"""Cached asset paths by their virutal path."""

@dataclass(slots=True)
class AssetSource:
    name: str
    """
    Name of the source, typically the mod id.
    Not unique: a mod's common and version directories use the same name.
    """
    root: Path
    """Root path of the source."""
    

asset_sources: list[AssetSource] = []
"""All asset sources."""


def sanitise_path(path: Path | str) -> VirtualPath:
    """
    Returns the corresponding VirtualPath to a string path.

    @arg path: Path to sanitise.
    @return: Sanitised path.
    """
    if isinstance(path, str):
        path = Path(path)
    
    return VirtualPath(path.as_posix().lower())


def build_asset_sources(pz_directory: str, mod_directories: list[PZ_ModDirectory]) -> None:
    """
    Builds the asset source list.
    You should call build_asset_cache() instead of calling this directly.
    """
    global asset_sources

    asset_sources = [
        AssetSource("pz-vanilla", Path(pz_directory))
    ]

    for mod in mod_directories:
        if not mod.active:
            continue
        dir = Path(mod.mod_dir)
        asset_sources.append(
            AssetSource(mod.name, dir)
        )
        common = dir.parent / "common"
        if common.is_dir():
            asset_sources.append(
                AssetSource(mod.name, common)
            )


def build_asset_cache(pz_directory: str, mod_directories: list[PZ_ModDirectory]) -> None:
    """
    Clears and builds the asset cache and source list from addon settings.
    """
    global asset_cache

    build_asset_sources(pz_directory, mod_directories)

    asset_cache = {}

    for source in asset_sources:
        for glob in cache_globs:
            for file in source.root.rglob(glob):
                if not file.is_file():
                    continue
                asset_cache[sanitise_path(file.relative_to(source.root))] = file


def get_file_all_sources(path: str) -> Iterable[tuple[Path, str]]:
    """
    Returns paths for a specific file from every source.
    Only files that exist will be added to the list.

    @param path: Path relative to the base of an asset root.
    @return: All matching files and the name of their source.
    """
    return [(source.root / path, source.name) for source in asset_sources if (source.root / path).is_file()]


def get_zomboid_asset_folders(context, parent_path: Path) -> Iterable[tuple[Path, str]]:
    """
    Returns an iterable of a specific directory from every source that contains it.
    
    @return: Iterable of a specified directory from every source that has it, and the name of that source.
    """
    return [(source.root / parent_path, source.name) for source in asset_sources if (source.root / parent_path).is_dir()]

def get_zomboid_asset(context, path: Path, allowed_types: list[str] = []) -> tuple[Path, str] | tuple[None, None]:
    """
    Returns a zomboid asset by its path, respecting overrides by mods.

    @param item_path: Path to the asset.
    @param allowed_types: Optional list of acceptable suffixes. Suffixes should be lowercase and include the leading '.'.
    @return: The asset and source. Both will be None if the asset does not exist.
    """
    # optimisation: if only one suffix is allowed, just set the suffix so we can look it up without loops and stuff
    if len(allowed_types) == 1:
        path = path.parent / (path.name + allowed_types[0])
        allowed_types = []

    if path.suffix == "":
        if len(allowed_types) < 0:
            print(f"Cannot check the cache for file '{path}' without a suffix and no allowed_types.")
        
        for type in allowed_types:
            with_suffix = sanitise_path(path.parent / (path.stem + type))
            if with_suffix in asset_cache:
                path = asset_cache[with_suffix]
                return path, type.lower()
    else:
        sanitised_path: VirtualPath = sanitise_path(path)
        if sanitised_path in asset_cache:
            path = asset_cache[sanitised_path]
            return path, path.suffix.lower()

    if 'bk/' not in path.as_posix():
        print(f"Asset '{path}'/'{sanitise_path(path)}' is not in cache, falling back to search. If the asset exists the cache patterns may need to be updated.")

    for source in asset_sources:
        found_file: Path | None = None

        if path.suffix != "":
            file = source.root / path
            if file.is_file():
                found_file = file
        else:
            for file in source.root.glob(f"{path.as_posix()}.*", case_sensitive=False):
                if file.is_file():
                    if len(allowed_types) < 1 or file.suffix.lower() in allowed_types:
                        found_file = file
                    
        if found_file is not None:
            asset_cache[sanitise_path(found_file.relative_to(source.root))] = found_file
            return found_file, found_file.suffix.lower()

    if 'bk/' not in path.as_posix():
        print('Could not find ' + path.as_posix())
        
    return (None, None)