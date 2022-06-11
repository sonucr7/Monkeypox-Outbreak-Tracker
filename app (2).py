import streamlit as st
import pandas as pd 
#from datetime import datetime
from datetime import datetime, timedelta
import plotly.express as px
from PIL import Image
import validators

st.set_page_config(page_title="Monkeypox Outbreak Tracker", page_icon="💹", layout="wide")


with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)

#load data function
@st.cache(allow_output_mutation=True)
def load_data(data):
    df = pd.read_csv(data)
    return df


def main():
    #menu = ["Home", "All about Monkeypox", "About Me"]
    
    #choice = st.sidebar.selectbox("Menu", menu)
    
    #if choice == "Home":
    st.markdown('''
                # Monkeypox Outbreak Tracker :chart:
                ''')
    
    st.write(" ")
    
    expander = st.expander(f"About this app!")
    expander.write('''
                    
                    **This app is a tool to track the number of monkeypox cases globally. Source of our data is https://global.health/ . Big kudos to them for providing real-time data.**''')
    
    st.write(" ")
    
    data = load_data("https://raw.githubusercontent.com/globaldothealth/monkeypox/main/latest.csv")
    #st.dataframe(data)
    
    col1, col2, col3 = st.columns([1,1,1])
    
    with col1:
        # datetime object containing current date and time
        #now = datetime.now()
        #dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        #st.info(f"Last updated at : {dt_string}")
        
        data['date'] = pd.to_datetime(data['Date_last_modified'])
        data_date = data['date'].max()
        st.info(f" **Last updated on** : {data_date}")
    
        total_affected_countries = data['Country'].nunique()
        st.error(f" **Total affected countries so far** : {total_affected_countries}")
    
    with col2:
        
        country_with_most_cases = data['Country'].value_counts().idxmax()
        st.info(f" **Country with the most cases** : {country_with_most_cases}")
        
        city_with_most_cases = data['City'].value_counts().idxmax()
        st.error(f" **City with the most cases** : {city_with_most_cases}")
        
    with col3:
        
        total_global_cases = data['Status'].value_counts().sum()
        st.info(f" **Total cases globally so far** : {total_global_cases}")
        
        most_common_symptoms = data['Symptoms'].value_counts().idxmax()
        st.error(f" **The most common symptoms found** : {most_common_symptoms}")
        
    col4, col5 = st.columns([1,1])
    
    with col4:
        
        st.subheader("****Last 7 days Curve****")
        data['Date_confirmation'] = pd.to_datetime(data['Date_confirmation'])
        data = data.sort_values(by=['Date_confirmation'], ascending=False )
        date_before_7_days = datetime.now() - timedelta(days=8)
        data_last_7_days = data.loc[data['Date_confirmation'] > date_before_7_days]
        data_last_7_days = data_last_7_days['Date_confirmation'].value_counts().to_frame()
        data_last_7_days['index'] = pd.to_datetime(data_last_7_days.index)
        data_last_7_days.reset_index(drop=True, inplace=True)
        data_last_7_days = data_last_7_days.rename(columns={'Date_confirmation': 'Count','index': 'Date_confirmation'})
        data_last_7_days = data_last_7_days.sort_values(by=['Date_confirmation'], ascending=False )
        fig_time = px.line(data_last_7_days,
                    x='Date_confirmation',
                    y='Count',
                    title='Number of cases in last 7 days')
        st.plotly_chart(fig_time)
        
    with col5:
        st.subheader("****Countries to avoid for travelling****")
        data_travel = data.loc[(data['Travel_history (Y/N/NA)'] == 'Y') & (data['Status'] == 'confirmed')]
        number_of_people_confirmed_with_travel_history = len(data_travel)
        top_3_country_avoid_for_travelling = data_travel['Travel_history_country'].value_counts().index.tolist()[:3]
        st.warning(f"**{number_of_people_confirmed_with_travel_history}** people who found positive have travelled to countries listed below 👇")
        st.json(top_3_country_avoid_for_travelling)
    
    col6, col7 = st.columns([1,1])
    
    with col6:
        st.subheader("****Global Monkeypox Cases****")
        st.write("Maximize the chart for a clear view of the data 👇")
        cases_per_country = data.groupby('Country')['Status'].count().reset_index()
        fig = px.bar(cases_per_country, x='Country', y='Status', color='Country')
        st.plotly_chart(fig)
        
    with col7:
        st.subheader("****Top 10 Affected Cities****")
        #data['City'].value_counts()
        cases_per_city = data.groupby('City')['Status'].count().reset_index()
        cases_per_city_top10 =cases_per_city.nlargest(n=10, columns='Status')
        fig1 = px.bar(cases_per_city_top10, x='City', y='Status', color='City')
        st.plotly_chart(fig1)
        
    col8, col9 = st.columns([1,1])
    
    with col8:
        top_10_countries = list(data['Country'].value_counts().to_frame().nlargest(10, 'Country').index)
        #st.write(top_10_countries)
        st.subheader("****Top 10 Affected Countries****")
        top_10_countries_affected = data.groupby('Country')['Status'].count().reset_index()
        top_10_countries_affected = top_10_countries_affected.nlargest(n=10, columns='Status')
        fig2 = px.bar(top_10_countries_affected, x='Country', y='Status', color='Country')
        st.plotly_chart(fig2)
        
    with col9:
        st.subheader("****Distribution of Cases by Status****")
        st.write("Status of reported cases in top 10 affected countries 👇")
        top_reported_countries = list(data['Country'].value_counts().to_frame().nlargest(10, 'Country').index)
        top_reported_countries_df = data[data['Country'].isin(top_reported_countries)]
        fig3 = px.bar(top_reported_countries_df, x='Country', y='Status', color='Status')
        st.plotly_chart(fig3)
        
    col10, col11 = st.columns([1,1])
    
    with col10:
        st.subheader("****Top 5 Reported Symptoms****")
        top_5_symptoms = data.groupby('Symptoms')['Status'].value_counts().groupby(level=0).head(5).sort_values(ascending=False).to_frame('counts').reset_index()
        top_5_symptoms = top_5_symptoms.nlargest(n=5, columns='counts')
        fig4 = px.bar(top_5_symptoms, x='Symptoms', y='counts', color='Symptoms')
        st.plotly_chart(fig4)
    
    with col11:
        st.subheader("****Cases by Gender****")
        st.write("For many cases, Gender information might not be available")
        data["Gender"] = data["Gender"].replace("male ", "male")
        data["Gender"] = data["Gender"].replace("Male", "male")
        data["Gender"] = data["Gender"].fillna("unknown")
        fig5 = px.pie(data['Gender'], values=data['Gender'].value_counts().values, names=data['Gender'].value_counts().index)
        fig5.update_traces(hoverinfo='label+percent', textinfo='value')
        st.plotly_chart(fig5)
        
    col12, col13 = st.columns([1,1])
    
    with col12:
        st.subheader("****Cases by Age****")
        data['Age'] = data["Age"].fillna("unknown")
        age_data=data['Age'].value_counts()
        age_data = age_data.to_frame().reset_index()
        age_data = age_data.rename(columns={'Age': 'Count','index': 'Age', })
        fig6 = px.bar(age_data,
                    x='Age',
                    y='Count',
                    title='Age Distribution',
                    barmode='stack')
        st.plotly_chart(fig6)
        
    with col13:
        st.subheader("****Confirmation Method****")
        data['Confirmation_method'] = data["Confirmation_method"].fillna("unknown")
        confirmation_method_data = data['Confirmation_method'].value_counts().to_frame().reset_index()
        confirmation_method_data = confirmation_method_data.rename(columns={'Confirmation_method': 'Count','index': 'Confirmation_method', })
        fig7 = px.bar(confirmation_method_data,
                    x='Confirmation_method',
                    y='Count',
                    title='Confirmation Method Distribution',
                    barmode='stack')
        st.plotly_chart(fig7)
        
    col14, col15 = st.columns([1,1])
    
    with col14:
        st.subheader("****Genomics Metadata of few Cases****")
        st.info("Genomics metadata of cases will be helpful for future analysis")
        data['Genomics_Metadata'] = data["Genomics_Metadata"].fillna("unknown")
        link_list = []
        for ind in data.index:
            valid=validators.url(data['Genomics_Metadata'][ind])
            if valid:
                link_list.append(data['Genomics_Metadata'][ind])
        st.json(link_list[:5])
        
    with col15:
        st.subheader("****Hospitalization/Isolation Distribution****")
        data_hospitalised = data.loc[data['Hospitalised (Y/N/NA)'] == 'Y']
        number_of_patients_hospitalised = len(data_hospitalised)
        data_isolated = data.loc[data['Isolated (Y/N/NA)'] == 'Y']
        number_of_patients_isolated = len(data_isolated)
        total_unknown_values = data['Isolated (Y/N/NA)'].isna().sum() + data['Hospitalised (Y/N/NA)'].isna().sum()
        data_h_vs_i = {'Category': ['Hospitalised', 'Isolated', 'Unknown'],
                'Count': [number_of_patients_hospitalised, number_of_patients_isolated, total_unknown_values]}
        df_h_vs_i = pd.DataFrame(data_h_vs_i)
        fig8 = px.bar(df_h_vs_i,
                    x='Category',
                    y='Count',
                    title='Hospitalized vs Isolated',
                    barmode='stack')
        st.plotly_chart(fig8)
        
    
        
        
    st.markdown("""--------------------------------------------------------------------------------------------""")
    st.markdown("""
**Want to say a "Hi" to the creator of the app? 🤔 Here you go 👉 https://www.linkedin.com/in/sonukr0/**
""")
                        

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if __name__ == '__main__':
    main()