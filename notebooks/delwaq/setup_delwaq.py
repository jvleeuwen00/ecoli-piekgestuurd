# %%
# import libraries

import pandas as pd

import subprocess
from pathlib import Path

from ribasim import Model
from ribasim.delwaq import generate, parse
from ribasim.delwaq import plot_fraction

# numba not installed warning, might cause slowness

# %%
ROOT = Path(__file__).resolve().parents[4]
model_name = "maasgebied_coupled"
toml_name = "maasgebied_coupled.toml"
model_path = (
    ROOT /
    "repositories/Ribasim-NL/data/Rijkswaterstaat/modellen/" / 
    model_name
)
toml_path = model_path / toml_name
assert toml_path.is_file()

output_folder = "delwaq"
output_path = model_path / output_folder

# %%
model_maas = Model.read(toml_path)

#%%

# specify nodes to add tracer to
node_ids = [8007826]

restim_loads = pd.DataFrame(
    [
        {
            "node_id": node_id,
            "time": model_maas.starttime,
            "substance": substance,
            "load": 1,
        }
        for i, node_id in enumerate(node_ids, start=1)
        for substance in (f"cTR{i}", f"dTR{i}")
    ]
)

model_maas.basin.mass_load = restim_loads
model_maas.write(toml_path) # fails right now, maybe just because I have files open?
model_maas.basin.concentration
#%%
# generate delwaq input

# graph, substances = generate(toml_path, output_path)

# %%
delwaq_inp = output_path / "delwaq.inp"
text = delwaq_inp.read_text()

old = """1 ; number of parameters listed
'Volume'"""

new = """8 ; number of parameters listed
'Volume'
'FlowSeg'
'AgeTR1'
'AgeTR2'
'AgeTR3'
'AgeTR4'
'AgeTR5'
'ResTim'"""

if old not in text:
    raise ValueError("Parameter block not found")

text = text.replace(old, new)

old = """CONSTANTS  'ONLY_ACTIVE' 	DATA	0               ; Only active processes

;INCLUDE 'includes_deltashell/B7_processes.inc'      ; From UI: Processes
;INCLUDE 'includes_deltashell/B7_constants.inc'      ; From UI: Constants"""

new = """CONSTANTS  'ONLY_ACTIVE' 	DATA	1               ; Only active processes

INCLUDE 'include_extra/B7_processes_onesource.inc'
INCLUDE 'include_extra/B7_constants_onesource.inc'"""

if old not in text:
    raise ValueError("ONLY_ACTIVE block not found")

text = text.replace(old, new)

delwaq_inp.write_text(text)
#%%

dimr_path = "c:/Program Files/Deltares/D-HYDRO Suite 2025.02 1D2D/plugins/DeltaShell.Dimr/kernels/x64/bin/run_dimr.bat"
dimr_config_path = "dimr_config.xml"  # had output path before it earlier but now we specify in subprocess

# %%
# run delwaq and stream output

cmd = f'"{dimr_path}" "{dimr_config_path}"'

proc = subprocess.Popen(
    cmd,
    cwd=output_path,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    shell=True,  # still required for .bat
)

with proc:
    for line in proc.stdout:
        print(line, end="")

returncode = proc.wait()

if returncode != 0:
    raise subprocess.CalledProcessError(returncode, cmd)


#%%
# currently generate takes a wrong version of the mass_load table, and since model.write does not allow me to overwrite (anymore), there is no way to re-run this whole script
# because of this, manually remove ctr2 and add dtr1 from substances variable

# substances.remove("cTR2")
# substances.add("dTR1")
# %%





