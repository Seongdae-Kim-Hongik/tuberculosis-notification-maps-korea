# build_manuscript_tbnw.py — TBNW 원고 조립(2026-11-20, 투고 저널 규격).
#  규정: 초록+본문+참고문헌 ≤4,000단어, 비구조 초록 ≤150, 키워드 ≤6, running title ≤40자,
#  이중 익명(본문 = 저자·기관·IRB·자료 진술 없음, 제목면 별도 파일), Vancouver [n], 표 세로선 금지, 그림 패널 굵은 소문자, 능동태, 미국식 철자.
import os, re, json, subprocess
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Cm
from jkms_engine import JKMS
import content_tbnw as C
from amer import amer
brit = amer
HERE = os.path.dirname(os.path.abspath(__file__)); MS = os.path.dirname(HERE); OUT = os.path.join(MS, "out"); os.makedirs(OUT, exist_ok=True)
N = C.N; REFS = json.load(open(os.path.join(HERE, "refs_tbnw.json"), encoding="utf-8"))
DRAFT = os.path.join(MS, "draft", "01_manuscript.md")
_zf = os.path.join(OUT, "zenodo_doi.txt"); ZENODO = open(_zf).read().strip() if os.path.exists(_zf) else "[ZENODO DOI]"
REPO = "tuberculosis-notification-maps-korea"; GITHUB = f"https://github.com/Seongdae-Kim-Hongik/{REPO}"
TITLE = C.TITLE; RUNNING = C.RUNNING; ORCID = "0000-0002-1525-0091"
AFFIL = "Department of Biohealth Convergence Open Sharing System, Hongik University, Seoul, Republic of Korea"
ADDRESS = "Department of Biohealth Convergence Open Sharing System, Hongik University, 94 Wausan-ro, Mapo-gu, Seoul 04066, Republic of Korea"
AI_TITLE = "Use of large language models"
AI_STATEMENT = "During the preparation of this work the author used Claude (Anthropic) and ChatGPT (OpenAI) only for translation and English-language editing of the manuscript. After using these tools, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article."
IRB = "The Institutional Review Board of Hongik University approved the study on November 4, 2025 (7002340-202511-HR-012) and its continuing review on November 3, 2026 (7002340-202611-HR-040), and waived informed consent because only published aggregate statistics were used."
FUNDING = "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors."
CONTRIB = "Seongdae Kim conceived and designed the study, curated and analyzed the data, wrote the analysis code, prepared the figures and wrote and revised the manuscript."
COI = "On behalf of all authors, the corresponding author states that there is no conflict of interest."
def data_statement(): return (f"All source data are publicly available aggregate statistics from the Korea Disease Control and Prevention Agency, Statistics Korea, the Ministry of the Interior and Safety, the Korea Community Health Survey and the National Health Insurance Service. The analysis code that generates every number, table and figure is openly available on Zenodo (https://doi.org/{ZENODO}) and GitHub ({GITHUB}). The processed district-year data are available from the corresponding author on reasonable request.")
KEY_MESSAGES = [
 "Tuberculosis notifications in Korea fell by about two thirds between 2013 and 2025, but the relative gap between high- and low-notification districts widened.",
 "Excess notifications persisted in inner-city wards and remote rural counties after accounting for age, sex and district characteristics.",
 "Health authorities can use routine standardized notification maps to choose districts in which to pilot and evaluate targeted case finding among older adults."]
assert len(KEY_MESSAGES) == 3 and all(len(k) <= 280 for k in KEY_MESSAGES)
def read_draft():
    md = open(DRAFT, encoding="utf-8").read(); md = re.sub(r"<!--.*?-->", "", md, flags=re.S); S = {}; cur = None
    for line in md.split("\n"):
        m = re.match(r"^## (.+)$", line)
        if m: cur = m.group(1).strip(); S[cur] = []; continue
        if cur is not None: S[cur].append(line)
    return {k: [p.strip() for p in "\n".join(v).split("\n\n") if p.strip()] for k, v in S.items()}
def pandoc_cites(t): return re.sub(r"\s*\[(@[^\]]+)\]", lambda m: " {{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}}", t)
def strip(t): return re.sub(r"\{\{[^}]+\}\}|<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))
def all_keys():
    src = open(os.path.join(HERE, "content_tbnw.py"), encoding="utf-8").read() + open(DRAFT, encoding="utf-8").read()
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S); src = re.sub(r"(?m)^\s*#.*$", "", src)
    return sorted(k for k in {k.strip().lstrip("@") for g in re.findall(r"\[(@[^\]]+)\]", src) for k in g.split(";")} if re.fullmatch(r"(web:)?[a-z][a-z0-9]*", k))
KEYS = all_keys()

def ref(k):   # Springer Vancouver 예: Smith JJ. The world of science. Am J Sci. 1999; 36:234–5. 저자 3명 + et al(전체 단어 한도), doi
    r = REFS[k]
    if r["type"] == "web": return f"{r['authors']}. {r['title']}. {r['url']}. Accessed {r['accessed']}."
    au = r["authors"]; a = ", ".join(au) if len(au) <= 3 else ", ".join(au[:3]) + ", et al"
    t = r["title"].rstrip("."); t = t + ("" if t.endswith(("?", "!")) else ".")
    s = f"{a}. {t} {r['journal']}. {r['year']}"
    if r.get("vol"): s += f"; {r['vol']}"
    if r.get("pages"): s += f":{r['pages'].replace('-', '–')}"
    return s + (f". https://doi.org/{r['doi']}" if r.get("doi") else "") + "."

class TX(JKMS):
    raw = False; table_bold = False
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
    def _emit(self, p, text, sz=12, bold=False, italic=False):
        if not self.raw:
            text = brit(text); text = re.sub(r"(^|[\s(])-(?=\d)", "\\1\u2212", text)
        return super()._emit(p, text, sz, bold, italic)

TAB1_COV = [(C.OS, "Older adults living alone, % of households"), (C.MA, "Medical Aid type 1 patients per 100,000"), (C.DM, "Suspected diabetes at screening, %"), (C.SM, "Current smoking, %"),
            (C.FR, "Foreign residents per 1,000, log(1 + x)"), (C.LTC, "Long-term care hospitals per 100,000 aged ≥ 65 years"), (C.GH, "General hospitals per 100,000"), ("pop80_share", "Population aged ≥ 80 years, %")]
WC = ["W1_2013-15", "W2_2016-19", "W3_2020-25", "ALL"]; WH = ["2013–2015", "2016–2019", "2020–2025", "2013–2025"]
def table1():
    T = N["T1"]; A = N["asr"]
    def mean_asr(a, b): return sum(A[(y, "Both")] for y in range(a, b + 1)) / (b - a + 1)
    rows = [["__H__", "Notifications"], ["  District-years, no."] + [f"{T[c]['n']:,}" for c in WC], ["  New cases notified, no."] + [f"{T[c]['cases']:,}" for c in WC],
            ["  Age-standardised rate per 100,000*"] + [f"{mean_asr(a, b):.1f}" for a, b in ((2013, 2015), (2016, 2019), (2020, 2025), (2013, 2025))],
            ["  District SIR, median (P10–P90)†"] + [f"{T[c]['med']:.2f} ({T[c]['p10']:.2f}–{T[c]['p90']:.2f})" for c in WC], ["__H__", "District characteristics, mean (SD)"]]
    for v, lab in TAB1_COV:
        mx = max(abs(T[c]['cov'][v][0]) for c in WC); dp = 0 if mx >= 100 else (2 if mx < 1 else 1)
        rows.append([f"  {lab}"] + [f"{T[c]['cov'][v][0]:.{dp}f} ({T[c]['cov'][v][1]:.{dp}f})" for c in WC])
    foot = ("P10–P90, 10th–90th percentile; SD, standard deviation; SIR, standardised incidence ratio. *Mean of annual national rates, direct standardization to the 2020 resident population. †Observed over sex- and age-standardised expected cases summed over the period. "
            "Characteristics are district-year means. For 2025, Medical Aid, suspected diabetes, long-term care and general hospitals were carried forward from 2024 in all districts, and a few district values of living alone, smoking and foreign residents were also carried forward (Supplementary Table S1).")
    return (f"Table 1. Notified new tuberculosis and district characteristics, {N['n_districts']} districts, Republic of Korea, 2013–2025", ["Characteristic"] + WH, rows, foot)

GROUPS = [("Household structure", [C.OS]), ("Deprivation and migration", [C.MA, C.FR]), ("Metabolic and behavioral risk", [C.DM, C.SM]), ("Care facilities", [C.LTC, C.GH]),
          ("Forced controls", ["urban_population_share", "physicians_per_1000", "sex_ratio", "fiscal_independence", "pop80_share"])]
LABEL = {C.OS: "Older adults living alone", C.MA: "Medical Aid type 1 patients", C.FR: "Foreign residents", C.DM: "Suspected diabetes at screening", C.SM: "Current smoking",
         C.LTC: "Long-term care hospitals", C.GH: "General hospitals",
         "urban_population_share": "Urban population share", "physicians_per_1000": "Physicians per 1,000", "sex_ratio": "Sex ratio", "fiscal_independence": "Fiscal autonomy", "pop80_share": "Population aged ≥ 80 years"}
def f3(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
def table2():
    rows = []; assert sum(len(v) for g, v in GROUPS[:-1]) == N["n_hyp"] and set(LABEL) == set(N["main"])
    for g, vs in GROUPS:
        rows.append(["__H__", g])
        for v in vs:
            m = N["main"][v]; mv = N["mv"].get(v); kh = N["s43"].get(("KH_typeII", v)); b = N["bw"].get(v + "__between"); w = N["bw"].get(v + "__within")
            rows.append([f"  {LABEL[v]}", f3((m["IRR"], m["lo"], m["hi"])), f"{round(mv['cred_frac']*mv['n_specs'])}/{mv['n_specs']}" if mv else "Forced", f3(kh) if kh else "–", f3(b) if b else "–", f3(w) if w else "–"])
    foot = (f"CrI, credible interval; RR, rate ratio per 1 standard deviation. All characteristics were expected to raise notifications. Principal model: negative binomial with a Besag–York–Mollié 2 district effect and random-walk and independent year effects, offset by sex- and age-standardised expected cases. "
            f"*Covariate-subset models (all {N['mv_total']} non-empty subsets of the seven characteristics) containing the characteristic in which the CrI excluded 1, over those containing it. †Knorr-Held type II space–time interaction, the best-fitting model. Bounds shown as 1.000 were classified from unrounded values. "
            "‡Between-district component = district mean over 2013–2025; within-district component = value minus district mean; entered together; –, not decomposed (decomposition was applied to the four characteristics credible in the principal model).")
    return (f"Table 2. District characteristics and notified new tuberculosis, {N['n_districts']} districts, Republic of Korea, 2013–2025",
            ["Characteristic", "Principal RR (95% CrI)", "Subsets credible, n/N*", "Space–time model RR†", "Between-district RR‡", "Within-district RR‡"], rows, foot)

FIGCAP = {
 1: "Notified new tuberculosis in the Republic of Korea, 2013–2025. (a) New cases by year and sex. (b) National age-standardised rates (2020 population) by sex. (c) Rates by sex and age group, 2013–2025 combined.",
 2: "District geography of notified new tuberculosis, 229 districts, Republic of Korea, 2013–2025. (a) Standardised incidence ratio (observed over sex- and age-standardised expected cases, 13 years pooled). (b) Residual spatial rate ratio from the principal model, that is, the district ratio not explained by the covariates. (c) Residual hot spots and cold spots (posterior probability of a residual spatial rate ratio above 1 greater than 0.95 or less than 0.05). District boundaries as of 2024. Map lines delineate study areas and do not necessarily depict accepted national boundaries.",
}
def foot_row(J, text, sz=9, ls=15):
    from docx.enum.text import WD_LINE_SPACING
    t = J.doc.tables[-1]; r = t.add_row(); m = r.cells[0].merge(r.cells[-1]); m.text = ""; p = m.paragraphs[0]
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY; p.paragraph_format.line_spacing = Pt(ls); p.paragraph_format.space_before = Pt(4)
    c = J.counting; J.counting = False; J._emit(p, text, sz); J.counting = c
def put_table(J, t, fs=9):
    c = J.counting; J.counting = False; J.table_fit(t[0], t[1], t[2], "", fs_max=fs, title_bold=False); foot_row(J, t[3], 8); J.counting = c

def build(stats=None):
    D = read_draft(); J = TX(cite="bracket")
    J.para(f"<b>{TITLE}</b>")
    J.para(f"<b>Abstract</b>", before=6)
    for p in D["Abstract"]: J.para(p)
    J.para(f"<b>Keywords:</b> {C.KEYWORDS}", before=6)
    J.page_break(); J.counting = True
    J.head("Introduction", 1)
    for p in D["Introduction"]: J.para(pandoc_cites(p), indent=True)
    J.head("Methods", 1)
    for x in C.METHODS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Results", 1)
    for x in C.RESULTS:
        J.head(x[0], 2)
        for p in x[1:]: J.para(pandoc_cites(p), indent=True)
    J.head("Discussion", 1)
    for p in D["Discussion"]:
        if p.startswith("### Conclusions"): J.head("Conclusions", 1); continue
        if p.startswith("### "): J.head(p[4:].strip(), 2); continue
        J.para(pandoc_cites(p), indent=True)
    J.counting = False
    assert sorted(J.cites) == KEYS, (set(J.cites) ^ set(KEYS))
    J.page_break(); J.head("References", 1); J.raw = True; rl = []
    for i, k in enumerate(J.cites, 1): s_ = f"{i}. " + ref(k); rl.append(s_); J.para(s_)
    J.raw = False
    J.page_break(); put_table(J, table1())
    J.new_page("landscape"); put_table(J, table2(), fs=8); J.new_page("portrait")
    J.head("Figure legends", 1)
    for k in sorted(FIGCAP): J.para(f"<b>Figure {k}.</b> {FIGCAP[k]}")
    return J, rl, D

def title_page(stats):
    T = TX(cite="bracket"); T.raw = False
    T.para(f"<b>{TITLE}</b>")
    T.para(f"<b>Running title:</b> {RUNNING}", before=6)
    T.para("Seongdae Kim", before=10)
    T.para(AFFIL)
    T.para(f"<b>Corresponding author:</b> Seongdae Kim, {ADDRESS}. E-mail: kimsd@hongik.ac.kr. ORCID: {ORCID}", before=6)
    T.para(f"<b>Word count:</b> {stats['total']:,} words in all (abstract {stats['aw']}, main text {stats['bw']:,}, references {stats['rw']:,}); 2 tables and 2 figures; {len(KEYS)} references.", before=6)
    T.raw = True
    for h, t in (("Conflict of interest", COI), ("Funding", FUNDING), ("Ethics approval", IRB), ("Author contributions", CONTRIB), ("Data availability", data_statement()), (AI_TITLE, AI_STATEMENT), ("Acknowledgements", "None.")):
        T.head(h, 2); T.para(amer(t))
    T.head("Key messages", 2)
    for k_ in KEY_MESSAGES: T.para("\u2022 " + amer(k_))
    T.raw = False
    return T

def section_words(path, a, b):
    from docx import Document
    t = "\n".join(x.text for x in Document(path).paragraphs)
    i = t.find("\n" + a + "\n"); j = t.find("\n" + b + "\n", i + 1)
    return len(t[i:j].split()) - 1
def strip(t): return re.sub(r"\{\{[^}]+\}\}|<[^>]+>", "", re.sub(r"\s*\[@[^\]]+\]", "", t))
if __name__ == "__main__":
    p = os.path.join(OUT, "Manuscript_TBNW.docx")
    J, rl, D = build(); J.doc_title = "Manuscript"; J.save(p)
    aw = sum(len(strip(x).split()) for x in D["Abstract"])
    bw = section_words(p, "Introduction", "References"); rw = sum(len(x.split()) for x in rl)
    st = {"aw": aw, "bw": bw, "rw": rw, "total": aw + bw + rw}
    T = title_page(st); tp = os.path.join(OUT, "Title_Page_TBNW.docx"); T.doc_title = "Title page"; T.save(tp)
    open(os.path.join(OUT, "wordcount_tbnw.txt"), "w").write(f"body_words={bw}\nabstract_words={aw}\nref_words={rw}\ntotal_words={aw+bw+rw}\nrefs={len(KEYS)}\ntables=2\nfigures=2\ntitle_words={len(TITLE.split())}\n")
    open(os.path.join(OUT, "Key_Messages_TBNW.txt"), "w").write("\n".join(KEY_MESSAGES) + "\n")
    print(f"abstract {aw} | body {bw} | refs words {rw} | TOTAL {aw+bw+rw} | refs {len(KEYS)} | running {len(RUNNING)}ch")
