
from . import register_extractor
import shutil
import tempfile
import subprocess
def xtxt_doc(file_buffer):
        if shutil.which("antiword") is None:
            print("⚠️ 'antiword' is not installed or is not in the system PATH.")
            return None
        try:
            file_buffer.seek(0)
            data = file_buffer.read()
            with tempfile.NamedTemporaryFile(suffix=".doc") as temp_file:
                temp_file.write(data)
                temp_file.flush()
                temp_path = temp_file.name
            result = subprocess.run(["antiword", temp_path],capture_output=True,text=True)
            if result.returncode != 0:
                print(f"⚠️ antiword failed: {result.stderr}")
                return None
            return result.stdout.strip()
        except Exception as e:
            print(f"⚠️ Error during extraction from DOC: {e}")
            return None

register_extractor("application/msword",xtxt_doc,name="DOC")
