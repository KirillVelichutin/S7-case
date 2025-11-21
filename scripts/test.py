import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import spacy
from seqeval.metrics import classification_report, f1_score
from sklearn.metrics import confusion_matrix
from spacy.training import biluo_to_iob
from spacy.training.iob_utils import offsets_to_biluo_tags

from reader import read_data

def evaluate_with_seqeval(nlp, test_data):
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

def _plot_heatmap(data, *, y_labels, x_labels=None, title, fmt, cmap, figsize=(12, 10), plot_num_str=""):
    x_labels = y_labels if x_labels is None else x_labels
    
    plt.figure(figsize=figsize)
    sns.heatmap(
        data, annot=True, fmt=fmt, cmap=cmap,
        xticklabels=x_labels, yticklabels=y_labels
    )
    plt.title(title, fontsize=16)
    plt.xlabel("Предсказанные метки", fontsize=12)
    plt.ylabel("Истинные метки", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    print(f"\nПоказываю Heatmap {plot_num_str}... Закройте окно для продолжения.")
    plt.show()


def create_ner_heatmaps(nlp, test_data):
    true_labels, pred_labels = [], []
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
    print("Сбор данных завершен. Начинаю построение графиков...")
    
    # 1) ОБЫЧНЫЙ HEATMAP (Абсолютные значения)
    _plot_heatmap(
        data=cm, y_labels=labels,
        title='Матрица ошибок NER — Абсолютные значения',
        fmt='d', cmap='Blues', plot_num_str="1/3"
    )

    # 2) НОРМАЛИЗОВАННЫЙ HEATMAP (Проценты)
    with np.errstate(divide='ignore', invalid='ignore'):
        cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    cm_norm = np.nan_to_num(cm_norm)
    _plot_heatmap(
        data=cm_norm, y_labels=labels,
        title='Матрица ошибок NER — Нормализованная (% от истинной метки)',
        fmt='.2f', cmap='Purples', plot_num_str="2/3"
    )

    # 3) ТОП-N ОШИБОК
    cm_no_diag = cm.copy()
    np.fill_diagonal(cm_no_diag, 0)
    top_n = 15
    
    error_pairs = []
    error_indices = np.argwhere(cm_no_diag > 0)
    for i, j in error_indices:
        error_pairs.append({'true': labels[i], 'pred': labels[j], 'count': cm[i, j]})
    error_pairs.sort(key=lambda x: (-x['count'], x['true'], x['pred']))
    top_pairs = error_pairs[:top_n]

    if top_pairs:
        counts_data = np.array([[p['count'] for p in top_pairs]]).T
        y_labels_top = [f"{p['true']} → {p['pred']}" for p in top_pairs]
        x_labels_top = ["Количество ошибок"]
        
        _plot_heatmap(
            data=counts_data, 
            y_labels=y_labels_top, 
            x_labels=x_labels_top,
            title=f"Топ-{top_n} самых частых ошибок NER",
            fmt='d', cmap='Reds',
            figsize=(8, len(top_pairs) * 0.5), # Динамический размер
            plot_num_str="3/3"
        )

    return cm, labels

if __name__ == "__main__":
    MODEL_PATH = "../the-coolest/models/best_model"
    TEST_DATA_PATH = "../data/json_format/val_nofaulty.json"
    
    print("Загрузка данных...")
    TEST_DATA = read_data(TEST_DATA_PATH)
    
    print(f"Загрузка модели из '{MODEL_PATH}'...")
    nlp = spacy.load(MODEL_PATH)
    print("Модель успешно загружена.")
    
    evaluate_with_seqeval(nlp, TEST_DATA)
    cm, labels = create_ner_heatmaps(nlp, TEST_DATA)