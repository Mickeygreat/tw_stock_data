import streamlit as st
import pandas as pd
import yfinance as yf
import time
import math
import datetime
import warnings

# Suppress warnings from yfinance
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")


def roundUp(number, ndigits=0):
    """Always round off"""
    exp = number * 10 ** ndigits
    if abs(exp) - abs(math.floor(exp)) < 0.5:
        return type(number)(math.floor(exp) / 10 ** ndigits)
    return type(number)(math.ceil(exp) / 10 ** ndigits)


def process_file(df):
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    volume_list = []

    for i in range(len(df)):
        try:
            ticker = df["代號"][i]
            yahoo_data = yf.download(f"{ticker}.TW", period="1d")
            open_price = yahoo_data["Open"][0].item()
            high = yahoo_data["High"][0].item()
            low = yahoo_data["Low"][0].item()
            close = yahoo_data["Close"][0].item()
            volume = yahoo_data["Volume"][0].item()

            open_list.append(open_price)
            high_list.append(high)
            low_list.append(low)
            close_list.append(close)
            volume_list.append(volume)
        except Exception:
            open_list.append(pd.NA)
            high_list.append(pd.NA)
            low_list.append(pd.NA)
            close_list.append(pd.NA)
            volume_list.append(pd.NA)

        progress_bar.progress((i + 1) / len(df))

    df["Open"] = open_list
    df["High"] = high_list
    df["Low"] = low_list
    df["Close"] = close_list
    df["Volume"] = volume_list

    return df


# Streamlit app
st.title("Financial Data Processor")

uploaded_file = st.file_uploader(
    "Upload an Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    st.write("Uploaded Data:")
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, index_col=None, engine="openpyxl")
    else:
        df = pd.read_csv(uploaded_file)
    st.write(df)

    start_time = datetime.datetime.now()
    st.write("Processing file...")
    progress_bar = st.progress(0)

    processed_df = process_file(df)

    end_time = datetime.datetime.now()
    runtime = end_time - start_time

    st.write("Processed Data:")
    st.write(processed_df)

    st.write(f"Runtime: {runtime}")

    # Option to download the processed file
    output_file_name = "processed_data.xlsx"
    processed_df.to_excel(output_file_name, index=False)
    with open(output_file_name, "rb") as file:
        btn = st.download_button(label="Download Processed Data", data=file, file_name=output_file_name,
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
