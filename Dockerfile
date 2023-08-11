FROM continuumio/miniconda3:23.5.2-0

COPY ./environment.yml .

RUN apt-get update \
    && conda env create -f ./environment.yml \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /opt/conda/envs/snowflake-env/bin:$PATH

RUN groupadd --gid 1000 streamlit \
    && useradd --uid 1000 --gid streamlit --shell /bin/bash --create-home streamlit \
    && mkdir /app \
    && chown -R streamlit:streamlit /app

EXPOSE 8501

WORKDIR /app

USER streamlit

COPY --chown=streamlit:streamlit ./snowflake-apps/src .

CMD ["streamlit", "run", "streamlit_app.py"]
