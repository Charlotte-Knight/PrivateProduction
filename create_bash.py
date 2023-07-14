import json
import os
import copy

script_template = """
#!/usr/bin/env bash

set -e
#set -x

SEED=1
EVENTS=10

export X509_USER_PROXY=/home/hep/mdk16/x509up_u958594
source /cvmfs/cms.cern.ch/cmsset_default.sh
source /cvmfs/grid.cern.ch/umd-c7ui-latest/etc/profile.d/setup-c7-ui-example.sh

workdir=${PWD}

"""

stage_template = """
echo "--------------------------------------------------------------------"
echo "Starting %(stage_name)s"
echo "--------------------------------------------------------------------"

if [ -r %(CMSSW_version)s/src ] ; then
  echo release %(CMSSW_version)s already exists
else
  scram p CMSSW %(CMSSW_version)s
fi

cd %(CMSSW_version)s/src
eval `scram runtime -sh`
%(extra_commands)s
scram b
mkdir -p %(outpath)s
cd %(outpath)s
%(cmsDriver)s
cd $workdir

"""

with open("config/config.json", "r") as f:
  config = json.load(f)

os.makedirs("scripts", exist_ok=True)

for era in config.keys():
  script = copy.copy(script_template)

  for stage in config[era]:
    stage["outpath"] = f"/vols/cms/mdk16/ggtt/PrivateProduction/out/{era}"
    script += stage_template % stage

  with open(os.path.join("scripts", f"{era}.sh"), "w") as f:
    f.write(script)
