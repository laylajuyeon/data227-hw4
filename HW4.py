import streamlit as st
import pandas as pd
import altair as alt

s2324 = pd.read_csv('PL-season-2324.csv')
st.title('DATA 22700 HW4')
st.subheader('Layla Juyeon Lee')
st.subheader('Q1: How consistent are score margins at half time versus at the end of the game?')
s2324['half_diff']=s2324['HTHG']-s2324['HTAG']
s2324['full_diff']=s2324['FTHG']-s2324['FTAG']

line_df = pd.DataFrame({'x': [-9, 7], 'y': [-9, 7]})
q1line = alt.Chart(line_df).mark_line(color='red',opacity=0.2).encode(
    x='x:Q',
    y='y:Q'
)

brush = alt.selection_interval(clear=True)

q1scatter = alt.Chart(
    s2324
).mark_circle(
).encode(
    x=alt.X('half_diff:Q',title='Score Difference (Home-Away) at Halftime'),
    y=alt.Y('full_diff:Q',title='Score Difference (Home-Away) at End of Game'),
    tooltip=[
        alt.Tooltip('count():Q',title='Number of Matches')
    ],
    opacity=alt.Opacity('count():Q',scale=alt.Scale(range=[0.2,1]),title='Number of Matches')
).add_params(
    brush
).properties(
    title='Score Differences at Halftime vs at End of Game'
)

q1bar = alt.Chart(s2324).mark_bar().transform_fold(
    ['HTHG','HTAG','FTHG','FTAG'], 
    as_=['key','value']
).encode(
    x=alt.X('key:N', 
            sort=['HTHG', 'HTAG', 'FTHG', 'FTAG'], 
            title='Team and Match Stage'),
    y=alt.Y('average(value):Q', title='Average Score'),
    color=alt.Color('key:N',
        sort=['HTHG', 'HTAG', 'FTHG', 'FTAG'],
        scale=alt.Scale(
            domain=['HTHG', 'HTAG', 'FTHG', 'FTAG'],
            range=['#3182bd', '#9ecae1', '#e6550d', '#fdae6b'] 
        ),
        legend=alt.Legend(title="Score Type",labelExpr="datum.label=='HTHG'?'Home (Half)':datum.label=='HTAG'?'Away (Half)':datum.label=='FTHG'?'Home(Full)':'Away (Full)'")
    ),
    tooltip=[alt.Tooltip('average(value):Q',title='Average Score')]
).transform_filter(
    brush
).properties(
    title='Average Scores for Selected Games'
)

q1 = (q1scatter+q1line)|q1bar

st.altair_chart(q1,use_container_width=True)

st.subheader('Q2: How consistent are teams’ accuracies at home vs away games?')
s2324['ht_accuracy']=s2324['HST']/s2324['HS']
s2324['at_accuracy']=s2324['AST']/s2324['AS']


home= s2324[['Date','HomeTeam','ht_accuracy']].rename(columns={'HomeTeam':'Team','ht_accuracy':'Accuracy'})
away= s2324[['Date','AwayTeam','at_accuracy']].rename(columns={'AwayTeam':'Team','at_accuracy':'Accuracy'})

selection = alt.selection_multi(fields=['Team'],bind='legend')

brush = alt.selection_interval(bind='scales', encodings=['x'])

home_chart = alt.Chart(home).mark_line(point=True).encode(
    x=alt.X('Date:T'),
    y=alt.Y('Accuracy:Q',title='Proportion of Total Shots Made on Target'),
    color=alt.Color('Team:N'),
    opacity=alt.condition(selection,alt.value(1),alt.value(0.1)),
    tooltip=[alt.Tooltip('Accuracy:Q',title='Proportion of Shots Made on Target by Home Team'),
             alt.Tooltip('Team:N',title='Team')]
).add_params(
    selection,brush
).properties(
)

away_chart = alt.Chart(away).mark_line(point=True).encode(
    x=alt.X('Date:T'),
    y=alt.Y('Accuracy:Q',title='Proportion of Total Shots Made on Target'),
    color=alt.Color('Team:N'),
    opacity=alt.condition(selection,alt.value(1),alt.value(0.1)),
    tooltip=[alt.Tooltip('Accuracy:Q',title='Proportion of Shots Made on Target by Home Team'),
             alt.Tooltip('Team:N',title='Team')]
).add_params(
    selection,brush
).properties(
)

q2 = home_chart&away_chart

st.altair_chart(q2,use_container_width=True)

st.subheader('Q3: How do infractions vary by team?')
s2324['total_infractions'] = s2324['HF']+s2324['HY']+s2324['HR']+s2324['AF']+s2324['AY']+s2324['AR']

selection = alt.selection_point(fields=['HomeTeam', 'AwayTeam'],clear=True)

q3heat = alt.Chart(s2324).mark_rect().encode(
    x=alt.X('HomeTeam:N', title='Home Team', sort='ascending'),
    y=alt.Y('AwayTeam:N', title='Away Team', sort='ascending'),
    color=alt.Color('mean(total_infractions):Q',
                    title='Average Number of Infractions'),
    opacity=alt.condition(selection,alt.value(1),alt.value(0.1)),
    tooltip=[
        alt.Tooltip('HomeTeam:N'),
        alt.Tooltip('AwayTeam:N'),
        alt.Tooltip('mean(total_infractions):Q',title='Average Number of Infractions Across Matches')
    ]
).properties(width=500
).add_params(selection)

q3bar = alt.Chart(s2324).transform_filter(
    selection 
).transform_fold(
    ['HF', 'AF', 'HY', 'AY', 'HR', 'AR'],
    as_=['InfractionType', 'Count']
).mark_bar().encode(
    x=alt.X('InfractionType:N', sort=['HF', 'HY', 'HR', 'AF', 'AY', 'AR'], title='Type of Infraction'),
    y=alt.Y('sum(Count):Q', title='Total Count'),
    color=alt.Color('InfractionType:N',
        sort=['HF', 'HY', 'HR', 'AF', 'AY', 'AR'],
        scale=alt.Scale(
            domain=['HF', 'HY', 'HR', 'AF', 'AY', 'AR'],
            range=['#3182bd', '#d95f0e','#de2d26','#9ecae1','#fec44f','#fc9272'] 
        ),
        legend=alt.Legend(
    title="Infraction Type",
    labelExpr="datum.label=='HF' ? 'Home Fouls' : "
              "datum.label=='HY' ? 'Home Yellows' : "
              "datum.label=='HR' ? 'Home Reds' : "
              "datum.label=='AF' ? 'Away Fouls' : "
              "datum.label=='AY' ? 'Away Yellows' : "
              "datum.label=='AR' ? 'Away Reds' : ''"
),
    ),tooltip=[alt.Tooltip('HomeTeam:N'),alt.Tooltip('AwayTeam:N'),alt.Tooltip('sum(Count):Q')]
)
q3 = q3heat | q3bar

st.altair_chart(q3)