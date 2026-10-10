#!/usr/bin/env python3
"""
tools/build_report.py
Consolida métricas e saídas de múltiplos sensores em um único `quality_report.json`:
1. JaCoCo (Cobertura de Testes e Complexidade das classes)
2. PMD (Violações de código, smells, complexidade ciclomática)
3. CPD (Código duplicado)
4. History Analyzer (Commits, churn e hotspots)
"""

import csv
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_jacoco_csv(csv_path):
    if not os.path.exists(csv_path):
        return {"instruction_coverage_pct": 0, "branch_coverage_pct": 0, "complexity_total": 0}

    missed_inst, covered_inst = 0, 0
    missed_branch, covered_branch = 0, 0
    total_complexity = 0

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            missed_inst += int(row.get("INSTRUCTION_MISSED", 0))
            covered_inst += int(row.get("INSTRUCTION_COVERED", 0))
            missed_branch += int(row.get("BRANCH_MISSED", 0))
            covered_branch += int(row.get("BRANCH_COVERED", 0))
            total_complexity += int(row.get("COMPLEXITY_MISSED", 0)) + int(row.get("COMPLEXITY_COVERED", 0))

    total_inst = missed_inst + covered_inst
    inst_cov = round((covered_inst / total_inst * 100), 2) if total_inst > 0 else 0

    total_b = missed_branch + covered_branch
    branch_cov = round((covered_branch / total_b * 100), 2) if total_b > 0 else 0

    return {
        "instruction_coverage_pct": inst_cov,
        "branch_coverage_pct": branch_cov,
        "total_cyclomatic_complexity": total_complexity
    }


def parse_checkstyle_xml(cs_path):
    if not os.path.exists(cs_path):
        return {"total_violations": 0, "violations": []}

    try:
        tree = ET.parse(cs_path)
        root = tree.getroot()
        violations = []
        for file_elem in root.findall(".//file"):
            filename = file_elem.get("name", "")
            if "src/main/java" in filename:
                filename = filename[filename.index("src/main/java"):]
            for err in file_elem.findall("error"):
                violations.append({
                    "file": filename,
                    "line": int(err.get("line", 0)),
                    "severity": err.get("severity", "warning"),
                    "source": err.get("source", "").split(".")[-1],
                    "message": err.get("message", "")
                })
        return {
            "total_violations": len(violations),
            "violations": violations[:20]
        }
    except Exception as e:
        return {"error": f"Failed to parse Checkstyle: {str(e)}", "total_violations": 0, "violations": []}


def parse_cpd_xml(cpd_path):
    if not os.path.exists(cpd_path):
        return {"total_duplications": 0, "duplications": []}

    try:
        tree = ET.parse(cpd_path)
        root = tree.getroot()
        dups = []
        for d in root.findall(".//duplication"):
            lines = int(d.get("lines", 0))
            tokens = int(d.get("tokens", 0))
            files = [f.get("path", "") for f in d.findall("file")]
            dups.append({
                "lines": lines,
                "tokens": tokens,
                "files": files
            })
        return {
            "total_duplications": len(dups),
            "duplications": dups
        }
    except Exception as e:
        return {"error": f"Failed to parse CPD: {str(e)}", "total_duplications": 0, "duplications": []}


def main():
    target = Path("target")
    jacoco_csv = target / "site/jacoco/jacoco.csv"
    checkstyle_xml = target / "checkstyle-result.xml"
    cpd_xml = target / "cpd.xml"
    history_json = target / "history_report.json"

    history_data = {}
    if history_json.exists():
        with open(history_json, "r", encoding="utf-8") as f:
            history_data = json.load(f)

    report = {
        "project": "NBA Hangman Web API",
        "coverage_metrics": parse_jacoco_csv(jacoco_csv),
        "code_smells_checkstyle": parse_checkstyle_xml(checkstyle_xml),
        "duplication_cpd": parse_cpd_xml(cpd_xml),
        "git_history": history_data
    }

    output_path = target / "quality_report.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[build_report] Relatório consolidado gerado em: {output_path}")


if __name__ == "__main__":
    main()
