import subprocess
import base64
import json
import os
import sys
import shutil
from io import BytesIO

class RenderedReport:
    def __init__(self, data: bytes):
        self._data = data
    
    def to_base64(self) -> str:
        return self._data.decode("utf-8")

    def to_stream(self) -> BytesIO:
        return BytesIO(self.to_bytes())

    def to_bytes(self) -> bytes:
        return base64.b64decode(self._data)

    def save(self, path: str) -> None:
        with open(path, "wb") as f:
            f.write(self.to_bytes())

def render_report(path, params, timeout=120) -> RenderedReport:
    """
    Generates a report in RDL/RDLC format using the specified parameters.

    For full documentation, usage examples, and advanced options, visit:
    🔗 https://github.com/mobster-dev/templates/pyrdlgen.html

    Args:
        path (str): Path to the RDL file.
        params (dict): Dictionary with connection string, parameters, and data sources.
            - ConnectionString (str): The connection string to the database.
            - RdlParameters (dict): A dictionary of parameters for the report.
            - DataSources (dict): A dictionary of data sources (sql procedures with parameters or dataframes (to_dict orient = records) from pandas)
            - Format: The format of the report (e.g., pdf, excel, html).
        timeout (int, optional): Timeout in seconds. Defaults to 120.

    Returns:
        RenderedReport: Callable object that returns bytes of the report.
        Provides helper methods like `.to_stream()`, `.to_base64()`, and `.save()`.

    Created by MobsterDev.
    """
    
    exe_path = os.path.join(os.path.dirname(__file__), 'bin', 'rdl-processor.exe')

    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"Executable not found: {exe_path}")
    
    required_keys = ["RdlParameters", "DataSources", "Format"]
    missing = [key for key in required_keys if key not in params]
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")

    if isinstance(params["DataSources"], dict):
        for key, value in params["DataSources"].items():
            if isinstance(value, list):
                params["DataFrames"] = params.pop("DataSources")
                params["ConnectionString"] = "None"
                break
            elif isinstance(value, dict) and "ConnectionString" not in params:
                raise ValueError("Missing required parameter: ConnectionString for DataSources from sql procedure")
            
    params["ReportFile"] = path
            
    if sys.platform == "win32":
        cmd = [exe_path]
    else:
        if shutil.which("wine") is None:
            raise EnvironmentError(
                "Wine is required to run the RDL processor on non-Windows systems, "
                "but it was not found in the system PATH. "
                "Please install Wine or ensure it's properly configured."
                "see https://wiki.winehq.org/Download for installation instructions."
            )
        cmd = ["wine", exe_path]

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = proc.communicate(
            input=json.dumps(params).encode("utf-8"),
            timeout=timeout
        )

        if proc.returncode != 0:
            error_message = stderr.decode(errors="replace").strip()
            raise RuntimeError(
                f"Failed to generate report. Exit code: {proc.returncode}. Error: {error_message}"
            )

        return RenderedReport(stdout)

    except subprocess.TimeoutExpired:
        proc.kill()
        raise TimeoutError("The report generation process timed out.")

    except FileNotFoundError as e:
        raise EnvironmentError(f"Failed to execute the process: {e}")
