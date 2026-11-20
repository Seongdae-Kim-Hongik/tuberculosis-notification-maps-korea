# check_tbnw.py — TBNW 원고 검사기(2026-11-20). 가이드라인 한도 > 플레이북(3선 표·네모·지문·익명) > 문체·수치. FAIL 0이면 PASS.
#  sanitize_docx.py 뒤에 돌린다.
import os, re, subprocess, zipfile
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
import content_tbnw as C
from build_manuscript_tbnw import read_draft, TITLE, RUNNING, ORCID, KEYS, AI_STATEMENT, GITHUB, FUNDING, CONTRIB, IRB, COI, KEY_MESSAGES, ZENODO
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out")
R = []
def ok(c, m): R.append(("ok  " if c else "FAIL") + " " + m)
W = dict(l.split("=") for l in open(os.path.join(OUT, "wordcount_tbnw.txt")).read().split())
D = read_draft(); ab = " ".join(D["Abstract"])
MSF, SUPF, CLF, TPF = "Manuscript_TBNW.docx", "Supplementary_Material_TBNW.docx", "Cover_Letter_TBNW.docx", "Title_Page_TBNW.docx"
HAS_CL = os.path.exists(os.path.join(OUT, CLF))   # 커버레터는 공개 저장소에 없음
for f in (MSF, SUPF, TPF, "Figures/Figure1.tif", "Figures/Figure2.tif", MSF[:-5] + ".pdf", SUPF[:-5] + ".pdf"): ok(os.path.exists(os.path.join(OUT, f)), f"파일 {f}")
# 1. 저널 규정
ok(int(W["total_words"]) <= 4000, f"초록+본문+참고문헌 {W['total_words']} ≤ 4,000")
ok(int(W["abstract_words"]) <= 150 and len(D["Abstract"]) == 1, f"비구조 초록 {W['abstract_words']} ≤ 150")
ok(not re.search(r"\[@", ab) and not re.search(r"\b(SD|SIR|RR|CrI|BYM2|OECD|KDCA)\b", ab), "초록 인용·약어 없음(비전문가용)")
KW = [k.strip() for k in C.KEYWORDS.split(";")]; ok(1 <= len(KW) <= 6, f"키워드 {len(KW)} ≤ 6")
ok(len(RUNNING) <= 40, f"running title {len(RUNNING)}자 ≤ 40")
ok(":" not in TITLE and "229" not in TITLE and "standardi" not in TITLE.lower() and "Where does tuberculosis remain" not in TITLE, "제목 쌍점·시리즈 틀 없음·이전 제목과 다름")
ok(len(KEY_MESSAGES) == 3 and all(len(k) <= 280 for k in KEY_MESSAGES), "Key messages 3개 ≤ 280자")
d = Document(os.path.join(OUT, MSF)); _ps = [p.text.strip() for p in d.paragraphs]; _dx = "\n".join(_ps)
# 이중 익명: 본문 파일에 식별 정보 없음
_all_ms = _dx + "\n" + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
bad = re.findall(r"(?i)hongik|seongdae|kimsd|7002340|0000-0002-1525|github|zenodo|review board|ethic|funding|acknowledg|author contribution|the author\b|claude|chatgpt|conflict of interest", _all_ms)
ok(not bad, f"원고 익명(식별어 0) {sorted(set(bad))[:5]}")
sup = Document(os.path.join(OUT, SUPF)); supt = "\n".join(p.text for p in sup.paragraphs) + "\n".join(c.text for t in sup.tables for r in t.rows for c in r.cells)
bad2 = re.findall(r"(?i)hongik|seongdae|kimsd|7002340|0000-0002-1525|github|zenodo|review board", supt); ok(not bad2, f"보충 익명 {sorted(set(bad2))[:5]}")
for f in (MSF, SUPF):
    core = zipfile.ZipFile(os.path.join(OUT, f)).read("docProps/core.xml").decode(); ok("<dc:creator></dc:creator>" in core and "Seongdae" not in core, f"{f} 파일 속성 저자 비움")
tp = Document(os.path.join(OUT, TPF)); tpt = "\n".join(p.text for p in tp.paragraphs)
for t in (TITLE, RUNNING, "Seongdae Kim", "Hongik University", "kimsd@hongik.ac.kr", ORCID, COI, FUNDING, IRB, CONTRIB, AI_STATEMENT, "https://doi.org/10.5281/zenodo.", GITHUB):
    ok(t in tpt, f"제목면 '{t[:40]}'")
ok("only for translation and English-language editing" in AI_STATEMENT and "full responsibility" in AI_STATEMENT, "AI 고지 = 번역·첨삭만 + 책임 문장")
_ord = ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusions", "References", "Figure legends"]; pos = [_ps.index(k) if k in _ps else -1 for k in _ord]
ok(all(p >= 0 for p in pos) and pos == sorted(pos), f"원고 순서 {pos}")
ok("Policy implications" in _ps, "정책 함의 절(규정: 정책 함의 명시)")
ok(re.search(r"(?i)other countries|beyond Korea", _dx) is not None, "다른 나라 교훈 서술")
ok(len(d.tables) == 2, "표 2(그림은 별도 파일)")
z = zipfile.ZipFile(os.path.join(OUT, MSF)); ok("<w:drawing" not in z.read("word/document.xml").decode(), "원고에 그림 삽입 없음")
for k in (1, 2):
    im = Image.open(os.path.join(OUT, "Figures", f"Figure{k}.tif")); ok(round(im.info.get("dpi", (0, 0))[0]) >= 300 and getattr(im, "n_frames", 1) == 1, f"Figure{k}.tif {round(im.info.get('dpi',(0,0))[0])} dpi")
legs = _dx[_dx.find("Figure legends"):]
ok(not re.search(r"\b(red|blue|green|orange|yellow|purple|colou?r)\b", legs, re.I), "그림 설명에 색 표현 없음(인쇄 흑백)")
ok("(a)" in legs and "(A)" not in legs, "그림 패널 소문자(규정)")
# 2. 표·문서 위생
for nm, f in (("원고", MSF), ("보충", SUPF), ("제목면", TPF)) + ((("커버", CLF),) if HAS_CL else ()):
    dd = Document(os.path.join(OUT, f))
    for i, t in enumerate(dd.tables):
        b = t._tbl.tblPr.find(qn("w:tblBorders"))
        ok(b is not None and all(b.find(qn(f"w:{s}")).get(qn("w:val")) == "nil" for s in ("insideV", "insideH", "left", "right")), f"{nm} 표{i+1} 3선")
        _rows = [row for k_, row in enumerate(t.rows) if k_ > 0 and len({id(c._tc) for c in row.cells}) > 1]
        badb = [r.text for row in _rows for c in row.cells for p in c.paragraphs for r in p.runs if r.bold and r.text.strip()]
        ok(not badb, f"{nm} 표{i+1} 데이터 칸 볼드 없음 {badb[:2]}")
    x = subprocess.run(["unzip", "-p", os.path.join(OUT, f), "word/*.xml"], capture_output=True, text=True).stdout
    ok(len(re.findall(r"<w:keepNext[ />]|<w:keepLines[ />]|<w:pageBreakBefore[ />]", x)) == 0, f"{nm} Word 검은 네모 0건")
    zz = zipfile.ZipFile(os.path.join(OUT, f)); core = zz.read("docProps/core.xml").decode(); app = zz.read("docProps/app.xml").decode()
    ok("2013-12-23" not in core and not any(n.startswith("customXml/") for n in zz.namelist()), f"{nm} python-docx 지문 없음")
    ok(re.search(r"<AppVersion>\d+\.\d+</AppVersion>", app) and re.search(r"<Application>[^<]+</Application>", app), f"{nm} AppVersion·Application 채움(빈 값 아님)")
# 3. 문체·인용
body = re.sub(r"\s+", " ", _dx[_dx.find("\nIntroduction\n"):_dx.find("\nReferences\n")])
ok(not re.search(r"\b(we|our|us|I)\b", body + " " + ab, re.I) or not re.search(r"\b(we|our|us)\b", body + " " + ab, re.I), "1인칭 없음")
ok(not re.search(r"\b(we|our|us)\b", body + " " + ab, re.I), "we/our/us 0건")
cov = subprocess.run(["pdftotext", os.path.join(OUT, CLF.replace(".docx", ".pdf")), "-"], capture_output=True, text=True).stdout if HAS_CL else ""
alltxt = _dx + supt + cov + tpt
ok("—" not in alltxt and not re.search(r"[가-힣]", alltxt), "em-dash·한글 없음")
ok(not re.search(r"\bsignifican", _dx + supt, re.I), "'significant' 없음")
UK = r"\b(\w*(standardis|harmonis|summaris|categoris|minimis|randomis|generalis|normalis|prioritis|organis|utilis|penalis)\w*|analys(e|ed|ing)|modelled|modelling|centre(s|d)?|neighbour\w*|behaviour\w*|ageing|colour|favour\w*|labelled|grey|programme)\b"
uk = sorted(set(m.group(0) for m in re.finditer(UK, body + " " + cov + " " + tpt))); ok(not uk, f"미국식 철자 통일 {uk}")
ok(not re.search(r"\[(@|web:)", _dx) and "{{" not in _dx, "미해결 인용 없음")
disc = _dx[_dx.find("\nDiscussion\n"):_dx.find("\nReferences\n")]; disc_nc = re.sub(r"\[[\d, \-–]+\]", "", disc)
_dn = re.findall(r".{15}\d.{8}", disc_nc)[:3]; ok(not _dn, f"고찰·결론에 숫자 없음 {_dn}")
refs = _dx[_dx.find("\nReferences\n"):_dx.find("\nTable 1")]
ok(not re.search(r"github|zenodo", refs, re.I), "참고문헌에 GitHub·Zenodo 없음")
_rl = [l for l in refs.split("\n") if re.match(r"^\d+\. ", l)]; ok(len(_rl) == len(KEYS) == int(W["refs"]), f"참고문헌 {len(_rl)}개")
_nodoi = [l[:60] for l in _rl if not re.search(r"doi\.org|http", l)]; ok(len(_nodoi) <= 3, f"DOI·URL 없는 문헌 ≤3 {_nodoi}")
cp = subprocess.run(["python3", os.path.join(os.path.expandvars("$ST_DATA_ROOT"), "G.Downloads/00_PLAYBOOK/검증기록/check_citation_order.py"), os.path.join(OUT, MSF)], capture_output=True, text=True).stdout
ok("FAIL" not in cp and ("PASS" in cp or "통과" in cp), "인용 번호 순서 검사기 PASS")
for k, lab in C.SUP.items(): ok(lab in body and lab.replace("Supplementary ", "") in supt, f"보충 '{lab}' 본문 인용·보충 존재")
_tf = os.path.join(OUT, "_trace_terms.txt"); _tt = open(_tf).read().strip() if os.path.exists(_tf) else "cerebrovascular|stroke"
ok(not re.search(_tt, alltxt, re.I), "다른 호·다른 저널 흔적 없음")
ok("[ZENODO DOI]" not in tpt + cov, "Zenodo DOI 채움")
open(os.path.join(OUT, "check_tbnw.txt"), "w").write("\n".join(R) + "\n\n" + cp); nf = sum(r.startswith("FAIL") for r in R)
print("\n".join(r for r in R if r.startswith("FAIL")) or "", f"\n{len(R)} checks, FAIL {nf}", "PASS" if nf == 0 else "")
