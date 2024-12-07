from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import itertools
from matplotlib.ticker import FuncFormatter

# Updated UI with title and inputs side-by-side
app_ui = ui.page_fluid(
    # Layout: Inputs on the left, Title and Description on the right
    ui.row(
        # Left column: Inputs
        ui.column(
            6,  # Adjust column width as needed
            ui.h2("Education and Housing Outcomes by Country"),
            ui.p(
                "This dashboard allows you to explore trends for various outcomes across different countries. The data originates from data obtained from Socio-Economic Datasets for Latin America and the Caribbean (SEDLAC), made available by the Center of Distributive, Labor and Social Studies from the National University of La Plata, in Argentina."

                "This dashboard is a part of a larger project created for the Data and Programming for Public Policy II - Python Progamming course, at the Harris School of Public Policy. The graphs presented in this dashboard motivated our research question regarding the differential rural and  urban impacts of Conditional Cash Transfer Programs in Latin America."

                "Use the inputs on the right to customize the visualization."
            )
        ),
        # Right column: Title and Description
        ui.column(
        6,  # Adjust column width as needed
            ui.input_selectize(
                id='countries',
                label='Choose one or more countries:',
                choices=["Brazil", "Chile", "Mexico", "Paraguay", "Peru"],
                multiple=True,
                selected=["Brazil", "Peru"]  # Default selection
            ),
            ui.input_checkbox_group(
                id='outcomes',
                label='Choose one or more outcomes:',
                choices=[
                    "Years of Education: Rural Population",
                    "Years of Education: Urban Population",
                    "Rural School Enrollment, 6- to 12-year-olds",
                    "Urban School Enrollment, 6- to 12-year-olds",
                    "Rural School Enrollment, 13- to 17-year-olds",
                    "Urban School Enrollment, 13- to 17-year-olds",
                    "Low-Quality Urban Dwellings",
                    "Low-Quality Rural Dwellings"
                ],
                selected=["Rural School Enrollment, 13- to 17-year-olds", "Urban School Enrollment, 13- to 17-year-olds"]  # Default selection
            )
        )
    ),
    # Output plot below the layout
    ui.output_plot('ts')
)

def server(input, output, session):
    # Load data once
    full_data = pd.read_csv("countries_with_cct_df.csv")
    
    outcome_mapping = {
        "Years of Education: Rural Population": "years_edu_all_rural",
        "Years of Education: Urban Population": "years_edu_all_urban",
        "Rural School Enrollment, 6- to 12-year-olds": "enrollment6_12yo_rural",
        "Urban School Enrollment, 6- to 12-year-olds": "enrollment6_12yo_urban",
        "Rural School Enrollment, 13- to 17-year-olds": "enrollment13_17yo_rural",
        "Urban School Enrollment, 13- to 17-year-olds": "enrollment13_17yo_urban",
        "Low-Quality Urban Dwellings": "dwellings_low_quality_urban",
        "Low-Quality Rural Dwellings": "dwellings_low_quality_rural"
    }

    @reactive.calc
    def subsetted_data():
        countries = input.countries() or []  # Handle no selection gracefully
        return full_data[full_data['country'].isin(countries)]

    @render.plot
    def ts():
        df = subsetted_data()
        selected_outcomes = input.outcomes() or []
        
        if df.empty or not selected_outcomes:
            return "No data available for the selected inputs."
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Define unique colors and line styles
        colors = itertools.cycle(plt.cm.tab10.colors)  # Use Matplotlib's color palette
        line_styles = itertools.cycle(["-", "--", "-.", ":"])  # Define line styles
        
        color_map = {country: next(colors) for country in input.countries()}
        style_map = {outcome: next(line_styles) for outcome in selected_outcomes}
        
        for outcome in selected_outcomes:
            column_name = outcome_mapping[outcome]
            for country in input.countries():
                country_data = df[df['country'] == country]
                ax.plot(
                    country_data['year'], 
                    country_data[column_name], 
                    label=f'{country} - {outcome}',
                    color=color_map[country], 
                    linestyle=style_map[outcome]
                )
        
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel('Year')
        ax.set_ylabel("Values")
        ax.set_title(f"Trends for {', '.join(selected_outcomes)} in {', '.join(input.countries())}")
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        return fig

app = App(app_ui, server)
