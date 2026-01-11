from dataset import data
from collections import defaultdict
from main import S7ner

def normalize_entity_value(value):
    if isinstance(value, str):
        return value.strip()
    else:
        return str(value)

def compute_f1_scores(test_cases):
    ner = S7ner()
    
    true_positives = defaultdict(int)
    false_positives = defaultdict(int)
    false_negatives = defaultdict(int)

    for text, ground_truth in test_cases:
        predictions_raw = ner.get_entities(text)
        predictions = set(
            (item[0], normalize_entity_value(item[1])) for item in predictions_raw
        )
        references = set(
            (label, normalize_entity_value(value)) for label, value in ground_truth
        )

        all_labels = set([lbl for lbl, _ in predictions | references])

        for label in all_labels:
            pred_vals = {val for (lbl, val) in predictions if lbl == label}
            ref_vals = {val for (lbl, val) in references if lbl == label}

            tp = len(pred_vals & ref_vals)
            fp = len(pred_vals - ref_vals)
            fn = len(ref_vals - pred_vals)

            true_positives[label] += tp
            false_positives[label] += fp
            false_negatives[label] += fn

    f1_per_label = {}
    total_tp, total_fp, total_fn = 0, 0, 0

    for label in true_positives.keys() | false_positives.keys() | false_negatives.keys():
        tp = true_positives[label]
        fp = false_positives[label]
        fn = false_negatives[label]

        total_tp += tp
        total_fp += fp
        total_fn += fn

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        f1_per_label[label] = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'support': tp + fn
        }

    micro_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

    valid_f1s = [metrics['f1'] for metrics in f1_per_label.values() if metrics['support'] > 0]
    macro_f1 = sum(valid_f1s) / len(valid_f1s) if valid_f1s else 0.0

    return {
        'micro_f1': micro_f1,
        'macro_f1': macro_f1,
        'per_label': f1_per_label,
        'totals': {
            'true_positives': total_tp,
            'false_positives': total_fp,
            'false_negatives': total_fn
        }
    }

if __name__ == "__main__":
    test_data = data
    
    results = compute_f1_scores(test_data)
    print(f"Micro F1: {results['micro_f1']:.4f}")
    print(f"Macro F1: {results['macro_f1']:.4f}")
    print("="*50)
    for label, metrics in results['per_label'].items():
        print(f"{label}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1']:.3f}")