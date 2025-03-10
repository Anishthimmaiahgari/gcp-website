from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from googleapiclient import discovery
from google.cloud import monitoring_v3
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Authenticate and get the active APIs for the GCP project
@app.route('/authenticate-gcp', methods=['POST'])
def authenticate_gcp():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith('.json'):
            return jsonify({"error": "Invalid file type. Only JSON files are allowed"}), 400

        # Save the file temporarily
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)

        # Load credentials from the file
        credentials = service_account.Credentials.from_service_account_file(file_path)

        # Build the Service Usage API client
        service = discovery.build('serviceusage', 'v1', credentials=credentials)

        # Fetch active APIs for the project
        request_body = {
            'parent': f'projects/{credentials.project_id}',
            'filter': 'state:ENABLED'
        }
        response = service.services().list(**request_body).execute()

        # Clean up the temporary file
        os.remove(file_path)

        # Return the list of active APIs
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New route to get details for a specific API
@app.route('/api-details', methods=['POST'])
def api_details():
    try:
        # Get the API name passed from the frontend
        api_name = request.json.get('apiName')
        if not api_name:
            return jsonify({"error": "API name is required"}), 400
            
        # Get the credentials file path from the request or from a session
        cred_file = request.json.get('credentialsFile')
        
        # If no credentials file is provided, check if we have one stored in the session
        if not cred_file:
            # In a production app, you might store this in a session or secure storage
            # For demonstration purposes, we'll use a global or environment variable
            if 'CREDENTIALS_PATH' not in app.config:
                return jsonify({"error": "No credentials available. Please authenticate first."}), 401
            cred_file = app.config['CREDENTIALS_PATH']
        
        # Set up credentials
        credentials = service_account.Credentials.from_service_account_file(cred_file)
        
        # Initialize clients for Billing and Monitoring API
        billing_client = discovery.build('cloudbilling', 'v1', credentials=credentials)
        monitoring_client = monitoring_v3.MetricServiceClient(credentials=credentials)
        
        # Fetch billing information (Cloud Billing API)
        billing_info = get_billing_info(billing_client, api_name)
        
        # Fetch CPU utilization (Cloud Monitoring API)
        cpu_utilization = get_cpu_utilization(monitoring_client, credentials.project_id, api_name)
        
        # Return the API details
        api_details = {
            'billing_info': billing_info,
            'cpu_utilization': cpu_utilization
        }
        
        return jsonify(api_details)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def get_billing_info(billing_client):
    # Placeholder for fetching actual billing info for the API
    try:
        # For now, we're simulating the response; you'd replace this with real API calls
        billing_info = {
            'cost': '$200',
            'usage': '75%'
        }

        # Example of querying the billing account or specific API cost would go here:
        # billing_account = billing_client.billingAccounts().list().execute()

        return billing_info
    except Exception as e:
        return {"error": f"Failed to fetch billing information: {str(e)}"}


def get_cpu_utilization(monitoring_client):
    try:
        # Placeholder for fetching actual CPU utilization for the project
        # Example: This assumes you have the resource (e.g., VM instance) where the CPU utilization data is available.
        # Here, we'll simulate CPU and memory usage for the sake of the example.

        cpu_utilization = {
            'cpu_usage': '65%',
            'memory_usage': '80%'
        }

        # You can fetch real CPU usage data from Google Cloud Monitoring API by querying a specific metric
        # Example query: client.projects().timeSeries().list(name='projects/{project_id}', filter='metric.type="compute.googleapis.com/instance/disk/write_bytes_count"')

        return cpu_utilization
    except Exception as e:
        return {"error": f"Failed to fetch CPU utilization: {str(e)}"}


if __name__ == '__main__':
    app.run(debug=True)
