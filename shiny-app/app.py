from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Updated UI to allow multi-selection
app_ui = ui.page_fluid(
    ui.input_selectize(
        id='countries',
        label='Choose one or more countries:',
        choices=["Argentina", "Brazil", "Chile", "Mexico", "Paraguay", "Peru"],
        multiple=True  # Allow multi-selection
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
        ]
    ),
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
        selected_outcomes = input.outcomes() or []  # Handle no selection gracefully
        
        if df.empty or not selected_outcomes:
            return "No data available for the selected inputs."
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for outcome in selected_outcomes:
            column_name = outcome_mapping[outcome]
            for country in input.countries():
                country_data = df[df['country'] == country]
                ax.plot(
                    country_data['year'], 
                    country_data[column_name], 
                    label=f'{country} - {outcome}'
                )
        
        # Construct a dynamic title and axis labels
        countries_text = ", ".join(input.countries())
        outcomes_text = ", ".join(selected_outcomes)
        
        ax.tick_params(axis='x', rotation=45)
        ax.set_xlabel('Year')
        ax.set_ylabel("Values")
        ax.set_title(f"Trends for {outcomes_text} in {countries_text}")
        ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize='small')
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{int(x):,}'))
        fig.tight_layout()
        return fig

app = App(app_ui, server)

