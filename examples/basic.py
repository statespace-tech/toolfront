import os

from dotenv import load_dotenv

from toolfront import Database

load_dotenv()


# snowflake = Database(url=os.environ["SNOWFLAKE_URL"] + "/NEW_YORK_CITIBIKE_1")
# avg_duration: float | None = snowflake.ask(
#     "What's the average bike rideshare duration in 2016-2018 in minutes?",
#     model="openai:gpt-4.1",
#     stream=True,  # Streaming mode - shows live progress in terminal
# )
# print(avg_duration)

# # Quiet mode (default) - no streaming output to terminal
pg = Database(url=os.environ["POSTGRES_URL"])
schema_summary = pg.ask(
    "Summarize the database schema including key tables and their relationships",
    model="openai:gpt-4.1",
)
print(schema_summary)
