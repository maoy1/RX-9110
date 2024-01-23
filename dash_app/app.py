import argparse
import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html
from dash.exceptions import PreventUpdate

parser = argparse.ArgumentParser(description="Dash application arguments")
parser.add_argument(
    "--JenkinsJobs",
    help="The Jenkins Job CSV data file",
    required=False,
    default="data/jenkins_jobs.csv",
)
parser.add_argument(
    "--JobDetails",
    help="The Job Detail CSV data file",
    required=False,
    default="data/job_details.csv",
)
argument = parser.parse_args()
job_file = argument.JenkinsJobs
detail_file = argument.JobDetails
SCRIPTPATH = sys.path[0]
WORKDIR = os.path.dirname(SCRIPTPATH)
JOBS_OPTIONS = []
BATCH_OPTIONS = []
STEP_OPTIONS = []
BATCHES = []
JOBS = []


def update_data_func(job_file, detail_file):
    # download, extract data
    df_jobs = pd.read_csv(job_file)
    global JOBS
    JOBS = df_jobs["batch"].sort_values(ascending=False).unique()
    global JOBS_OPTIONS
    JOBS_OPTIONS = [{"label": value, "value": value} for value in JOBS]

    # use the output from the extract_xfire_log.py
    df_details = pd.read_csv(detail_file)
    global BATCHES
    BATCHES = df_details["batch"].sort_values(ascending=False).unique()
    global BATCH_OPTIONS
    BATCH_OPTIONS = [{"label": value, "value": value} for value in BATCHES]

    filtered_df = df_details.sort_values(by="duration", ascending=False)
    global STEP_OPTIONS
    STEP_OPTIONS = [
        {"label": value, "value": value} for value in filtered_df["name"].unique()
    ]
    return df_jobs, df_details


update_data_func(job_file, detail_file)
app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Store(id="memory-output-all-jobs"),
        dcc.Store(id="memory-output-jobs"),
        dcc.Store(id="memory-output-all-details"),
        dcc.Store(id="memory-output-details"),
        # html.Div(children=[
        html.H1("Xfire Fabrication Time Analyse"),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Button(
                            "Download Jenkins Jobs Data csv",
                            id="btn-download-jenkins-jobs-data",
                            n_clicks=0,
                        ),
                        dcc.Download(id="download-jenkins-jobs-data"),
                    ],
                    style={"flex": 1},
                ),
                html.Div(
                    children=[
                        html.Button(
                            "Download Jobs Details csv",
                            id="btn-download-job-details-data",
                            n_clicks=0,
                        ),
                        dcc.Download(id="download-job-details-data"),
                    ],
                    style={"flex": 1},
                ),
                html.Div(
                    children=[
                        html.Button("Update Data Files", id="btn-fetch-data", n_clicks=0,),
                        html.Label(f"   Last Update: {JOBS[0]} and {BATCHES[0]}"),
                    ],
                    style={
                        "flex": 2,
                    },
                ),
            ],
            style={"padding": 10, "display": "flex", "flexDirection": "row"},
        ),
        html.Br(),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Label('Jenkins Logs for "start db fabrication" Analyse'),
                        dcc.Dropdown(
                            id="job_log", options=JOBS_OPTIONS, value=JOBS[-3]
                        ),
                        html.Label("Jobs Relationship"),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Graph(id="graph-jobs-timeline"),
                                    ],
                                    style={"flex": 3},
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(id="graph-jobs-trend"),
                                    ],
                                    style={"flex": 1},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row"},
                        ),
                        html.Label(
                            "Choose xfrun_build to see Data Merge Substeps Analyse(7b), choose summus to see summus substeps analyse (7c)"
                        ),
                        dcc.Dropdown(
                            id="batch_name", options=BATCH_OPTIONS, value=BATCHES[0]
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="graph-batch-pie",
                                            figure=go.Figure(go.Sunburst()),
                                        ),
                                    ],
                                    style={"padding": 10, "flex": 1},
                                ),
                                html.Div(
                                    children=[
                                        dcc.Graph(
                                            id="graph-batch-multi-pie",
                                            figure=go.Figure(go.Sunburst()),
                                        ),
                                    ],
                                    style={"padding": 10, "flex": 1},
                                ),
                            ],
                            style={"display": "flex", "flexDirection": "row"},
                        ),
                        dcc.Graph(id="graph-batch-timeline"),
                    ],
                    style={"padding": 10, "flex": 2},
                ),
            ],
            style={"display": "flex", "flexDirection": "row"},
        ),
        # ]),
        html.Label("Steps/Jobs Excution Time Trend"),
        dcc.Dropdown(
            id="steps-name",
            options=STEP_OPTIONS,
            value=[":substances", "get_kws.sh", "drop_orphans"],
            multi=True,
        ),
        dcc.Graph(id="graph-steps-trend"),
    ]
)


@app.callback(
    [
        Output("memory-output-all-jobs", "data"),
        Output("memory-output-all-details", "data"),
    ],
    Input("btn-fetch-data", "n_clicks"),
    prevent_initial_call=True,
)
def update_data(n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    print (f"update_data {WORKDIR}/scripts/prepare_data.sh {job_file} {detail_file}")
    os.system(f"{WORKDIR}/scripts/prepare_data.sh {job_file} {detail_file}")

    df_jobs, df_details = update_data_func(job_file, detail_file)
    return df_jobs.to_dict("records"), df_details.to_dict("records")


@app.callback(
    Output("download-jenkins-jobs-data", "data"),
    Input("btn-download-jenkins-jobs-data", "n_clicks"),
    Input("memory-output-all-jobs", "data"),
    prevent_initial_call=True,
)
def func1(n_clicks, dict):
    if n_clicks == 0 or dict is None:
        raise PreventUpdate
    return dcc.send_data_frame(pd.DataFrame.from_dict(dict).to_csv, "jenkins_jobs.csv")


@app.callback(
    Output("download-job-details-data", "data"),
    Input("btn-download-job-details-data", "n_clicks"),
    Input("memory-output-all-details", "data"),
    prevent_initial_call=True,
)
def func2(n_clicks, dict):
    if n_clicks == 0 or dict is None:
        raise PreventUpdate
    return dcc.send_data_frame(pd.DataFrame.from_dict(dict).to_csv, "job_details.csv")


@app.callback(
    Output("memory-output-jobs", "data"),
    Input("job_log", "value"),
    Input("memory-output-all-jobs", "data"),
    prevent_initial_call=True,
)
def on_set_table_job(job_name, data_dict):
    if job_name is None or data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    return df[df["batch"] == job_name].to_dict("records")


@app.callback(
    Output("memory-output-details", "data"),
    Input("batch_name", "value"),
    Input("memory-output-all-details", "data"),
    prevent_initial_call=True,
)
def on_set_table_detail(batch_name, data_dict):
    if batch_name is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    return df[df["batch"] == batch_name].to_dict("records")


@app.callback(
    Output("graph-jobs-trend", "figure"),
    Input("memory-output-all-jobs", "data"),
)
def update_jobs_trend(data_dict):
    if data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    data = df[df["phase"] == "complete"]
    fig = px.scatter(
        data,
        x="start_time",
        y="duration",
        title="Xfire Fabrication Time Trend",
        hover_data=["duration_string"],
    )
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig


@app.callback(
    Output("graph-jobs-timeline", "figure"), Input("memory-output-jobs", "data")
)
def update_jobs_timeline(data_dict):
    if data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    start_date = min(df["start_time"])
    end_date = max(df["end_time"])
    # duration_all = df['duration_string'].iloc[0]
    df = df[1:]
    fig = px.timeline(
        df,
        x_start="start_time",
        x_end="end_time",
        y="name",
        color="phase",
        hover_data=["duration_string"],
    )
    px.colors
    fig.add_shape(
        type="line",
        yref="paper",
        x0=start_date,
        x1=start_date,
        y0=0,
        y1=1,
        yanchor="bottom",
        line=dict(color="green"),
    )
    fig.add_shape(
        type="line",
        yref="paper",
        x0=end_date,
        x1=end_date,
        y0=0,
        y1=1,
        yanchor="bottom",
        line=dict(color="green"),
    )
    # Set the layout of the figure
    fig.update_layout(
        title='The complete Jenkins Job "start db fabrication"',
    )
    return fig


@app.callback(
    Output("graph-batch-pie", "figure"), Input("memory-output-details", "data")
)
def update_batch_pie(data_dict):
    if data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    df = df[df["isLeaf"]]
    fig = px.pie(df, values="duration", names="name", hover_data=["duration_string"])
    fig.update_traces(textposition="inside")
    fig.update_layout(title="Substeps within one Batch")
    fig.update_yaxes(type="category", categoryorder="category ascending")
    fig.update_xaxes(type="-")
    return fig


@app.callback(
    Output("graph-batch-multi-pie", "figure"), Input("memory-output-details", "data")
)
def update_multi_pie(data_dict):
    if data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    df = df[df["isLeaf"]]
    fig = px.sunburst(
        df,
        path=["parent", "name"],
        values="duration",
        color="parent",
        hover_data=["duration_string"],
    )
    fig.update_layout(title="Substeps with parent step within one Batch")
    return fig


@app.callback(
    Output("graph-batch-timeline", "figure"), Input("memory-output-details", "data")
)
def update_chart(data_dict):
    if data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    start_xfrun = df[df["name"] == "xfrun"]["start_time"].iloc[0]
    end_xfrun = df[df["name"] == "xfrun"]["end_time"].iloc[0]
    # duration_xfrun = str(df[dadfta['name'] == 'xfrun']['duration_string'].iloc[0])
    df = df[df["isLeaf"]]
    fig = px.timeline(
        df,
        x_start="start_time",
        x_end="end_time",
        y="name",
        color="name",
        hover_data=["duration_string"],
    )
    fig.update_yaxes(autorange="reversed")
    fig.add_shape(
        type="line",
        yref="paper",
        x0=start_xfrun,
        x1=start_xfrun,
        y0=0,
        y1=1,
        yanchor="bottom",
        line=dict(color="green"),
    )
    fig.add_shape(
        type="line",
        yref="paper",
        x0=end_xfrun,
        x1=end_xfrun,
        y0=0,
        y1=1,
        yanchor="bottom",
        line=dict(color="green"),
    )
    fig.update_layout(
        title="The Job xfrun/data merge/summus",
        # showlegend=False,
        # xaxis=dict(title='Date'),
        # yaxis=dict(title='Task', showgrid=False),
    )
    return fig


@app.callback(
    Output("graph-steps-trend", "figure"),
    Input("steps-name", "value"),
    Input("memory-output-all-details", "data"),
)
def update_step_trend(steps_name, data_dict):
    if steps_name is None or data_dict is None:
        raise PreventUpdate
    df = pd.DataFrame.from_dict(data_dict)
    data = df.query("name in @steps_name")
    # fig = px.timeline(data, x_start="start_time", x_end="end_time", y="name", color="name", hover_data='duration_string')
    fig = px.line(
        data, x="start_time", y="duration", color="name", hover_data=["duration_string"]
    )
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig


if __name__ == "__main__":
    # update_data(job_file, detail_file)

    app.run_server(debug=False, host="0.0.0.0", port="8080")
