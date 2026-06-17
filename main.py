import streamlit as st
import pandas as pd

# ══════════════════════════════════════════════════════════════
#  파일명 (레포 루트에 그대로 올려주세요)
# ══════════════════════════════════════════════════════════════
FILE_SLEEP = "청소년.xlsx"
FILE_LIFE  = "청소년생활시간.xlsx"

# ══════════════════════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="청소년 건강 & 생활시간",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  전역 CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}
[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.85);
    border-right: 1px solid rgba(167,139,250,0.15);
}
.hero {
    background: linear-gradient(120deg,rgba(99,102,241,.22),rgba(168,85,247,.22));
    border: 1px solid rgba(168,85,247,.35);
    border-radius: 22px;
    padding: 2.2rem 2.5rem 1.9rem;
    text-align: center;
    margin-bottom: 1.8rem;
}
.hero h1 {
    font-size: 2.25rem; font-weight: 900; margin: 0 0 .45rem;
    background: linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.hero p { color: rgba(255,255,255,.52); font-size: .92rem; margin: 0; }
.kcard {
    background: rgba(255,255,255,.05);
    border: 1px solid rgba(255,255,255,.09);
    border-radius: 18px;
    padding: 1.25rem 1rem;
    text-align: center;
}
.kcard .klabel {
    font-size: .7rem; color: rgba(255,255,255,.42);
    text-transform: uppercase; letter-spacing: .08em; margin-bottom: .45rem;
}
.kcard .kval   { font-size: 1.95rem; font-weight: 800; color: #a78bfa; line-height: 1.1; }
.kcard .kval-s { font-size: 1.45rem; font-weight: 800; color: #a78bfa; line-height: 1.1; }
.pos { color: #34d399; font-size: .78rem; }
.neg { color: #f87171; font-size: .78rem; }
.sh {
    font-size: 1.03rem; font-weight: 700; color: #e2e8f0;
    padding-bottom: .45rem; margin: 1.7rem 0 .7rem;
    border-bottom: 1px solid rgba(255,255,255,.08);
}
.ibox {
    background: rgba(99,102,241,.11); border-left: 3px solid #6366f1;
    border-radius: 0 12px 12px 0; padding: .85rem 1.2rem;
    color: rgba(255,255,255,.77); font-size: .85rem; line-height: 1.7; margin-top: .5rem;
}
.wbox {
    background: rgba(251,191,36,.09); border-left: 3px solid #fbbf24;
    border-radius: 0 12px 12px 0; padding: .85rem 1.2rem;
    color: rgba(255,255,255,.77); font-size: .85rem; line-height: 1.7; margin-top: .5rem;
}
.gbox {
    background: rgba(52,211,153,.09); border-left: 3px solid #34d399;
    border-radius: 0 12px 12px 0; padding: .85rem 1.2rem;
    color: rgba(255,255,255,.77); font-size: .85rem; line-height: 1.7; margin-top: .5rem;
}
.tag {
    display:inline-block; background:rgba(167,139,250,.18); color:#a78bfa;
    border-radius:999px; padding:.16rem .7rem; font-size:.7rem;
    font-weight:600; margin:.15rem .15rem;
}
.divider { border-top:1px solid rgba(255,255,255,.07); margin:1.2rem 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  데이터 로드
# ══════════════════════════════════════════════════════════════
@st.cache_data
def load_sleep():
    try:
        raw = pd.read_excel(FILE_SLEEP, sheet_name="데이터", header=None)
    except Exception as e:
        st.error(f"❌ '{FILE_SLEEP}' 로드 실패: {e}")
        st.stop()
    df = raw.iloc[2:].copy()
    df.columns = ["시점","수면_전체","수면_남","수면_여",
                  "건강인지_전체","건강인지_남","건강인지_여"]
    df["시점"] = pd.to_numeric(df["시점"], errors="coerce")
    df = df.dropna(subset=["시점"])
    df["시점"] = df["시점"].astype(int)
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.reset_index(drop=True)


@st.cache_data
def load_life():
    try:
        raw = pd.read_excel(FILE_LIFE, sheet_name="데이터", header=None)
    except Exception as e:
        st.error(f"❌ '{FILE_LIFE}' 로드 실패: {e}")
        st.stop()

    def to_min(v):
        if pd.isna(v) or str(v).strip() == "-":
            return None
        s = str(v).strip()
        if ":" in s:
            h, m = s.split(":")
            return int(h) * 60 + int(m)
        return None

    years   = ["1999","2004","2009","2014","2019","2024"]
    row_map = {3:"필수생활시간", 4:"수면", 5:"식사및간식",
               8:"개인건강관리",  9:"개인위생및외모관리"}
    records = []
    for i, yr in enumerate(years):
        base = 2 + i * 12
        r = {"연도": int(yr)}
        for ridx, lbl in row_map.items():
            for gi, gk in enumerate(["계","남","여"]):
                r[f"{lbl}_{gk}"] = to_min(raw.iloc[ridx, base + gi])
            for dk, doff in [("평일",3),("토요일",6),("일요일",9)]:
                r[f"{lbl}_{dk}"] = to_min(raw.iloc[ridx, base + doff])
        records.append(r)
    return pd.DataFrame(records)


def fmt(m):
    if m is None or (isinstance(m, float) and pd.isna(m)):
        return "-"
    return f"{int(m)//60}시간 {int(m)%60:02d}분"


sleep_df = load_sleep()
life_df  = load_life()


# ══════════════════════════════════════════════════════════════
#  사이드바
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎛️ 탐색 메뉴")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    page = st.radio(
        "", ["🏠 종합 대시보드","🌙 수면 & 건강인지율","⏰ 필수생활시간"],
        label_visibility="collapsed",
    )
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if page == "🌙 수면 & 건강인지율":
        st.markdown("**📊 분석 필터**")
        gender_s = st.multiselect("성별", ["전체","남학생","여학생"],
                                  default=["전체","남학생","여학생"])
        ymin = int(sleep_df["시점"].min())
        ymax = int(sleep_df["시점"].max())
        yr   = st.slider("연도 범위", ymin, ymax, (ymin, ymax))

    elif page == "⏰ 필수생활시간":
        st.markdown("**📊 분석 필터**")
        g_raw   = st.selectbox("성별", ["전체","남자","여자"])
        g_key   = {"전체":"계","남자":"남","여자":"여"}[g_raw]
        daytype = st.selectbox("요일", ["요일평균","평일","토요일","일요일"])
        dt_key  = {"요일평균":"계","평일":"평일","토요일":"토요일","일요일":"일요일"}[daytype]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div style='font-size:.7rem;color:rgba(255,255,255,.28);line-height:1.85'>
    📌 질병관리청 청소년건강행태조사<br>
    📌 서울특별시 생활시간조사<br>
    🗓️ 기준: 2026.06.11
    </div>""", unsafe_allow_html=True)


# ── KPI 카드 헬퍼 ──
def kpi_card(label, val, delta, is_pos, small=False):
    vcls = "kval-s" if small else "kval"
    dcls = "pos" if is_pos else "neg"
    st.markdown(f"""<div class="kcard">
        <div class="klabel">{label}</div>
        <div class="{vcls}">{val}</div>
        <span class="{dcls}">{delta}</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  페이지 A — 종합 대시보드
# ══════════════════════════════════════════════════════════════
if page == "🏠 종합 대시보드":
    st.markdown("""<div class="hero">
        <h1>🌙 청소년 건강 & 생활시간 대시보드</h1>
        <p>청소년 수면·건강인지율 변화 추이 &amp; 서울시민 필수생활시간 25년 종합 분석</p>
    </div>""", unsafe_allow_html=True)

    ls  = sleep_df[sleep_df["시점"] == sleep_df["시점"].max()].iloc[0]
    ll  = life_df.iloc[-1]
    lf  = life_df.iloc[0]
    sv  = float(ls["수면_전체"])
    hv  = float(ls["건강인지_전체"]) if pd.notna(ls["건강인지_전체"]) else 0.0
    slv = int(ll["수면_계"])
    lv  = int(ll["필수생활시간_계"])
    dl  = lv - int(lf["필수생활시간_계"])

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("😴 수면 증감 (최신)", f"{sv:+.1f}h", "2007년 대비", sv >= 0)
    with c2: kpi_card("💪 건강인지율 증감", f"{hv:+.1f}%p", "2007년 대비", hv >= 0)
    with c3: kpi_card("🛌 2024 하루 수면", f"{slv//60}h{slv%60:02d}m", "서울시민 요일평균", True)
    with c4: kpi_card("⏱️ 2024 필수생활시간", f"{lv//60}h{lv%60:02d}m",
                      f"1999 대비 {'+' if dl>=0 else ''}{dl}분", dl >= 0)

    st.markdown("<br>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="sh">📉 청소년 수면시간 증감 추이 (2007=0 기준)</div>', unsafe_allow_html=True)
        sc = sleep_df[["시점","수면_전체","수면_남","수면_여"]].set_index("시점")
        sc.columns = ["전체","남학생","여학생"]
        st.line_chart(sc, use_container_width=True, height=255)
        st.markdown('<div class="wbox">⚠️ 2017년 이후 지속 감소. 여학생(-0.4h) 감소폭이 남학생(-0.2h)의 2배.</div>', unsafe_allow_html=True)

    with cb:
        st.markdown('<div class="sh">💪 주관적 건강인지율 증감 추이 (2007=0 기준)</div>', unsafe_allow_html=True)
        hc = sleep_df[["시점","건강인지_전체","건강인지_남","건강인지_여"]].set_index("시점")
        hc.columns = ["전체","남학생","여학생"]
        st.area_chart(hc, use_container_width=True, height=255)
        st.markdown('<div class="ibox">🔍 2015년 정점 이후 하락 반전. 여학생은 2021년부터 기준치(0) 아래로 진입.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">⏱️ 서울시민 필수생활시간 구성 변화 (분, 1999→2024)</div>', unsafe_allow_html=True)
    bd = life_df[["연도","수면_계","식사및간식_계","개인위생및외모관리_계","개인건강관리_계"]].set_index("연도")
    bd.columns = ["수면","식사 및 간식","개인위생·외모","개인건강관리"]
    st.bar_chart(bd, use_container_width=True, height=285)
    st.markdown('<div class="gbox">📈 1999년 617분 → 2024년 682분. 25년간 <strong>65분</strong> 증가. 수면이 전체의 약 70% 차지.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">🔗 수면 감소 ↔ 건강인지율 변화 상관 분석</div>', unsafe_allow_html=True)
    scat = sleep_df[["수면_전체","건강인지_전체"]].dropna()
    scat.columns = ["수면 증감(h)","건강인지율 증감(%p)"]
    st.scatter_chart(scat, x="수면 증감(h)", y="건강인지율 증감(%p)", use_container_width=True, height=250)
    if len(scat) > 1:
        corr = scat.corr().iloc[0, 1]
        st.markdown(f'<div class="ibox">📐 피어슨 상관계수 <strong>{corr:.3f}</strong> — 수면시간 변화와 건강인지율 변화가 같은 방향으로 움직이는 경향이 있습니다.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  페이지 B — 수면 & 건강인지율
# ══════════════════════════════════════════════════════════════
elif page == "🌙 수면 & 건강인지율":
    st.markdown("""<div class="hero">
        <h1>🌙 수면 & 주관적 건강인지율</h1>
        <p>질병관리청 청소년건강행태조사 · 2007년 대비 증감 분석</p>
    </div>""", unsafe_allow_html=True)

    fdf = sleep_df[(sleep_df["시점"] >= yr[0]) & (sleep_df["시점"] <= yr[1])].copy()
    gm  = {"전체":("수면_전체","건강인지_전체"),
           "남학생":("수면_남","건강인지_남"),
           "여학생":("수면_여","건강인지_여")}

    st.markdown('<div class="sh">😴 주중 평균 수면시간 증감 (h)</div>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="tag">📌 2007 기준 = 0</span>'
        f'<span class="tag">📅 {yr[0]}~{yr[1]}</span>'
        + "".join(f'<span class="tag">{g}</span>' for g in gender_s),
        unsafe_allow_html=True,
    )
    if gender_s:
        sc2 = fdf[["시점"] + [gm[g][0] for g in gender_s]].set_index("시점")
        sc2.columns = gender_s
        st.line_chart(sc2, use_container_width=True, height=290)

    c1, c2, c3 = st.columns(3)
    for col, g in zip([c1,c2,c3], ["전체","남학생","여학생"]):
        scol  = gm[g][0]
        vals  = fdf[scol].dropna()
        v     = float(vals.iloc[-1]) if len(vals) else 0.0
        worst = int(fdf.loc[fdf[scol].idxmin(),"시점"]) if len(vals) else "-"
        with col:
            st.metric(f"{'🔴' if v<0 else '🟢'} {g}", f"{v:+.2f}h",
                      f"최저: {worst}년", delta_color="inverse")

    st.markdown('<div class="sh">💪 주관적 건강인지율 증감 (%p)</div>', unsafe_allow_html=True)
    if gender_s:
        hc2 = fdf[["시점"] + [gm[g][1] for g in gender_s]].set_index("시점")
        hc2.columns = gender_s
        st.area_chart(hc2, use_container_width=True, height=290)

    c1, c2, c3 = st.columns(3)
    for col, g in zip([c1,c2,c3], ["전체","남학생","여학생"]):
        hcol = gm[g][1]
        vals = fdf[hcol].dropna()
        v    = float(vals.iloc[-1]) if len(vals) else 0.0
        best = int(fdf.loc[fdf[hcol].idxmax(),"시점"]) if len(vals) else "-"
        with col:
            st.metric(f"{'🔴' if v<0 else '🟢'} {g}", f"{v:+.1f}%p", f"최고: {best}년")

    st.markdown('<div class="sh">👫 남·여학생 비교 — 최근 5개년</div>', unsafe_allow_html=True)
    last5 = fdf.tail(5).set_index("시점")
    ca2, cb2 = st.columns(2)
    with ca2:
        st.caption("😴 수면시간 증감 (h)")
        st.bar_chart(last5[["수면_남","수면_여"]].rename(
            columns={"수면_남":"남학생","수면_여":"여학생"}),
            use_container_width=True, height=230)
    with cb2:
        st.caption("💪 건강인지율 증감 (%p)")
        st.bar_chart(last5[["건강인지_남","건강인지_여"]].rename(
            columns={"건강인지_남":"남학생","건강인지_여":"여학생"}),
            use_container_width=True, height=230)

    st.markdown('<div class="sh">🔗 수면 vs 건강인지율 상관 (선택 기간)</div>', unsafe_allow_html=True)
    scat2 = fdf[["수면_전체","건강인지_전체"]].dropna()
    scat2.columns = ["수면 증감(h)","건강인지율 증감(%p)"]
    st.scatter_chart(scat2, x="수면 증감(h)", y="건강인지율 증감(%p)",
                     use_container_width=True, height=260)
    if len(scat2) > 1:
        corr2 = scat2.corr().iloc[0, 1]
        st.markdown(
            f'<div class="ibox">📐 선택 기간 피어슨 상관계수: <strong>{corr2:.3f}</strong> '
            f'— {"정(+)의 상관 (수면↑ → 건강인지율↑)" if corr2>0 else "부(-)의 상관"}</div>',
            unsafe_allow_html=True)

    with st.expander("📋 원본 데이터 테이블"):
        disp = fdf.copy()
        disp.columns = ["연도","수면(전체)","수면(남)","수면(여)",
                        "건강인지(전체)","건강인지(남)","건강인지(여)"]
        st.dataframe(disp.set_index("연도"), use_container_width=True)


# ══════════════════════════════════════════════════════════════
#  페이지 C — 필수생활시간
# ══════════════════════════════════════════════════════════════
elif page == "⏰ 필수생활시간":
    st.markdown("""<div class="hero">
        <h1>⏰ 서울시민 필수생활시간</h1>
        <p>서울특별시 생활시간조사 · 1999~2024년 5년 주기 분석</p>
    </div>""", unsafe_allow_html=True)

    suffix = g_key if dt_key == "계" else dt_key
    items  = {
        "필수생활시간":      f"필수생활시간_{suffix}",
        "수면":             f"수면_{suffix}",
        "식사 및 간식":     f"식사및간식_{suffix}",
        "개인건강관리":      f"개인건강관리_{suffix}",
        "개인위생·외모관리": f"개인위생및외모관리_{suffix}",
    }
    emos = ["🕐","😴","🍽️","💊","🚿"]
    ll2  = life_df.iloc[-1]
    lf2  = life_df.iloc[0]

    cols5 = st.columns(5)
    for col, (lbl, key), em in zip(cols5, items.items(), emos):
        vn = ll2.get(key)
        vf = lf2.get(key)
        dm = int(vn) - int(vf) if (vn is not None and vf is not None) else None
        ds = (f"{'+' if (dm or 0)>=0 else ''}{dm}분") if dm is not None else "-"
        dc = "pos" if (dm or 0) >= 0 else "neg"
        with col:
            st.markdown(f"""<div class="kcard">
                <div class="klabel">{em} {lbl}</div>
                <div class="kval-s">{fmt(vn)}</div>
                <span class="{dc}">{ds} vs 1999</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ldisp = f"{daytype} / {g_raw}"
    st.markdown(f'<div class="sh">📈 항목별 시간 추이 — {ldisp} (분)</div>', unsafe_allow_html=True)
    sub = {k: v for k, v in items.items() if k != "필수생활시간"}
    vld = {k: v for k, v in sub.items() if v in life_df.columns}
    tdf = life_df[["연도"] + list(vld.values())].set_index("연도")
    tdf.columns = list(vld.keys())
    st.line_chart(tdf, use_container_width=True, height=295)
    st.markdown('<div class="ibox">🔍 모든 항목이 1999→2019 지속 증가 후 2024년 소폭 조정. 개인위생·외모 시간 증가폭이 가장 두드러집니다.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">📊 연도별 절댓값 비교 (분)</div>', unsafe_allow_html=True)
    st.bar_chart(tdf, use_container_width=True, height=265)

    st.markdown('<div class="sh">📅 2024년 요일별 항목 비교 (분)</div>', unsafe_allow_html=True)
    row24  = life_df[life_df["연도"] == 2024].iloc[0]
    dmap   = {"요일평균":"계","평일":"평일","토요일":"토요일","일요일":"일요일"}
    si     = ["수면","식사및간식","개인위생및외모관리","개인건강관리"]
    sl     = ["수면","식사 및 간식","개인위생·외모","개인건강관리"]
    ddata  = {dl: [row24.get(f"{s}_{dk}") for s in si] for dl, dk in dmap.items()}
    day_df = pd.DataFrame(ddata, index=sl).T
    st.bar_chart(day_df, use_container_width=True, height=260)

    wk  = int(row24.get("수면_평일")  or 0)
    sat = int(row24.get("수면_토요일") or 0)
    sun = int(row24.get("수면_일요일") or 0)
    st.markdown(
        f'<div class="gbox">🛋️ 2024년 일요일 수면은 평일보다 <strong>{sun-wk}분</strong>, '
        f'토요일보다 <strong>{sun-sat}분</strong> 더 깁니다. 주말 수면 보충 패턴이 뚜렷합니다.</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="sh">👫 연도별 수면시간 성별 비교 (요일평균, 분)</div>', unsafe_allow_html=True)
    gc = life_df[["연도","수면_계","수면_남","수면_여"]].set_index("연도")
    gc.columns = ["전체","남자","여자"]
    st.line_chart(gc, use_container_width=True, height=245)
    st.markdown('<div class="wbox">⚠️ 여자가 남자보다 수면시간이 일관되게 깁니다. 2024년엔 남녀 모두 2019년 대비 소폭 감소.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sh">🥧 2024년 필수생활시간 구성 비율</div>', unsafe_allow_html=True)
    total = int(row24.get("필수생활시간_계") or 1)
    comp  = {
        "수면":          int(row24.get("수면_계") or 0),
        "식사 및 간식":  int(row24.get("식사및간식_계") or 0),
        "개인위생·외모": int(row24.get("개인위생및외모관리_계") or 0),
        "개인건강관리":  int(row24.get("개인건강관리_계") or 0),
    }
    pct_df = pd.DataFrame({
        "분":      list(comp.values()),
        "비율(%)": [round(v / total * 100, 1) for v in comp.values()],
    }, index=list(comp.keys()))
    st.dataframe(pct_df, use_container_width=True)
    st.bar_chart(pct_df[["분"]], use_container_width=True, height=200)

    with st.expander("📋 전체 원본 데이터 (분 단위)"):
        sc2 = ["연도"] + [v for v in items.values() if v in life_df.columns]
        st.dataframe(life_df[sc2].set_index("연도"), use_container_width=True)
