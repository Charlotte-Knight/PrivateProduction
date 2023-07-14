import json
import os

REDOWNLOAD = False

def processCmsDriver(command, filein=None, fileout=None):
  command = command.replace(" || exit $? ;", "")
  command = command.replace("--no_exec", "")

  if filein is not None:
    assert "--filein" in command
    filename = command.split("--filein ")[1].split(" ")[0]
    filein_part = "--filein "+filename

    command = command.replace(filein_part, " ")
    command += f" --filein {filein}"

  if fileout is not None:
    assert "--fileout" in command
    filename = command.split("--fileout ")[1].split(" ")[0]
    fileout_part = "--fileout "+filename

    command = command.replace(fileout_part, " ")
    command += f" --fileout {fileout}"

  if "GEN,LHE" in command:
    command += ' --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})"'

  if "NANO" in command:
    command = command.replace("NANOEDMAODSIM", "NANOAODSIM")
  return command

with open("setup_urls.json", "r") as f:
  setup_urls = json.load(f)

config_dir = os.path.join(os.getcwd(), "config")
os.makedirs(config_dir, exist_ok=True)

config = {}

for era in setup_urls.keys():
  era_dir = os.path.join(config_dir, era)
  os.makedirs(era_dir, exist_ok=True)
  os.chdir(era_dir)

  config[era] = []

  for stage_i, url in enumerate(setup_urls[era]):
    name = url.split("/")[-1]
    if (not os.path.exists(name)) or REDOWNLOAD:
      os.system(f"wget -O {name} {url} --no-check-certificate")

    with open(name, "r") as f:
      setup = f.read()

    stage_config = {}
    stage_config["extra_commands"] = setup.split("eval `scram runtime -sh`")[1].split("scram b")[0]
    stage_config["stage_name"] = name

    if stage_i != 0:
      filein = "file:"+config[era][-1]["stage_name"]+".root"
    else:
      filein = None
    fileout = "file:"+name+".root"

    for line in setup.split("\n"):
      if "cmsDriver.py" in line:
        stage_config["cmsDriver"] = processCmsDriver(line, filein, fileout)
      elif "scram p" in line:
        stage_config["CMSSW_version"] = "CMSSW" + line.split("CMSSW")[-1]

      

    config[era].append(stage_config)

os.chdir(config_dir)
with open("config.json", "w") as f:
  json.dump(config, f, indent=2)

  