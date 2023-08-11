# snowflake-app-with-docker

## 概要・解説

→解説記事：[Snowflakeアプリ開発環境をDockerで構築](https://zenn.dev/al_everywhere/articles/snowflake-app-with-docker)

## 構築方法

```
$ export OPENAI_API_KEY=sk-ABCDE...
$ export SNOWFLAKE_ACCOUNT=ex12345.ap-northeast-1.aws
$ export SNOWFLAKE_USERNAME=XXX
$ export SNOWFLAKE_PASSWORD=P@ssword!
$ docker compose build
$ docker compose up -d
```
