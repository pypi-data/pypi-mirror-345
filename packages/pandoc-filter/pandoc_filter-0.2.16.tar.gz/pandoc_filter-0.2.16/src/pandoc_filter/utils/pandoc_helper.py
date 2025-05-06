import subprocess
from packaging import version

def get_pandoc_version()->str:
    try:
        output = subprocess.check_output(['pandoc', '--version'], stderr=subprocess.STDOUT, text=True)
        lines = output.splitlines()
        for line in lines:
            if line.startswith("pandoc "):
                version_str = line.split()[1]
                return version_str
    except subprocess.CalledProcessError as e:
        return None

def check_pandoc_version(required_version:str):
    current_version = version.parse(get_pandoc_version())
    required_version = version.parse(required_version)
    if current_version >= required_version:
        return None
    else:
        raise Exception(f"pandoc version {required_version} or higher is required, but you have {current_version}.")