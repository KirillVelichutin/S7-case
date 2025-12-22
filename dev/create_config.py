from pathlib import Path
from thinc.api import Config
import subprocess

def create_config(lang, pipeline, transformer, path_to_save, gpu):
    
    cmd = [
        "python", "-m", "spacy", "init", "config", path_to_save, "-F",
        "--lang", lang,
        "--pipeline", pipeline,
        "--optimize", "efficiency",
    ]
    
    
    if gpu:
        cmd += ["--gpu"]
        
        
    subprocess.run(cmd)
    
    
    if "transformer" in pipeline:
        print("Transformer added")
        config = Config().from_disk(path_to_save)
        config["components"]["transformer"]["model"]["name"] = transformer
        config.to_disk(path_to_save)


    
if __name__ == '__main__':
    
    lang = "ru"
    pipeline = '["transformer","spancat"]'
    transformer = "../transformers/models/rubert-tiny2"
    path_to_save  = "../models/config.cfg"
    gpu = True
    
    
    create_config(
            lang,
            pipeline,
            transformer,
            path_to_save,
            gpu
            )