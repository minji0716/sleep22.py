import streamlit as st
import pandas as pd

st.set_page_config(page_title="필수생활시간 분석", page_icon="🕐", layout="wide")

st.title("🕐 필수생활시간 분석")
st.caption("출처: 서울특별시 생활시간조사 | 단위: 시간:분")
st.markdown("---")

# ── 데이터 로드 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_excel(
        "필수생활시간.xlsx",
        sheet_name="데이터",
        header=None,
    )

    # 헤더 행: 0=행동분류(1), 1=행동분류(2), 이후는 연도/요일/성별 3단 헤더
    years   = []  # row 0 (index 0)
    daytype = []  # row 1
    gender  = []  # row 2

    for col_idx in range(2, df_raw.shape[1]):
        years.append(str(df_raw.iloc[0, col_idx]))
        daytype.append(str(df_raw.iloc[1, col_idx]))
        gender.append(str(df_raw.iloc[2, col_idx]))

    # 데이터 행: row 3 이후
    records = []
    for _, row in df_raw.iloc[3:].iterrows():
        cat1 = str(row.iloc[0]).strip()
        cat2 = str(row.iloc[1]).strip()
        for i, (y, d, g) in enumerate(zip(years, daytype, gender)):
            val = row.iloc[2 + i]
            records.append({
                "대분류": cat1,
                "소분류": cat2,
                "연도": int(y) if y.isdigit() else y,
                "요일": d,
                "성별": g,
                "시간_원본": str(val),
            })

    df = pd.DataFrame(records)

    # 시간 문자열(H:MM) → 분으로 변환
    def to_minutes(t):
        try:
            parts = str(t).split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return None

    df["분"] = df["시간_원본"].apply(to_minutes)
    df = df[df["분"].notna()]
    return df


df = load_data()

# ── 사이드바 필터 ─────────────────────────────────────────────
st.sidebar.header("🔧 필터")

years_avail = sorted(df["연도"].unique())
sel_years   = st.sidebar.multiselect("연도 선택", years_avail, default=years_avail)

daytypes_avail = sorted(df["요일"].unique())
sel_day = st.sidebar.selectbox("요일 구분", daytypes_avail)

genders_avail = sorted(df["성별"].unique())
sel_gender = st.sidebar.selectbox("성별", genders_avail)

# 대분류 목록 (NaN·공백 제외)
cats = [c for c in df["대분류"].unique() if c not in ("nan", "", "행동분류별(1)")]
sel_cats = st.sidebar.multiselect("행동 대분류", cats, default=cats)

# ── 필터 적용 ─────────────────────────────────────────────────
mask = (
    df["연도"].isin(sel_years)
    & (df["요일"] == sel_day)
    & (df["성별"] == sel_gender)
    & df["대분류"].isin(sel_cats)
    & (df["소분류"] == "소계")
)
filtered = df[mask].copy()

# ── 요약 지표 ─────────────────────────────────────────────────
if not filtered.empty:
    col1, col2, col3 = st.columns(3)
    total_avg = filtered["분"].mean()
    sleep_avg = df[mask & (df["대분류"] == "수면")]["분"].mean() if "수면" in sel_cats else 0
    meal_avg  = df[mask & (df["대분류"] == "식사 및 간식 섭취")]["분"].mean() if "식사 및 간식 섭취" in sel_cats else 0

    col1.metric("📊 평균 필수생활시간", f"{int(total_avg // 60)}h {int(total_avg % 60)}m" if total_avg else "-")
    col2.metric("😴 평균 수면시간", f"{int(sleep_avg // 60)}h {int(sleep_avg % 60)}m" if sleep_avg else "-")
    col3.metric("🍽️ 평균 식사시간", f"{int(meal_avg // 60)}h {int(meal_avg % 60)}m" if meal_avg else "-")

st.markdown("---")

# ── 차트 1: 연도별 추이 (꺾은선) ─────────────────────────────
st.subheader("📈 연도별 필수생활시간 추이 (분)")

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
else:
    pivot = (
        filtered.groupby(["연도", "대분류"])["분"]
        .mean()
        .reset_index()
        .pivot(index="연도", columns="대분류", values="분")
    )
    st.line_chart(pivot)

st.markdown("---")

# ── 차트 2: 대분류별 막대 (연도 평균) ────────────────────────
st.subheader("📊 행동 대분류별 평균 시간 (분)")

bar_data = (
    filtered.groupby("대분류")["분"]
    .mean()
    .rename("평균(분)")
    .reset_index()
    .set_index("대분류")
)
if bar_data.empty:
    st.warning("데이터가 없습니다.")
else:
    st.bar_chart(bar_data)

st.markdown("---")

# ── 차트 3: 성별 비교 (선택 연도 전체 평균) ──────────────────
st.subheader("👥 성별 비교 – 행동 대분류별 평균 시간 (분)")

gender_data = (
    df[
        df["연도"].isin(sel_years)
        & (df["요일"] == sel_day)
        & df["대분류"].isin(sel_cats)
        & (df["소분류"] == "소계")
        & df["성별"].isin(["남자", "여자"])
    ]
    .groupby(["성별", "대분류"])["분"]
    .mean()
    .reset_index()
    .pivot(index="대분류", columns="성별", values="분")
)

if gender_data.empty:
    st.warning("성별 비교 데이터가 없습니다.")
else:
    st.bar_chart(gender_data)

st.markdown("---")

# ── 원본 데이터 테이블 ────────────────────────────────────────
with st.expander("🗂️ 원본 데이터 보기"):
    show = filtered[["연도", "요일", "성별", "대분류", "소분류", "시간_원본", "분"]].sort_values(["연도", "대분류"])
    st.dataframe(show, use_container_width=True)

st.caption("데이터 출처: 서울특별시 생활시간조사 (stat.eseoul.go.kr)")
import streamlit as st
import pandas as pd

st.set_page_config(page_title="청소년 수면시간 분석", page_icon="😴", layout="wide")

st.title("😴 청소년 수면시간 및 건강 인지율 분석")
st.caption("출처: 질병관리청 청소년건강행태조사 | 2007년 대비 증감값")
st.markdown("---")

# ── 데이터 로드 ──────────────────────────────────────────────
@st.cache_data
def load_data():
    df_raw = pd.read_excel(
        "청소년_수면시간.xlsx",
        sheet_name="데이터",
        header=None,
    )

    # row 0: 대항목명, row 1: 세부항목(전체/남학생/여학생), row 2~: 데이터
    col_labels = []
    for col_idx in range(1, df_raw.shape[1]):
        cat  = str(df_raw.iloc[0, col_idx]).strip()
        sub  = str(df_raw.iloc[1, col_idx]).strip()
        col_labels.append(f"{cat}_{sub}")

    records = []
    for _, row in df_raw.iloc[2:].iterrows():
        year_val = row.iloc[0]
        try:
            year = int(year_val)
        except Exception:
            continue
        entry = {"연도": year}
        for i, label in enumerate(col_labels):
            raw = row.iloc[1 + i]
            try:
                entry[label] = float(raw)
            except Exception:
                entry[label] = None
        records.append(entry)

    return pd.DataFrame(records)


df = load_data()

# ── 컬럼 정의 ─────────────────────────────────────────────────
SLEEP_COLS  = {
    "전체":   "주중 평균 수면시간 (시간)_전체",
    "남학생": "주중 평균 수면시간 (시간)_남학생",
    "여학생": "주중 평균 수면시간 (시간)_여학생",
}
HEALTH_COLS = {
    "전체":   "주관적 건강 인지율 (%)_전체",
    "남학생": "주관적 건강 인지율 (%)_남학생",
    "여학생": "주관적 건강 인지율 (%)_여학생",
}

# ── 사이드바 필터 ─────────────────────────────────────────────
st.sidebar.header("🔧 필터")

years_avail = sorted(df["연도"].dropna().unique())
sel_years = st.sidebar.slider(
    "연도 범위",
    min_value=int(min(years_avail)),
    max_value=int(max(years_avail)),
    value=(int(min(years_avail)), int(max(years_avail))),
)

sel_groups = st.sidebar.multiselect(
    "성별 그룹",
    options=["전체", "남학생", "여학생"],
    default=["전체", "남학생", "여학생"],
)

# ── 필터 적용 ─────────────────────────────────────────────────
mask = (df["연도"] >= sel_years[0]) & (df["연도"] <= sel_years[1])
filtered = df[mask].copy().set_index("연도")

# ── 요약 지표 ─────────────────────────────────────────────────
latest_year = filtered.index.max()
latest = filtered.loc[latest_year]

col1, col2, col3 = st.columns(3)
col1.metric(
    f"😴 수면시간 증감 (전체, {latest_year}년)",
    f"{latest.get(SLEEP_COLS['전체'], 0):+.1f}h",
    help="2007년 대비 증감"
)
col2.metric(
    f"💪 건강 인지율 증감 (남학생, {latest_year}년)",
    f"{latest.get(HEALTH_COLS['남학생'], 0):+.1f}%p",
)
col3.metric(
    f"💪 건강 인지율 증감 (여학생, {latest_year}년)",
    f"{latest.get(HEALTH_COLS['여학생'], 0):+.1f}%p",
)

st.markdown("---")

# ── 차트 1: 수면시간 증감 추이 ────────────────────────────────
st.subheader("📈 주중 평균 수면시간 변화 (2007년 대비 증감, 시간)")

sleep_chart_cols = {k: SLEEP_COLS[k] for k in sel_groups if k in SLEEP_COLS}
if sleep_chart_cols:
    sleep_df = filtered[[v for v in sleep_chart_cols.values() if v in filtered.columns]].copy()
    sleep_df.columns = list(sleep_chart_cols.keys())
    sleep_df = sleep_df.dropna(how="all")
    if sleep_df.empty:
        st.warning("수면시간 데이터가 없습니다.")
    else:
        st.line_chart(sleep_df)
else:
    st.warning("성별 그룹을 선택하세요.")

st.markdown("---")

# ── 차트 2: 건강 인지율 증감 추이 ────────────────────────────
st.subheader("📈 주관적 건강 인지율 변화 (2007년 대비 증감, %p)")

health_chart_cols = {k: HEALTH_COLS[k] for k in sel_groups if k in HEALTH_COLS}
if health_chart_cols:
    health_df = filtered[[v for v in health_chart_cols.values() if v in filtered.columns]].copy()
    health_df.columns = list(health_chart_cols.keys())
    health_df = health_df.dropna(how="all")
    if health_df.empty:
        st.warning("건강 인지율 데이터가 없습니다.")
    else:
        st.line_chart(health_df)
else:
    st.warning("성별 그룹을 선택하세요.")

st.markdown("---")

# ── 차트 3: 특정 연도 성별 비교 막대 ─────────────────────────
st.subheader("📊 특정 연도 성별 비교")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**수면시간 증감 (시간)**")
    bar_sleep = {}
    for g in sel_groups:
        col_name = SLEEP_COLS.get(g)
        if col_name and col_name in filtered.columns:
            bar_sleep[g] = filtered[col_name]
    if bar_sleep:
        st.bar_chart(pd.DataFrame(bar_sleep))
    else:
        st.info("데이터 없음")

with col_b:
    st.markdown("**건강 인지율 증감 (%p)**")
    bar_health = {}
    for g in sel_groups:
        col_name = HEALTH_COLS.get(g)
        if col_name and col_name in filtered.columns:
            bar_health[g] = filtered[col_name].dropna()
    if bar_health:
        st.bar_chart(pd.DataFrame(bar_health))
    else:
        st.info("데이터 없음")

st.markdown("---")

# ── 상관관계 산점도 (area chart 대용) ────────────────────────
st.subheader("📉 수면시간 vs 건강 인지율 – 전체 연도 추세 비교")
st.caption("수면시간(파란선)과 건강 인지율(주황선)을 같은 축에 표시 (단위 상이 – 참고용)")

if SLEEP_COLS["전체"] in filtered.columns and HEALTH_COLS["전체"] in filtered.columns:
    combo = filtered[[SLEEP_COLS["전체"], HEALTH_COLS["전체"]]].dropna()
    combo.columns = ["수면시간 증감(h)", "건강 인지율 증감(%p)"]
    st.area_chart(combo)
else:
    st.warning("비교 데이터를 불러올 수 없습니다.")

st.markdown("---")

# ── 원본 데이터 테이블 ────────────────────────────────────────
with st.expander("🗂️ 원본 데이터 보기"):
    show_cols = ["연도"] + list(SLEEP_COLS.values()) + list(HEALTH_COLS.values())
    show_cols = [c for c in show_cols if c in df.columns or c == "연도"]
    show_df = df[mask][show_cols].reset_index(drop=True)
    show_df.columns = (
        ["연도"]
        + [f"수면({k})" for k in SLEEP_COLS]
        + [f"건강인지({k})" for k in HEALTH_COLS]
    )
    st.dataframe(show_df, use_container_width=True)

st.caption("데이터 출처: 질병관리청 청소년건강행태조사 (stat.eseoul.go.kr)")
