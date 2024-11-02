import streamlit as st
import json
import statistics as stats
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import graphviz as gv




with open("data/data-2006-2024.json", "r", encoding="UTF-8") as file:
    data = json.load(file)

contests = data["contests"]
regions = data["regions"]
countries = data["countries"]
cstats = data["stats"]

years = [int(x) for x in contests]

minimal = 2010
maximal = max(years)

def get_contests_from_period(first=minimal, last=maximal):
    return {x: y for x, y in contests.items() if first <= int(x) <= last}

def get_university_participations(university, contests):
    cu = {}
    for y, c in contests.items():
        for u in c:
            if u["university"] == university:
                cu[y] = u
    return cu

def get_university_graph(university_contest, name):
    g1 = gv.Digraph(name + "-parent")
    c1 = gv.Digraph(name + "-child")
    c1.attr(rank="same")
    for y in range(2010, 2025):
        if not str(y) in university_contest:
            c1.node(str(y), shape="square")
        else:
            c1.node(str(y), shape="square", style="filled", fillcolor="#40e0d0")
    fr = 2010
    for y in range(2011, 2025):
        c1.edge(str(fr), str(y), style="invis")
        fr = y
    for y1 in range(2010, 2024):
        for y2 in range(y1 + 1, 2025):
            if (str(y1) in university_contest) and (str(y2) in university_contest):
                s1 = set(university_contest[str(y1)]["players"])
                s2 = set(university_contest[str(y2)]["players"])
                s = s1.intersection(s2)
                if len(s) != 0:
                    c1.edge(str(y1), str(y2), label=str(len(s)))
    g1.subgraph(c1)
    return g1

with st.container(border=True):
    st.text("Participaciones por país")

    with st.expander("Parámetros:"):

        first, last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
        )

        participations = [i for i in range(1, 16)]

        min_parts = st.selectbox(
            "Seleccione la cantidad de participaciones mínima",
            options=participations,
            index=9,
        )



        d_regions = {regions[x]["spanish_name"]: x for x in regions}
        n_regions = ["Todas"] + [x for x in d_regions]

        s_regions = st.multiselect(
            "Selecione las regiones", options=n_regions, default=["Todas"]
        )

    with st.expander("Gráfico:"):
        c_countries = {}
        for year in range(first, last + 1):
            year = str(year)
            country_set = set()
            for team in contests[year]:
                c = team["country"]
                if not c in country_set:
                    country_set.add(c)
                    if c in c_countries:
                        c_countries[c] += 1
                    else:
                        c_countries[c] = 1

        if "Todas" not in s_regions:
            c_countries = {
                x: y
                for x, y in c_countries.items()
                if regions[countries[x]["region"]]["spanish_name"] in s_regions
            }

        x_c = []
        y_c = []
        c_items = [i for i in c_countries.items() if i[1] >= min_parts]
        c_items.sort(key=lambda x: x[1])

        for item in c_items:
            x_c.append(item[1])
            y_c.append(item[0])

        fig = go.Figure(go.Bar(x=x_c, y=y_c, orientation="h"))

        fig.update_layout(
            margin={"t": 0, "l": 0},
            height=450 if 450 > 18 * len(x_c) else 18 * len(x_c),
        )

        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.text("Participaciones por universidades")

    with st.expander("Parámetros:"):

        u_first, u_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="u_part_period",
        )

        u_participations = [i for i in range(1, 16)]


        u_min_parts = st.selectbox(
            "Seleccione la cantidad de participaciones mínima",
            options=u_participations,
            index=9,
            key="u_part_min",
        )

        u_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        u_n_regions = ["Todas"] + [x for x in u_d_regions]

        u_s_regions = st.multiselect(
            "Selecione las regiones",
            options=u_n_regions,
            default=["Todas"],
            key="u_part_regions",
        )

    with st.expander("Gráfico:"):
        universities = {}
        for year in range(u_first, u_last + 1):
            year = str(year)
            for team in contests[year]:
                c = team["university"]
                if c in universities:
                    universities[c]["count"] += 1
                else:
                    universities[c] = {"count": 1, "country": team["country"]}

        if "Todas" not in u_s_regions:
            universities = {
                x: y
                for x, y in universities.items()
                if regions[countries[y["country"]]["region"]]["spanish_name"]
                in u_s_regions
            }

        x_u = []
        y_u = []
        u_items = [i for i in universities.items() if i[1]["count"] >= u_min_parts]
        u_items.sort(key=lambda x: x[1]["count"])
        for item in u_items:
            x_u.append(item[1]["count"])
            y_u.append(item[0])

        fig_u = go.Figure(go.Bar(x=x_u, y=y_u, orientation="h"))

        fig_u.update_layout(
            margin={"t": 0, "l": 0},
            height=700 if 700 > 18 * len(x_u) else 18 * len(x_u),
        )

        st.plotly_chart(fig_u, use_container_width=True)

with st.container(border=True):
    st.text("Problemas resueltos por universidad")

    with st.expander("Parámetros:"):
        p_first, p_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="p_part_period",
        )

        p_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        p_n_regions = ["Todas"] + [x for x in p_d_regions]

        p_s_regions = st.multiselect(
            "Selecione las regiones para estadísticas generales",
            options=p_n_regions,
            default=["Todas"],
            key="p_part_regions",
        )

        p_contests = get_contests_from_period(p_first, p_last)

        m_p_univs = (
            st.session_state["m_p_univs"] if "m_p_univs" in st.session_state else []
        )

        p_univs = set()
        for x, c in p_contests.items():
            for team in c:
                p_univs.add(team["university"])

        p_univs = st.multiselect(
            "Selecciona las universidades:",
            options=list(p_univs),
        )
        

    with st.expander("Gráfico:"):
        p_max = []
        p_mode = []
        p_mean = []
        p_median = []
        p_min = []
        d_univs = {u: [] for u in p_univs}

        for x, c in p_contests.items():
            l_univs = [i for i in p_univs]
            p_solves = []
            for team in c:
                if team["university"] in l_univs:
                    d_univs[team["university"]].append(team["solved"])
                    l_univs.remove(team["university"])
                if "Todas" not in p_s_regions:
                    c_reg = regions[countries[team["country"]]["region"]][
                        "spanish_name"
                    ]
                    if c_reg in p_s_regions:
                        p_solves.append(int(team["solved"]))
                else:
                    p_solves.append(int(team["solved"]))
            for u in l_univs:
                d_univs[u].append(None)
            if len(p_solves) != 0:
                p_max.append(max(p_solves))
                p_min.append(min(p_solves))
                p_mode.append(stats.mode(p_solves))
                p_mean.append(stats.mean(p_solves))
                p_median.append(round(stats.median(p_solves)))

        years = [y for y in range(p_first, p_last + 1)]
        pfig = go.Figure()
        pfig.add_trace(
            go.Scatter(x=years, y=p_min, name="Mínimo", mode="lines+markers")
        )
        pfig.add_trace(
            go.Scatter(x=years, y=p_max, name="Máximo", mode="lines+markers")
        )
        pfig.add_trace(go.Scatter(x=years, y=p_mode, name="Moda", mode="lines+markers"))
        pfig.add_trace(
            go.Scatter(x=years, y=p_median, name="Mediana", mode="lines+markers")
        )
        pfig.add_trace(
            go.Scatter(x=years, y=p_mean, name="Media", mode="lines+markers")
        )
        for u, s in d_univs.items():
            pfig.add_bar(x=years, y=s, name=u)
        pfig.update_xaxes(showgrid=True, dtick=1)
        pfig.update_layout(
            legend=dict(orientation="h"),
            margin={"t": 0, "l": 0},
            xaxis_title="Ediciones",
            yaxis_title="Problemas resueltos",
        )
        st.plotly_chart(pfig, use_container_width=True)

with st.container(border=True):
    st.text("Lugar general por universidades")

    with st.expander("Parámetros:"):
        po_first, po_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="po_period",
        )

        po_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        po_n_regions = ["Todas"] + [x for x in po_d_regions]

        po_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=p_n_regions,
            default=["Todas"],
            key="po_part_regions",
        )

        po_contests = get_contests_from_period(po_first, po_last)

        po_univs = set()
        for x, c in po_contests.items():
            for team in c:
                if (
                    "Todas" in po_s_region
                    or regions[countries[team["country"]]["region"]]["spanish_name"]
                    in po_s_region
                ):
                    po_univs.add(team["university"])

        po_univs = st.multiselect(
            "Selecciona las universidades:",
            options=list(po_univs),
            key="po_multiselect",
            # default=m_p_univs
        )

    with st.expander("Gráficos:"):
        pu_univs = {u: {"place": [], "solved": []} for u in po_univs}
        quartiles4 = []
        quantities = {int(x): [] for x in po_contests}
        for x, c in po_contests.items():
            lo_univs = [i for i in pu_univs]
            ind = 0
            for t in c:
                if (
                    "Todas" in po_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in po_s_region
                ):
                    ind += 1
                    quantities[int(x)].append(int(t["solved"]))
                    if t["university"] in lo_univs:
                        pu_univs[t["university"]]["place"].append(ind)
                        pu_univs[t["university"]]["solved"].append(int(t["solved"]))
                        lo_univs.remove(t["university"])
            quartiles4.append(ind)
            for u in lo_univs:
                pu_univs[u]["place"].append(None)
                pu_univs[u]["solved"].append(None)

        years = [y for y in range(po_first, po_last + 1)]
        quartiles1 = []
        quartiles2 = []
        quartiles3 = []
        for n in quartiles4:
            quartiles1.append(int(n / 4))
            quartiles2.append(int(n / 4 * 2))
            quartiles3.append(int(n / 4 * 3))
        po_fig = go.Figure()
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles1,
                name="Cuartil 1",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(130, 200, 254, 0.5)",
                line=dict(color="rgba(130, 200, 254, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles2,
                name="Cuartil 2",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(0, 101, 195, 0.5)",
                line=dict(color="rgba(0, 101, 195, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles3,
                name="Cuartil 3",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(255, 171, 171, 0.5)",
                line=dict(color="rgba(255, 171, 171, 1)"),
            )
        )
        po_fig.add_trace(
            go.Scatter(
                x=years,
                y=quartiles4,
                name="Cuartil 4",
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(250, 42, 42, 0.5)",
                line=dict(color="rgba(250, 42, 42, 1)"),
            )
        )
        for u, v in pu_univs.items():
            po_fig.add_trace(go.Scatter(x=years, y=v["place"], name=u, mode="markers"))
        po_fig.update_xaxes(showgrid=True, dtick=1)
        po_fig.update_yaxes(autorange="reversed")
        po_fig.update_layout(
            legend=dict(orientation="h"),
            margin={"t": 0, "l": 0},
            xaxis_title="Ediciones",
            yaxis_title="Lugar",
        )
        st.text("Distribución por ubicación")
        st.plotly_chart(po_fig, use_container_width=True)

        if len(po_s_region) != 0:
            quantities1 = []
            quantities2 = []
            quantities3 = []
            quantities4 = []

            i = 0
            for y in years:
                p = quantities[y]
                p.sort(reverse=True)
                quantities1.append(p[0])
                quantities2.append(p[quartiles1[i] + 1])
                quantities3.append(p[quartiles2[i] + 1])
                quantities4.append(p[quartiles3[i] + 1])
                i += 1

            ps_fig = go.Figure()
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities4,
                    name="Cuartil 4",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(250, 42, 42, 0.5)",
                    line=dict(color="rgba(250, 42, 42, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities3,
                    name="Cuartil 3",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(255, 171, 171, 0.5)",
                    line=dict(color="rgba(255, 171, 171, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities2,
                    name="Cuartil 2",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(0, 101, 195, 0.5)",
                    line=dict(color="rgba(0, 101, 195, 1)"),
                )
            )
            ps_fig.add_trace(
                go.Scatter(
                    x=years,
                    y=quantities1,
                    name="Cuartil 1",
                    mode="lines",
                    fill="tonexty",
                    fillcolor="rgba(130, 200, 254, 0.5)",
                    line=dict(color="rgba(130, 200, 254, 1)"),
                )
            )
            for u, v in pu_univs.items():
                ps_fig.add_trace(
                    go.Scatter(x=years, y=v["solved"], name=u, mode="markers")
                )
            ps_fig.update_xaxes(showgrid=True, dtick=1)
            ps_fig.update_layout(
                legend=dict(orientation="h"),
                margin={"t": 0, "l": 0},
                xaxis_title="Ediciones",
                yaxis_title="Problemas resueltos",
            )
            st.text("Distribución por problemas resueltos")
            st.plotly_chart(ps_fig, use_container_width=True)

with st.container(border=True):
    st.text("Acumulado de problemas resueltos")

    with st.expander("Parámetros:"):
        a_first, a_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="a_period",
        )

        a_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        a_n_regions = ["Todas"] + [x for x in a_d_regions]

        a_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=a_n_regions,
            default=["Todas"],
            key="a_part_regions",
        )

        a_contests = get_contests_from_period(a_first, a_last)
        a_univs = {}
        for x, c in a_contests.items():
            for t in c:
                if (
                    "Todas" in a_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in a_s_region
                ):
                    if t["university"] in a_univs:
                        a_univs[t["university"]]["solved"] += int(t["solved"])
                        a_univs[t["university"]]["total"] += len(cstats[x]["problems"])
                    else:
                        a_univs[t["university"]] = {
                            "solved": int(t["solved"]),
                            "total": len(cstats[x]["problems"]),
                        }
        amount = 0
        if a_univs:
            amount = st.slider(
                "Cantidad de lugares a mostrar",
                min_value=1,
                max_value=len(a_univs),
                value=len(a_univs) if len(a_univs) < 50 else 50,
            )

    with st.expander("Gráficos:"):

        prob_solv = [(x, y["solved"]) for x, y in a_univs.items()]
        perc_solv = [(x, y["solved"] * 100 / y["total"]) for x, y in a_univs.items()]
        prob_solv.sort(key=lambda x: x[1], reverse=True)
        perc_solv.sort(key=lambda x: x[1], reverse=True)

        if len(prob_solv) < amount:
            y_a = [c[0] for c in prob_solv]
            x_a = [c[1] for c in prob_solv]
            y_pe = [c[0] for c in perc_solv]
            x_pe = [c[1] for c in perc_solv]
        else:
            y_a = [c[0] for c in prob_solv[:amount]]
            x_a = [c[1] for c in prob_solv[:amount]]
            y_pe = [c[0] for c in perc_solv[:amount]]
            x_pe = [c[1] for c in perc_solv[:amount]]

        a_fig = go.Figure(go.Bar(x=x_a, y=y_a, orientation="h"))
        a_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=600 if 600 > 18 * len(x_a) else 18 * len(x_a),
        )
        a_fig.update_yaxes(autorange="reversed")

        st.text("Por total de problemas resueltos")
        st.plotly_chart(a_fig, use_container_width=True)

        ape_fig = go.Figure(go.Bar(x=x_pe, y=y_pe, orientation="h"))
        ape_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=600 if 600 > 18 * len(x_pe) else 18 * len(x_pe),
        )
        ape_fig.update_yaxes(autorange="reversed")

        st.text("Por porciento de problemas resueltos")
        st.plotly_chart(ape_fig, use_container_width=True)

with st.container(border=True):
    st.text("Miembros de los equipos")

    with st.expander("Parámetros:"):
        t_first, t_last = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="t_period",
        )

        t_d_regions = {regions[x]["spanish_name"]: x for x in regions}
        t_n_regions = ["Todas"] + [x for x in t_d_regions]

        t_s_region = st.multiselect(
            "Selecione la región a analizar",
            options=a_n_regions,
            default=["Todas"],
            key="t_part_regions",
        )

        teams = {}
        t_contests = get_contests_from_period(t_first, t_last)
        for x, c in t_contests.items():
            for t in c:
                if (
                    "Todas" in t_s_region
                    or regions[countries[t["country"]]["region"]]["spanish_name"]
                    in t_s_region
                ):
                    if t["university"] in teams:
                        teams[t["university"]]["teams"] += 1
                        repeated = False
                        for s in t["players"]:
                            if s in teams[t["university"]]["players"]:
                                teams[t["university"]]["repeated_players"] += 1
                                if not repeated:
                                    teams[t["university"]]["repeated"] += 1
                                    repeated = True
                            else:
                                teams[t["university"]]["players"].add(s)
                    else:
                        teams[t["university"]] = {
                            "players": set(),
                            "teams": 1,
                            "repeated": 0,
                            "repeated_players": 0,
                        }
                        for s in t["players"]:
                            teams[t["university"]]["players"].add(s)

        t_amount = 0
        if teams:
            t_amount = st.slider(
                "Cantidad de lugares a mostrar",
                min_value=1,
                max_value=len(teams),
                value=len(teams) if len(teams) < 50 else 50,
                key="t_slider",
            )

    with st.expander("Gráficos:"):
        t_repeated_teams = [
            (x, y["repeated"]) for x, y in teams.items() if y["repeated"] != 0
        ]
        t_percent_repeated_teams = [
            (x, y["repeated"] * 100 / y["teams"])
            for x, y in teams.items()
            if y["repeated"] != 0
        ]
        t_repeated_players = [
            (x, y["repeated_players"]) for x, y in teams.items() if y["repeated"] != 0
        ]
        t_percent_repeated_players = [
            (x, y["repeated_players"] * 100 / len(y["players"]))
            for x, y in teams.items()
            if y["repeated"] != 0
        ]

        t_repeated_teams.sort(key=lambda x: x[1], reverse=True)
        t_percent_repeated_teams.sort(key=lambda x: x[1], reverse=True)
        t_repeated_players.sort(key=lambda x: x[1], reverse=True)
        t_percent_repeated_players.sort(key=lambda x: x[1], reverse=True)

        if len(t_repeated_teams) < t_amount:
            y_rt = [c[0] for c in t_repeated_teams]
            x_rt = [c[1] for c in t_repeated_teams]
            y_prt = [c[0] for c in t_percent_repeated_teams]
            x_prt = [c[1] for c in t_percent_repeated_teams]
            y_rp = [c[0] for c in t_repeated_players]
            x_rp = [c[1] for c in t_repeated_players]
            y_prp = [c[0] for c in t_percent_repeated_players]
            x_prp = [c[1] for c in t_percent_repeated_players]
        else:
            y_rt = [c[0] for c in t_repeated_teams[:t_amount]]
            x_rt = [c[1] for c in t_repeated_teams[:t_amount]]
            y_prt = [c[0] for c in t_percent_repeated_teams[:t_amount]]
            x_prt = [c[1] for c in t_percent_repeated_teams[:t_amount]]
            y_rp = [c[0] for c in t_repeated_players[:t_amount]]
            x_rp = [c[1] for c in t_repeated_players[:t_amount]]
            y_prp = [c[0] for c in t_percent_repeated_players[:t_amount]]
            x_prp = [c[1] for c in t_percent_repeated_players[:t_amount]]

        rt_fig = go.Figure(go.Bar(x=x_rt, y=y_rt, orientation="h"))
        rt_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        rt_fig.update_yaxes(autorange="reversed")

        st.text("Total de equipos con miembros participantes en otra edición")
        st.plotly_chart(rt_fig, use_container_width=True)

        prt_fig = go.Figure(go.Bar(x=x_prt, y=y_prt, orientation="h"))
        prt_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        prt_fig.update_yaxes(autorange="reversed")

        st.text("Porciento de equipos con miembros participantes en otra edición")
        st.plotly_chart(prt_fig, use_container_width=True)

        rp_fig = go.Figure(go.Bar(x=x_rp, y=y_rp, orientation="h"))
        rp_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        rp_fig.update_yaxes(autorange="reversed")

        st.text("Total de estudiantes participantes en otra edición")
        st.plotly_chart(rp_fig, use_container_width=True)

        prp_fig = go.Figure(go.Bar(x=x_prp, y=y_prp, orientation="h"))
        prp_fig.update_layout(
            margin={"t": 0, "l": 0},
            height=400 if 400 > 18 * len(x_a) else 18 * len(x_a),
        )
        prp_fig.update_yaxes(autorange="reversed")

        st.text("Porciento de estudiantes participantes en otra edición")
        st.plotly_chart(prp_fig, use_container_width=True)

with st.container(border=True):
    st.text("Secuencia de participaciones por universidad")

    with st.expander("Gráficos:"):

        s_univs = set()
        for x, c in po_contests.items():
            for team in c:
                s_univs.add(team["university"])

        s_univs = list(s_univs)
        hi = s_univs.index("Universidad de La Habana")
        oi = s_univs.index("Universidad de Oriente - Sede Antonio Maceo")

        s1_univs = st.selectbox(
            "Selecciona una universidad:", options=s_univs, index=hi, key="s1_univs"
        )

        u1 = get_university_participations(s1_univs, contests)

        try:
            st.graphviz_chart(get_university_graph(u1, "s1"))
        except:
            pass

        s2_univs = st.selectbox(
            "Selecciona otra universidad:", options=s_univs, index=oi, key="s2_univs"
        )

        u2 = get_university_participations(s2_univs, contests)

        try:
            st.graphviz_chart(st.graphviz_chart(get_university_graph(u2, "s2")))
        except:
            pass

with st.container(border=True):
    st.text("Cantidad de universidades finalistas por país")

    with st.expander("Parámetros:"):

        start_year, end_year = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="univ_period",
        )

        univ_counts = [i for i in range(1, 16)]

        min_finalists = st.selectbox(
            "Seleccione la cantidad mínima de universidades finalistas",
            options=univ_counts,
            index=4,
            key="univ_min",
        )

        st.session_state["min_univ_count"] = min_finalists

        regions_map = {regions[x]["spanish_name"]: x for x in regions}
        u_regions = ["Todas"] + [x for x in regions_map]

        selected_regions = st.multiselect(
            "Seleccione la región deseada", options=u_regions, default=["Todas"]
        )

    with st.expander("Gráficos:"):
        finalists_by_country = {}

        for year in range(start_year, end_year + 1):
            year = str(year)
            for team in contests[year]:
                country = team["country"]
                university = team["university"]

                if country not in finalists_by_country:
                    finalists_by_country[country] = set()

                finalists_by_country[country].add(university)

        finalists_by_country = {
            country: universities
            for country, universities in finalists_by_country.items()
            if len(universities) >= min_finalists
        }

        if "Todas" not in selected_regions:
            selected_region_keys = {regions_map[region] for region in selected_regions}
            finalists_by_country = {
                country: universities
                for country, universities in finalists_by_country.items()
                if countries[country]["region"] in selected_region_keys
            }

        x_counts = []
        y_countries = []
        filtered_finalists = [
            (country, len(universities))
            for country, universities in finalists_by_country.items()
        ]
        filtered_finalists.sort(key=lambda x: x[1])

        for item in filtered_finalists:
            x_counts.append(item[1])
            y_countries.append(item[0])

        fig_finalists = go.Figure(go.Bar(x=x_counts, y=y_countries, orientation="h"))

        fig_finalists.update_layout(
            margin={"t": 0, "l": 0},
            height=700 if 700 > 18 * len(x_counts) else 18 * len(x_counts),
        )

        st.plotly_chart(fig_finalists, use_container_width=True)

# Alberto
def get_position(range_year):
    end = {}
    d = set()
    for i in range_year:
        a = []
        for j in contests[str(i)]:
            a.append(j["university"])
            d.add(j["country"])
        end[str(i)] = a
    return end, d

def get_uni_country_regions(izq, der, _country, filters):
    if "Todas" in filters:
        return None
    if len(filters) == 0:
        return "void"
    domain = []
    for i in _country:
        domain.append((i, countries[i]["region"]))
    result = []
    for i in domain:
        if regions[i[1]]["spanish_name"] in filters:
            result.append(i[0])
    end = {}
    for i in range(izq, der + 1):
        a = []
        for j in contests[str(i)]:
            if j["country"] in result:
                a.append(j["university"])
        end[str(i)] = a
    return end

def medal_table(df):
    df.columns= [x for x in range(1,15)]
    new_df = df.iloc[:,:-1]
    count_gold = new_df.iloc[:,:4].sum(axis=1)
    count_silver = new_df.iloc[:,4:8].sum(axis=1)            
    count_bronze = new_df.iloc[:,8:].sum(axis=1)
    result = pd.concat([count_gold,count_silver,count_bronze],axis=1)
    result['total']=result.sum(axis=1)
    return result

def apply_filter(df,r,count_participation):
    def occurrences(row):
        counting = {}
        for element in row:
            if pd.notnull(element):
                counting[element] = row.tolist().count(element)
        return counting

    count_row = df.apply(occurrences, axis=1)
    count_df = pd.DataFrame(count_row.tolist()).fillna(0).astype(int)
    count_df=count_df.T
    count_df= count_df.iloc[:,:12]
    
    count_df['Total'] = count_df[count_df.columns].sum(axis=1)
    count_df = pd.concat([count_df,count_participation],axis=1)

    count_df.columns = [f"{x}º" for x in range(1, 13)] + ["Total"]+['Paticipaciones']
    
    if len(r)!=0:
        #table1
        p = count_df.loc[r]
        p.rename_axis("Universidades",inplace=True)
        p=p.sort_values(
        by=[f"{x}º" for x in range(1, 13)] + ["Total"]+['Paticipaciones'],
        ascending=False
    )
        st.write("Tabla de posiciones por universidades:")
        st.dataframe(p,use_container_width=True)
         
        #table 2
        m = medal_table(p)
        m = pd.concat([m,count_participation],axis=1)
        m.rename_axis("Universidades",inplace=True)
        m.columns = ['Oro','Plata','Bronce']+['Total']+['Paticipaciones']
        m =  m.sort_values(
        by=["Oro", "Plata", "Bronce"] + ["Total"],
        ascending=False
        )
        st.write("Tabla de medallas por universidades:")
        st.dataframe(m,use_container_width=True)

    else:
        #table1
        count_df.rename_axis("Universidades",inplace=True)
        count_df=count_df.sort_values(
        by=[f"{x}º" for x in range(1, 13)] + ["Total"]+['Paticipaciones'],
        ascending=False
        )
        st.write("Tabla de posiciones por universidades:")
        st.dataframe(count_df)

        #table 2
        m = medal_table(count_df)
        m = pd.concat([m,count_participation],axis=1)
        m.rename_axis("Universidades",inplace=True)
        m.columns = ['Oro','Plata','Bronce']+['Total']+['Paticipaciones']
        m =  m.sort_values(
        by=["Oro", "Plata", "Bronce"] + ["Total"],
        ascending=False
        )
        st.write("Tabla de medallas por universidades:")
        st.dataframe(m, use_container_width=True)

with st.container(border=True):
    st.text("Posiciones y medallas por universidades")

    with st.expander("Parámetros:"):
        izq, der = st.select_slider(
            "Selecciona el rango de años",
            options=range(minimal, maximal + 1),
            value=(2010, maximal),
            key="minimal_position_parts1",
        )
        minimal_u_parts = (
            st.session_state["minimal_u1_parts"]
            if "minimal_u1_parts" in st.session_state
            else 1
        )
        u_participations = [i for i in range(1, der - izq + 2)]

        if minimal_u_parts < der - izq + 1:
            u_ind = u_participations.index(minimal_u_parts)
        else:
            u_ind = u_participations.index(der - izq + 1)

        u_min_parts = st.selectbox(
            "Seleccione la cantidad de participaciones mínima",
            options=u_participations,
            index=u_ind,
            key="u_part_min1",
        )

        st.session_state["minimal_u1_parts"] = u_min_parts

        a_n_regions = ["Todas"] + [x for x in a_d_regions]
        region_uni = st.multiselect(
            "Selecione la región a analizar",
            options=a_n_regions,
            default=["Todas"],
            key="regions_uni",
        )
    
    with st.expander("Gráficos:"):
        df, country = get_position(range(izq, der + 1))
        df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in df.items()]))
        count_total = df.values.flatten()  
        count_series = pd.Series(count_total).value_counts()
        ranks = count_series[count_series >= u_min_parts].index
        region_filter = get_uni_country_regions(izq,der,country,region_uni)
        if region_filter is None:
            apply_filter(df,ranks,count_series)
        elif region_filter =='void':
            st.dataframe([],use_container_width=True)
            st.dataframe([],use_container_width=True)
        else:
            region_filter = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in region_filter.items()]))
            count_total_ = region_filter.values.flatten()  
            count_series_ = pd.Series(count_total_).value_counts()
            rank = count_series_[count_series_ >= u_min_parts ].index
            apply_filter(region_filter,rank,count_series_)
            
#Diego
with st.container(border=True):

    st.text("Posiciones y medallas por País")

    with st.expander("Parámetros:"):

        years = list(map(int, contests.keys()))
        min_year, max_year = 2010, max(years)
        year_range = st.slider(
            "Seleccione el rango de años", min_year, max_year, (min_year, max_year)
        )

        max_participations = year_range[1] - year_range[0] + 1
        participaciones_minimas_options = []
        for i in range(1, max_participations + 1):
            participaciones_minimas_options.append(i)
        participaciones_minimas = st.selectbox(
            "Selecccione la cantidad de participaciones Mínimas", participaciones_minimas_options, index=0
        )

        region_names = []
        for region_code in regions:
            region_names.append(regions[region_code]["spanish_name"])
        region_names.append("Todas")
        selected_region_names = st.multiselect(
            "Seleccione las regiones", options=region_names, default=["Todas"]
        )

        selected_region_codes = []
        if "Todas" in selected_region_names:
            selected_region_codes = list(regions.keys())
        else:
            for region_code in regions:
                if regions[region_code]["spanish_name"] in selected_region_names:
                    selected_region_codes.append(region_code)

    with st.expander("Gráficos"):

        def count_places(contests, selected_regions):
            data = {}
            participations = {}
            for region_code in selected_regions:
                for country, details in countries.items():
                    if details["region"] == region_code:
                        participations[country] = set()

            for year, contest in contests.items():
                regional_contestants = []
                for entry in contest:
                    if countries[entry["country"]]["region"] in selected_regions:
                        regional_contestants.append(entry)

                def sort_key(entry):
                    try:
                        return int(entry["position"])
                    except ValueError:
                        return float("inf")

                regional_contestants.sort(key=sort_key)

                i = 1
                for entry in regional_contestants:
                    country = entry["country"]
                    try:
                        position = i
                    except ValueError:
                        position = 0
                    if country not in data:
                        data[country] = {
                            "País": country,
                            "Oro": 0,
                            "Plata": 0,
                            "Bronce": 0,
                            "Total": 0,
                            "Participaciones": 0,
                        }
                    if 1 <= position <= 4:
                        data[country]["Oro"] += 1
                    elif 5 <= position <= 8:
                        data[country]["Plata"] += 1
                    elif 9 <= position <= 12:
                        data[country]["Bronce"] += 1
                    participations[country].add(year)
                    i += 1

            for country in data:
                data[country]["Total"] = (
                    data[country]["Oro"]
                    + data[country]["Plata"]
                    + data[country]["Bronce"]
                )
                data[country]["Participaciones"] = len(participations[country])

            filtered_data = []
            for entry in data.values():
                if entry["Participaciones"] >= participaciones_minimas:
                    filtered_data.append(entry)

            return filtered_data

        def count_detailed_places(contests, selected_regions):
            data = {}
            participations = {}
            for region_code in selected_regions:
                for country, details in countries.items():
                    if details["region"] == region_code:
                        participations[country] = set()

            for year, contest in contests.items():
                regional_contestants = []
                for entry in contest:
                    if countries[entry["country"]]["region"] in selected_regions:
                        regional_contestants.append(entry)

                def sort_key(entry):
                    try:
                        return int(entry["position"])
                    except ValueError:
                        return float("inf")

                regional_contestants.sort(key=sort_key)

                idx = 1
                for entry in regional_contestants:
                    country = entry["country"]
                    try:
                        position = idx
                    except ValueError:
                        position = 0
                    if country not in data:
                        data[country] = {"País": country}
                        for i in range(1, 13):
                            data[country][f"{i}º"] = 0
                        data[country]["Total"] = 0
                        data[country]["Participaciones"] = 0
                    if 1 <= position <= 12:
                        data[country][f"{position}º"] += 1
                        data[country]["Total"] += 1
                    participations[country].add(year)
                    idx += 1

            for country in data:
                data[country]["Participaciones"] = len(participations[country])

            filtered_data = []
            for entry in data.values():
                if entry["Participaciones"] >= participaciones_minimas:
                    filtered_data.append(entry)

            return filtered_data

        filtered_contests = {}
        for year in contests:
            if year_range[0] <= int(year) <= year_range[1]:
                filtered_contests[year] = contests[year]

        selected_regions = selected_region_codes

        summary_table = count_places(filtered_contests, selected_regions)
        detailed_table = count_detailed_places(filtered_contests, selected_regions)

        df_summary = pd.DataFrame(
            summary_table,
            columns=["País", "Oro", "Plata", "Bronce", "Total", "Participaciones"],
        )
        df_summary = df_summary.sort_values(by=["Oro", "Plata", "Bronce", "Total", "Participaciones"], ascending=False)

        df_detailed = pd.DataFrame(
            detailed_table,
            columns=["País"]
            + [f"{i}º" for i in range(1, 13)]
            + ["Total", "Participaciones"],
        )

        df_detailed = df_detailed.sort_values(
            by=[f"{i}º" for i in range(1, 13)] + ["Total", "Participaciones"],
            ascending=False,
        )

        df_summary.index = df_summary.index + 1
        df_detailed.index = df_detailed.index + 1

        st.write("Tabla de posiciones por país:")
        st.dataframe(df_detailed, hide_index=True, use_container_width=True)

        st.write("Tabla de medallas por país:")
        st.dataframe(df_summary, hide_index=True, use_container_width=True)
