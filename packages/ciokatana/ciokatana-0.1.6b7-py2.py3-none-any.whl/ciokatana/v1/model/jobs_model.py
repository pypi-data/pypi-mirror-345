import os
import re
from Katana import NodegraphAPI, FarmAPI

from contextlib import contextmanager
from cioseq.sequence import Sequence
from ciopath.gpath_list import PathList
from ciopath.gpath import Path

TITLE_PARAM = "jobTitle"
CHUNK_SIZE_PARAM = "chunkSize"
FRAMES_PARAM = "frameSpec"
SCOUT_FRAMES_PARAM = "scoutSpec"
CHUNK_PARAM = "chunk"
RENDER_NODES_PARAM = "renderNodes"
CURRENT_RENDER_NODE_PARAM = "renderNode"
TASK_TEMPLATE_PARAM = "taskCommand"
POSIX_PROJECT_PARAM = "posixProject"
DEFAULT_TASK_TEMPLATE = 'f"katana --batch --katana-file=\\"{posixProject}\\" --render-node=\\"{renderNode}\\" -t={chunk}"'
POSIX_PROJECT_EXPRESSION = 're.sub(r"^[A-Z]:", "", "{}".format(project.assetID), re.IGNORECASE).replace("\\\\", "/")'
TITLE_EXPRESSION = 'f"Katana - {renderNode} - {project.katanaSceneName}"'
SCOUT_AUTO_REGEX = re.compile(r"^auto[, :]+(\d+)$")
SCOUT_FML_REGEX = re.compile(r"^fml[, :]+(\d+)$")

FARM_SETTING_OVERRIDES_PARAM = "farmSettings.conductorOverrides"
FARM_SETTING_FRAMESPEC_PARAM = "farmSettings.conductorFrameSpec"
FARM_SETTING_SCOUTSPEC_PARAM = "farmSettings.conductorScoutSpec"
FARM_SETTING_CHUNKSIZE_PARAM = "farmSettings.conductorChunkSize"


@contextmanager
def remember_parameter(param):
    """Context manager to remember and restore the state of a parameter."""
    is_expression = param.isExpression()
    current = param.getExpression() if is_expression else param.getValue(0)
    try:
        yield
    finally:
        param.setExpression(current) if is_expression else param.setValue(current, 0)


def create(node):
    """Create parameters for the node.

    Swt some defaults and expressions.
    """
    params = node.getParameters()

    # RENDER NODES
    nodes_param = params.createChildStringArray(RENDER_NODES_PARAM, 0)
    nodes_param.resizeArray(1)
    nodes_param.getChildByIndex(0).setValue("Empty", 0)

    # TITLE
    title_param = params.createChildString(TITLE_PARAM, "untitled")
    title_param.setExpression(TITLE_EXPRESSION)

    # FRAMES PARAMS
    params.createChildNumber(CHUNK_SIZE_PARAM, 1)
    scene_range = FarmAPI.GetSceneFrameRange()
    params.createChildString(FRAMES_PARAM, "{start}-{end}x1".format(**scene_range))
    params.createChildString(SCOUT_FRAMES_PARAM, "auto:3")

    # POSIX PROJECT PARAM
    posix_project_param = params.createChildString(POSIX_PROJECT_PARAM, "")
    posix_project_param.setExpression(POSIX_PROJECT_EXPRESSION)

    # TASK TEMPLATE PARAM
    task_template_param = node.getParameters().createChildString(
        TASK_TEMPLATE_PARAM, ""
    )
    task_template_param.setExpression(DEFAULT_TASK_TEMPLATE)

    # CURRENT CHUNK PLACEHOLDERS (Hidden)
    current_node_param = params.createChildString(CURRENT_RENDER_NODE_PARAM, "untitled")
    expr = f"={RENDER_NODES_PARAM}.i0"
    current_node_param.setExpression(expr)

    params.createChildString(CHUNK_PARAM, str(scene_range.get("start", 1)))


def get_node_references(node):
    """Get the render nodes referenced by the node."""
    return [
        NodegraphAPI.GetNode(child.getValue(0))
        for child in node.getParameter(RENDER_NODES_PARAM).getChildren()
    ]


def set_node_references(node, nodes):
    """Set up expressions to reference render nodes."""
    num = len(nodes)
    param = node.getParameter(RENDER_NODES_PARAM)
    param.resizeArray(num)
    for i, node in enumerate(nodes):
        expr = f"@{node.getName()}"
        param.getChildByIndex(i).setExpression(expr)
    param.setTupleSize(1)


def resolve(node):
    """Generator to emit the payload for each render job.

    Collect up the payload data for each render node. Only focus on fields this
    model cares about - i.e. job_title, output_path, tasks_data, scout_frames.
    """
    current_render_node_param = node.getParameter(CURRENT_RENDER_NODE_PARAM)
    title_param = node.getParameter(TITLE_PARAM)

    with remember_parameter(current_render_node_param):
        for i, render_node_data in enumerate(resolve_overrides(node)):
            expr = f"={RENDER_NODES_PARAM}.i{i}"
            current_render_node_param.setExpression(expr)
            frame_spec = render_node_data["frame_spec"]
            scout_spec = render_node_data["scout_spec"]
            chunk_size = render_node_data["chunk_size"]
            render_node = render_node_data["render_node"]

            main_sequence = Sequence.create(frame_spec, chunk_size=chunk_size)
            scout_sequence = _get_scout_sequence(scout_spec, main_sequence)
            tasks_data = _generate_tasks_data(node, main_sequence)
            output_path = get_output_path(render_node)

            result = {
                "job_title": title_param.getValue(0),
                "output_path": output_path or "INVALID OUTPUT PATH",
                "tasks_data": tasks_data,
            }
            if scout_sequence:
                result["scout_frames"] = ",".join([str(s) for s in scout_sequence])

            yield result


def resolve_overrides(node):
    """Generator yields data for the given render nodes.

    Result contains the defaults on each node unless values have been overridden.
    """
    default_frame_spec = node.getParameter(FRAMES_PARAM).getValue(0)
    default_scout_spec = node.getParameter(SCOUT_FRAMES_PARAM).getValue(0)
    default_chunk_size = node.getParameter(CHUNK_SIZE_PARAM).getValue(0)

    for render_node in get_node_references(node):
        do_override = render_node.getParameter(FARM_SETTING_OVERRIDES_PARAM).getValue(0)
        if do_override:
            frame_spec = render_node.getParameter(
                FARM_SETTING_FRAMESPEC_PARAM
            ).getValue(0)
            scout_spec = render_node.getParameter(
                FARM_SETTING_SCOUTSPEC_PARAM
            ).getValue(0)
            chunk_size = render_node.getParameter(
                FARM_SETTING_CHUNKSIZE_PARAM
            ).getValue(0)

        else:
            frame_spec = default_frame_spec
            scout_spec = default_scout_spec
            chunk_size = default_chunk_size

        yield {
            "frame_spec": frame_spec,
            "scout_spec": scout_spec,
            "chunk_size": int(chunk_size),
            "do_override": do_override,
            "render_node": render_node,
        }


# Private
def _generate_tasks_data(node, main_sequence):
    """Generate tasks data for the given node.

    This looks a bit confusing because we're using the chunk parameter to
    repeatedly set a string that is referenced by the task template parameter.
    Then we get the final value of the task template parameter and use it as the
    command for the task.

    Note, the whole point of having a task template is that the user can edit
    it, and this is why we can't presume it's structure and set the chunk value
    directly. The user may or may not choose to use the chunk value, but it's
    available should they want to.

    For Katana commandline, we must format the chunk (the -t option) a little differently
    than other DCCs. Katana understands frame specs like 1-5,10,20-24, but it
    doesn't understand step-frame notation like 1-10x2. So we need to remove the x2 from
    the frame spec and instead expand any progressions with a step greater
    than 1 into comma separated lists. So 1-10x2 becomes 1,3,5,7,9. This is done
    in the chunk.to() method of cioseq::Sequence.
    """

    tasks = []

    chunk_param = node.getParameter(CHUNK_PARAM)
    task_template_param = node.getParameter(TASK_TEMPLATE_PARAM)
    with remember_parameter(chunk_param):
        for chunk in main_sequence.chunks():
            chunk_spec = str(chunk)
            chunk_param.setValue(chunk.to("-", "", ","), 0)
            tasks.append(
                {"command": task_template_param.getValue(0), "frames": chunk_spec}
            )

    return tasks


def _get_scout_sequence(scout_spec, main_sequence):
    """Get the scout sequence from the spec.

    Scout sequence can be specified in a few ways:
    auto:N where N is the number of samples to take from the main sequence, minimizing gaps.
    fml:N where N is the number of samples to take from the main sequence, bookmarked to first and last.
    TODO: off
    """
    match = SCOUT_AUTO_REGEX.match(scout_spec)
    if match:
        num_samples = int(match.group(1))
        return main_sequence.subsample(num_samples)
    match = SCOUT_FML_REGEX.match(scout_spec)
    if match:
        num_samples = int(match.group(1))
        return main_sequence.calc_fml(num_samples)

    # If scout_spec is blank, then no scout frames.
    try:
        scout_sequence = Sequence.create(scout_spec)
        scout_sequence = scout_sequence.intersection(main_sequence)
        return scout_sequence
    except (ValueError, TypeError):
        pass
    return None


def get_output_path(render_node):
    """Get the output path from the render node.

    We do this by looking at the dependencies of the render node to find the
    output location. If there is only one output location, we use the directory,
    otherwise we use the common path of all the output locations.
    """

    path_list = PathList()
    outputs = get_outputs(render_node, allow_absolute=True, allow_relative=False,allow_tmpdir=False)
    for output in outputs:
        if output["outputLocation"]:
            try:
                path_list.add(output["outputLocation"])
            except Exception:
                continue

    output_dir = ""
    if len(path_list) == 1:
        output_dir = os.path.dirname(list(path_list)[0].fslash())
    elif len(path_list) > 1:
        common = path_list.common_path()
        if common.depth > 0:
            output_dir = common.fslash()

    return output_dir



def get_outputs(render_node, allow_absolute=True, allow_relative=True, allow_tmpdir=True):
    """Get the render outputs.
    
    We only care about outputs that are:
    A. Absolute.
    B. Enabled.
    C. Not in the temp folder.
    """
    result = []
    try:
        dependencies = FarmAPI.GetSortedDependencies(render_node)
    except:
        dependencies = []

    for dependency in dependencies:
        for output in dependency.outputs:
            is_in_tmpdir = False
            if not output["outputLocation"]:
                continue
            if not output["enabled"]:
                continue
            try:
                pth = Path(output["outputLocation"])
                tmp_path = Path(os.environ["TMPDIR"])
                if pth.startswith(tmp_path):
                    is_in_tmpdir = True
            except ValueError:
                continue

            is_abs =  Path(output["outputLocation"]).absolute
            if (allow_absolute and is_abs) or (allow_relative and not is_abs):
                if allow_tmpdir or not is_in_tmpdir:
                    result.append(
                        {
                            "name": output["name"],
                            "enabled": output["enabled"],
                            "absolute": is_abs,
                            "tmpdir": is_in_tmpdir,
                            "outputLocation": output["outputLocation"],
                            "tempRenderLocation": output["tempRenderLocation"],
                        }
                    )


    return result
