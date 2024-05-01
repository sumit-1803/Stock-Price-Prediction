from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import base64
import io

app = Flask(__name__)

uploaded_df = None

# Define your routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global uploaded_df
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if the file is empty
        if file.filename == '':
            return redirect(request.url)
        
        # Read the CSV file into a DataFrame
        if file:
            csv_contents = file.stream.read().decode("utf-8")
            uploaded_df = pd.read_csv(StringIO(csv_contents))
        
        # Redirect back to the upload page after successful upload
        return redirect(url_for('upload'))
    
    return render_template('upload.html')


@app.route('/view_table')
def view_table():
    global uploaded_df
    
    if uploaded_df is not None:
        return render_template('view_table.html', table_data=uploaded_df.to_html(index=False))
    else:
        return "No table data uploaded yet."
    

    

@app.route('/analyze', methods=['POST'])
def analyze():
    global uploaded_df
    
    if uploaded_df is None:
        return 'No data uploaded yet.'
    
    # Access the uploaded DataFrame (uploaded_df) and perform analysis
    # Example analysis code:
    
    # 1. Data Exploration
    data_shape = uploaded_df.shape
    null_values = uploaded_df.isnull().sum()
    data_info = uploaded_df.info()
    unique_names = uploaded_df['Name'].unique()
    statistical_summary = uploaded_df.describe()
    
    # 2. Data Preprocessing
    uploaded_df['date'] = pd.to_datetime(uploaded_df['date'])
    eda_data_summary = uploaded_df.head(3).append(uploaded_df.tail(3))
    eda_statistical_summary = uploaded_df.describe()
    
    # 3. Time Series Analysis
    time_series_plot = plt.figure(figsize=(12, 6))
    plt.plot(uploaded_df['date'], uploaded_df['close'], label='Closing Price')
    plt.title('Stock Closing Price Over Time')
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.legend()
    
    # Save the plot to a BytesIO object
    time_series_plot_bytes = io.BytesIO()
    plt.savefig(time_series_plot_bytes, format='png')
    time_series_plot_bytes.seek(0)
    
    # Convert the image to a base64 string
    time_series_plot_base64 = base64.b64encode(time_series_plot_bytes.read()).decode('utf-8')
    time_series_plot_bytes.close()  # Close the BytesIO object
    
    # 4. Stock Price Visualization
    # Similar process for other plots
    
    # Prepare analysis results to be returned as JSON
    analysis_results = {
        "data_exploration": {
            "data_shape": data_shape,
            "null_values": null_values,
            "data_info": data_info,
            "unique_names": unique_names,
            "statistical_summary": statistical_summary
        },
        "data_preprocessing": {
            "eda_data_summary": eda_data_summary,
            "eda_statistical_summary": eda_statistical_summary
        },
        "time_series_plot": time_series_plot_base64,
        # Include other plots in a similar way
    }
    
    # Return the analysis results in JSON format
    return jsonify(analysis_results)

if __name__ == '__main__':
    app.run(debug=True)
