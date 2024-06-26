# -*- coding: utf-8 -*-
"""DATAVIZ_BANKAI_PANEL_LAYOUT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1J9wg-8qjGTCrEYSzlWgdJmeQl2mAorIJ

# **Preparing the data**
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.colors
import panel as pn
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import plotly.graph_objs as go

df = pd.read_csv('Unicorn_Companies.tsv', sep='\t')

df['Founded Year'] = pd.to_numeric(df['Founded Year'], errors='coerce')
df['Valuation ($B)'] = df['Valuation ($B)'].replace('[\$,]', '', regex=True).astype(float)
df.dropna(subset=['Founded Year'], inplace=True)
df['Founded Year'] = df['Founded Year'].astype(int)

df['Valuation ($M)'] = df['Valuation ($B)'] * 1000

df.head()

valid_industries = [
    'Artificial intelligence', 'Other', 'Fintech',
    'Internet software & services', 'Supply chain, logistics, & delivery',
    'Data management & analytics', 'E-commerce & direct-to-consumer', 'Edtech',
    'Hardware', 'Consumer & retail', 'Health', 'Auto & transportation',
    'Cybersecurity', 'Mobile & telecommunications', 'Travel'
]

# Correction 'Finttech' to 'Fintech'
df['Industry'] = df['Industry'].replace('Finttech', 'Fintech')

# Remplacement the non valid values by 'Other'
df['Industry'] = df['Industry'].apply(lambda x: x if x in valid_industries else 'Other')

print(df['Industry'].unique())

# Adjsting orders of magnitude
def convert_raised_amount(raised_str):
    if pd.isnull(raised_str):
        return 0
    raised_str = raised_str.upper().replace('$', '').strip()
    multiplier = 1
    if 'B' in raised_str:
        multiplier = 1000000000
        raised_str = raised_str.replace('B', '')
    elif 'M' in raised_str:
        multiplier = 1000000
        raised_str = raised_str.replace('M', '')
    elif 'K' in raised_str:
        multiplier = 1000
        raised_str = raised_str.replace('K', '')

    try:
        return float(raised_str) * multiplier
    except ValueError:  
        return 0


df['Total Raised ($M)'] = df['Total Raised'].apply(convert_raised_amount) / 1000000  # Convertir en millions de dollars

"""# **Creating Panel Application**"""

pn.extension('plotly')

# Function Definitions
def map_value_to_color(value, min_val, max_val, color_scale):
    value_scaled = (value - min_val) / (max_val - min_val)
    for i, (limit, color) in enumerate(color_scale):
        if value_scaled <= limit:
            lower_limit, lower_color = color_scale[i-1] if i > 0 else (0, color)
            upper_limit, upper_color = color_scale[i]
            ratio = (value_scaled - lower_limit) / (upper_limit - lower_limit)
            return interpolate_color(lower_color, upper_color, ratio)
    return color_scale[-1][1]

def interpolate_color(color1, color2, ratio):
    color1_rgb = matplotlib.colors.hex2color(color1)
    color2_rgb = matplotlib.colors.hex2color(color2)
    inter_color = [((1 - ratio) * c1 + ratio * c2) for c1, c2 in zip(color1_rgb, color2_rgb)]
    return matplotlib.colors.rgb2hex(inter_color)


# Page 1 Components
@pn.depends()
def page_1_view():
    unicorn_counts = df['Founded Year'].value_counts().reset_index()
    unicorn_counts.columns = ['Founded Year', 'Number of Unicorns']
    unicorn_counts.sort_values('Founded Year', inplace=True)
    fig_unicorn_counts = px.bar(unicorn_counts, x='Founded Year', y='Number of Unicorns', labels={'Number of Unicorns': 'Number of Unicorns', 'Founded Year': 'Founded Year'}, title="Number of Unicorns Founded per Year")
    description_style = {'text-align': 'center', 'width': '400px', 'margin': '0 auto'}

    desc_unicorn_counts = pn.pane.Markdown(
    "A histogram that highlights the surge in unicorn company formations starting in the 2000s, with a slight dip around the COVID-19 era.",
    styles=description_style
)

    valuation_by_year = df.groupby('Founded Year')['Valuation ($B)'].sum().reset_index()
    fig_valuation_by_year = px.line(valuation_by_year, x='Founded Year', y='Valuation ($B)', labels={'Valuation ($B)': 'Total Valuation ($B)', 'Founded Year': 'Founded Year'}, title="Evolution of Total Unicorn Valuation over the Years")
    desc_valuation_by_year = pn.pane.Markdown(
    "The line graph depicts a significant increase in total unicorn valuation from the 2000s, with a temporary decline during the COVID-19 pandemic.",
    styles=description_style
)
    top_10_valued_companies = df.nlargest(10, 'Valuation ($B)')  # Sélectionner les 10 entreprises avec la plus grande valuation
    fig_top_10_valued = px.bar(top_10_valued_companies, x='Valuation ($B)', y='Company', orientation='h', labels={'Valuation ($B)': 'Valuation ($B)', 'Company': 'Company'}, title='Top 10 Most Valuable Companies',  color='Country')
    desc_top_10_valued = pn.pane.Markdown(
    "A bar chart presenting the ten highest-valued unicorn companies, differentiated by color according to their country of origin, showcasing a snapshot of leading companies by market valuation.",
    styles=description_style
)

    fig_top_10_valued.update_layout(width=1500, height=600)  # Adjust the size accordingly
    fig_unicorn_counts.update_layout(width=500, height=300)  # Adjust the size accordingly
    fig_valuation_by_year.update_layout(width=500, height=300)  # Adjust the size accordingly

    # This Markdown pane holds the title
    title = pn.pane.Markdown("# Global Overview of the Unicorns Landscape")

    # The first chart is the top 10 valued companies and its description
    first_chart = pn.Column(fig_top_10_valued, desc_top_10_valued)

    # The second and third charts are the unicorn counts and valuation by year and their descriptions
    # We place these two in a Row to make them appear side by side
    second_chart = pn.Column(fig_unicorn_counts, desc_unicorn_counts)
    third_chart = pn.Column(fig_valuation_by_year, desc_valuation_by_year)
    second_and_third_charts_row = pn.Row(second_chart, third_chart)

    # The layout is a Column with the first chart on top followed by the row of the other two
    layout = pn.Column(title, first_chart, second_and_third_charts_row)

    return layout

# Global variable to hold the selected country
selected_country = pn.widgets.StaticText(name='Selected Country', value='')

# Update functions for the interactive charts
def update_bar_chart(country):
    if not country:
        return go.Figure()

    companies = df[df['Country'] == country].nlargest(10, 'Valuation ($B)')
    bar_chart = px.bar(
        companies,
        x='Valuation ($B)',
        y='Company',
        title=f'Top 10 Companies in {country}',
        orientation='h',
        color='Valuation ($B)',
        color_continuous_scale='Blues',
    )

    # Set the background color to dark grey
    bar_chart.update_layout(plot_bgcolor='rgba(200, 200, 200, 1)')

    return bar_chart

def update_pie_chart(country):
    if not country:
        return go.Figure()

    industries = df[df['Country'] == country]['Industry'].value_counts().reset_index()
    industries.columns = ['Industry', 'Count']
    return px.pie(
        industries,
        values='Count',
        names='Industry',
        title=f'Industries Distribution in {country}'
    )

def update_time_series(country):
    if not country:
        return go.Figure()

    funding_data = df[df['Country'] == country].groupby('Founded Year')['Total Raised ($M)'].sum().reset_index()
    return px.line(
        funding_data,
        x='Founded Year',
        y='Total Raised ($M)',
        title=f'Total Funding Over Time in {country}',
        markers=True
    )

description_style = {'text-align': 'center', 'width': '400px', 'margin': '0 auto'}

# Descriptions for the charts
desc_bar = "A bar chart showing the top 10 companies arranged in descending order of valuation, which is represented on the x-axis in billions of dollars."
desc_pie = "A multi-colored pie chart illustrating the diverse industrial sectors represented within a certain group, each sector's share depicted by a distinct color and percentage."
desc_line = "A line graph depicting the trend of total funds raised by companies over years."

# Create Markdown panes for the descriptions with the defined style
desc_bar_pane = pn.pane.Markdown(desc_bar, styles=description_style)
desc_pie_pane = pn.pane.Markdown(desc_pie, styles=description_style)
desc_line_pane = pn.pane.Markdown(desc_line, styles=description_style)

# Update function for the interactive charts
@pn.depends(selected_country.param.value)
def interactive_charts_view(country):
    if not country:
        return pn.pane.HTML("<p style='font-weight:bold; font-size:1.5em;'>Please click on a country to see the data</p>")

    # Update each chart with the given country
    bar_chart = update_bar_chart(country)
    pie_chart = update_pie_chart(country)
    time_series = update_time_series(country)

    # Combine each chart with its description
    bar_chart_column = pn.Column(pn.pane.Plotly(bar_chart), desc_bar_pane)
    pie_chart_column = pn.Column(pn.pane.Plotly(pie_chart), desc_pie_pane)
    time_series_column = pn.Column(pn.pane.Plotly(time_series), desc_line_pane)

    # Arrange the charts in a row
    charts_row = pn.Row(bar_chart_column, pie_chart_column, time_series_column)

    return charts_row

# Now you can display the interactive charts view
interactive_charts_view(selected_country.value)

@pn.depends()
def page_2_view():
    # Data
    unicorns_per_country = df['Country'].value_counts().reset_index(name='Number of Unicorns')
    unicorns_per_country.columns = ['Country', 'Number of Unicorns']

    # Personnalized color scale
    color_scale_custom = [(0, "#add8e6"), (0.5, "#0000ff"), (1, "#00008b")]


    top_countries = unicorns_per_country.head(10)
    min_val = unicorns_per_country['Number of Unicorns'].min()
    max_val = unicorns_per_country['Number of Unicorns'].max()
    bar_colors = [map_value_to_color(val, min_val, max_val, color_scale_custom) for val in top_countries['Number of Unicorns']]


    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "choropleth"}, {"type": "bar"}]], column_widths=[0.8, 0.2])

    # Choropleth
    choropleth_trace = go.Choropleth(
        locations=unicorns_per_country['Country'],
        locationmode='country names',
        z=unicorns_per_country['Number of Unicorns'],
        colorscale= color_scale_custom,
        colorbar_title="Number of Unicorns",
        hoverinfo='location+z'
    )
    fig.add_trace(choropleth_trace, row=1, col=1)

    # Bar plot
    for i, country in enumerate(top_countries['Country']):
        fig.add_trace(
            go.Bar(
                x=[top_countries['Number of Unicorns'].iloc[i]],
                y=[country],
                orientation='h',
                marker=dict(color=bar_colors[i]),
                hoverinfo='x+y'
            ),
            row=1, col=2
        )

    # Layout
    fig.update_layout(
        title_text='Global Distribution of Unicorn Companies and Top 10 Countries',
        width=2500,
        height=800,
        showlegend=False
    )
    fig.update_yaxes(title_text="Country", row=1, col=2)
    fig.update_xaxes(title_text="Number of Unicorns", row=1, col=2)


    choropleth_pane = pn.pane.Plotly(fig)
    choropleth_pane.param.watch(lambda event: setattr(selected_country, 'value', event.new['points'][0]['location']) if event.new else None, 'click_data')

    return pn.Column(pn.pane.Markdown("# The goegraphy of Innovation"),choropleth_pane, interactive_charts_view)

@pn.depends()
def page_3_view():

    # Slider for Year Range
    min_year = int(df['Founded Year'].min())
    max_year = int(df['Founded Year'].max())
    year_slider = pn.widgets.IntRangeSlider(name='Select Year Range', start=min_year, end=max_year, value=(min_year, max_year), step=1)

    # Define the style for the description
    description_style = {
        'text-align': 'center',
        'max-width': '1200px',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'font-size': '1.1em',
        'margin-top': '1em'
    }

    # Create the Markdown pane for the description with the style
    desc_treemap_pane = pn.pane.Markdown(
        "The image presents a colorful treemap visualizing the total value of various industries. Each block represents a different industry, with the size indicating the industry's total valuation. The chart embodies the shift towards a digitized industry landscape.",
        styles=description_style
    )

    # Treemap Interactive Visualization
    @pn.depends(year_slider.param.value)
    def filtered_treemap(year_range):
        filtered_df = df[(df['Founded Year'] >= year_range[0]) & (df['Founded Year'] <= year_range[1])]
        valuation_by_industry = filtered_df.groupby('Industry')['Valuation ($B)'].sum().reset_index()
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        fig_treemap = px.treemap(
            valuation_by_industry,
            path=['Industry'],
            values='Valuation ($B)',
            title=f'Total value per industry from {year_range[0]} to {year_range[1]}',
            color_discrete_sequence=colors
        )
        fig_treemap.update_layout(width=1500, height=600)
        return pn.pane.Plotly(fig_treemap)

    # Combine the slider, treemap, and description into a column layout
    layout = pn.Column(
        pn.pane.Markdown("# Embracing the Digital Revolution: Pioneering Towards an Evermore Digitized Industry"),
        year_slider,
        filtered_treemap,
        desc_treemap_pane  # Ensure the description pane is below the treemap
    )

    return layout

# Dropdown
industry_selector = pn.widgets.Select(name='Select Industry', options=df['Industry'].unique().tolist(), value=df['Industry'].unique()[0])

# Update the pie chart
def update_pie_2_chart(industry):
    filtered_df = df[df['Industry'] == industry]
    deal_terms = filtered_df['Deal Terms'].sum()
    portfolio_exits = filtered_df['Portfolio Exits'].sum()

    pie_fig = go.Figure(data=[go.Pie(labels=['Deal Terms', 'Portfolio Exits'],
                                     values=[deal_terms, portfolio_exits], hole=.4)])
    pie_fig.update_traces(hoverinfo="label+percent+name+value")
    pie_fig.update_layout(title_text=f"Deal Terms vs. Portfolio Exits for {industry}", width = 1000, height = 400)
    return pie_fig

# Update the stacked area chart
def update_area_chart(industry):
    filtered_df = df[df['Industry'] == industry]

    area_fig = go.Figure()
    area_fig.add_trace(go.Scatter(x=filtered_df['Founded Year'], y=filtered_df['Valuation ($M)'],
                                  stackgroup='one', name='Valuation ($M)'))
    area_fig.add_trace(go.Scatter(x=filtered_df['Founded Year'], y=filtered_df['Total Raised ($M)'],
                                  stackgroup='one', name='Total Raised ($M)'))
    area_fig.update_layout(title_text=f"Valuation and Total Raised over Time for {industry}", width = 1000, height = 400)
    return area_fig

# Descriptions for the charts
desc_pie_chart = "The donut chart contrasts the proportion of favorable deal terms against successful portfolio exits, providing insights into the sector's investment landscape and exit strategy success rates."
desc_area_chart = "The line graph tracks the evolution of the industry's valuation and the total capital raised over the years, highlighting trends and potential growth patterns within the sector."

# Define the style for the descriptions
description_style = {
    'text-align': 'center',
    'max-width': '90%',
    'margin-left': 'auto',
    'margin-right': 'auto',
    'font-size': '1.1em',
    'margin-top': '10px'
}

# Create the description panes for the charts
desc_pie_pane = pn.pane.Markdown(desc_pie_chart, styles=description_style)
desc_area_pane = pn.pane.Markdown(desc_area_chart, styles=description_style)

@pn.depends(industry_selector.param.value)
def reactive_pie_chart(industry):
    pie_chart = update_pie_2_chart(industry)
    return pn.Column(pn.pane.Plotly(pie_chart, height=350), desc_pie_pane)

@pn.depends(industry_selector.param.value)
def reactive_area_chart(industry):
    area_chart = update_area_chart(industry)
    return pn.Column(pn.pane.Plotly(area_chart, height=350), desc_area_pane)


def page_4_view():
    return pn.Column(
        pn.pane.Markdown("# How attractive is each sector?"),
        industry_selector,
        pn.Row(reactive_pie_chart, reactive_area_chart)
    )

tabs = pn.Tabs(
    ("Introduction", page_1_view),
    ("Geography Analysis", page_2_view),
    ("Industry Analysis - Overview", page_3_view),
    ("Industry Analysis - Financial Analysis", page_4_view),

)

tabs.servable()
