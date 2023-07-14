import json
import os

REDOWNLOAD = False

def processCmsDriver(command):
  command = command.replace(" || exit $? ;", "")
  command = command.replace("--no_exec", "")

  if "GEN,LHE" in command:
    #command = command.replace("Configuration", "${CMSSW_BASE}/src/Configuration")
    command += ' --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})"'
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

  for url in setup_urls[era]:
    name = url.split("/")[-1]
    if (not os.path.exists(name)) or REDOWNLOAD:
      os.system(f"wget -O {name} {url} --no-check-certificate")

    with open(name, "r") as f:
      setup = f.read()

    stage_config = {}
    for line in setup.split("\n"):
      if "cmsDriver" in line:
        stage_config["cmsDriver"] = processCmsDriver(line)
      elif "scram p" in line:
        stage_config["CMSSW_version"] = "CMSSW" + line.split("CMSSW")[-1]

      stage_config["extra_commands"] = setup.split("eval `scram runtime -sh`")[1].split("scram b")[0]
      stage_config["stage_name"] = name

    config[era].append(stage_config)

os.chdir(config_dir)
with open("config.json", "w") as f:
  json.dump(config, f)

  