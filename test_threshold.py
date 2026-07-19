"""
Script pengujian perbandingan threshold Cosine Similarity
untuk chatbot navigasi Coretax.
"""

import pandas as pd
from similarity import CoretaxChatbot

THRESHOLDS_TO_TEST = [0.30, 0.40, 0.50, 0.60, 0.65, 0.70, 0.80]

DATASET_PATH = "data/dataset_csv.xlsx"
GROUND_TRUTH_PATH = "ground_truth.csv"


def evaluate_at_threshold(df_gt, dataset_path, threshold):
    bot = CoretaxChatbot(dataset_path=dataset_path, threshold=threshold)

    tp = fp = fn = tn = 0
    detail_rows = []

    for _, row in df_gt.iterrows():
        pertanyaan = row["pertanyaan_uji"]
        in_scope = int(row["in_scope"]) == 1
        kata_kunci = row["kata_kunci_jawaban"]

        hasil = bot.get_response(pertanyaan)
        found = hasil["found"]
        jawaban = hasil["answer"]

        if in_scope:
            if found and kata_kunci.lower() in jawaban.lower():
                tp += 1
                status = "TP"
            elif found and kata_kunci.lower() not in jawaban.lower():
                fp += 1
                status = "FP (jawaban salah)"
            else:
                fn += 1
                status = "FN (tidak ditemukan, padahal ada)"
        else:
            if not found:
                tn += 1
                status = "TN"
            else:
                fp += 1
                status = "FP (harusnya tidak relevan tapi dijawab)"

        detail_rows.append({
            "pertanyaan": pertanyaan,
            "skor": round(hasil["score"], 3),
            "status": status
        })

    total = tp + fp + fn + tn
    accuracy = (tp + tn) / total if total else 0
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0

    return {
        "threshold": threshold,
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "accuracy": round(accuracy, 3),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "detail": detail_rows
    }


def main():
    df_gt = pd.read_csv(GROUND_TRUTH_PATH)
    print(f"Jumlah pertanyaan uji: {len(df_gt)}")
    print(f"  - In-scope (relevan Coretax): {(df_gt['in_scope']==1).sum()}")
    print(f"  - Out-of-scope (tidak relevan): {(df_gt['in_scope']==0).sum()}")
    print()

    hasil_semua = []
    for th in THRESHOLDS_TO_TEST:
        hasil = evaluate_at_threshold(df_gt, DATASET_PATH, th)
        hasil_semua.append(hasil)
        print(f"Threshold {th:.2f} | Acc={hasil['accuracy']:.3f} "
              f"Prec={hasil['precision']:.3f} Rec={hasil['recall']:.3f} "
              f"F1={hasil['f1_score']:.3f} "
              f"(TP={hasil['TP']} FP={hasil['FP']} FN={hasil['FN']} TN={hasil['TN']})")

    ringkasan = pd.DataFrame([
        {k: v for k, v in h.items() if k != "detail"} for h in hasil_semua
    ])
    ringkasan.to_csv("hasil_uji_threshold.csv", index=False)
    print("\nRingkasan disimpan ke hasil_uji_threshold.csv")

    terbaik = max(hasil_semua, key=lambda h: h["f1_score"])
    print(f"\n>> Threshold terbaik berdasarkan F1-score: {terbaik['threshold']} "
          f"(F1={terbaik['f1_score']})")


if __name__ == "__main__":
    main()
    