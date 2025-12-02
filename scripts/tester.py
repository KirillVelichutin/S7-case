import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from typing import List, Tuple, Dict, Any
from collections import defaultdict

from reader import read_data
from spacy.training import offsets_to_biluo_tags
from visualizer import create_confusion_matrix
from visualizer import entity_error_ratio



def evaluate_ner_model(model_path, test_data):
    nlp = spacy.load(model_path)
    
    scorer = Scorer()
    
    examples = []
    for text, annotations in test_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        example.predicted = nlp(example.reference.text)
        examples.append(example)
    
    scores = scorer.score(examples)
    
    print( 
            f"=== Метрики модели ===", 
            f"Точность (Precision): {scores['ents_p']:.3f}",
            f"Полнота (Recall): {scores['ents_r']:.3f}",
            f"F-мера (F1-score): {scores['ents_f']:.3f}",
            sep = '\n'            
        )
    
    print("\n=== Метрики по сущностям ===")
    for entity_type, metrics in scores['ents_per_type'].items():
        print(f"{entity_type}: P={metrics['p']:.3f}, R={metrics['r']:.3f}, F1={metrics['f']:.3f}")
    
    return scores


def analyze_boundary_errors(
    model_path,
    test_data: List[Tuple[str, Dict[str, List[Tuple[int, int, str]]]]],
    context_window: int = 2,
    verbose: bool = True
) -> Dict[str, Any]:
    
    nlp = spacy.load(model_path)
    
    boundary_errors = []
    total_boundary_tokens = 0
    error_counts = defaultdict(int)
    
    for doc_id, (text, annot) in enumerate(test_data):
        doc = nlp.make_doc(text)
        
        true_bilou = offsets_to_biluo_tags(doc, annot["entities"])
        pred_doc = nlp(text)
        pred_ents = [(ent.start_char, ent.end_char, ent.label_) for ent in pred_doc.ents]
        pred_bilou = offsets_to_biluo_tags(doc, pred_ents)
        
        true_bilou = [tag if tag != "-" else "O" for tag in true_bilou]
        pred_bilou = [tag if tag != "-" else "O" for tag in pred_bilou]
        
        tokens = [token.text for token in doc]
        
        for i, (true_tag, pred_tag) in enumerate(zip(true_bilou, pred_bilou)):
            if true_tag.startswith(("B-", "L-", "U-")):
                total_boundary_tokens += 1
                
                if true_tag != pred_tag:
                    start_ctx = max(0, i - context_window)
                    end_ctx = min(len(tokens), i + context_window + 1)
                    context = " ".join(tokens[start_ctx:end_ctx])
                    current_token = tokens[i]
                    
                    error_type = f"{true_tag} → {pred_tag}"
                    error_counts[error_type] += 1
                    
                    boundary_errors.append({
                        "doc_id": doc_id,
                        "token_index": i,
                        "true_tag": true_tag,
                        "pred_tag": pred_tag,
                        "token": current_token,
                        "context": context,
                        "error_type": error_type
                    })
    
    sorted_errors = sorted(error_counts.items(), key=lambda x: -x[1])
    
    if verbose:
        print(
            "\n=== Boundary Error Analysis ===",
            f"Всего граничных токенов: {total_boundary_tokens}",
            f"Ошибок на границах: {len(boundary_errors)}",
            f"Точность на границах: {1 - len(boundary_errors)/total_boundary_tokens:.2%}",
            sep='\n'
            )
        
        print("Топ-10 типов ошибок на границах:")
        for err_type, count in sorted_errors[:10]:
            print(f"  {count:3d}× {err_type}")
        
        print("\nПримеры ошибок:")
        for err in boundary_errors[:5]:
            print(f"  [{err['true_tag']} → {err['pred_tag']}] '{err['token']}' | контекст: ...{err['context']}...")
    
    return {
        "total_boundary_tokens": total_boundary_tokens,
        "boundary_errors": boundary_errors,
        "error_counts": dict(error_counts),
        "boundary_accuracy": 1 - len(boundary_errors) / total_boundary_tokens if total_boundary_tokens > 0 else 1.0
    }


if __name__ == "__main__":
    model_path = "../models/model-best"
    data_path = "../data/json_format/processed_data.json"
    
    TEST_DATA = read_data(data_path)

    evaluate_ner_model(model_path, TEST_DATA)

    # results = analyze_boundary_errors(model_path, TEST_DATA, context_window=3)
    # print(results)

    create_confusion_matrix(model_path, TEST_DATA)