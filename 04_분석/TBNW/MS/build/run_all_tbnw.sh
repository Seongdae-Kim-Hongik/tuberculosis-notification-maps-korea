#!/bin/bash
# run_all_tbnw.sh — TBNW 빌드(수치 → 그림 → 원고·제목면 → 보충 → (커버) → 정리 → 검사). 참고문헌 캐시는 refs_tbnw.json.
set -e; cd "$(dirname "$0")"
python3 numbers_tbnw.py >/dev/null
python3 figs_tbnw.py
python3 build_manuscript_tbnw.py
python3 esm_tbnw.py
FILES="Manuscript_TBNW Supplementary_Material_TBNW Title_Page_TBNW"
if [ -f cover_tbnw.py ]; then python3 cover_tbnw.py; FILES="$FILES Cover_Letter_TBNW"; fi
for f in $FILES; do python3 sanitize_docx.py ../out/$f.docx; /opt/homebrew/bin/soffice --headless -env:UserInstallation=file:///tmp/lo_tbnw_jp --convert-to pdf --outdir ../out ../out/$f.docx >/dev/null 2>&1; done
python3 check_tbnw.py
