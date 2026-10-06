# pyright: reportInvalidTypeForm=false,reportMissingModuleSource=false
import bpy

from pathlib import Path
from typing import NewType
from collections.abc import Iterable
from dataclasses import dataclass

from ..PropertyGroups.General.PZ_ModDirectory import PZ_ModDirectory


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

cache_files: list[str] = [
    "media/lua/shared/NPCs/BodyLocations.lua",
    "media/scripts/generated/items/clothing.txt",
    "media/scripts/generated/items/container.txt",
]
"""Relative files to files to add to the cache."""

cache_paths: list[str] = [
    "media/clothing",
    "media/textures",
    "media/models_X",
]
"""Relative paths to add to the cache."""

asset_cache: dict[VirtualPath, Path] = {}
"""Cached asset paths by their virutal path."""

ADDON_ROOT: Path = Path(__file__).parent.parent
"""Root path of the addon."""

ERROR_TEXTURE: Path = ADDON_ROOT / "Assets/Textures/TEX-Error.png"
"""Texture used to indicate that an error has occured relating to textures."""


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


def sanitise_path(path: Path) -> VirtualPath:
    """
    Returns the corresponding VirtualPath to a string path.

    @arg path: Path to sanitise.
    @return: Sanitised path.
    """
    return VirtualPath(path.as_posix().lower())


def sanitise_path_str(path: str) -> VirtualPath:
    """
    Returns the corresponding VirtualPath to a string path without creating a new Path object.

    @arg path: Path string to sanitise.
    @return: Sanitised path string.
    """
    return VirtualPath(path.replace("\\", "/").lower())


def parse_path(path: str) -> Path:
    """
    Returns a path from a string in the format expected by the game.

    @arg path: Path to parse
    @return: Parsed path
    """
    return Path(path.replace("\\", "/"))


def scan_path(
    root_path: str,
    max_depth: int = 1,
    follow_symlinks: bool = False,
) -> Iterator[str]:
    queue: list[tuple[str, int]] = [(root_path, 1)]
    while queue:
        curr, depth = queue.pop(0)
        if depth > max_depth:
            continue

        with os.scandir(curr) as entries:
            for entry in entries:
                yield entry.path

                if not entry.is_dir(follow_symlinks=follow_symlinks):
                    continue

                if depth + 1 <= max_depth:
                    queue.append((entry.path, depth + 1))


def build_asset_sources(pz_directory: str, mod_directories: list[PZ_ModDirectory]) -> None:
    """
    Builds the asset source list.
    You should call build_asset_cache() instead of calling this directly.
    """
    global asset_sources

    # Check if this system is using the Linux directory style
    vanilla_source = None
    if (Path(pz_directory) / 'projectzomboid').is_dir():
        vanilla_source = AssetSource("Project Zomboid", Path(pz_directory) / 'projectzomboid')
    else:
        vanilla_source = AssetSource("Project Zomboid", Path(pz_directory))

    asset_sources = [
        vanilla_source
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
        for cached_file in cache_files:
            file: str = os.path.join(str(source.root), cached_file)
            if os.path.isfile(file):
                asset_cache[sanitise_path_str(cached_file)] = Path(file)

        for cached_path in cache_paths:
            root_path: str = os.path.join(str(source.root), cached_path)
            for path in scan_path(root_path):
                if os.path.isfile(path):
                    asset_cache[sanitise_path_str(os.path.relpath(path, source.root))] = Path(path)


def get_file_all_sources(path: str) -> Iterable[tuple[Path, str]]:
    """
    Returns paths for a specific file from every source.
    Only files that exist will be added to the list.

    @param path: Path relative to the base of an asset root.
    @return: All matching files and the name of their source.
    """

    # paths: list[tuple[Path, str]] = []
    # for source in asset_sources:
    #     for dir in source.root.glob(Path(path).as_posix() + "/", case_sensitive=False):
    #         if dir.is_file():
    #             paths.append((dir, source.name))
    # return paths

    return [(source.root / path, source.name) for source in asset_sources if (source.root / path).is_file()]


def get_zomboid_asset_folders(context, parent_path: str) -> Iterable[tuple[Path, str]]:
    """
    Returns an iterable of a specific directory from every source that contains it.
    
    @return: Iterable of a specified directory from every source that has it, and the name of that source.
    """

    return [(Path(os.path.join(s.root, parent_path + "/")), s.name) for s in asset_sources]


def get_zomboid_asset(
    context, path: Path, allowed_types: list[str] = []
) -> tuple[Path, str] | tuple[None, None]:
    """
    Returns a zomboid asset by its path, respecting overrides by mods.

    @param item_path: Path to the asset.
    @param allowed_types: Optional list of acceptable suffixes. Suffixes should be lowercase and include the leading '.'.
    @return: The asset and source. Both will be None if the asset does not exist.
    """
    # optimisation: if only one suffix is allowed, just set the suffix so we can look it up without loops and stuff
    # TODO(aoqia): use str instead of path here
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


def get_zomboid_texture(context, path: Path) -> tuple[Path, str]:
    """
    Returns a texture, respecting mod overrides.
    If a texture does not exist, ERROR_TEXTURE will be returned instead.
    """
    texture = get_zomboid_asset(context, path, [".png"])

    if texture[0] is not None:
        return texture
    
    return (ERROR_TEXTURE, "Community Rig")
