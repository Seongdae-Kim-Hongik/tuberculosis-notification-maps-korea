# content_tbnw.py — TBNW 원저의 제목·Methods·Results 문장(수치는 numbers_tbnw에서만, 2026-11-20). 기술 세부는 보충 Appendix A.
#  저널 규정: 초록+본문+참고문헌 ≤4,000, 비구조 초록 ≤150, 키워드 ≤6, 능동태, 이중 익명(본문에 기관·IRB 없음), 인과 표현 금지.
#  단독 저자 → 1인칭 금지. 결과 절에 해석 금지. 제목·소제목 쌍점 금지.
from numbers_tbnw import load, HYP, FORCED, P80, OS, MA, DM, SM, FR, LTC, GH
N = load()
def tci(t): return f"RR {t[0]:.3f}, 95% CrI {t[1]:.3f}–{t[2]:.3f}"
def ci(v): r = N["main"][v]; return tci((r["IRR"], r["lo"], r["hi"]))
def sh(t): return f"{t[0]:.3f} ({t[1]:.3f}–{t[2]:.3f})"
M = N["main"]; T1 = N["T1"]
S43 = lambda a, v: N["s43"][(a, v)]
S41 = lambda a, v: N["s41"][(a, v)]
BW = lambda k: N["bw"][k]
NCO = lambda o, v: N["nco"][(o, v)]
SEN = lambda s, v: N["sens"][s][v]
WIN = lambda v, w: N["win"][(v, w)]
KH = ("KH_typeI", "KH_typeII", "KH_typeIII", "KH_typeIV"); BEST_KH = min(KH, key=lambda a: N["s43_waic"][a])
EN = {"서울시": "Seoul", "경기도": "Gyeonggi-do", "충청남도": "Chungcheongnam-do", "충청북도": "Chungcheongbuk-do", "부산시": "Busan", "전라남도": "Jeollanam-do", "전라북도": "Jeollabuk-do",
      "광주시": "Gwangju", "경상남도": "Gyeongsangnam-do", "경상북도": "Gyeongsangbuk-do", "강원도": "Gangwon-do", "인천시": "Incheon", "대전시": "Daejeon", "울산시": "Ulsan", "대구시": "Daegu",
      "세종시": "Sejong", "제주도": "Jeju"}
def sidos(d, k=4): return ", ".join(f"{EN[a]} ({b})" for a, b in list(d.items())[:k])
TITLE = "Can notification maps guide tuberculosis case finding as incidence falls in Korea?"
RUNNING = "Mapping tuberculosis for case finding"
KEYWORDS = "tuberculosis; case finding; health policy; notification; spatial analysis; Korea"
assert len(TITLE.split()) <= 20 and ":" not in TITLE and "229" not in TITLE
SUP = {"methods": "Supplementary Appendix A", "covariates": "Supplementary Table S1", "lik": "Supplementary Table S2", "specs": "Supplementary Table S3", "forest": "Supplementary Fig. S1", "hot": "Supplementary Table S4", "strobe": "Supplementary Appendix B"}
sup = lambda k: SUP[k]
RET = N["ret"]
MVN = lambda v: f"{round(N['mv'][v]['cred_frac']*N['mv'][v]['n_specs'])}/{N['mv'][v]['n_specs']}"
A0 = lambda y: N["asr"][(y, "Both")]
GAP = N["gap"]
METHODS = [
("Study design and data",
 f"This ecological study covered all {N['n_districts']} districts (urban wards, cities and counties) of the Republic of Korea, harmonized to 2024 boundaries, from 2013 to 2025 ({N['n_rows']:,} district-years). "
 "Tuberculosis is a notifiable disease in Korea, and the national surveillance system collects notifications from all medical institutions [@lew2006an]; the Korea Disease Control and Prevention Agency (the national public health agency) publishes annual counts of new cases (people never treated or treated for less than 1 month, regardless of nationality) by district of residence from 2013 and nationally by sex and age group [@web:kdca2026tb]. "
 "The analysis excluded 2026 because the year was incomplete. Resident populations by sex and age came from resident registration, which covers Korean nationals [@web:mois2026population]. The analysis linked sources by administrative district code only "
 f"({sup('methods')}). The study used only published aggregate statistics."),
("Outcome and expected cases",
 "The outcome was the annual number of notified new tuberculosis cases by district of residence. The analysis obtained expected cases by indirect standardization, applying national new-case rates by year, sex and eight age groups (10-year groups to 70 years or older) to each district population; the ratio of observed to expected cases is the standardized incidence ratio (SIR) of notifications [@inskip1983methods]. "
 "Respiratory tuberculosis deaths by district, standardized in the same way, served as an auxiliary outcome."),
("District characteristics",
 f"The analysis plan fixed seven characteristics before fitting any covariate model (the plan was not registered), each expected to accompany more notifications ({sup('covariates')}). They were contextual district indicators rather than measures of individual risk: the share of households that are older adults living alone, a marker of older populations with less household support [@carauxpaz2021tuberculosis; @nordholm2022social]; "
 "Medical Aid type 1 patients (recipients of Korea's means-tested public coverage) per 100,000 residents, a marker of the poorest households [@choi2023lower; @nguipdopdjomo2020smallarea]; the share of national health-screening participants with suspected diabetes and the current smoking rate [@jeon2008diabetes; @yoo2021diabetes; @jee2009smoking]; "
 "foreign residents per 1,000 residents (log scale) [@lee2024incidence]; long-term care hospitals per 100,000 residents aged 65 years or older [@seto2017mycobacterium]; and general hospitals per 100,000 residents. "
 "Every model included five controls: urban population share, physicians per 1,000 residents, sex ratio, fiscal autonomy and the population share aged 80 years or older, the last also addressing ageing within the open-ended oldest age group. The analysis scaled all characteristics to standard deviation (SD) units over the district-year panel. The aim was to describe associations, not to estimate causal effects."),
("Statistical analysis",
 f"A prespecified comparison with Poisson in models with the forced controls only selected a negative binomial principal model; other likelihoods served as sensitivity analyses ({sup('lik')}). The model had an offset of log expected cases, a Besag–York–Mollié 2 district effect and year effects, and the analysis fitted it by integrated nested Laplace approximation in R 4.6.0 [@besag1991bayesian; @riebler2016an; @rue2009approximate]. "
 "The results report rate ratios (RRs) per 1 SD with 95% credible intervals (CrIs); the analysis called an association credible when its interval excluded 1, and robust when it was also credible in at least 75% of covariate-subset models containing it. "
 "Residual hot spots and cold spots were districts whose posterior probability of a residual spatial RR above 1 exceeded 0.95 or fell below 0.05; they describe excess after adjustment for the covariates and need not have high observed SIRs. The ratio of the 90th to the 10th percentile of annual smoothed district SIRs measured relative concentration, multiplying the percentiles by the national age-standardized rate gave the corresponding absolute difference, and Kendall's W measured persistence of rankings.",
 f"Robustness checks covered all {N['mv_total']} models formed by the subsets of the seven characteristics, in space–time interaction models, in separate calendar periods, by splitting each association into between-district and within-district components, in {len(N['alt_valid'])} alternative specifications of likelihood, temporal structure, lags, spatial confounding and odd or even years, and with three negative control exposures ({sup('methods')}; {sup('specs')}). "
 "Transport-injury deaths and patients treated for gastric cancer, which share the social gradients of Korean districts but not the pathogen, served as comparison outcomes, and the analysis computed E-values [@vanderweele2017sensitivity]. "
 f"Reporting follows the STROBE statement [@vonelm2007strengthening] ({sup('strobe')})."),
]

hot = sidos(N["hot_by_sido"], 5); cold = sidos(N["cold_by_sido"], 3)
AK = N["altk"]; NA = len(N["alt_valid"]); F15 = N["f15"]
ABS = lambda y: (GAP[y]['p90'] - GAP[y]['p10']) * A0(y)
S41 = lambda a, v: N["s41"][(a, v)]
RESULTS = [
("Notifications fell and shifted to older adults",
 f"From 2013 to 2025, medical institutions notified {N['cases_total']:,} new tuberculosis cases. Annual counts fell from {N['n_y'][2013]:,} to {N['n_y'][2025]:,} ({100*(1-N['n_y'][2025]/N['n_y'][2013]):.0f}% fewer), and the age-standardized rate fell from {A0(2013):.1f} to {A0(2025):.1f} per 100,000 ({100*(1-A0(2025)/A0(2013)):.0f}% lower; Fig. 1; Table 1). "
 f"The share of cases aged 65 years or older rose from {N['pct65'][2013]:.1f}% to {N['pct65'][2025]:.1f}%, and rates were highest at 70 years or older ({N['agerate'][('Men', '70세 이상')]:.1f} per 100,000 person-years in men and {N['agerate'][('Women', '70세 이상')]:.1f} in women; Fig. 1c)."),
("Relative differences widened and excess clustered",
 f"The ratio of the 90th to the 10th percentile of annual smoothed district SIRs rose from {GAP[2013]['ratio']:.2f} in 2013 to {GAP[2025]['ratio']:.2f} in 2025, the highest of the 13 years, whereas the corresponding absolute difference narrowed from {ABS(2013):.1f} to {ABS(2025):.1f} per 100,000 as rates fell. Annual district rankings were concordant (Kendall's W {N['kendall']['2013-2025']:.2f}), and spatial clustering increased (Moran's I {N['moran_y'][2013]:.2f} in 2013 and {N['moran_y'][2025]:.2f} in 2025). "
 f"In the pooled model, {N['n_hot']} districts were residual hot spots, most in {hot}, and {N['n_cold']} were residual cold spots, most in {cold} (Fig. 2; {sup('hot')}); hot spots included inner-city wards of Seoul and Daegu and counties of eastern Gangwon-do, inland Gyeongsangbuk-do and southwestern Jeollanam-do. In year-by-year emerging hot spot analysis, {N['ehsa'].get('Persistent hot', 0)} districts were persistent hot spots."),
("District characteristics",
 f"In the principal model, current smoking ({ci(SM)}), the share of older adults living alone ({ci(OS)}) and general hospitals ({ci(GH)}) were associated with more notifications; the association with suspected diabetes was borderline ({ci(DM)}) and that with foreign residents was not credible ({ci(FR)}) (Table 2). One SD corresponded to {N['sd'][SM]:.1f} percentage points of current smoking and {N['sd'][OS]:.1f} percentage points of households. "
 f"Medical Aid patients ({ci(MA)}) and long-term care hospitals ({ci(LTC)}) were not associated with notifications overall; Medical Aid patients were associated in 2020–2025 only ({tci(WIN(MA, 'W3_2020-25')[:3])}).",
 f"The smoking association was small but credible in {MVN(SM).replace('/', ' of ')} covariate subsets, in all four space–time models and in {AK[SM]} of {NA} alternative specifications; it was larger between districts ({tci(BW(SM + '__between'))}) than within districts over time ({tci(BW(SM + '__within'))}), and it was not credible with 1- or 2-year lags ({tci(S41('E1_lag1', SM)[:3])} and {tci(S41('E2_lag2', SM)[:3])}) or in 2020–2025 alone ({tci(WIN(SM, 'W3_2020-25')[:3])}) ({sup('forest')}). It was not associated with the comparison outcomes and was associated with respiratory tuberculosis deaths ({tci(N['tbd'][('TBD', SM)][:3])}). "
 f"The living-alone association was credible in all covariate subsets and space–time models, but only through its between-district component ({tci(BW(OS + '__between'))}; within {tci(BW(OS + '__within'))}). It was credible in 2013–2015 ({tci(WIN(OS, 'W1_2013-15')[:3])}), when values were partly interpolated from the 2010 census, but not in 2020–2025 ({tci(WIN(OS, 'W3_2020-25')[:3])}) or in 2015–2025, the years with observed values ({tci(F15[OS][:3])}); it was strongly correlated with the share aged 80 years or older. "
 f"Suspected diabetes was not credible in the best-fitting space–time model ({tci(S43('KH_typeII', DM))}). E-values for the point estimates were {N['evalue'][SM]['E_point']:.2f} for smoking and {N['evalue'][OS]['E_point']:.2f} for living alone ({sup('methods')})."),
]
