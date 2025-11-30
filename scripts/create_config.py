from thinc.api import Config
import subprocess
import sys

def create_config(lang, pipeline_components, path_to_save):
    
    result = subprocess.run([
        sys.executable, "-m", "spacy", "init", "config",
        f"{path_to_save}",
        "--lang", f"{lang}",
        "--pipeline", f"{pipeline_components}",
        "--optimize", "efficiency"
    ], capture_output=True, text=True)
    

    config = Config().from_disk(f"{path_to_save}")
    
    if "components" not in config:
            config["components"] = {}
            
    
    config.to_disk(path_to_save)
    
    
    if result.returncode == 0:
        print("Config создан успешно")
    else:
        print("Ошибка:", result.stderr)


    
if __name__ == '__main__':
    
    lang = "ru"
    pipeline_components = ["ner"]
    path_to_save  = "./config/config.cfg"
    
    
    create_config(
            lang,
            pipeline_components,
            path_to_save
            )