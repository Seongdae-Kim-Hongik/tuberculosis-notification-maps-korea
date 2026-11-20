# amer.py — 영국식 → 미국식 철자(2026-11-20). 명사 analyses는 건드리지 않음.
import re
_R = [(r"\b(\w*?)(standard|harmon|penal|characteri|summar|organ|minim|priorit|normal|categor|util|general|random|recogn|special|stabil|optim|emphas|real|hospital)is(e|ed|es|ing|ation|ations)\b", lambda m: m.group(1)+m.group(2)+"iz"+m.group(3)),
      (r"\bmodelled\b", "modeled"), (r"\bmodelling\b", "modeling"), (r"\bequalled\b", "equaled"), (r"\blabelled\b", "labeled"), (r"\btravelled\b", "traveled"),
      (r"\bneighbour", "neighbor"), (r"\bbehaviour", "behavior"), (r"\bageing\b", "aging"), (r"\bprogrammes?\b", lambda m: m.group(0).replace("programme", "program")),
      (r"\bcentre(s|d)?\b", lambda m: "center" + (m.group(1) or "")), (r"\bcolour", "color"), (r"\bfavour", "favor"), (r"\bgrey\b", "gray"),
      (r"\banalys(e|ed|ing)\b", lambda m: "analyz" + m.group(1)), (r"haemo", "hemo"), (r"aemia\b", "emia"), (r"\boesophag", "esophag"), (r"\bartefact", "artifact"), (r"\bpre-specified\b", "prespecified"), (r"\bfibre", "fiber"), (r"\bpaediatric", "pediatric")]
def amer(t):
    for a, b in _R: t = re.sub(a, b, t)
    return t
if __name__ == "__main__":
    for s in ("standardised incidence", "harmonised to", "modelled", "neighbours", "analyses", "analysed", "Organisation for Economic", "hyperglycaemia", "penalised-complexity", "programme"): print(s, "->", amer(s))
