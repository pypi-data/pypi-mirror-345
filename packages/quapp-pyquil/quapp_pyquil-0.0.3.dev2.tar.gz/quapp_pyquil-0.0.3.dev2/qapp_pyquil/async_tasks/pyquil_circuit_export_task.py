"""
    QApp Platform Project pennylane_circuit_export_task.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
# from ..quapp_common.config.logging_config import logger
# from pyquil.latex import to_latex
# import os
# import subprocess


class PyquilCircuitExportTask(CircuitExportTask):
        
    def _convert(self):
        
        # circuit = self.circuit_data_holder.circuit

        # latex_code = to_latex(circuit)

        # latex_filename = "quantikz.tex"
        # pdf_filename = "quantikz.pdf"
        # svg_filename = "quantikz.svg"

        
        # try:

        #     with open(latex_filename, "w") as latex_file:
        #         latex_file.write(latex_code)

        #     subprocess.run(["pdflatex", latex_filename], check=True)
        #     subprocess.run(["pdf2svg", pdf_filename, svg_filename], check=True)

        #     with open(svg_filename, "rb") as svg_file:
        #         svg_bytes = svg_file.read()

        # except subprocess.CalledProcessError:
        #     logger.error('[PyquilCircuitExportTask] Fail to convert to svg')
        #     return None
        
        # finally:
            
        #     logger.info('[PyquilCircuitExportTask] Cleaning up temporary files')

        #     files_to_cleanup = [
        #         "quantikz.tex",    # LaTeX source file
        #         "quantikz.pdf",    # Generated PDF file
        #         "quantikz.svg",    # Generated SVG file
        #         "quantikz.aux",    # Auxiliary file created during LaTeX compilation
        #         "quantikz.log",    # Log file created during LaTeX compilation
        #     ]
        #     # Clean up each file if it exists
        #     for file in files_to_cleanup:
        #         try:
        #             os.remove(file)
        #             logger.info(f'[PyquilCircuitExportTask] Successfully removed: {file}')
        #         except FileNotFoundError:
        #             logger.error(f'[PyquilCircuitExportTask] File not found: {file}')

        

        # return svg_bytes

        return None