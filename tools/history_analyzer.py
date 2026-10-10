#!/usr/bin/env python3
"""
tools/history_analyzer.py
Analisa o histórico Git para identificar:
1. Tamanho dos commits recentes (LOC alteradas).
2. Qualidade das mensagens de commit.
3. Dispersão de arquivos (arquivos demais tocados em um só commit).
4. Hotspots (Arquivos com alta taxa de modificação - churn).
"""

import json
import subprocess
import sys
from pathlib import Path


def run_git_command(args):
    try:
        res = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def analyze_history(max_commits=15):
    # Log dos últimos commits
    log_format = "%H|%an|%s"
    raw_log = run_git_command(["log", f"-n{max_commits}", f"--pretty=format:{log_format}"])
    
    if not raw_log:
        return {
            "status": "warning",
            "message": "Histórico Git não encontrado ou repositório raso.",
            "commits": [],
            "hotspots": {}
        }

    commits = []
    file_churn = {}

    for line in raw_log.split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        commit_hash, author, message = parts[0], parts[1], parts[2]

        # Estatística de arquivos alterados no commit
        stat = run_git_command(["show", "--numstat", "--pretty=format:", commit_hash])
        changed_files = 0
        added_lines = 0
        deleted_lines = 0

        for stat_line in stat.split("\n"):
            stat_line = stat_line.strip()
            if not stat_line:
                continue
            cols = stat_line.split("\t")
            if len(cols) == 3:
                try:
                    add = int(cols[0]) if cols[0] != "-" else 0
                    dele = int(cols[1]) if cols[1] != "-" else 0
                    filepath = cols[2]

                    added_lines += add
                    deleted_lines += dele
                    changed_files += 1

                    # Incrementa Churn
                    file_churn[filepath] = file_churn.get(filepath, 0) + (add + dele)
                except ValueError:
                    pass

        # Análise de Code Smell no Commit
        warnings = []
        if len(message) < 10:
            warnings.append("Mensagem de commit muito curta ou vaga.")
        if changed_files > 8:
            warnings.append("Dispersão alta: muitos módulos modificados em um único commit.")
        if (added_lines + deleted_lines) > 400:
            warnings.append("Commit muito grande (> 400 linhas alteradas).")

        commits.append({
            "hash": commit_hash[:8],
            "author": author,
            "message": message,
            "changed_files": changed_files,
            "added_lines": added_lines,
            "deleted_lines": deleted_lines,
            "warnings": warnings
        })

    # Top Hotspots (arquivos que mais mudam)
    sorted_hotspots = sorted(file_churn.items(), key=lambda x: x[1], reverse=True)[:5]
    hotspots = [{"file": f, "churn_loc": c} for f, c in sorted_hotspots]

    return {
        "status": "success",
        "analyzed_commits": len(commits),
        "recent_commits": commits[:5],
        "hotspots": hotspots
    }


def main():
    report = analyze_history()
    output_path = Path("target/history_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"[history_analyzer] Relatório gerado em: {output_path}")


if __name__ == "__main__":
    main()
