import pandas as pd
from bokeh.layouts import row
from bokeh.models import ColumnDataSource, HoverTool, Select
from bokeh.plotting import figure, curdoc

# callback function for the Select widget
def select_data(attr, old, new):
    if new == 'Mammalia':
        plot_source.data = dict(data_source_mam.data)
        plot_1.y_range.factors = list(plot_source.data['species'])

    elif new == 'Aves':
        plot_source.data = dict(data_source_aves.data)
        plot_1.y_range.factors = list(plot_source.data['species'])

    else:
        plot_source.data = dict(data_source_rept.data)
        plot_1.y_range.factors = list(plot_source.data['species'])


# read data from .csv file
df = pd.read_csv('AZA_MLE_Jul2018_utf8.csv', encoding='utf-8')
# construct list of indizes to remove unnecessary columns
cols = [1, 3]
cols.extend([i for i in range(7, 15)])
df.drop(df.columns[cols], axis=1, inplace=True)

# rename the columns of the data frame
df.rename(columns={'Species Common Name': 'species', 'TaxonClass': 'taxon_class', 'Overall CI - lower': 'ci_lower',
                   'Overall CI - upper': 'ci_upper', 'Overall MLE': 'mle', 'Male Data Deficient': 'male_deficient',
                   'Female Data Deficient': 'female_deficient'}, inplace=True)


# task 1:
# Remove outliers, split the dataframe by taxon_class and and construct a ColumnDataSource from the clean DataFrames

# split the dataframe by taxon_class (Mammalia, Aves, Reptilia) and remove the outliers
# outliers are entries which have male and/or female data deficient set to yes.
df_mam = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Mammalia')]
df_aves = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Aves')]
df_rept = df.loc[(df['male_deficient'] != 'yes') & (df['female_deficient'] != 'yes') & (df['taxon_class'] == 'Reptilia')]

# sort the dataframes by 'mle' in descending order and then reset the index
df_mam = df_mam.sort_values(by='mle', ascending=False)
df_aves = df_aves.sort_values(by='mle', ascending=False)
df_rept = df_rept.sort_values(by='mle', ascending=False)
df_mam.reset_index(drop=True, inplace=True)
df_aves.reset_index(drop=True, inplace=True)
df_rept.reset_index(drop=True, inplace=True)

# reduce each dataframe to contain only the 10 species with the highest 'mle'
df_mam = df_mam.loc[(df_mam.index < 10)]
df_aves = df_aves.loc[(df_aves.index < 10)]
df_rept = df_rept.loc[(df_rept.index < 10)]

# sort the dataframe in the correct order to display it in the plot and reset the index again.
# index modified because it defines the y location of the bars in the final plot

df_mam = df_mam[::-1].reset_index(drop=True)
df_aves = df_aves[::-1].reset_index(drop=True)
df_rept = df_rept[::-1].reset_index(drop=True)
df_mam.index += 0.5
df_aves.index += 0.5
df_rept.index += 0.5

# Renaming an entry in the aves dataframe of the species named 'Penguin, Northern & Southern Rockhopper (combined)'.
df_aves.loc[df_aves['species'].str.contains('Rockhopper'), 'species'] = 'Penguin, Rockhopper'

# construct a ColumDataSource for each of the dataframes
data_source_mam = ColumnDataSource(data=df_mam)
data_source_aves = ColumnDataSource(data=df_aves)
data_source_rept = ColumnDataSource(data=df_rept)

# construct a fourth ColumnDataSource that is used as input for the plot and set it to the Mammalian ColumnDataSource
# as initial value. This is required to later be able to change the data interactively with the dropdown menu.
plot_source = ColumnDataSource(data_source_mam.data)

# task 2:
# configure mouse hover tool
# reference: https://bokeh.pydata.org/en/latest/docs/user_guide/categorical.html#hover-tools
hover = HoverTool(names=['mle_hbar'], tooltips=[('low', '@ci_lower'), ('high', '@ci_upper')])

# construct a figure with the correct title, axis labels, x and y range, add the hover tool and disable the toolbar
plot_1 = figure(plot_height=700, plot_width=1500, x_axis_label='Medium life expectancy [Years]', y_axis_label='Species',
                toolbar_location=None, x_range=(0, 5 + max(plot_source.data['ci_upper'])),
                y_range=plot_source.data['species'], tools=[hover], title='Medium Life Expectancy of Animals in Zoos')

# add the horizontal bar chart to the figure and configure it correctly.
plot_1.hbar(y='index', left='ci_lower', right='ci_upper', height=0.5, source=plot_source, name='mle_hbar')

# add a Select tool (dropdown selection) and configure its 'on_change' callback.
data_select = Select(title='Taxonomic Class', value='Mammalia', options=['Mammalia', 'Aves', 'Reptilia'])
data_select.on_change('value', select_data)

# using curdoc to add plot and Select widget to the document for interactive plotting session
curdoc().add_root(row(plot_1, data_select))
curdoc().title = 'dva_ex1'
