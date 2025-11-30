import json
import pandas as pd
import matplotlib.pyplot as plt

def read_spacy_jsonl_logs(jsonl_file_path):
    
    training_data = []
    evaluation_data = []
    
    with open(jsonl_file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            entry = json.loads(line)
            
            if 'losses' in entry and entry['losses']:
                training_data.append({
                    'step': entry.get('step', 0),
                    'epoch': entry.get('epoch', 0),
                    'loss_ner': entry.get('losses', {}).get('ner', 0),
                    'loss_tok2vec': entry.get('losses', {}).get('tok2vec', 0),
                    'loss_total': sum(entry.get('losses', {}).values()) if entry.get('losses') else 0,
                    'type': 'training'
                })
            
            if "scores" in entry and entry["scores"]:
                evaluation_data.append({
                    'step': entry.get('step', 0),
                    'epoch': entry.get('epoch', 0),
                    'ents_f': entry.get('scores', {}).get('ents_f', 0),
                    'ents_p': entry.get('scores', {}).get('ents_p', 0),
                    'ents_r': entry.get('scores', {}).get('ents_r', 0),
                    'score': entry.get('scores', {}).get('speed', 0),
                    'type': 'evaluation'
                })
                        
    return training_data, evaluation_data

def visualize_from_jsonl(jsonl_file_path):
    training_data, evaluation_data = read_spacy_jsonl_logs(jsonl_file_path)
    
    df_train = pd.DataFrame(training_data) if training_data else pd.DataFrame()
    df_eval = pd.DataFrame(evaluation_data) if evaluation_data else pd.DataFrame()
    
    create_training_plots(df_train, df_eval)
    
    return df_train, df_eval

def create_training_plots(df_train, df_eval):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Анализ истории тренировки модели', fontsize=16, fontweight='bold')
    
    if not df_train.empty:
        axes[0, 0].plot(df_train['step'], df_train['loss_ner'], 'b-', alpha=0.7, label='NER Loss')
        if 'loss_tok2vec' in df_train.columns:
            axes[0, 0].plot(df_train['step'], df_train['loss_tok2vec'], 'r-', alpha=0.7, label='Tok2Vec Loss')
        axes[0, 0].set_title('Training Loss')
        axes[0, 0].set_xlabel('Step')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    if not df_eval.empty:
        axes[0, 1].plot(df_eval['epoch'], df_eval['ents_f'], 'g-', marker='o', label='F1 Score')
        axes[0, 1].set_title('F1 Score Development')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('F1 Score')
        axes[0, 1].grid(True, alpha=0.3)
    
    if not df_eval.empty:
        axes[1, 0].plot(df_eval['epoch'], df_eval['ents_p'], 'b-', marker='s', label='Precision')
        axes[1, 0].plot(df_eval['epoch'], df_eval['ents_r'], 'r-', marker='^', label='Recall')
        axes[1, 0].plot(df_eval['epoch'], df_eval['ents_f'], 'g-', marker='o', label='F1')
        axes[1, 0].set_title('Precision, Recall & F1 Score')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    if not df_train.empty and not df_eval.empty:
        ax_twin = axes[1, 1].twinx()
        
        axes[1, 1].plot(df_train['step'], df_train['loss_ner'], 'b-', alpha=0.5, label='Loss')
        axes[1, 1].set_xlabel('Step')
        axes[1, 1].set_ylabel('Loss', color='b')
        axes[1, 1].tick_params(axis='y', labelcolor='b')
        
        max_step = df_train['step'].max()
        eval_steps = [max_step * (i + 1) / len(df_eval) for i in range(len(df_eval))]
        ax_twin.plot(eval_steps, df_eval['ents_f'], 'g-', marker='o', label='F1 Score')
        ax_twin.set_ylabel('F1 Score', color='g')
        ax_twin.tick_params(axis='y', labelcolor='g')
        
        axes[1, 1].set_title('Loss vs F1 Score')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    plt.savefig('../history/training_history_analysis.png', dpi=300, bbox_inches='tight')
    print("График сохранен как 'training_history_analysis.png'")