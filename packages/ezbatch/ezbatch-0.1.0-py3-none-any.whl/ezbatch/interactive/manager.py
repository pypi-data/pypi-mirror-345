from pathlib import Path
from typing import cast

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Footer,
    Header,
    Markdown,
    Select,
    TabbedContent,
    TabPane,
)

from ezbatch.job import list_jobs

THIS_DIR = Path(__file__).resolve().parent


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        with Center():
            yield Select(
                options=[
                    ("SUBMITTED", "SUBMITTED"),
                    ("PENDING", "PENDING"),
                    ("RUNNABLE", "RUNNABLE"),
                    ("STARTING", "STARTING"),
                    ("RUNNING", "RUNNING"),
                    ("SUCCEEDED", "SUCCEEDED"),
                    ("FAILED", "FAILED"),
                ],
                allow_blank=False,
                value="RUNNING",
                prompt="Job Status",
                id="job-status-select",
                classes="sidebar-element",
            )


class WorkflowsTab(TabPane):
    pass


class JobsTab(TabPane):
    def compose(self) -> ComposeResult:
        yield Sidebar(id="sidebar")
        with VerticalScroll(id="main-content"):
            yield Markdown(id="jobs-markdown")

    @on(Select.Changed, "#job-status-select")
    def select_changed(self, event: Select.Changed):
        jobs = list_jobs("DefaultFargateQueue", event.value).to_markdown(index=False)  # type: ignore
        cast(Markdown, self.query_one("#jobs-markdown")).update(jobs)


class EZBatchManager(App):
    """EZBatchManager Application"""

    CSS_PATH = str(THIS_DIR / "manager.tcss")
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme = "textual-dark"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with TabbedContent(id="tabs"):
            yield JobsTab(title="Jobs")
