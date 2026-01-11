from collections import defaultdict
from main import S7ner

def normalize_value(val):
    return str(val).strip()

def compute_f1_with_errors(test_cases, verbose=True):
    ner = S7ner()
    
    true_positives = defaultdict(int)
    false_positives = defaultdict(int)
    false_negatives = defaultdict(int)
    
    all_errors = {
        'false_positives': [],
        'false_negatives': [],
        'mismatches': []
    }

    for text, ground_truth in test_cases:
        raw_preds = ner.get_entities(text)
        predictions = set(
            (item[0], normalize_value(item[1])) for item in raw_preds
        )
        references = set(
            (label, normalize_value(value)) for label, value in ground_truth
        )

        fps = predictions - references
        for lbl, val in fps:
            all_errors['false_positives'].append((text, lbl, val))

        fns = references - predictions
        for lbl, val in fns:
            all_errors['false_negatives'].append((text, lbl, val))

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
    total_tp = total_fp = total_fn = 0
    for label in true_positives.keys() | false_positives.keys() | false_negatives.keys():
        tp = true_positives[label]
        fp = false_positives[label]
        fn = false_negatives[label]

        total_tp += tp
        total_fp += fp
        total_fn += fn

        p = tp / (tp + fp) if tp + fp > 0 else 0
        r = tp / (tp + fn) if tp + fn > 0 else 0
        f1 = 2 * p * r / (p + r) if p + r > 0 else 0

        f1_per_label[label] = {'precision': p, 'recall': r, 'f1': f1, 'support': tp + fn}

    micro_p = total_tp / (total_tp + total_fp) if total_tp + total_fp > 0 else 0
    micro_r = total_tp / (total_tp + total_fn) if total_tp + total_fn > 0 else 0
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r) if micro_p + micro_r > 0 else 0

    valid_f1s = [m['f1'] for m in f1_per_label.values() if m['support'] > 0]
    macro_f1 = sum(valid_f1s) / len(valid_f1s) if valid_f1s else 0

    results = {
        'micro_f1': micro_f1,
        'macro_f1': macro_f1,
        'per_label': f1_per_label,
        'errors': all_errors
    }

    if verbose:
        print("\nFALSE POSITIVES:")
        for text, lbl, val in results['errors']['false_positives'][:30]:
            print(f"  [{lbl}] '{val}' in: \"{text}\"")

        print("\nFALSE NEGATIVES:")
        for text, lbl, val in results['errors']['false_negatives'][:30]:
            print(f"  [{lbl}] '{val}' missing in: \"{text}\"")

    return results

if __name__ == "__main__":
    from dataset import data as test_data
    

    results = compute_f1_with_errors(test_data, verbose=True)

    print(f"\nMicro F1: {results['micro_f1']:.4f}")
    print(f"Macro F1: {results['macro_f1']:.4f}")