# filebundler/managers/ProjectSettingsManager.py
import logging

from pathlib import Path

from filebundler.utils import json_dump, read_file
from filebundler.models.ProjectSettings import ProjectSettings

logger = logging.getLogger(__name__)


class ProjectSettingsManager:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.project_settings = ProjectSettings()
        self.filebundler_dir = self.project_path / ".filebundler"
        self.filebundler_dir.mkdir(exist_ok=True)
        self.settings_file = self.filebundler_dir / "settings.json"
        self.load_project_settings()

    def load_project_settings(self):
        # initialize ignore patterns based on .gitignore file
        if not self.settings_file.exists():
            project_gitignore_path = self.project_path / ".gitignore"
            try:
                if project_gitignore_path:
                    gitignore_content = read_file(project_gitignore_path)
                    if gitignore_content:
                        # Extract ignore patterns from the .gitignore file
                        ignore_patterns = [
                            line.strip()
                            for line in gitignore_content.splitlines()
                            if line.strip()
                        ]
                        self.project_settings.ignore_patterns.extend(ignore_patterns)
                        self.project_settings.ignore_patterns = list(
                            set(self.project_settings.ignore_patterns)
                        )
            except Exception as e:
                logger.warning(
                    f"Error reading .gitignore file: {str(e)}. Using default ignore patterns."
                )
            self.save_project_settings()
            return self.project_settings

        try:
            json_text = read_file(self.settings_file)
            self.project_settings = ProjectSettings.model_validate_json(json_text)
        except Exception as e:
            logger.error(
                f"Error loading project settings from {self.settings_file}: {str(e)}"
            )

    def save_project_settings(self):
        try:
            with open(self.settings_file, "w") as f:
                json_dump(self.project_settings.model_dump(), f)
            logger.info(f"Project settings saved to {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving project settings: {str(e)}")
            return False
