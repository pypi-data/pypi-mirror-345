import os
from typing import List
from testgen.models.test_case import TestCase
from testgen.service.logging_service import get_logger
from testgen.util.coverage_visualizer import CoverageVisualizer
from testgen.service.analysis_service import AnalysisService


class CFGService:
    """Service for generating and managing Control Flow Graph visualizations."""
    def __init__(self):
        self.analysis_service = AnalysisService()
        self.visualizer = None
        self.logger = get_logger()

    def initialize_visualizer(self, service):
        self.visualizer = CoverageVisualizer()
        self.visualizer.set_service(service)

    @staticmethod
    def create_visualization_directory() -> str:
        """Create visualization directory if it doesn't exist."""
        visualization_dir = os.path.join(os.getcwd(), "visualize")
        if not os.path.exists(visualization_dir):
            os.makedirs(visualization_dir)
            print(f"Created visualization directory: {visualization_dir}")
        return visualization_dir

    @staticmethod
    def get_versioned_filename(directory: str, base_filename: str) -> str:
        """Generate a versioned filename to avoid overwriting existing files."""
        version = 1
        output_path = os.path.join(directory, f"{base_filename}.png")

        while os.path.exists(output_path):
            output_path = os.path.join(directory, f"{base_filename}_v{version}.png")
            version += 1

        return output_path

    def visualize_test_coverage(self, file_path: str, test_cases: List[TestCase]) -> str | None:
        visualization_dir = self.create_visualization_directory()

        analysis_context = self.analysis_service.create_analysis_context(file_path)

        filename = os.path.basename(file_path).replace('.py', '')

        for func in analysis_context.function_data:
            self.visualizer.get_covered_lines(file_path, analysis_context.class_name, func.func_def, test_cases)

            base_filename = f"{filename}_{func.function_name}_coverage"
            output_filepath = self.get_versioned_filename(visualization_dir, base_filename)

            self.visualizer.generate_colored_cfg(func.function_name, output_filepath)

        print(f"Generated CFG visualizations in {visualization_dir}")
        return visualization_dir