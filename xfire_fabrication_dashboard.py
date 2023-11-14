import dash
from dash import Dash, html,dcc, Input, Output, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# Use the output from the extract_start_db_jenkins_build_xml.py
df_jobs = pd.read_csv('RX-9110/jenkins_jobs.csv')
jobs = df_jobs['batch'].sort_values(ascending=False).unique()
jobs_options = [{"label": value, "value": value} for value in jobs]

# use the output from the extract_xfire_log.py
df_xfire = pd.read_csv('RX-9110/job_details.csv')
batchs = df_xfire['batch'].sort_values(ascending=False).unique()
batch_options = [{"label": value, "value": value} for value in batchs]

filtered_df = df_xfire.sort_values(by='duration', ascending=False)
step_options = [{"label": value, "value": value} for value in filtered_df['name'].unique()]

app = Dash(__name__)

app.layout = html.Div([
    dcc.Store(id='memory-output-batches'),
    dcc.Store(id='memory-output-jobs'),
    #html.Div(children=[
    html.H1('Xfire Fabrication Time Analyse'),
    html.Div(children=[
        html.Div(children=[
            html.Button("Update Data Files", id="btn-fetch-data"),
            html.Label(f'   Last Update was {jobs[0]}'),
        ], style={ 'flex': 1}),
        html.Div(children=[
            html.Button("Download Jenkins Jobs Data csv", id="btn-download-jenkins-jobs-data"),
            dcc.Download(id="download-jenkins-jobs-data"),
        ], style={'flex': 1}),
        html.Div(children=[
            html.Button("Download Jobs Details csv", id="btn-download-job-details-data"),
            dcc.Download(id="download-job-details-data"),
        ], style={ 'flex': 1}),
    ], style={'padding': 10, 'display': 'flex', 'flexDirection': 'row'}),
    
    html.Br(),   html.Br(),
    html.Div(children=[
        html.Div(children=[
        html.Label('Jenkins Logs for \"start db fabrication\" Analyse'),
        dcc.Dropdown(id="job_log", options=jobs_options, value=jobs[-1]),
        html.Label('Jobs Relationship'),
        html.Div(children=[
            html.Div(children=[
                dcc.Graph(id="graph-jobs-timeline"),
            ], style={'flex': 3}),
            html.Div(children=[
                dcc.Graph(id="graph-jobs-trend"),
            ], style={ 'flex': 1}),
        ], style={'display': 'flex', 'flexDirection': 'row'}),

        html.Label('Choose xfrun_build to see Data Merge Substeps Analyse(7b), choose summus to see summus substeps analyse (7c)'),
        dcc.Dropdown(id="batch_name",
                        options=batch_options,
                        value=batchs[0]),
        html.Div(children=[
            html.Div(children=[
                dcc.Graph(id="graph-batch-pie", figure=go.Figure(go.Sunburst())),
            ], style={'padding': 10,'padding': 10, 'flex': 1}),
            html.Div(children=[
                dcc.Graph(id="graph-batch-multi-pie", figure=go.Figure(go.Sunburst())),
            ], style={'padding': 10, 'flex': 1}),
        ], style={'display': 'flex', 'flexDirection': 'row'}),
        dcc.Graph(id="graph-batch-timeline"),
        ], style={'padding': 10, 'flex': 2},),
    ], style={'display': 'flex', 'flexDirection': 'row'}),
    #]),
     
    html.Label('Steps/Jobs Excution Time Trend'),
    dcc.Dropdown(id="steps-name",
                options=step_options,
                value=[':substances', 'get_kws.sh', 'drop_orphans'],
                multi=True,),
    dcc.Graph(id="graph-steps-devel"),
])

@app.callback(Output('memory-output-jobs', 'data'),
              Input('job_log', 'value'))
def on_set_table(job_name):
    if job_name is None :
        raise PreventUpdate
    return df_jobs[df_jobs['batch'] == job_name].to_dict('records')


@app.callback(Output('memory-output-batches', 'data'),
              Input('batch_name', 'value'))
def on_set_table(batch_name):
    if batch_name is None :
        raise PreventUpdate
    return df_xfire[df_xfire['batch'] == batch_name].to_dict('records')


@app.callback(Output("graph-jobs-trend", "figure"), 
               Input('batch_name', 'value'))
def update_chart(data):
    data = df_jobs[df_jobs['phase'] == 'complete']
    fig = px.scatter(data, x='start_time', y='duration', title="Xfire Fabrication Time Trend", hover_data='duration_string')
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig

@app.callback(Output("graph-jobs-timeline", "figure"), 
               Input("memory-output-jobs", "data"))
def update_chart(data_dict):
    data = pd.DataFrame.from_dict(data_dict)
    start_date = min(data['start_time'])
    end_date = max(data['end_time'])
    duration_all = data['duration_string'].iloc[0]
    data = data[1:]
    fig = px.timeline(data, x_start="start_time", x_end="end_time", y="name", color="phase", hover_data='duration_string')
    px.colors
    fig.add_shape(type='line', yref='paper', x0=start_date, x1=start_date, y0=0, y1=1, yanchor='bottom', line=dict(color='green'))
    fig.add_shape(type='line', yref='paper', x0=end_date, x1=end_date, y0=0, y1=1, yanchor='bottom', line=dict(color='green'),label=dict(text=duration_all))
    # Set the layout of the figure
    fig.update_layout(
        title='The complete Jenkins Job \"start db fabrication\"',
    )
    return fig


@app.callback(Output("graph-batch-pie", "figure"), 
               Input("memory-output-batches", "data"))
def update_chart(data_dict):
    data = pd.DataFrame.from_dict(data_dict)
    data = data[data['isLeaf']]
    fig = px.pie(data, values='duration', names='name', hover_data='duration_string')
    fig.update_traces(textposition='inside')
    fig.update_layout(title="Substeps within one Batch")
    fig.update_yaxes(type="category", categoryorder="category ascending")
    fig.update_xaxes(type="-")
    return fig


@app.callback(Output("graph-batch-multi-pie", "figure"), 
               Input("memory-output-batches", "data"))
def update_chart(data_dict):
    data = pd.DataFrame.from_dict(data_dict)
    data = data[data['isLeaf']]
    fig = px.sunburst(data, path=['parent', 'name'], values='duration', color='parent', hover_data='duration_string')
    fig.update_layout(title="Substeps with parent step within one Batch")
    return fig


@app.callback(Output("graph-batch-timeline", "figure"), 
               Input("memory-output-batches", "data"))
def update_chart(data_dict):
    data = pd.DataFrame.from_dict(data_dict)

    start_xfrun = data[data['name']== 'xfrun']['start_time'].iloc[0]
    end_xfrun = data[data['name'] == 'xfrun']['end_time'].iloc[0]
    duration_xfrun = str(data[data['name'] == 'xfrun']['duration_string'].iloc[0])
    data = data[data['isLeaf']]
    fig = px.timeline(data, x_start="start_time", x_end="end_time", y="name", color="name", hover_data='duration_string')
    fig.update_yaxes(autorange="reversed")
    fig.add_shape(type='line', yref='paper', x0=start_xfrun, x1=start_xfrun, y0=0, y1=1, yanchor='bottom', line=dict(color='green'))
    fig.add_shape(type='line', yref='paper', x0=end_xfrun, x1=end_xfrun, y0=0, y1=1, yanchor='bottom', line=dict(color='green'),label=dict(text=duration_xfrun))
    fig.update_layout(
        title='The Job xfrun/data merge/summus',
        #showlegend=False,
        #xaxis=dict(title='Date'),
        #yaxis=dict(title='Task', showgrid=False),
    )
    return fig


@app.callback(Output("graph-steps-devel", "figure"), 
               Input("steps-name", "value"))
def update_chart(steps_name):
    if steps_name is None:
        raise PreventUpdate
    data = df_xfire.query('name in @steps_name')
    print(data)
    fig = px.line(data, x='start_time', y='duration', color='name', hover_data='duration_string')
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig


@app.callback(
    Output("download-jenkins-jobs-data", "data"),
    Input("btn-download-jenkins-jobs-data", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_jobs.to_csv, "jenkins_jobs.csv")


@app.callback(
    Output("download-job-details-data", "data"),
    Input("btn-download-job-details-data", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_xfire.to_csv, "job_details.csv")

if __name__ == "__main__":
    app.run_server(debug=True)