import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import warnings

# Suppress warnings from yfinance
warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")

def process_file(df, selected_date):
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    volume_list = []
    failed_tickers = []

    tickers = df["代號"].tolist()
    batch_size = 10  # Adjust batch size based on API limits and performance

    for i in range(0, len(tickers), batch_size):
        batch_tickers = tickers[i:i + batch_size]
        try:
            yahoo_data = yf.download(" ".join([f"{ticker}.TW" for ticker in batch_tickers]), start=selected_date, end=selected_date + datetime.timedelta(days=1))
            if not yahoo_data.empty:
                for ticker in batch_tickers:
                    if ticker in yahoo_data.columns.levels[1]:
                        open_list.append(yahoo_data[ticker]['Open'][0])
                        high_list.append(yahoo_data[ticker]['High'][0])
                        low_list.append(yahoo_data[ticker]['Low'][0])
                        close_list.append(yahoo_data[ticker]['Close'][0])
                        volume_list.append(yahoo_data[ticker]['Volume'][0])
                    else:
                        open_list.append(pd.NA)
                        high_list.append(pd.NA)
                        low_list.append(pd.NA)
                        close_list.append(pd.NA)
                        volume_list.append(pd.NA)
                        failed_tickers.append(ticker)
            else:
                open_list.extend([pd.NA] * len(batch_tickers))
                high_list.extend([pd.NA] * len(batch_tickers))
                low_list.extend([pd.NA] * len(batch_tickers))
                close_list.extend([pd.NA] * len(batch_tickers))
                volume_list.extend([pd.NA] * len(batch_tickers))
                failed_tickers.extend(batch_tickers)
        except Exception:
            open_list.extend([pd.NA] * len(batch_tickers))
            high_list.extend([pd.NA] * len(batch_tickers))
            low_list.extend([pd.NA] * len(batch_tickers))
            close_list.extend([pd.NA] * len(batch_tickers))
            volume_list.extend([pd.NA] * len(batch_tickers))
            failed_tickers.extend(batch_tickers)

        progress = (i + batch_size) / len(tickers)
        progress_bar.progress(progress)
        progress_text.text(f"{int(progress * 100)}% completed")

    df["Open"] = open_list
    df["High"] = high_list
    df["Low"] = low_list
    df["Close"] = close_list
    df["Volume"] = volume_list

    st.write(f"Failed to fetch data for tickers: {failed_tickers}")

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

    max_date = datetime.date.today()
    selected_date = st.date_input("Select a date", value=max_date, max_value=max_date)
    st.write(f"Selected date: {selected_date}")

    if st.button("Process File"):
        start_time = datetime.datetime.now()
        st.write("Processing file...")
        progress_bar = st.progress(0)
        progress_text = st.empty()

        processed_df = process_file(df, selected_date)

        end_time = datetime.datetime.now()
        runtime = end_time - start_time

        st.write("Processed Data:")
        st.write(processed_df)

        st.write(f"Runtime: {runtime}")

        # Change progress bar color to green
        st.success('Processing complete!')

        # Option to download the processed file
        output_file_name = "processed_data.xlsx"
        processed_df.to_excel(output_file_name, index=False)
        with open(output_file_name, "rb") as file:
            btn = st.download_button(label="Download Processed Data", data=file, file_name=output_file_name,
                                     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
