import subprocess
import sys
from spacy.tokens import DocBin
from thinc.api import Config
import spacy

from visualizer import visualize_from_jsonl
from parse import prepare_data


def training(config_path, output_dir, train_path, dev_path, model):
    config = Config().from_disk(config_path)
    doc_bin = DocBin().from_disk(train_path)
    
    
    nlp = spacy.blank("ru")
    
    if model == "null":
        print("new model created")
    else:
        nlp = spacy.load(f"{model}")
        config["initialize"]["init_tok2vec"] = model
        print(f"loaded: {model}")


    docs = list(doc_bin.get_docs(nlp.vocab))
    n_examples = len(docs)
    print(n_examples)
    
    if n_examples < 1000:
        batch_size = 16
        max_epochs = 100
        eval_freq = 50
    elif n_examples < 10000:
        batch_size = 32
        max_epochs = 50
        eval_freq = 10
    else:
        batch_size = 128
        max_epochs = 20
        eval_freq = 10
        
        
    config["paths"]["train"] = train_path
    config["paths"]["dev"] = dev_path
    config["corpora"]["dev"]["path"] = "${paths.dev}"
    config["corpora"]["train"]["path"] = "${paths.dev}"
            
    config["nlp"]["batch_size"] = batch_size
    config["training"]["max_epochs"] = max_epochs
    config["training"]["dropout"] = 0.2
    config["training"]["optimizer"]["learn_rate"] = 0.002
    config["training"]["max_steps"] = 20000
    config["training"]["eval_frequency"] = eval_freq
    
    config["training"]["logger"]["@loggers"] = "spacy.ConsoleLogger.v3"
    config["training"]["logger"]["progress_bar"] = "eval"
    config["training"]["logger"]["console_output"] = "true"
    config["training"]["logger"]["output_file"] = "../analysis/training_history/training_history.jsonl"
    

    config.to_disk(config_path)
    print("Config updated")
    
    cmd = [
        sys.executable, "-m", "spacy", "train",
        config_path,
        "--output", output_dir,
        "--paths.train", train_path,
        "--paths.dev", dev_path,
        "--training.max_epochs", f"{max_epochs}",
    ]
        
    
    result = subprocess.run(cmd, capture_output=True, text=True)
        
    print(result.stdout)



if __name__ == '__main__':
    config_path = "../models/config.cfg"
    output_dir = "../models"
    train_path = "../data/spacy_format/train.spacy"
    dev_path = "../data/spacy_format/dev.spacy"
    
    prepare_data("../data/initial_data/composit2.json")
    
    model = "null"
    
    training(
            config_path,
            output_dir,
            train_path,
            dev_path,
            model
            )
    
    visualize_from_jsonl("../analysis/training_history/training_history.jsonl")