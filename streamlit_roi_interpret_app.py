import streamlit as st
import shap
from shap import TreeExplainer
from sklearn.ensemble import RandomForestRegressor
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import pickle

# APP
st.title("Interpreting College ROI")

st.markdown("""There are many factors leading to choice of college to attend, one of the largest being the level of employeement opportunities available after attend a given college, which can be termed a "return on investment", or ROI.
            This page is intended to help explain both expected income and how this is estimated through a machine learning model.
            """)
st.markdown(""" 
            Explore the tabs below to find both the **expected post-entry income** of your favorite school and **how different variables contributed** to that expected income score.
            Information from 4-year degree awarding US universities, recorded in the Department of Education's [College Scorecard](https://collegescorecard.ed.gov/) are included in this analysis.
            """)
st.markdown('Much of this work is done using the [`shap`](https://shap.readthedocs.io/en/latest/index.html) python package, which calculates the average contribution of model inputs to expected income measures.')

# TODO: clean 10 year data, and edit data import accordingly
outcome = st.sidebar.radio(
    "Number of years post college entry:",
    [6, 10]
)

# SOURCE CODE
# cache data
@st.experimental_memo
def data_import():
    # import data
    # read in preprocessed data
    X_filled = pd.read_csv("./saved_data/X_filled.csv",index_col="School Name")
    Xtrain_filled = pd.read_csv("./saved_data/Xtrain_filled.csv",index_col="School Name")
    ytrain = pd.read_csv("./saved_data/ytrain.csv",index_col="School Name").squeeze()
    Xtest_filled = pd.read_csv("./saved_data/Xtest_filled.csv",index_col="School Name")
    ytest0 = pd.read_csv("./saved_data/ytest.csv",index_col="School Name").squeeze()
    # 10 year post entry data
    X_filled10 = pd.read_csv("./saved_data/X_filled10.csv",index_col="School Name")
    Xtrain_filled10 = pd.read_csv("./saved_data/Xtrain_filled10.csv",index_col="School Name")
    ytrain10 = pd.read_csv("./saved_data/ytrain10.csv",index_col="School Name").squeeze()
    Xtest_filled10 = pd.read_csv("./saved_data/Xtest_filled10.csv",index_col="School Name")
    ytest10 = pd.read_csv("./saved_data/ytest10.csv",index_col="School Name").squeeze()

    # X_filled = pd.read_csv("X_filled.csv",index_col="School Name")
    # Xtrain_filled = pd.read_csv("Xtrain_filled.csv", index_col="School Name")
    # Xtest_filled = pd.read_csv("Xtest_filled.csv", index_col="School Name")
    # ytrain = pd.read_csv("ytrain.csv", index_col="School Name").squeeze()
    # ytest0 = pd.read_csv("ytest.csv", index_col="School Name").squeeze()
    # ytrain10 = pd.read_csv("ytrain10.csv", index_col="School Name").squeeze()
    # ytest010 = pd.read_csv("ytest10.csv", index_col="School Name").squeeze()
    # eventually, will call DataCollectClean script, which will produced these csvs,
    # and then will read them in as done here
    
    #ytrain_chosen = ytrain if outcome == 6 else ytrain10

    return X_filled,Xtrain_filled,ytrain,X_filled10,Xtrain_filled10,ytrain10

X_filled,Xtrain_filled,ytrain,X_filled10,Xtrain_filled10,ytrain10 = data_import()

# for now can comment this out, as shap values read in from pickle
# train chosen model(s)
# @st.experimental_singleton
# def model_fit(X,y):
#     rf = RandomForestRegressor(n_estimators=200, criterion='squared_error', max_features="sqrt").fit(X,y)
#     # rf10 = RandomForestRegressor(n_estimators=150, criterion='squared_error').fit(Xtrain_filled,ytrain10)
#     return rf

# rf = model_fit(Xtrain_filled,ytrain)
# rf10 = model_fit(Xtrain_filled10,ytrain10)
# if time: could also fit quantile regressor! and get ci's of expected income for each school

# get shap values
# NEED to cache these shap values
@st.experimental_memo
def get_shap_values(file_name):  
    #(_fitted_model, feature_set):
    # explainer = TreeExplainer(_fitted_model)
    # shap_values = explainer(feature_set) # get shap values for all colleges
    # above takes several minutes
    # faster: read in shap values from pickle
    fileObj = open(file_name, 'rb')
    shap_values = pickle.load(fileObj)
    fileObj.close()
    return shap_values

# add ability to switch models based on chosen response variable
# with pickle values, this only takes a few seconds (rather than several minutes)
shap_values6 = get_shap_values("./saved_data/shap_values6.obj")
shap_values10 = get_shap_values("./saved_data/shap_values10.obj")
shap_values = shap_values6 if outcome == 6 else shap_values10
school_inds = X_filled.index if outcome == 6 else X_filled10.index
# APP continued

# if desire 2 columns
# col1, col2 = st.columns(2)


tab1, tab2, tab3 = st.tabs(["School Specific", "Feature Contributions", "Global Summary"])

# trying to edit plot dims in side bar didn't work,
# but is good template if desiring to use a side bar
# plot_width = st.sidebar.slider("plot width", 1, 25, 3)
# plot_height = st.sidebar.slider("plot height", 1, 25, 1)

with tab1:
    st.header("School Specific Expected Income: Explained")
    school = st.selectbox("Select a school (sorted alphabetically)", options = school_inds.sort_values(),
                          label_visibility="visible")
    idx_of_interest = np.argwhere(school_inds == f'{school}')[0][0]
    school_fig, ax1 = plt.subplots(1,1)
    shap.plots.waterfall(shap_values[idx_of_interest],show=True,
                         max_display = 15)
    plt.title(f'{school} Expected Income {outcome}-years Post Entry: Explained')
    # plt.xlim([30000,100000])
    # plt.show()
    st.pyplot(school_fig)

with tab2:
    # TODO: change y-axis label
    st.header("Feature Contribution Summary")
    disp_feat = st.selectbox('Select a feature to display', options=X_filled.columns.sort_values())
    st.subheader(f'Scatterplot of {disp_feat} Contribution')
    shap.plots.scatter(shap_values[:, f'{disp_feat}'],show=True)
    plt.ylabel("Expected Contribution to post-entry Income")
    st.pyplot(plt.gcf())

    # if time: add interaction plot
    
with tab3:
    # feature importance plot
    st.subheader('Feature Importance')
    # outcome = st.selectbox("Choose outcome of interest", options = [])
    st.markdown("This plot helps us see the average contribution of each feature to expected income")
    # if get current figure does not work, try this:
    fig, ax = plt.subplots(nrows=1,ncols=1)
    #shap.plots.bar(shap_values,max_display = 15)
    shap.summary_plot(shap_values,max_display = 15,plot_type = 'bar')
    # as stated in documentation, setting show to false allows for further customization
    # https://shap.readthedocs.io/en/latest/generated/shap.plots.bar.html
    #st.pyplot(plt.gcf())
    # get current figure and attempt to set xlabel
    plt.title("Relative Contributions to Expected Income Outputs")
    plt.xlabel("Average absolute impact on model output\n(mean(|SHAP value|))")
    st.pyplot(fig) # may want to add clear_figure = True

    # COULD ADD: 
    # st.header("Sorted Expected Income Outputs")
    # enter here: table of sorted predictions


st.write("""""")
st.write("""
         Copyright &copy; 2023 Tyler Ward. All rights reserved.
         """)
