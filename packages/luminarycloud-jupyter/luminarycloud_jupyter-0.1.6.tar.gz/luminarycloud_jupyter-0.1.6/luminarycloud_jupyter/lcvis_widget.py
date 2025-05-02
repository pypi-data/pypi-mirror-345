import anywidget
import array
import pathlib
import traitlets
import json
from typing import Any, Optional, TYPE_CHECKING
from luminarycloud.vis.display import DisplayAttributes
from luminarycloud.enum.vis_enums import visquantity_text, SceneMode
from luminarycloud._proto.api.v0.luminarycloud.vis import vis_pb2

from luminarycloud_jupyter.vis_enums import (
    field_component_to_lcvis,
    representation_to_lcvis,
)

if TYPE_CHECKING:
    # We need to be careful w/ this import for typing otherwise
    # we'll introduce a circular import issue
    from luminarycloud.vis import Scene

base_path = pathlib.Path(__file__).parent / "static"


class LCVisWidget(anywidget.AnyWidget):
    _esm: pathlib.Path = base_path / "lcvis.js"

    # TODO: we'll bundle the single threaded wasm here for vanilla Jupyter

    # We send the workspace state as a traitlet instead of a cmd message
    # so that it can be set when first creating the widget, before it's
    # able to receive messages.
    workspace_state: traitlets.Unicode = traitlets.Unicode().tag(sync=True)

    scene_mode: traitlets.Unicode = traitlets.Unicode().tag(sync=True)

    last_screenshot: Optional[bytes] = None

    camera_position: traitlets.List = traitlets.List().tag(sync=True)
    camera_look_at: traitlets.List = traitlets.List().tag(sync=True)
    camera_up: traitlets.List = traitlets.List().tag(sync=True)

    # TODO will: we should also expose pan as a param on the camera

    def __init__(self, scene_mode: SceneMode, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.scene_mode = scene_mode
        self.on_msg(self.receive_widget_message)

    def receive_widget_message(self, widget: Any, content: str, buffers: list[bytes]) -> None:
        if content == "screenshot taken":
            self.last_screenshot = buffers[0]

    def set_workspace_state(
        self, scene: "Scene", render_data_urls: vis_pb2.GetRenderDataUrlsResponse
    ) -> None:
        workspace_state = json.loads(render_data_urls.workspace_state)

        filter_urls = {}
        for i in range(len(render_data_urls.urls.filter_ids)):
            filter_id = render_data_urls.urls.filter_ids[i]
            url = render_data_urls.urls.data_files[i].signed_url
            filter_urls[filter_id] = url
        workspace_state["filters_to_url"] = filter_urls

        self.workspace_state = json.dumps(workspace_state)

    def take_screenshot(self) -> None:
        self.last_screenshot = None
        self.send({"cmd": "screenshot"})

    def set_surface_visibility(self, surface_id: str, visible: bool) -> None:
        self.send(
            {
                # TODO: put these in some shared JSON defs/constants file for cmds?
                "cmd": "set_surface_visibility",
                "surfaceId": surface_id,
                "visible": visible,
            }
        )

    def set_surface_color(self, surface_id: str, color: list[float]) -> None:
        if len(color) != 3:
            raise ValueError("Surface color must be list of 3 RGB floats, in [0, 1]")
        if any(c < 0 or c > 1 for c in color):
            raise ValueError("Surface color must be list of 3 RGB floats, in [0, 1]")
        self.send(
            {
                # TODO: put these in some shared JSON defs/constants file for cmds
                "cmd": "set_surface_color",
                "surfaceId": surface_id,
            },
            [array.array("f", color)],
        )

    def set_display_attributes(self, object_id: str, attrs: DisplayAttributes) -> None:
        cmd = {
            "cmd": "set_display_attributes",
            "objectId": object_id,
            "visible": attrs.visible,
            "representation": representation_to_lcvis(attrs.representation),
        }
        if attrs.field:
            cmd["field"] = {
                "name": visquantity_text(attrs.field.quantity),
                "component": field_component_to_lcvis(attrs.field.component),
            }
        self.send(cmd)

    def reset_camera(self) -> None:
        self.send({"cmd": "reset_camera"})
