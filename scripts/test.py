import warnings
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import spacy
from spacy.scorer import Scorer
from seqeval.metrics import classification_report, f1_score
from sklearn.metrics import confusion_matrix
from spacy.training import biluo_to_iob, Example
from spacy.training.iob_utils import offsets_to_biluo_tags

from reader import read_data

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
            "Метрики модели:", 
            f"Точность (Precision): {scores['ents_p']:.3f}",
            f"Полнота (Recall): {scores['ents_r']:.3f}",
            f"F-мера (F1-score): {scores['ents_f']:.3f}",     
            sep = '\n'            
        )
    
    print("\nМетрики по сущностям")
    for entity_type, metrics in scores['ents_per_type'].items():
        print(f"{entity_type}: P={metrics['p']:.3f}, R={metrics['r']:.3f}, F1={metrics['f']:.3f}")
    
    return scores

def evaluate_with_seqeval(model_path, test_data):
    nlp = spacy.load(model_path)
    all_true_tags_bio = []
    all_pred_tags_bio = []

    #   print("\nПодготовка данных для оценки с помощью seqeval (BILUO -> BIO)")
    for text, annotations in test_data:
        doc = nlp(text)
        
        pred_ents = [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
        pred_tags_biluo = offsets_to_biluo_tags(doc, pred_ents)
        
        gold_ents = annotations.get("entities", [])
        true_tags_biluo = offsets_to_biluo_tags(doc, gold_ents)
        
        all_true_tags_bio.append(biluo_to_iob(true_tags_biluo))
        all_pred_tags_bio.append(biluo_to_iob(pred_tags_biluo))
        
    print("\n--- Отчет по метрикам от seqeval (строгая оценка) ---")
    print(classification_report(all_true_tags_bio, all_pred_tags_bio, digits=3))
    
    f1 = f1_score(all_true_tags_bio, all_pred_tags_bio, average="micro")
    print(f"\nMicro F1-score (seqeval): {f1:.3f}")

    return all_true_tags_bio, all_pred_tags_bio

def create_ner_confusion_matrix(model_path, test_data):
    nlp = spacy.load(model_path)
    
    
    true_labels = []
    pred_labels = []
    
    for text, annotations in test_data:
        doc = nlp(text)
        
        true_entities = {(start, end): label for start, end, label in annotations["entities"]}
        
        token_true_labels = []
        token_pred_labels = []
        
        for token in doc:
            true_label = "O"
            for (start, end), label in true_entities.items():
                if start <= token.idx < end:
                    true_label = label
                    break
            
            token_true_labels.append(true_label)
            
            pred_label = "O"
            for ent in doc.ents:
                if ent.start_char <= token.idx < ent.end_char:
                    pred_label = ent.label_
                    break
            
            token_pred_labels.append(pred_label)
        
        true_labels.extend(token_true_labels)
        pred_labels.extend(token_pred_labels)
    
    labels = sorted(set(true_labels) | set(pred_labels))
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels)
    plt.title('Матрица ошибок для NER')
    plt.xlabel('Предсказанные метки')
    plt.ylabel('Истинные метки')
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()
    
    return cm, labels

def create_ner_heatmaps(model_path, test_data): # Показывает результат в токенах
    nlp = spacy.load(model_path)
    true_labels, pred_labels = [], []

    #   print("Шаг 1: Сбор и выравнивание меток...")
    for text, annotations in test_data:
        doc = nlp(text)
        
        token_pred_labels = [token.ent_type_ if token.ent_type_ else "O" for token in doc]
        pred_labels.extend(token_pred_labels)
        
        gold_ents = annotations.get("entities", [])
        true_biluo_tags = offsets_to_biluo_tags(doc, gold_ents)
        token_true_labels = [tag.split('-')[-1] for tag in true_biluo_tags]
        true_labels.extend(token_true_labels)

    all_model_labels = list(nlp.get_pipe("ner").labels) + ["O"]
    labels = sorted(list(set(true_labels) | set(pred_labels) | set(all_model_labels)))
    
    cm = confusion_matrix(true_labels, pred_labels, labels=labels)
    #   print("Сбор данных завершен. Начинаю построение графиков...")

    # 1) ОБЫЧНЫЙ HEATMAP (Сырые значения)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title('Матрица ошибок NER — Абсолютные значения')
    plt.xlabel('Предсказанные метки')
    plt.ylabel('Истинные метки')
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    print("\nПоказываю Heatmap 1/5 (Абсолютные значения)... Закройте окно для продолжения.")
    plt.show()

    # 2) НОРМАЛИЗОВАННЫЙ HEATMAP (Проценты)
    with np.errstate(divide='ignore', invalid='ignore'):
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Purples', xticklabels=labels, yticklabels=labels)
    plt.title('Матрица ошибок NER — Нормализованная (% от истинной метки)')
    plt.xlabel('Предсказанные метки')
    plt.ylabel('Истинные метки')
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    print("Показываю Heatmap 2/5 (Нормализованная)... Закройте окно для продолжения.")
    plt.show()

    # 3) HEATMAP БЕЗ ДИАГОНАЛИ (Только ошибки)
    cm_no_diag = cm.copy()
    np.fill_diagonal(cm_no_diag, 0)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm_no_diag, annot=True, fmt='d', cmap='OrRd', xticklabels=labels, yticklabels=labels)
    plt.title('Матрица ошибок NER — Только ошибки (без диагонали)')
    plt.xlabel('Предсказанные метки')
    plt.ylabel('Истинные метки')
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    print("Показываю Heatmap 3/5 (Только ошибки)... Закройте окно для продолжения.")
    plt.show()

    # 4) ТОП-N ОШИБОК
    top_n = 15
    error_pairs = []
    error_indices = np.argwhere(cm_no_diag > 0)
    for i, j in error_indices:
        error_pairs.append({'true': labels[i], 'pred': labels[j], 'count': cm[i, j]})

    error_pairs.sort(key=lambda x: (-x['count'], x['true'], x['pred']))
    top_pairs = error_pairs[:top_n]

    if top_pairs:
        plt.figure(figsize=(8, len(top_pairs) * 0.5))
        sns.heatmap(
            np.array([[p['count'] for p in top_pairs]]).T, 
            annot=True, fmt='d', cmap='Reds',
            yticklabels=[f"{p['true']} → {p['pred']}" for p in top_pairs],
            xticklabels=["Количество ошибок"]
        )
        plt.title(f"Топ-{top_n} самых частых ошибок NER")
        plt.tight_layout()
        print(f"Показываю Heatmap 4/5 (Топ-{top_n} ошибок)... Закройте окно для продолжения.")
        plt.show()

    # 5) HEATMAP ПО СЕМЕЙСТВАМ СУЩНОСТЕЙ
    families = {
        "PERSONAL_DATA": {'NAME', 'DOB'},
        "CONTACT_INFO": {'PHONE', 'EMAIL'},
        "DOCUMENT": {'PASSPORT', 'INTERNATIONAL_PASSPORT', 'BIRTH_CERTIFICATE', 'VISA'},
        "TRAVEL_ID": {'TICKET_NUMBER', 'BOOKING_REF', 'BOARDING_PASS', 'EMD_NUMBER', 'ORDER_NUMBER', 'FFP_NUMBER'},
        "LOCATION": {'AIRPORT', 'CITY', 'COUNTRY'},
        "FLIGHT_DETAILS": {'FLIGHT', 'TIME', 'DATE'},
        "OUTSIDE": {"O"},
        "UNGROUPED": set() 
        }
    
    label_to_family = {}
    all_family_labels = set()
    for fname, members in families.items():
        for label in members:
            label_to_family[label] = fname
            all_family_labels.add(label)

    for label in labels:
        if label not in all_family_labels:
            label_to_family[label] = "UNGROUPED"
            warnings.warn(f"Метка '{label}' не найдена ни в одной семье и отнесена к 'UNGROUPED'.")
    
    fam_names = list(families.keys())
    if not any(v == "UNGROUPED" for v in label_to_family.values()):
        fam_names.remove("UNGROUPED")

    fam_cm = np.zeros((len(fam_names), len(fam_names)), dtype=int)
    family_index = {f: i for i, f in enumerate(fam_names)}

    for i, j in np.argwhere(cm > 0):
        t_label, p_label = labels[i], labels[j]
        
        fam_i_name = label_to_family.get(t_label, "UNGROUPED")
        fam_j_name = label_to_family.get(p_label, "UNGROUPED")
        
        if fam_i_name in family_index and fam_j_name in family_index:
            fam_i = family_index[fam_i_name]
            fam_j = family_index[fam_j_name]
            fam_cm[fam_i, fam_j] += cm[i, j]

    plt.figure(figsize=(10, 8))
    sns.heatmap(fam_cm, annot=True, fmt='d', cmap='Greens', xticklabels=fam_names, yticklabels=fam_names)
    plt.title("Матрица ошибок между семействами сущностей")
    plt.xlabel("Предсказанная семья")
    plt.ylabel("Истинная семья")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    print("Показываю Heatmap 5/5 (По семействам)... Закройте окно для завершения.")
    plt.show()

    return cm, labels

def analyze_common_errors(model_path, test_data, top_n=15): # Cчитает на уровне сущностей, спанов, показывает: Пропуски (FN), Ложные срабатывания (FP), Неверная классификация (True Span, Wrong Label)
    nlp = spacy.load(model_path)
    errors = Counter()
    error_examples = {}

    print("\nСбор и анализ ошибок модели...")
    for text, annotations in test_data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        pred_doc = nlp(example.reference.text)

        true_spans = { (ent.start_char, ent.end_char): ent.label_ for ent in example.reference.ents }
        pred_spans = { (ent.start_char, ent.end_char): ent.label_ for ent in pred_doc.ents }

        common_spans = true_spans.keys() & pred_spans.keys()
        for span in common_spans:
            if true_spans[span] != pred_spans[span]:
                true_label = true_spans[span]
                pred_label = pred_spans[span]
                error_key = (f"Классификация", f"{true_label} → {pred_label}")
                errors[error_key] += 1
                
                start, end = span
                if error_key not in error_examples:
                    error_examples[error_key] = f"...{text[max(0, start-20):end+20]}... ('{text[start:end]}')"

        fn_spans = true_spans.keys() - pred_spans.keys()
        for span in fn_spans:
            label = true_spans[span]
            error_key = (f"Пропуск", label)
            errors[error_key] += 1
            
            start, end = span
            if error_key not in error_examples:
                error_examples[error_key] = f"...{text[max(0, start-20):end+20]}... ('{text[start:end]}')"

        fp_spans = pred_spans.keys() - true_spans.keys()
        for span in fp_spans:
            label = pred_spans[span]
            error_key = (f"Ложное срабатывание", label)
            errors[error_key] += 1
            
            start, end = span
            if error_key not in error_examples:
                error_examples[error_key] = f"...{text[max(0, start-20):end+20]}... ('{text[start:end]}')"


    print(f"\n--- Топ-{top_n} самых частых ошибок ---")
    if not errors:
        print("Ошибок не найдено!")
        return

    for (error_type, details), count in errors.most_common(top_n):
        print(f"\n{count} раз | {error_type}: {details}")
        if (error_type, details) in error_examples:
            print(f"  Пример: {error_examples[(error_type, details)]}")

TEST_DATA = read_data("../data/json_format/val_nofaulty.json")
evaluate_ner_model("../the-coolest/models/best_model", TEST_DATA)
# cm, labels = create_ner_confusion_matrix("/home/svya1/Documents/the-coolest/models/best_model", TEST_DATA)
evaluate_with_seqeval("../the-coolest/models/best_model", TEST_DATA)
cm, labels = create_ner_heatmaps("../the-coolest/models/best_model", TEST_DATA)
analyze_common_errors("../the-coolest/models/best_model", TEST_DATA)