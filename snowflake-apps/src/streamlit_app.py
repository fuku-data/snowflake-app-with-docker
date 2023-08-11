from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os
import pandas as pd
import plotly.express as px
from snowflake.snowpark.session import Session
import streamlit as st


def init_page():
    st.set_page_config(
        page_title="Snowflake App",
        page_icon=":snowflake:"
    )
    st.header("Snowflakeアプリ開発環境をDockerで構築")
    st.sidebar.title("LLM Option")


def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"

    temperature = st.sidebar.slider("Temperature:",
                                    min_value=0.0,
                                    max_value=2.0,
                                    value=0.0,
                                    step=0.1
                                    )

    return ChatOpenAI(temperature=temperature, model_name=model_name)


def init_messages():
    clear_button = st.sidebar.button("チャットをクリア", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]
        st.session_state.costs = []


def create_session_object():
    connection_parameters = {
        "account": os.environ['SNOWFLAKE_ACCOUNT'],
        "user": os.environ['SNOWFLAKE_USERNAME'],
        "password": os.environ['SNOWFLAKE_PASSWORD'],
        "role": "ACCOUNTADMIN",
        "warehouse": "COMPUTE_WH",
        "database": "COVID19_EPIDEMIOLOGICAL_DATA",
        "schema": "PUBLIC"
    }
    session = Session.builder.configs(connection_parameters).create()
    return session


def get_df_date_vs_cases(session):
    df_all_country = session.sql(
        """
        SELECT COUNTRY_REGION FROM PUBLIC.ECDC_GLOBAL GROUP BY COUNTRY_REGION;
        """
    ).to_pandas()

    df_selected_country = st.multiselect(
        '調査したい国名を選択してください。',
        df_all_country,
        ['United States', 'India', 'France']
    )

    # vertically concat DATE, CASES, and COUNTRY_REGION by country
    df_date_vs_cases = pd.DataFrame()
    for i in range(len(df_selected_country)):
        df_date_vs_cases_in_a_country = session.sql(
            f"""
            SELECT DATE, CASES, COUNTRY_REGION FROM PUBLIC.ECDC_GLOBAL
            WHERE COUNTRY_REGION = '{df_selected_country[i]}';
            """
        ).to_pandas()

        df_date_vs_cases = pd.concat([df_date_vs_cases,
                                      df_date_vs_cases_in_a_country
                                      ])

    return df_date_vs_cases


def draw_graph(df_selected_cases):
    # exception handling when none of the countries are selected
    try:
        fig = px.line(df_selected_cases,
                      x='DATE',
                      y='CASES',
                      color='COUNTRY_REGION')

        fig.update_layout(xaxis_title='date',
                          legend_title='country',
                          yaxis_title='number of cases'
                          )
        st.write(fig)

    except ValueError:
        st.write("⛔国名を1つ以上、選択してください")


def converse_with_ai(llm):
    container = st.container()
    with container:
        with st.form(key='your_form', clear_on_submit=True):
            user_input = st.text_area(label='質問はありませんか？',
                                      key='input',
                                      height=100
                                      )

            # leave nothing against line breaks
            content = user_input.replace('\n', '')
            submit_button = st.form_submit_button(label='送信')

    if submit_button and user_input:
        st.session_state.messages.append(HumanMessage(content=content))
        with st.spinner("Waiting ..."):
            response = llm(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    # present chat history
    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:
            st.write(f"System message: {message.content}")


def main():
    init_page()
    llm = select_model()
    init_messages()

    st.subheader("COVID-19 国別感染者数の表示📉")
    session = create_session_object()
    df_cases = get_df_date_vs_cases(session)
    draw_graph(df_cases)

    st.subheader("AIサポート🤖")
    converse_with_ai(llm)


if __name__ == '__main__':
    main()
