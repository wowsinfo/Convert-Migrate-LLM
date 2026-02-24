from ..transpiler import Transpiler
import os

class ProjectMigration:
    def __init__(
        self,
        src_folder: str,
        src_formats: tuple,
        output_format: str,
        output_folder: str,
    ):
        self.src_folder = src_folder
        self.src_formats = src_formats
        self.output_format = output_format
        self.output_folder = output_folder

    def migrate(self, transpiler: Transpiler):
        for root, _, files in os.walk(self.src_folder):
            for file in files:
                if not file.endswith(self.src_formats):
                    continue
                src_file = os.path.join(root, file)
                print(f"Processing {src_file}")
                output = transpiler.convert_file(src_file)
                print("Writing result...")
                output_file = (
                    os.path.join(
                        self.output_folder, os.path.relpath(src_file, self.src_folder)
                    )
                    + self.output_format
                )
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as out_file:
                    out_file.write(output)
