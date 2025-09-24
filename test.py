from toolfront import Browser, Database

browser = Browser("http://0.0.0.0:8000")

response = browser.ask("What are some products and revenues", model="anthropic:claude-3-5-sonnet-latest", stream=True)

# # response = browser.ask(
#     # "What is the percentage of population under 25 years old for different countries in 2020?", model="anthropic:claude-3-5-sonnet-latest", stream=True
# # )


# response = browser.ask("Find the best queries to execute and execute one", model="openai:gpt-4o", stream=True)
# print(response)

db = Database(url="postgres://localhost:5432/postgres")

db.ask("What's available in the database?", stream=True)

# db = Database(
#     url="snowflake://gavin_kruskal:zKfzVOmwY1lPp8@RSRSBDK-YDB67606/NEW_YORK_CITIBIKE_1",
# )


# db = Database(
#     url="snowflake://gavin_kruskal:zKfzVOmwY1lPp8@RSRSBDK-YDB67606/NEW_YORK_CITIBIKE_1",
# )

# class Ride(BaseModel):
#     start_station_name: str
#     end_station_name: str
#     duration_minutes: int


# # Test the clean implementation
# answer: db.Table[Ride] = db.ask(
#     "What are the 5 longest NYC bike rides?", model="anthropic:claude-3-5-sonnet-latest", stream=False
# )
# print(answer.to_dataframe())

# # ATTACH 'project=spider-2-456320' as bq(TYPE bigquery, READ_ONLY)
# # SELECT * FROM `bigquery-public-data.austin_311.311_service_requests` LIMIT 10;
