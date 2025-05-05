from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ezbatch.interactive.manager import EZBatchManager, JobsTab, Sidebar, WorkflowsTab


class TestSidebar:
    def test_sidebar_options(self):
        """Test that Sidebar has the correct job status options."""
        # Create sidebar
        sidebar = Sidebar()

        # Directly check the options in the Select widget
        # This is testing the implementation details, but it's better than trying to mock the UI framework
        options = [
            ("SUBMITTED", "SUBMITTED"),
            ("PENDING", "PENDING"),
            ("RUNNABLE", "RUNNABLE"),
            ("STARTING", "STARTING"),
            ("RUNNING", "RUNNING"),
            ("SUCCEEDED", "SUCCEEDED"),
            ("FAILED", "FAILED"),
        ]

        # Verify the options are correct by checking the source code
        from inspect import getsource

        source = getsource(Sidebar.compose)
        for status in ["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING", "SUCCEEDED", "FAILED"]:
            assert f'("{status}", "{status}")' in source, f"Option {status} not found in Sidebar.compose"


class TestJobsTab:
    def test_jobs_tab_widgets(self):
        """Test that JobsTab has the correct widgets."""
        # Verify the widgets are correct by checking the source code
        from inspect import getsource

        source = getsource(JobsTab.compose)

        # Check for Sidebar
        assert 'Sidebar(id="sidebar")' in source, "Sidebar not found in JobsTab.compose"

        # Check for VerticalScroll
        assert 'VerticalScroll(id="main-content")' in source, "VerticalScroll not found in JobsTab.compose"

        # Check for Markdown
        assert 'Markdown(id="jobs-markdown")' in source, "Markdown not found in JobsTab.compose"

    @patch("ezbatch.interactive.manager.list_jobs")
    def test_select_changed(self, mock_list_jobs):
        """Test that select_changed updates the markdown content."""
        # Setup mocks
        mock_df = MagicMock(spec=pd.DataFrame)
        mock_df.to_markdown.return_value = "# Jobs\n\n| Job | Status |\n|-----|--------|\n| job1 | RUNNING |"
        mock_list_jobs.return_value = mock_df

        mock_markdown = MagicMock()
        mock_query = MagicMock()
        mock_query.query_one.return_value = mock_markdown

        # Create event
        event = MagicMock()
        event.value = "RUNNING"

        # Create jobs tab with mocked query
        jobs_tab = JobsTab(title="Jobs")
        jobs_tab.query_one = mock_query.query_one

        # Call select_changed
        jobs_tab.select_changed(event)

        # Verify
        mock_list_jobs.assert_called_once_with("DefaultFargateQueue", "RUNNING")
        mock_df.to_markdown.assert_called_once_with(index=False)
        mock_query.query_one.assert_called_once_with("#jobs-markdown")
        mock_markdown.update.assert_called_once_with(mock_df.to_markdown.return_value)


class TestEZBatchManager:
    def test_app_initialization(self):
        """Test that EZBatchManager initializes with the correct theme."""
        app = EZBatchManager()
        assert app.theme == "textual-dark"

    def test_app_widgets(self):
        """Test that EZBatchManager has the correct widgets."""
        # Verify the widgets are correct by checking the source code
        from inspect import getsource

        source = getsource(EZBatchManager.compose)

        # Check for Header
        assert "Header()" in source, "Header not found in EZBatchManager.compose"

        # Check for Footer
        assert "Footer()" in source, "Footer not found in EZBatchManager.compose"

        # Check for TabbedContent
        assert 'TabbedContent(id="tabs")' in source, "TabbedContent not found in EZBatchManager.compose"

        # Check for JobsTab
        assert 'JobsTab(title="Jobs")' in source, "JobsTab not found in EZBatchManager.compose"
