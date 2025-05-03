import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import yaml
import lamini
from lamini import Lamini

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))
from utils.utils import (
    save_results_to_jsonl,
    load_config,
    format_glossary,
    read_jsonl,
)

from lamini.experiment.error_analysis_eval import SQLExecutionPipeline


def read_test_set(parquet_path: Path) -> List[Dict[str, str]]:
    """Return list of {'question', 'ref_query'} from a parquet file."""
    df = pd.read_parquet(parquet_path)
    required_cols = {"input"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"{parquet_path.name} missing columns: {missing}")
    return [
        {
            "question": row["input"],
            "ref_query": row.get("output", ""),
        }
        for _, row in df.iterrows()
    ]


def _to_plain_text(resp: Any) -> str:
    """Normalize Lamini response into a plain SQL string."""
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        if "generated_text" in resp:
            return resp["generated_text"]
        if "choices" in resp and resp["choices"]:
            return resp["choices"][0].get("text", str(resp))
    return str(resp)


def run_inference(
    test_cases: List[Dict[str, str]], model_id: str
) -> List[Dict[str, str]]:
    llm = Lamini(model_name=model_id, api_key=os.environ["LAMINI_API_KEY"])
    results: List[Dict[str, str]] = []

    total = len(test_cases)

    for idx, tc in enumerate(test_cases, 1):
        prompt = (
            "<|start_header_id|>user<|end_header_id|>"
            f"{tc['question']}"
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )

        try:
            resp = llm.generate(prompt)
            generated_query = _to_plain_text(resp)
        except Exception as exc:
            generated_query = f"Error: {exc}"

        results.append(
            {
                "question": tc["question"],
                "ref_query": tc.get("ref_query", ""),
                "generated_query": generated_query,
            }
        )
        if idx % 25 == 0 or idx == total:
            print(f"Processed {idx}/{total}")

    return results


def prepare_for_evaluation(
    inference_results: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """Drop rows whose model call failed."""
    return [
        r for r in inference_results if not r["generated_query"].startswith("Error:")
    ]


def main(project_name: str) -> None:
    project_root = PROJECT_ROOT / "projects" / project_name
    yml_path = project_root / "ymls" / "project.yml"
    data_dir = project_root / "data"
    local_db_dir = PROJECT_ROOT / "local-db"
    results_dir = project_root / "experiment_results"
    results_dir.mkdir(parents=True, exist_ok=True)

    if not yml_path.exists():
        sys.exit(f"Config file not found: {yml_path}")
    with open(yml_path, "r") as f:
        cfg = yaml.safe_load(f)

    try:
        lamini.api_url = cfg["Lamini"]["base_url_inf"]
        lamini.api_key = cfg["Lamini"]["api_key"]
        analysis_model_id = cfg["Project"]["model"]
    except KeyError as ke:
        sys.exit(f"project.yml missing key: {ke}")

    os.environ.update(
        LAMINI_API_URL=lamini.api_url,
        LAMINI_API_KEY=lamini.api_key,
    )

    # --- paths ---------------------------------------------------------------
    parquet_path = local_db_dir / "evalset.parquet"
    db_path = data_dir / f"{project_name}.sqlite"
    # --- run -----------------------------------------------------------------
    model_id = input("Enter the fine-tuned model ID to use for inference: ").strip()

    print("➜ Reading test set …")
    test_cases = read_test_set(parquet_path)
    print(f"   {len(test_cases)} cases loaded")

    print("➜ Running inference …")
    inference_results = run_inference(test_cases, model_id)
    inf_out = results_dir / "inference_results.jsonl"
    save_results_to_jsonl(inference_results, inf_out)
    print("➜ Preparing evaluation set …")
    eval_cases = prepare_for_evaluation(inference_results)
    print(f"   {len(eval_cases)} cases will be evaluated against the database")

    print("➜ Executing SQL & scoring …")
    pipeline = SQLExecutionPipeline(model=analysis_model_id, db_type="sqlite")
    evaluation_results = pipeline.evaluate_queries(
        eval_cases,
        connection_params={"db_path": str(db_path)},
    )
    eval_out = results_dir / "analysis_results_with_data.jsonl"
    save_results_to_jsonl(evaluation_results, eval_out)

    print("➜ Generating markdown report …")
    report_md = pipeline.generate_report(evaluation_results)
    report_path = results_dir / "analysis_report.md"
    report_path.write_text(report_md, encoding="utf-8")

    print("\n✅ Finished!")
    print(f"• Inference results:  {inf_out}")
    print(f"• Evaluation results: {eval_out}")
    print(f"• Report:            {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run inference + SQL evaluation")
    parser.add_argument("--project", required=True, help="Project name")
    main(parser.parse_args().project)
