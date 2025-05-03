import re
import logging
from Katana import NodegraphAPI, AssetAPI # Ensure AssetAPI is imported
from ciopath.gpath_list import PathList
from ciopath.gpath import Path
import os # Import os for path manipulation

# Setup logging (ensure it's configured to show INFO or DEBUG)
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG) # Uncomment for detailed debug logs

# --- Constants ---

# Regex for UDIMs/Sequences after initial processing
GLOBBABLE_REGEX = re.compile(r"<\w+>|(#+)|(%\d*d)", re.IGNORECASE)

# Node types KNOWN to reference external file assets AND their primary asset parameters
# Format: "NodeType": ["paramName1", "paramName2", ...]
ASSET_NODE_TYPES = {
    # --- Geometry / Scene Description ---
    "Alembic_In":       ["fileName", "abcAsset"], # Confirmed for Alembic files
    "UsdIn":            ["fileName"], # USD assets
    "ScenegraphXml_In": ["xmlFile"], # Scenegraph XML files
    "Importomatic":     ["fileName", "asset"], # Multiple asset imports
    # Add VdbIn, ReadGeo, PointCacheIn, FbxIn, ObjIn etc. if used

    # --- Textures / Images ---
    "ImageRead":        ["file", "filename"], # Texture/image files
    # Add DeepRead, specific renderer image nodes (ArnoldImage, RedshiftNormalMap etc.)

    # --- Look / Material / Shading ---
    "LookFileRead":     ["filename", "lookfile"], # Katana look files (.klf)
    "Material":         ["materialFile", "file"], # Material library files
    # Add MaterialNetwork, specific renderer shading nodes (PxrTexture etc.)

    # --- Procedurals / Archives / Assemblies ---
    "KatanaProcedural": ["fileName", "file", "proceduralFile"], # Procedurals (e.g., .ass, .rib)
    # Add ArnoldProcedural, PrmanProcPrim, VrayScene, VrayProxy etc.

    # --- Scripting / Other ---
    "LiveGroup":        ["source"], # LiveGroup source files (.klf)
    "RenderScript":     ["scriptFile", "file"], # External scripts (e.g., .py, .lua)
    "OpScript":         ["scriptFile", "file"], # Lua scripts (or Python)
    "CameraCreate":     ["renderSettings.cameraSettings.filename"], # Camera settings file (verify path)
    "VariableSet":      ["value"], # File paths in variables (needs careful validation in scrape logic)
    "Cryptomatte":      ["manifestFile", "file"], # Cryptomatte manifest files

    # --- Lighting ---
    "GafferThree":      ["iesProfile", "file"], # IES profiles for lighting (Verify node name/param)
    # Add LightCreate, specific renderer light nodes (ArnoldSkyDomeLight, RedshiftIESLight etc.)

    # --- Renderer Specific Shading Nodes (Examples - covered also by SHADING_NODE_PREFIXES/PARAM_NAMES) ---
    "ArnoldShadingNode": ["filename", "texture", "file"], # Arnold-specific shading nodes
    "PrmanShadingNode": ["filename", "texture", "file"], # RenderMan-specific shading nodes
    "VRayShadingNode":  ["filename", "texture", "file"], # V-Ray shading nodes (if V-Ray plugin used)
    "RedshiftShadingNode": ["filename", "texture", "file"], # Redshift shading nodes (if Redshift plugin used)

    # Add more nodes as needed for your pipeline
}

# General prefixes for shading nodes
SHADING_NODE_PREFIXES = ("Arnold", "Prman", "Redshift", "Standard") # Add other renderers

# Parameters on shading nodes likely to be file paths (case-insensitive check)
SHADING_NODE_ASSET_PARAM_NAMES = {
    "filename", "file", "texture", "map", "picture", "image",
    "hdr", "iesprofile", "ramp_color_file", "ramp_float_file",
    "osl_filepath", "tex", "file_texture_name", # Add more variations
}

# Node types/parameters to EXCLUDE explicitly
DEFAULT_NODE_PARAM_BLACKLIST = (
    "Group", "GroupStack", "GroupMerge",
    # "LiveGroup", # Keep LiveGroup node check, but allow 'source' param processing
    "ErrorNode", "RootNode",
    "Render", "DiskRender", "ConductorRender", # Output nodes
    "AttributeScript::user.outputPath", "AttributeScript::user.outputStats", "AttributeScript::user.scenePath",
    "Viewer", "MonitorLayer", "RenderOutputDefine",
    "Alembic_In::name", "ImageRead::colorSpace",
    # Add any other known non-asset parameters here
)

# Path prefixes to EXCLUDE
DEFAULT_PATH_PREFIX_BLACKLIST = (
    "/tmp/", "/var/tmp/", "/usr/tmp/", "/root",
    "//*/", # Katana internal paths often start like this
    "{", "[", # Likely expression remnants or unresolved variables
    # System folders (adjust for your OS if needed)
    "/System", "/Library", "/Applications", "/usr", "/opt",
    "C:\\Program Files", "C:\\ProgramData", "C:\\Windows",
    # User folders (use environment variables if possible, otherwise wildcards)
    # Consider if assets *could* legitimately be in Documents/Downloads for some workflows
    # "C:\\Users\\*\\AppData", "/Users/*/Library", "/Users/*/AppData",
)

# File extensions considered valid render assets (keep this reasonably broad)
VALID_FILE_EXTENSIONS = (
    # Images
    ".exr", ".tx", ".tiff", ".tif", ".jpg", ".jpeg", ".png", ".hdr", ".tga", ".rat",
    # Geometry/Scene
    ".abc", ".usd", ".usda", ".usdc", ".usdz", ".vdb", ".obj", ".fbx", ".gltf", ".glb", ".ass", ".rib", ".vrscene",
    # Look/Material/Other
    ".mtl", ".xml", ".osl", ".oso", ".ies", ".klf", ".ass.gz", ".json", ".ocio", ".spi1d", ".spi3d", ".cube",
    # Add others as needed (.mov for preview? .wav for audio?)
)

# --- Helper Functions ---

def _flatten_param(param, result):
    """
    Recursively traverses parameter hierarchies (groups, arrays) and appends
    any found string parameters to the result list.

    Args:
        param (NodegraphAPI.Parameter): The starting parameter to flatten.
        result (list): A list to which found string parameters will be appended.
    """
    param_type = param.getType()
    if param_type == "string":
        result.append(param)
    elif param_type in ("group", "stringArray", "groupArray"):
        for child in param.getChildren():
            _flatten_param(child, result)

def _find_expression_source(param):
    """
    Finds the ultimate source parameter referenced by an expression chain.

    Traverses 'getParam' and 'getParent' expressions until a non-expression
    parameter is found, the expression is unresolvable, a cycle is detected,
    or the maximum recursion depth is reached.

    Args:
        param (NodegraphAPI.Parameter): The parameter potentially holding an expression.

    Returns:
        NodegraphAPI.Parameter or None: The source parameter, or the last valid
            parameter in the chain if resolution fails, or None if the input was None.
    """
    if not param: return None # Safety check
    # Limit recursion depth to prevent infinite loops in complex cases
    MAX_RECURSION = 10
    depth = 0
    current_param = param
    # Keep track of visited params during resolution to detect cycles
    visited_during_resolve = {current_param}
    while current_param and current_param.isExpression() and depth < MAX_RECURSION:
        depth += 1
        expr = current_param.getExpression().strip()
        # logger.debug(f"Resolving depth {depth}: {current_param.getFullName()} Expr: {expr}")

        getparam_match = re.match(r"^getParam\(['\"]([^'\"]+)['\"]\)$", expr)
        getparent_match = re.match(r"^getParent\(\)\.([\w\.]+)$", expr)
        resolved_next = None

        if getparam_match:
            node_param = getparam_match.group(1)
            try:
                node_name, param_name = node_param.split('.', 1)
            except ValueError:
                logger.warning(f"Could not split getParam ref '{node_param}' in {current_param.getFullName()}. Stopping resolution.")
                break # Stop resolving this chain
            node = NodegraphAPI.GetNode(node_name)
            if node:
                resolved_next = node.getParameter(param_name)
                if not resolved_next:
                    logger.warning(f"Param '{param_name}' not found on node '{node_name}' referenced by {current_param.getFullName()}.")
            else:
                logger.warning(f"Node '{node_name}' not found referenced by {current_param.getFullName()}.")

        elif getparent_match:
            node = current_param.getNode().getParent()
            if node:
                param_name = getparent_match.group(1)
                resolved_next = node.getParameter(param_name)
                if not resolved_next:
                    logger.warning(f"Param '{param_name}' not found on parent of {current_param.getNode().getName()} referenced by {current_param.getFullName()}.")
            else:
                logger.warning(f"Parent node not found for {current_param.getNode().getName()} referenced by {current_param.getFullName()}.")

        if resolved_next:
            # Check for cycles
            if resolved_next in visited_during_resolve:
                logger.warning(f"Expression cycle detected involving {resolved_next.getFullName()}. Stopping resolution.")
                break
            visited_during_resolve.add(resolved_next)
            current_param = resolved_next
        else:
            # logger.debug("Expression not resolved further or target not found.")
            break # Stop if no resolution occurred or target missing

    if depth >= MAX_RECURSION:
        logger.warning(f"Expression resolution exceeded max depth for {param.getFullName()}. Returning last valid parameter.")

    # logger.debug(f"Resolved source for {param.getFullName()} -> {current_param.getFullName()}")
    return current_param

# --- Reinstated _get_gpath for validation ---
def _get_gpath(filename):
    """
    Validates if a filename string represents a plausible, absolute file path
    with a recognized asset extension.

    Args:
        filename (str): The filename string to validate.

    Returns:
        Path or None: A ciopath.gpath.Path object if the filename is deemed
            a valid potential asset path, otherwise None.
    """
    # logger.debug(f"Validating filename for gpath: {filename}")
    if not filename or not isinstance(filename, str):
        # logger.debug("Filename is empty or not a string.")
        return None

    # Basic check: Does it contain likely path separators?
    # Allow network paths starting with // or \\
    # Allow single drive letters C: D: etc.
    if not filename.startswith(("//", "\\\\")) and \
       '/' not in filename and '\\' not in filename and \
       not re.match(r"^[a-zA-Z]:$", filename): # Check for simple drive letter only
        # logger.debug("Filename does not contain typical path separators or drive letter.")
        return None

    # Check for invalid characters or expression remnants more strictly
    # Allow '*' and '?' now, as globbing happens later. Check for '{', '(', etc.
    if any(char in filename for char in ['{', '[', '(', ')']):
        # logger.debug("Filename contains invalid characters or expression remnants.")
        return None

    # Check extension (case-insensitive) - Allow paths without extensions? Maybe not for assets.
    path_part = filename.split('?')[0].split('#')[0]
    # Make extension check slightly less strict? Or keep it? Let's keep it for now.
    if not any(path_part.lower().endswith(ext) for ext in VALID_FILE_EXTENSIONS):
        # logger.debug(f"Filename '{path_part}' does not have a valid render asset extension.")
        return None

    try:
        # logger.debug("Instantiating Path object.")
        asset = Path(filename)
    except (ValueError, TypeError) as e:
        logger.warning(f"Error creating Path object for '{filename}': {e}")
        return None

    # Check if absolute (allow network paths)
    # A simple drive letter like "C:" is not considered absolute by Pathlib/GPath
    if not asset.absolute and not re.match(r"^[a-zA-Z]:$", str(asset)):
        # logger.debug("Path is not absolute.")
        return None

    # logger.debug(f"Path '{asset}' seems valid for further processing.")
    return asset
# --- End reinstated _get_gpath ---

def _is_blacklisted(node, param):
    """
    Checks if a given node or parameter should be excluded based on type,
    specific name, or the parameter value's path prefix.

    Args:
        node (NodegraphAPI.Node): The original node where the parameter search started
                                  (used for context, though checks use param's node).
        param (NodegraphAPI.Parameter): The resolved source parameter to check.

    Returns:
        bool: True if the node/parameter/path is blacklisted, False otherwise.
    """
    param_node = param.getNode()
    node_type = param_node.getType()

    # Check for macro type
    macro_type_param = param_node.getParameter("user.macroType")
    if macro_type_param:
        macro_type_value = macro_type_param.getValue(0)
        if macro_type_value:
            node_type = macro_type_value

    # 1. Check Node Type Blacklist
    if node_type in DEFAULT_NODE_PARAM_BLACKLIST:
        # logger.debug(f"Node type '{node_type}' is blacklisted.")
        return True

    # 2. Check Specific Node::Parameter Blacklist
    param_name = param.getFullName(False)
    specific_param_key = f"{node_type}::{param_name}"
    if specific_param_key in DEFAULT_NODE_PARAM_BLACKLIST:
        # logger.debug(f"Specific parameter '{specific_param_key}' is blacklisted.")
        return True

    # 3. Check Path Prefix Blacklist (using the parameter's value)
    filename = param.getValue(0)
    if filename and isinstance(filename, str):
        norm_filename = filename.replace("\\", "/")
        # Use os.path.normpath? Might resolve ../ etc. but could be slow
        # norm_filename = os.path.normpath(norm_filename)
        for prefix in DEFAULT_PATH_PREFIX_BLACKLIST:
            # Simple startswith check is usually sufficient and safer than regex
            if norm_filename.startswith(prefix):
                 # logger.debug(f"Filename '{filename}' starts with blacklisted prefix '{prefix}'.")
                 return True

    # logger.debug("Not blacklisted.")
    return False


def _make_globbable(filename):
    """
    Replaces common sequence and UDIM patterns (e.g., %04d, ####, <UDIM>)
    in a filename string with a wildcard ('*').

    Args:
        filename (str): The filename string potentially containing sequence patterns.

    Returns:
        str: The filename with sequence patterns replaced by '*'. Returns the
             original string if input is invalid or no patterns are found.
    """
    if not filename or not isinstance(filename, str):
        return filename
    # logger.debug(f"Making globbable: {filename}")
    globbed = GLOBBABLE_REGEX.sub("*", filename)
    # logger.debug(f"Result: {globbed}")
    return globbed

# --- AssetScraper Class ---

class AssetScraper(object):
    """
    Scans a Katana scene's nodegraph to identify and collect potential external
    file asset paths referenced by specific node types and parameters.

    It resolves parameter expressions, validates potential paths, handles
    common sequence/UDIM patterns, and applies blacklists to filter results.
    """

    def __init__(
        self,
        node_param_blacklist=DEFAULT_NODE_PARAM_BLACKLIST,
        path_prefix_blacklist=DEFAULT_PATH_PREFIX_BLACKLIST,
    ):
        """
        Initializes the AssetScraper.

        Args:
            node_param_blacklist (tuple or set, optional): A collection of node types
                (e.g., "Render") or specific parameters ("NodeType::paramName")
                to exclude from scraping. Defaults to DEFAULT_NODE_PARAM_BLACKLIST.
            path_prefix_blacklist (tuple or set, optional): A collection of string
                prefixes. Any resolved path starting with one of these prefixes
                will be excluded. Defaults to DEFAULT_PATH_PREFIX_BLACKLIST.
        """
        logger.info("Initializing AssetScraper...")
        self.asset_paths = set() # Stores unique, globbed asset path strings
        self.node_param_blacklist = set(node_param_blacklist) # Use set for faster lookups
        self.path_prefix_blacklist = tuple(path_prefix_blacklist) # Keep as tuple for startswith
        self.seen_params = set() # Track resolved params to avoid redundant processing
        logger.info("AssetScraper initialized.")

    def scrape(self):
        """
        Performs the scan of the Katana nodegraph.

        Iterates through all nodes, identifies potentially relevant ones,
        finds their string parameters, resolves expressions, validates values
        as asset paths, applies blacklists, handles sequence patterns, and
        stores the unique results.

        Returns:
            PathList: A ciopath.gpath_list.PathList object containing the
                      unique, globbed asset paths found.
        """
        logger.info("Starting asset scrape...")
        self.asset_paths.clear()
        self.seen_params.clear()

        all_nodes = NodegraphAPI.GetAllNodes(includeDeleted=False)
        logger.info(f"Found {len(all_nodes)} total nodes.")

        for node in all_nodes:
            node_name = node.getName()
            node_type = node.getType()

            # --- Filter 1: Check if node type is potentially relevant ---
            is_asset_node = node_type in ASSET_NODE_TYPES
            is_shading_node = any(node_type.startswith(prefix) for prefix in SHADING_NODE_PREFIXES)

            if not is_asset_node and not is_shading_node:
                continue

            # logger.debug(f"Processing node: {node_name} (Type: {node_type})")

            string_params = []
            _flatten_param(node.getParameters(), string_params)

            for param in string_params:
                param_full_name = param.getFullName()
                # logger.debug(f"Checking parameter: {param_full_name}")

                # --- Filter 2: Resolve Expression & Check Seen ---
                resolved_param = _find_expression_source(param)
                if not resolved_param: # Skip if resolution failed badly
                    logger.warning(f"Could not resolve parameter source for {param_full_name}. Skipping.")
                    continue
                if resolved_param in self.seen_params:
                    continue
                self.seen_params.add(resolved_param)
                resolved_param_full_name = resolved_param.getFullName()
                # logger.debug(f"Resolved source: {resolved_param_full_name}")

                # --- Filter 3: Check Blacklists (Node/Param/Prefix) ---
                # Pass original node for context if needed, but resolved for checks
                if _is_blacklisted(node, resolved_param):
                    # logger.debug(f"Parameter {resolved_param_full_name} is blacklisted.")
                    continue

                # --- Filter 4: Check Specific Parameter Names ---
                param_name = resolved_param.getName()
                param_node_type = resolved_param.getNode().getType() # Use resolved node's type

                # Handle Macro Type for parameter check
                macro_type_param = resolved_param.getNode().getParameter("user.macroType")
                if macro_type_param:
                    macro_type_value = macro_type_param.getValue(0)
                    if macro_type_value:
                        param_node_type = macro_type_value # Override type if macro exists

                is_param_node_asset_type = param_node_type in ASSET_NODE_TYPES
                is_param_node_shading_type = any(param_node_type.startswith(prefix) for prefix in SHADING_NODE_PREFIXES)

                param_allowed = False
                if is_param_node_asset_type:
                    allowed_params = ASSET_NODE_TYPES.get(param_node_type, [])
                    if "*" in allowed_params or param_name in allowed_params:
                        param_allowed = True
                elif is_param_node_shading_type:
                    if param_name.lower() in SHADING_NODE_ASSET_PARAM_NAMES:
                        param_allowed = True

                if not param_allowed:
                    # logger.debug(f"Parameter name '{param_name}' not in allowed list for node type '{param_node_type}'. Skipping.")
                    continue

                # --- Get Value and Use Manual Validation ---
                raw_filename = resolved_param.getValue(0)
                # logger.debug(f"Raw filename value: {raw_filename}")

                if not raw_filename or not isinstance(raw_filename, str):
                    # logger.debug("Filename is empty or not a string. Skipping.")
                    continue

                # --- Filter 5: Use _get_gpath for validation ---
                path_obj = _get_gpath(raw_filename) # Validate the raw path string

                if not path_obj:
                    # logger.debug(f"Value '{raw_filename}' rejected by _get_gpath validation. Skipping.")
                    continue

                # --- Path seems valid according to _get_gpath, make globbable and store ---
                # Use the raw_filename which passed validation for globbing
                globbed_path_str = _make_globbable(raw_filename)

                # Store the globbed string path in the set
                if globbed_path_str not in self.asset_paths:
                    logger.info(f"Found valid asset: {globbed_path_str} (from Param: {resolved_param_full_name}, Raw: {raw_filename})")
                    self.asset_paths.add(globbed_path_str) # Store the string

        logger.info(f"Asset scrape finished. Found {len(self.asset_paths)} unique asset paths.")
        return self.get_path_list() # Return PathList

    def get_path_list(self):
        """
        Returns a PathList object containing the unique, globbed asset paths
        found during the scrape.

        Returns:
            PathList: A ciopath.gpath_list.PathList object.
        """
        logger.debug(f"Creating PathList from {len(self.asset_paths)} unique paths.")
        path_list = PathList()
        # Add the collected strings to the PathList
        path_list.add(*list(self.asset_paths))
        return path_list