import importlib

from ciokatana.v1.model import (
    array_model,
    hardware_model,
    jobs_model,
    misc_model,
    project_model,
    software_model,
    environment_model,
    metadata_model,
    assets_model,
    asset_scraper,
    collapsible_panel_model,
    
)

from ciokatana.v1.components import (
    buttoned_scroll_panel,
    checkbox_grp,
    combo_box_grp,
    int_field_grp,
    key_value_grp,
    notice_grp,
    software_combo_box_grp,
    text_field_grp,
    text_grp,
    widgets,
    render_node_table,
)

from ciokatana.v1.sections import (
    assets_section,
    collapsible_section,
    general_section,
    hardware_section,
    jobs_section,
    software_section,
    environment_section,
    metadata_section,
    advanced_section,
)

from ciokatana.v1 import (
    Panel,
    configuration_tab,
    preview_tab,
    progress_tab,
    response_tab,
    Node,
    Editor,
    dialog,
    render_file_dialog,
    utils,
    tooltips,
    const,
    setup,
    validation_tab,
    validation
)

from ciokatana.v1.progress import (
    file_status_row,
    file_status_panel,
    progress_widget_base,
    md5_progress_widget,
    upload_progress_widget,
    jobs_progress_widget,
    submission_worker
)


def reload():
    importlib.reload(tooltips)
    importlib.reload(const)
    importlib.reload(utils)
    importlib.reload(asset_scraper)
    importlib.reload(array_model)
    importlib.reload(project_model)
    importlib.reload(software_model)
    importlib.reload(hardware_model)
    importlib.reload(jobs_model)
    importlib.reload(environment_model)
    importlib.reload(metadata_model)
    importlib.reload(assets_model)
    importlib.reload(misc_model)
    importlib.reload(collapsible_panel_model)

    importlib.reload(Node)

    # components
    importlib.reload(widgets)

    importlib.reload(checkbox_grp)
    importlib.reload(combo_box_grp)
    importlib.reload(int_field_grp)
    importlib.reload(key_value_grp)
    importlib.reload(render_node_table)
    importlib.reload(notice_grp)
    importlib.reload(software_combo_box_grp)
    importlib.reload(text_field_grp)
    importlib.reload(text_grp)

    # sections
    importlib.reload(collapsible_section)
    importlib.reload(general_section)
    importlib.reload(hardware_section)
    importlib.reload(jobs_section)
    importlib.reload(software_section)
    importlib.reload(assets_section)
    importlib.reload(environment_section)
    importlib.reload(metadata_section)
    importlib.reload(advanced_section)

    # progress
    importlib.reload(submission_worker)
    importlib.reload(file_status_row)
    importlib.reload(file_status_panel)
    importlib.reload(progress_widget_base)
    importlib.reload(md5_progress_widget)
    importlib.reload(upload_progress_widget)
    importlib.reload(jobs_progress_widget)

    # top UI
    importlib.reload(buttoned_scroll_panel)
    importlib.reload(preview_tab)
    importlib.reload(configuration_tab)
    importlib.reload(progress_tab)
    importlib.reload(validation_tab)
    importlib.reload(response_tab)
    importlib.reload(Node)
    importlib.reload(validation)
    importlib.reload(Panel)
    importlib.reload(Editor)
    importlib.reload(dialog)
    importlib.reload(render_file_dialog)
    importlib.reload(setup)
