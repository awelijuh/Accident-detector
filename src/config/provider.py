from pathlib import Path

from omegaconf import OmegaConf

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]

print(ROOT)


# @hydra.main(config_path='.', config_name="config", version_base=None)
def get_conf():
    conf = OmegaConf.load(ROOT / 'config.yaml')
    return conf
