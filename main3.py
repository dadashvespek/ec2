
# Import the necessary classes and functions
import pytesseract
from aiogram import Bot, Dispatcher, types, executor
import openai
import re
import asyncpg  # Import the asyncpg library
import pymysql
# Initialize the OpenAI client
openai.api_key = "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"
import pandas as pd
# First, install SQLAlchemy if you don't already have it:
# !pip install sqlalchemy
from tabulate import tabulate
import io
import matplotlib.pyplot as plt

#cursor.execute("CREATE TABLE user_inputs (chat_id INTEGER, text VARCHAR(255), username VARCHAR(255))")


# Create a bot instance and a dispatcher instance
bot = Bot(token="6264813204:AAHLQrfz3IZfiD7ZAdol83BKgBO1U3LsRRY")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # Send a welcome message to the user
    await bot.send_message(
        chat_id=message.chat.id,
        text="Hello",
    )
con=pymysql.connect(host='database-2.c9hiv3qctimr.us-east-1.rds.amazonaws.com',
                                                                user='admin',
                                                                password='12Adfs12',
                                                                database='user'
                                                                )
df = pd.read_sql("SELECT * FROM Xeneta", con)
del df['Unnamed: 0']
con.close()
for j,row in df.iterrows():
    df.at[j,"To"]=df.at[j,"Rate - Valid to"].split(', ')[0]
    df.at[j,"From"]=df.at[j,"Rate - Valid from"].split(', ')[0]
@dp.message_handler()
async def handle_message(message: types.Message):
    # Connect to the database and read the data into a DataFrame

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f'from the text derive these informations in this format format:[Origin City (from),Destination City(to)] example:text:"how much would it be to send some goods from Anqing China to Colombo, the city in Sri Lanka?" reply:[Anqing,Colombo] example2:text: "ship from bangkok to mangalore?" reply:[Bangkok,Mangalore] note: if text doesnt have destination or origin city reply put NaN instead, example:text:"I want to ship some goods from Anqing, China" reply:[Anqing,NaN] \n text:{message.text} reply:',
        temperature=0,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    try:
        print(response["choices"][0]["text"].strip().split(", "))
        destination = response["choices"][0]["text"].strip().split(",")[1][:-1]
        origin = response["choices"][0]["text"].strip().split(",")[0][1:]
        filtered_df = df[(df["To"] == destination) & (df["From"] == origin)]
        # Drop all rows with at least one NaN value
        filtered_df = filtered_df.dropna(axis=1,how='any')

    # Extract the data you want from the filtered DataFrame and format it as a string
        filtered_df = filtered_df[['BAS, Currency','BAS, 20DC', 'BAS, 40DC','BAS, 40HC']]
        # Continue after the for-loop

        # Create the output string that you want to pass to the OpenAI API
        output_string = f"Here are the BAS charges for shipping from {origin} to {destination}:\n\n"
        for i, row in filtered_df.iterrows():
            output_string += f"{row['BAS, Currency']} {row['BAS, 20DC']} for 20DC\n"
            output_string += f"{row['BAS, Currency']} {row['BAS, 40DC']} for 40DC\n"
            output_string += f"{row['BAS, Currency']} {row['BAS, 40HC']} for 40HC\n\n"

        # Pass the output string as the prompt to the OpenAI API
        # Pass the output string as the prompt to the OpenAI API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"act as if you are a freight straight-to-the-point customer representative wanting to inform the customer of the BAS (BAS is the Basic freight rate) charges of different container sizes for shipping from {origin} to {destination}:\n\n the costs:{output_string} your response to the customer (remember to stay in character):",
            temperature=0,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

    # Extract the response from the API and send it to the customer
        relay_message = response["choices"][0]["text"].strip()
        await message.answer(f'{relay_message}\n\nAdditionally, you can refer to the table below:')

        
        fig, ax = plt.subplots(figsize=(5, 0.5))

        # Use the table method to generate the table
        table = ax.table(cellText=filtered_df.values, colLabels=[i.split(', ')[1] for i in filtered_df.columns], loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(0.8, 1.5)

        # Remove the axis and set the borders of the cells
        ax.axis('tight')
        ax.axis('off')
        for pos, cell in table.get_celld().items():
            cell.set_edgecolor('black')
            cell.set_text_props(wrap=True, ha='center', fontsize=10)

        # Save the figure to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Send the buffer as a file
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=buf
        )

        # Close the buffer and plot
        buf.close()
        plt.close()
    except: 
        await message.answer(f"Sorry, I couldn't find anything on that")



   

# Start the bot
executor.start_polling(dp)
'''
#5817675604:AAF3u7dzcQQLCaPnbV-wAEv_WvWvSprmKe8

# Connect to the database
conn = pymysql.connect(host='database-2.c9hiv3qctimr.us-east-1.rds.amazonaws.com',
                       user='admin',
                       password='12Adfs12',
                       database='user'
                       )

# Create a cursor
cursor = conn.cursor()

# Use the TRUNCATE TABLE statement to clear the data in the chat_message table
truncate_table_sql = 'TRUNCATE TABLE chat_message'
cursor.execute(truncate_table_sql)

# Commit the changes
cursor.connection.commit()

# Close the cursor and the connection
cursor.close()
conn.close()
'''