"""
RBA Multi-Model Ensemble Detector
Integrates 4 models from Book1.xlsx RBA dataset:
  1. Label Propagation     (semi-supervised)
  2. Label Spreading       (semi-supervised)
  3. Self-Training RF      (semi-supervised)
  4. Self-Training ET      (semi-supervised)

Training: call train(df, label_column)
Scoring : call score_df(df) for batch, or score_event(row_dict) for single events.
"""
from __future__ import annotations

import json
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

from sklearn.decomposition import PCA
from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_recall_curve,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder, StandardScaler
from sklearn.semi_supervised import (
    LabelPropagation,
    LabelSpreading,
    SelfTrainingClassifier,
)

# ── Data paths ────────────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

ENSEMBLE_META_PATH = _DATA_DIR / "rba_ensemble_meta.joblib"
ENSEMBLE_EVAL_PATH = _DATA_DIR / "rba_ensemble_eval.json"

MODEL_PATHS: Dict[str, Path] = {
    "lp":    _DATA_DIR / "rba_lp_model.joblib",
    "ls":    _DATA_DIR / "rba_ls_model.joblib",
    "st_rf": _DATA_DIR / "rba_st_rf_model.joblib",
    "st_et": _DATA_DIR / "rba_st_et_model.joblib",
}

# ── Constants ─────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
LABEL_RATIO  = 0.40          # 40 % of train rows labelled
TEST_SIZE    = 0.20
PCA_COMPONENTS = 15
RISKY_COUNTRIES = {"RU", "CN", "KP", "IR", "NG"}

_CAT_COLS = [
    "Country", "Region", "City",
    "OS Name and Version",
    "Browser Name and Version",
    "Device Type",
]
_EXCLUDE = {
    "Is Attack IP",
    "Is Account Takeover",
    "index",
    "IP Address",
    "User Agent String",
    "Login Timestamp",
}


# ─────────────────────────────────────────────────────────────────────────────
# Feature engineering (leakage-safe — fit on train only)
# ─────────────────────────────────────────────────────────────────────────────

def _temporal(df: pd.DataFrame) -> pd.DataFrame:
    if "Login Timestamp" not in df.columns:
        return df
    ts = pd.to_datetime(df["Login Timestamp"], errors="coerce")
    df = df.copy()
    df["hour_of_day"] = ts.dt.hour.fillna(0).astype(int)
    df["day_of_week"]  = ts.dt.dayofweek.fillna(0).astype(int)
    df["is_night"]     = ((ts.dt.hour >= 22) | (ts.dt.hour <= 5)).astype(int)
    df["is_weekend"]   = (ts.dt.dayofweek >= 5).astype(int)
    return df


def engineer(
    df: pd.DataFrame,
    fit_objects: Optional[Dict[str, Any]] = None,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Build feature matrix from a Book1 RBA dataframe.
    Pass fit_objects=None to fit (train set); pass a returned dict to transform (test set).
    Returns (feature_df, fit_objects).
    """
    out = df.copy()
    is_train = fit_objects is None
    if is_train:
        fit_objects = {}

    out = _temporal(out)

    rtt_col = "Round-Trip Time [ms]"
    if rtt_col in out.columns:
        out["rtt_log"] = np.log1p(out[rtt_col].fillna(0).clip(0))
        if is_train:
            fit_objects["rtt_q95"] = float(out[rtt_col].quantile(0.95))
        out["rtt_high"] = (out[rtt_col] > fit_objects["rtt_q95"]).astype(int)
    else:
        out["rtt_log"]  = 0.0
        out["rtt_high"] = 0
        if is_train:
            fit_objects["rtt_q95"] = 0.0

    if "Login Successful" in out.columns:
        out["login_fail"] = (~out["Login Successful"].astype(bool)).astype(int)
    else:
        out["login_fail"] = 0

    if "User ID" in out.columns:
        if is_train:
            user_stats = out.groupby("User ID")["login_fail"].agg(
                fail_rate="mean", login_count="count"
            )
            fit_objects["user_stats"]   = user_stats
            fit_objects["overall_fail"] = float(out["login_fail"].mean())
        us = fit_objects["user_stats"]
        out["user_fail_rate"]   = out["User ID"].map(us["fail_rate"]).fillna(
            fit_objects["overall_fail"])
        out["user_login_count"] = out["User ID"].map(us["login_count"]).fillna(1)

    if "Country" in out.columns:
        out["country_risky"] = out["Country"].isin(RISKY_COUNTRIES).astype(int)

    if "ASN" in out.columns:
        out["asn_suspicious"] = (
            pd.to_numeric(out["ASN"], errors="coerce").fillna(0) >= 500_000
        ).astype(int)

    present_cats = [c for c in _CAT_COLS if c in out.columns]
    if present_cats:
        if is_train:
            enc = OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
                dtype=np.float64,
            )
            enc.fit(out[present_cats].astype(str))
            fit_objects["ord_enc"]  = enc
            fit_objects["cat_cols"] = present_cats
        enc = fit_objects["ord_enc"]
        encoded = enc.transform(out[fit_objects["cat_cols"]].astype(str))
        for j, col in enumerate(fit_objects["cat_cols"]):
            out[col + "_enc"] = encoded[:, j]

    # Convert bools → int
    for col in out.columns:
        if out[col].dtype == bool:
            out[col] = out[col].astype(int)

    to_drop  = [c for c in _EXCLUDE if c in out.columns]
    to_drop += [c for c in _CAT_COLS if c in out.columns]
    out = out.drop(columns=to_drop, errors="ignore")

    # Numeric-only
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    return out, fit_objects


# ─────────────────────────────────────────────────────────────────────────────
# Main class
# ─────────────────────────────────────────────────────────────────────────────

class RBAEnsembleDetector:
    """
    Multi-model weighted ensemble for RBA anomaly detection.

    Models
    ------
    lp    : Label Propagation   (semi-supervised, PCA input)
    ls    : Label Spreading     (semi-supervised, PCA input)
    st_rf : Self-Training RF    (semi-supervised, scaled input)
    st_et : Self-Training ET    (semi-supervised, scaled input)
    iso   : Isolation Forest    (unsupervised, scaled input)
    ocsvm : One-Class SVM       (unsupervised, scaled input)
    """

    def __init__(self) -> None:
        self.models: Dict[str, Any]        = {}
        self.weights: Dict[str, float]     = {}
        self.best_threshold: float         = 0.5
        self.metrics: Dict[str, Any]       = {}
        self.feature_names: List[str]      = []

        # preprocessing objects
        self._fit_objects: Dict[str, Any]  = {}
        self._imputer: Optional[SimpleImputer]  = None
        self._scaler:  Optional[StandardScaler] = None
        self._pca:     Optional[PCA]            = None

        # normalisation constants for un-supervised scores
        self._iso_min: float   = 0.0
        self._iso_max: float   = 1.0
        self._ocs_min: float   = 0.0
        self._ocs_max: float   = 1.0

        self.trained: bool = False
        self._try_load()

    # ── public interface ──────────────────────────────────────────────────────

    @property
    def is_trained(self) -> bool:
        return self.trained

    @property
    def model_names(self) -> List[str]:
        return ["lp", "ls", "st_rf", "st_et"]

    @property
    def display_names(self) -> Dict[str, str]:
        return {
            "lp":    "Label Propagation",
            "ls":    "Label Spreading",
            "st_rf": "Self-Training Random Forest",
            "st_et": "Self-Training Extra Trees",
        }

    def train(
        self,
        df: pd.DataFrame,
        label_column: str = "Is Attack IP",
    ) -> Dict[str, Any]:
        """
        Train all 4 models on *df* (Book1 DataFrame).
        Returns a dict with per-model and ensemble metrics on the held-out test set.
        """
        np.random.seed(RANDOM_STATE)

        # ── 0. Prepare labels ─────────────────────────────────────────────
        assert label_column in df.columns, f"Label column '{label_column}' not found"
        df = df.copy()
        df[label_column] = df[label_column].astype(bool).astype(int)

        # ── 1. Train / test split BEFORE feature engineering ─────────────
        idx = np.arange(len(df))
        train_idx, test_idx = train_test_split(
            idx,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=df[label_column].values,
        )
        df_train_raw = df.iloc[train_idx].copy().reset_index(drop=True)
        df_test_raw  = df.iloc[test_idx ].copy().reset_index(drop=True)

        y_train = df_train_raw[label_column].astype(int).values
        y_test  = df_test_raw[label_column].astype(int).values

        # ── 2. Feature engineering (fit on train only) ────────────────────
        df_train_fe, fit_objects = engineer(df_train_raw, fit_objects=None)
        df_test_fe,  _           = engineer(df_test_raw,  fit_objects=fit_objects)

        # Align columns
        feat_cols = [c for c in df_train_fe.columns if c != label_column]
        for col in feat_cols:
            if col not in df_test_fe.columns:
                df_test_fe[col] = 0.0
        feat_cols = [c for c in feat_cols if c != label_column]

        X_train_raw = df_train_fe[feat_cols].values
        X_test_raw  = df_test_fe[feat_cols].values

        # ── 3. Impute + scale ─────────────────────────────────────────────
        imputer = SimpleImputer(strategy="median")
        X_train_imp = imputer.fit_transform(X_train_raw)
        X_test_imp  = imputer.transform(X_test_raw)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_imp)
        X_test_scaled  = scaler.transform(X_test_imp)

        # ── 4. PCA (for graph-based models) ──────────────────────────────
        n_comp = min(PCA_COMPONENTS, X_train_scaled.shape[1])
        pca = PCA(n_components=n_comp, random_state=RANDOM_STATE)
        X_train_pca = pca.fit_transform(X_train_scaled)
        X_test_pca  = pca.transform(X_test_scaled)

        # ── 5. Semi-supervised label masking (40 % labelled) ─────────────
        y_semi = np.full(len(y_train), -1, dtype=int)
        pos_idx = np.where(y_train == 1)[0]
        neg_idx = np.where(y_train == 0)[0]

        n_pos   = max(2, int(len(pos_idx) * LABEL_RATIO))
        n_neg   = min(len(neg_idx), n_pos * 9)
        lab_pos = np.random.choice(pos_idx, n_pos, replace=False)
        lab_neg = np.random.choice(neg_idx, n_neg, replace=False)
        lab_idx = np.concatenate([lab_pos, lab_neg])
        y_semi[lab_idx] = y_train[lab_idx]

        lab_X     = X_train_scaled[lab_idx]
        lab_y     = y_train[lab_idx]
        lab_X_pca = pca.transform(lab_X)

        # ── 6. Train the 6 models ─────────────────────────────────────────
        print("Training Label Propagation...")
        lp = LabelPropagation(kernel="rbf", gamma=20, max_iter=1000, tol=1e-3)
        lp.fit(X_train_pca, y_semi)

        print("Training Label Spreading...")
        ls = LabelSpreading(
            kernel="rbf", gamma=20, alpha=0.2, max_iter=1000, tol=1e-4, n_jobs=-1
        )
        ls.fit(X_train_pca, y_semi)

        print("Training Self-Training Random Forest...")
        st_rf = SelfTrainingClassifier(
            estimator=RandomForestClassifier(
                n_estimators=500, min_samples_leaf=2,
                class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE,
            ),
            threshold=0.70, criterion="threshold", max_iter=20, verbose=False,
        )
        st_rf.fit(X_train_scaled, y_semi)

        print("Training Self-Training Extra Trees...")
        st_et = SelfTrainingClassifier(
            estimator=ExtraTreesClassifier(
                n_estimators=500, min_samples_leaf=2,
                class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE,
            ),
            threshold=0.70, criterion="threshold", max_iter=20, verbose=False,
        )
        st_et.fit(X_train_scaled, y_semi)

        # ── 7. Derive ensemble weights from labelled validation AP (4 models) ──
        def _safe_ap(y: np.ndarray, s: np.ndarray) -> float:
            try:
                return max(float(average_precision_score(y, s)), 0.01)
            except Exception:
                return 0.01

        val_lp  = np.nan_to_num(lp.predict_proba(lab_X_pca)[:, 1], nan=0.0)
        val_ls  = np.nan_to_num(ls.predict_proba(lab_X_pca)[:, 1], nan=0.0)
        val_st  = st_rf.predict_proba(lab_X)[:, 1]
        val_et  = st_et.predict_proba(lab_X)[:, 1]

        w = {
            "lp":    _safe_ap(lab_y, val_lp),
            "ls":    _safe_ap(lab_y, val_ls),
            "st_rf": _safe_ap(lab_y, val_st),
            "st_et": _safe_ap(lab_y, val_et),
        }
        w_tot = sum(w.values())
        weights = {k: v / w_tot for k, v in w.items()}

        # ── 8. Ensemble predictions (test set) ────────────────────────────
        lp_test   = np.nan_to_num(lp.predict_proba(X_test_pca)[:, 1], nan=0.0)
        ls_test   = np.nan_to_num(ls.predict_proba(X_test_pca)[:, 1], nan=0.0)
        st_test   = st_rf.predict_proba(X_test_scaled)[:, 1]
        et_test   = st_et.predict_proba(X_test_scaled)[:, 1]

        risk_test = self._ensemble_score(lp_test, ls_test, st_test, et_test, weights)

        # Threshold from labelled val
        val_risk = self._ensemble_score(val_lp, val_ls, val_st, val_et, weights)
        prec_v, rec_v, thresh_v = precision_recall_curve(lab_y, val_risk)
        f1_v = 2 * prec_v * rec_v / (prec_v + rec_v + 1e-9)
        best_thresh = float(np.clip(thresh_v[np.argmax(f1_v[:-1])], 0.0, 1.0))

        # ── 9. Collect metrics ────────────────────────────────────────────
        def _model_metrics(name: str, proba: np.ndarray) -> Dict[str, float]:
            pred = (proba >= 0.5).astype(int)
            return {
                "roc_auc":  float(roc_auc_score(y_test, proba)),
                "avg_prec": float(average_precision_score(y_test, proba)),
                "f1":       float(f1_score(y_test, pred, zero_division=0)),
                "recall":   float(recall_score(y_test, pred, zero_division=0)),
                "accuracy": float(accuracy_score(y_test, pred)),
                "weight":   weights[name],
            }

        y_ens_pred = (risk_test >= best_thresh).astype(int)
        metrics = {
            "timestamp":      datetime.now().isoformat(),
            "best_threshold": best_thresh,
            "n_train":        int(len(y_train)),
            "n_test":         int(len(y_test)),
            "label_ratio":    LABEL_RATIO,
            "feature_names":  feat_cols,
            "weights":        weights,
            "models": {
                "lp":    _model_metrics("lp",    lp_test),
                "ls":    _model_metrics("ls",    ls_test),
                "st_rf": _model_metrics("st_rf", st_test),
                "st_et": _model_metrics("st_et", et_test),
            },
            "ensemble": {
                "roc_auc":  float(roc_auc_score(y_test, risk_test)),
                "avg_prec": float(average_precision_score(y_test, risk_test)),
                "f1":       float(f1_score(y_test, y_ens_pred, zero_division=0)),
                "recall":   float(recall_score(y_test, y_ens_pred, zero_division=0)),
                "accuracy": float(accuracy_score(y_test, y_ens_pred)),
            },
        }

        # ── 10. Persist state ─────────────────────────────────────────────
        self.models        = {"lp": lp, "ls": ls, "st_rf": st_rf, "st_et": st_et}
        self.weights       = weights
        self.best_threshold = best_thresh
        self.metrics       = metrics
        self.feature_names  = feat_cols
        self._fit_objects  = fit_objects
        self._imputer      = imputer
        self._scaler       = scaler
        self._pca          = pca
        self.trained       = True

        self.save()
        self._print_summary(metrics)
        return metrics

    # ── scoring ───────────────────────────────────────────────────────────────

    def score_df(
        self,
        df: pd.DataFrame,
        label_column: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Score a Book1-style DataFrame. Returns df with added columns:
          risk_score, is_anomaly, alert_level, and per-model scores.
        """
        if not self.trained:
            raise RuntimeError("Model not trained. Call train() first.")

        df_fe, _ = engineer(df, fit_objects=self._fit_objects)
        X_imp    = self._imputer.transform(df_fe[self.feature_names].values)
        X_scaled = self._scaler.transform(X_imp)
        X_pca    = self._pca.transform(X_scaled)

        lp_s   = np.nan_to_num(self.models["lp"].predict_proba(X_pca)[:, 1], nan=0.0)
        ls_s   = np.nan_to_num(self.models["ls"].predict_proba(X_pca)[:, 1], nan=0.0)
        st_s   = self.models["st_rf"].predict_proba(X_scaled)[:, 1]
        et_s   = self.models["st_et"].predict_proba(X_scaled)[:, 1]

        risk = self._ensemble_score(lp_s, ls_s, st_s, et_s, self.weights)

        out = df.copy().reset_index(drop=True)
        out["score_lp"]    = lp_s
        out["score_ls"]    = ls_s
        out["score_st_rf"] = st_s
        out["score_st_et"] = et_s
        out["risk_score"]  = risk
        out["is_anomaly"]  = (risk >= self.best_threshold).astype(int)
        out["alert_level"] = pd.cut(
            risk,
            bins=[0.0, 0.35, 0.55, 0.75, 1.001],
            labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            include_lowest=True,
        )
        return out

    def score_event(self, row: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Score a single event dict (Book2-style fields).
        Returns (risk_score, per_model_scores).
        """
        df_single = pd.DataFrame([row])
        scored    = self.score_df(df_single)
        risk      = float(scored["risk_score"].iloc[0])
        per_model = {
            "lp":    float(scored["score_lp"].iloc[0]),
            "ls":    float(scored["score_ls"].iloc[0]),
            "st_rf": float(scored["score_st_rf"].iloc[0]),
            "st_et": float(scored["score_st_et"].iloc[0]),
        }
        return risk, per_model

    # ── persistence ───────────────────────────────────────────────────────────

    def save(self) -> None:
        """Persist all models and preprocessing objects."""
        for name, path in MODEL_PATHS.items():
            joblib.dump(self.models[name], path)

        meta = {
            "weights":      self.weights,
            "best_threshold": self.best_threshold,
            "feature_names":  self.feature_names,
            "iso_min":      self._iso_min,
            "iso_max":      self._iso_max,
            "ocs_min":      self._ocs_min,
            "ocs_max":      self._ocs_max,
            "fit_objects":  self._fit_objects,
            "imputer":      self._imputer,
            "scaler":       self._scaler,
            "pca":          self._pca,
        }
        joblib.dump(meta, ENSEMBLE_META_PATH)

        with open(ENSEMBLE_EVAL_PATH, "w") as f:
            # Numpy floats → plain float for JSON
            json.dump(_json_safe(self.metrics), f, indent=2)

        print(f"Ensemble saved → {_DATA_DIR}")

    def load(self) -> None:
        """Load all models from disk."""
        if not ENSEMBLE_META_PATH.exists():
            raise FileNotFoundError(f"Ensemble meta not found at {ENSEMBLE_META_PATH}")

        meta = joblib.load(ENSEMBLE_META_PATH)
        self.weights        = meta["weights"]
        self.best_threshold = meta["best_threshold"]
        self.feature_names  = meta["feature_names"]
        self._iso_min       = meta["iso_min"]
        self._iso_max       = meta["iso_max"]
        self._ocs_min       = meta["ocs_min"]
        self._ocs_max       = meta["ocs_max"]
        self._fit_objects   = meta["fit_objects"]
        self._imputer       = meta["imputer"]
        self._scaler        = meta["scaler"]
        self._pca           = meta["pca"]

        self.models = {
            name: joblib.load(path) for name, path in MODEL_PATHS.items()
        }

        if ENSEMBLE_EVAL_PATH.exists():
            with open(ENSEMBLE_EVAL_PATH) as f:
                self.metrics = json.load(f)

        self.trained = True
        print("Ensemble loaded from disk.")

    # ── internal helpers ──────────────────────────────────────────────────────

    def _try_load(self) -> None:
        if ENSEMBLE_META_PATH.exists() and all(p.exists() for p in MODEL_PATHS.values()):
            try:
                self.load()
            except Exception:
                pass

    @staticmethod
    def _ensemble_score(
        lp: np.ndarray,
        ls: np.ndarray,
        st: np.ndarray,
        et: np.ndarray,
        weights: Dict[str, float],
    ) -> np.ndarray:
        return (
            weights["lp"]    * lp
            + weights["ls"]    * ls
            + weights["st_rf"] * st
            + weights["st_et"] * et
        )

    @staticmethod
    def _print_summary(metrics: Dict[str, Any]) -> None:
        ens = metrics["ensemble"]
        print("\n" + "=" * 62)
        print("  RBA ENSEMBLE (4 MODELS) — TEST SET RESULTS")
        print("=" * 62)
        print(f"  Ensemble ROC-AUC  : {ens['roc_auc']:.4f}")
        print(f"  Ensemble F1-Score : {ens['f1']:.4f}")
        print(f"  Ensemble Recall   : {ens['recall']:.4f}")
        print(f"  Ensemble Accuracy : {ens['accuracy']*100:.2f}%")
        print(f"  Best threshold    : {metrics['best_threshold']:.4f}")
        print("-" * 62)
        print(f"  {'Model':<30} {'ROC-AUC':>8}  {'F1':>6}  {'Weight':>7}")
        print(f"  {'-'*30} {'-'*8}  {'-'*6}  {'-'*7}")
        for name, m in metrics["models"].items():
            dname = {
                "lp": "Label Propagation",
                "ls": "Label Spreading",
                "st_rf": "Self-Training RF",
                "st_et": "Self-Training ET",
            }[name]
            print(
                f"  {dname:<30} {m['roc_auc']:>8.4f}"
                f"  {m['f1']:>6.4f}  {m['weight']:>7.3f}"
            )
        print("=" * 62)


# ── JSON helper ───────────────────────────────────────────────────────────────

def _json_safe(obj: Any) -> Any:
    """Recursively convert numpy scalars / arrays to Python-native types."""
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj
