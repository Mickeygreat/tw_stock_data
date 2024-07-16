import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress warnings from yfinance
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")


def roundUp(number, ndigits=0):
    """Always round off"""
    exp = number * 10 ** ndigits
    if abs(exp) - abs(math.floor(exp)) < 0.5:
        return type(number)(math.floor(exp) / 10 ** ndigits)
    return type(number)(math.ceil(exp) / 10 ** ndigits)


def fetch_data(ticker, start_date, end_date):
    try:
        yahoo_data = yf.download(f"{ticker}.TW", start=start_date, end=end_date)
        if not yahoo_data.empty:
            open_price = yahoo_data["Open"][0].item()
            high = yahoo_data["High"][0].item()
            low = yahoo_data["Low"][0].item()
            close = yahoo_data["Close"][0].item()
            volume = yahoo_data["Volume"][0].item()
        else:
            open_price = high = low = close = volume = pd.NA
    except Exception as e:
        open_price = high = low = close = volume = pd.NA
        print(f"Error fetching data for {ticker}: {e}")

    return open_price, high, low, close, volume


def process_file(df, selected_date):
    start_date = selected_date
    end_date = start_date + datetime.timedelta(days=1)
    open_list = [pd.NA] * len(df)
    high_list = [pd.NA] * len(df)
    low_list = [pd.NA] * len(df)
    close_list = [pd.NA] * len(df)
    volume_list = [pd.NA] * len(df)

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_data, df["代號"][i], start_date, end_date): i for i in range(len(df))}
        for future in as_completed(futures):
            i = futures[future]
            open_price, high, low, close, volume = future.result()
            open_list[i] = open_price
            high_list[i] = high
            low_list[i] = low
            close_list[i] = close
            volume_list[i] = volume
            progress_bar.progress((i + 1) / len(df))

    df["Open"] = open_list
    df["High"] = high_list
    df["Low"] = low_list
    df["Close"] = close_list
    df["Volume"] = volume_list

    return df


# Streamlit app
st.title("Financial Data Processor")

uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file:
    st.write("Uploaded Data:")
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file, index_col=None, engine="openpyxl")
    else:
        df = pd.read_csv(uploaded_file)
    st.write(df)

    selected_date = st.date_input("Select a date", value=datetime.date.today())
    st.write(f"Selected date: {selected_date}")

    if st.button("Process File"):
        start_time = datetime.datetime.now()
        st.write("Processing file...")
        progress_bar = st.progress(0)

        processed_df = process_file(df, selected_date)

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
