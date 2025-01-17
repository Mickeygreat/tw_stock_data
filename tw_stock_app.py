import streamlit as st
import pandas as pd
import yfinance as yf
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


def process_file(df, selected_date):
    open_list = []
    high_list = []
    low_list = []
    close_list = []
    volume_list = []

    for i in range(len(df)):
        try:
            ticker = df["代號"][i]
            yahoo_data = yf.download(f"{ticker}.TW", start=selected_date, end=selected_date + datetime.timedelta(days=1))
            if not yahoo_data.empty:
                open_price = yahoo_data["Open"].iloc[0].item()
                high = yahoo_data["High"].iloc[0].item()
                low = yahoo_data["Low"].iloc[0].item()
                close = yahoo_data["Close"].iloc[0].item()
                volume = yahoo_data["Volume"].iloc[0].item()

            else:
                open_price = high = low = close = volume = pd.NA
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

        progress = (i + 1) / len(df)
        progress_bar.progress(progress)
        progress_text.text(f"{int(progress * 100)}% completed")

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




###--- Fastest Code: But Yahoo Finance API has issue processing that fast ---###
# import streamlit as st
# import pandas as pd
# import yfinance as yf
# import datetime
# import math
# import warnings
# from concurrent.futures import ThreadPoolExecutor

# # Suppress warnings from yfinance
# warnings.filterwarnings("ignore", category=UserWarning, module="yfinance")


# def process_file(df, selected_date):
#     open_list = []
#     high_list = []
#     low_list = []
#     close_list = []
#     volume_list = []

#     total_rows = len(df)
#     progress_bar = st.progress(0)
#     progress_text = st.empty()

#     for i, ticker in enumerate(df["代號"]):
#         try:
#             yahoo_data = yf.download(
#                 f"{ticker}.TW", start=selected_date, end=selected_date + datetime.timedelta(days=1))

#             if not yahoo_data.empty:
#                 open_price = float(yahoo_data["Open"].iloc[0])
#                 high = float(yahoo_data["High"].iloc[0])
#                 low = float(yahoo_data["Low"].iloc[0])
#                 close = float(yahoo_data["Close"].iloc[0])
#                 volume = float(yahoo_data["Volume"].iloc[0])
#             else:
#                 open_price = high = low = close = volume = pd.NA

#             open_list.append(open_price)
#             high_list.append(high)
#             low_list.append(low)
#             close_list.append(close)
#             volume_list.append(volume)

#         except Exception as e:
#             print(f"Error processing ticker {ticker}: {e}")
#             open_list.append(pd.NA)
#             high_list.append(pd.NA)
#             low_list.append(pd.NA)
#             close_list.append(pd.NA)
#             volume_list.append(pd.NA)

#         # Update progress
#         progress = (i + 1) / total_rows
#         progress_bar.progress(progress)
#         progress_text.text(f"{int(progress * 100)}% completed")

#     df["Open"] = open_list
#     df["High"] = high_list
#     df["Low"] = low_list
#     df["Close"] = close_list
#     df["Volume"] = volume_list

#     return df


# # Streamlit app
# st.title("Financial Data Processor")

# uploaded_file = st.file_uploader(
#     "Upload an Excel or CSV file", type=["xlsx", "csv"])

# if uploaded_file:
#     st.write("Uploaded Data:")
#     if uploaded_file.name.endswith('.xlsx'):
#         df = pd.read_excel(uploaded_file, dtype={"代號": str}, index_col=None, engine="openpyxl")
#     else:
#         df = pd.read_csv(uploaded_file, dtype={"代號": str})

#     st.write(df)

#     max_date = datetime.date.today()
#     selected_date = st.date_input(
#         "Select a date", value=max_date, max_value=max_date, help="Weekends will return no values")
    
#     # Display a warning if the selected date is a weekend
#     if selected_date.weekday() >= 5:
#         st.warning("Selected date is a weekend. Weekends will return no values.")

#     if st.button("Process File"):
#         start_time = datetime.datetime.now()
#         st.write("Processing file...")

#         processed_df = process_file(df, selected_date)

#         end_time = datetime.datetime.now()
#         runtime = end_time - start_time

#         st.write("Processed Data:")
#         st.write(processed_df)

#         st.write(f"Runtime: {runtime}")

#         # Change progress bar color to green
#         st.success('Processing complete!')

#         # Option to download the processed file
#         output_file_name = "processed_data.xlsx"
#         processed_df.to_excel(output_file_name, index=False)
#         with open(output_file_name, "rb") as file:
#             btn = st.download_button(label="Download Processed Data", data=file, file_name=output_file_name,
#                                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# # Custom CSS to mark weekends as red
# st.markdown(
#     """
#     <style>
#     [class*="stDatepicker-day--weekday-5"], [class*="stDatepicker-day--weekday-6"] {
#         color: red !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

