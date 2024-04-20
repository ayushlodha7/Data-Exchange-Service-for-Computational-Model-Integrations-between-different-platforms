import requests
import struct


SERVER_URL = "http://128.55.151.69:8080"

client_id  = "ClientB"

def create_session(source_model_ID, destination_model_ID, 
                   initiator_id, 
                   inviter_id,
                   no_of_input_variables=0, input_variables_ID=[], input_variables_size=[], no_of_output_variables=0, output_variables_ID=[], output_variables_size=[]):
    data = {
        "client_id": client_id,
        "source_model_ID": source_model_ID,
        "destination_model_ID": destination_model_ID,
        "initiator_id": initiator_id,  # New field
        "inviter_id": inviter_id,      # New field
        "no_of_input_variables": no_of_input_variables,
        "input_variables_ID": input_variables_ID,
        "input_variables_size": input_variables_size,
        "no_of_output_variables": no_of_output_variables,
        "output_variables_ID": output_variables_ID,
        "output_variables_size": output_variables_size
    }

    response = requests.post(f"{SERVER_URL}/create_session/{client_id}", json=data)
    if response.ok:
        session_info = response.json()
        print(f"Session status: {session_info['status']}. Session ID: {session_info['session_id']}")
    else:
        print("Error occurred:", response.text)
    return response.json()

def join_session(session_id):
    data = {
        "client_id": client_id,
        "session_id": session_id,
    }
    response = requests.post(f"{SERVER_URL}/join_session", json=data)
    if response.ok:
        print(f"Successfully joined session {session_id}")
    else:
        print("Error occurred while joining session:", response.text)

def get_all_session_statuses():
    response = requests.get(f"{SERVER_URL}/list_sessions")
    if response.ok:
        sessions = response.json()
        print("Session statuses:")
        for session_id, status in sessions.items():
            print(f"Session ID: {session_id}, Status: {status}")
    else:
        print(f"Error occurred while retrieving session statuses: {response.text}")

def get_flags(session_id):
    response = requests.get(f"{SERVER_URL}/get_flags", params={"session_id": session_id})
    if response.ok:
        flags = response.json()
        print(f"Flags for session {session_id}: {flags}")
    else:
        print("Error occurred while retrieving flags:", response.text)

def get_variable_flag(session_id, var_id):
    # Build the URL for the GET request
    url = f"{SERVER_URL}/get_variable_flag"
    # Set the parameters with session_id and var_id
    params = {'session_id': session_id, 'var_id': var_id}
    # Make the GET request
    response = requests.get(url, params=params)
    # Check if the response is successful
    if response.ok:
        # Extract the flag status from the JSON response
        flag_status = response.json().get('flag_status')
        print(f"Flag for session {session_id} variable {var_id}: {flag_status}")
        return flag_status
    else:
        # Print the error message if something went wrong
        print("Error occurred while retrieving flag status:", response.text)
        return None

def send_data(session_id, var_id, data):
    # Convert data (list of doubles) to binary
    binary_data = struct.pack('<' + 'd'*len(data), *data)

    headers = {
        'Session-ID': session_id,
        'Var-ID': str(var_id)
    }

    response = requests.post(f"{SERVER_URL}/send_data", data=binary_data, headers=headers)
    if response.ok:
        print(f"Data sent for {var_id}.")
    else:
        print("Error sending data:", response.text)

def receive_data(session_id, var_id):
    params = {"session_id": session_id, "var_id": var_id}
    response = requests.get(f"{SERVER_URL}/receive_data", params=params)

    # Check if the response is JSON
    if response.headers['Content-Type'] == 'application/json':
        try:
            data = response.json()
            if 'error' in data:
                print(f"Error: {data['error']}")
            else:
                print(f"Received JSON data: {data}")
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
    elif response.headers['Content-Type'] == 'application/octet-stream':
        # Handle binary data
        binary_data = response.content
        # Assuming the binary data consists of a series of doubles
        num_doubles = len(binary_data) // 8  # Each double is 8 bytes
        unpacked_data = struct.unpack(f'<{num_doubles}d', binary_data)
        print(f"Received binary data of length {len(binary_data)}")
        print("Data array:", unpacked_data)
    else:
        print("Received unexpected content type:", response.headers['Content-Type'])
    
def end_session(session_id):
    data = {
        "session_id": session_id,
        "client_id": client_id
    }
    response = requests.post(f"{SERVER_URL}/end_session", json=data)
    if response.ok:
        print(response.json().get("status"))
    else:
        print("Error ending session:", response.text)

def menu():
    while True:
        print("\nMenu:")
        print("1. Create Session")
        print("2. Get All Session Statuses")
        print("3. Join Session")
        print("4. Get variable flags")
        print("5. Send Data")
        print("6. Receive Data")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            source_model_ID = int(input("Enter source model ID: "))
            destination_model_ID = int(input("Enter destination model ID: "))

            initiator_id = int(input("Enter Initiator ID: "))
            inviter_id = int(input("Enter Inviter ID: "))

            # Handling input variables
            print("Add input variables")
            # Remove leading/trailing quotes from the input string
            input_variables_ID_input = input("Enter input variable IDs separated by spaces (e.g., 1 2 3): ").strip().strip('"').strip("'")
            input_variables_size_input = input("Enter input variable sizes separated by spaces, corresponding to each ID (e.g., 20 25 30): ").strip().strip('"').strip("'")

            # Convert the cleaned strings to lists of integers
            input_variables_ID = [int(var_id) for var_id in input_variables_ID_input.split()]
            input_variables_size = [int(var_size) for var_size in input_variables_size_input.split()]

            # Handling output variables
            print("Add output variables")
            # Similarly, remove leading/trailing quotes for output variable inputs
            output_variables_ID_input = input("Enter output variable IDs separated by spaces (e.g., 4 5 6): ").strip().strip('"').strip("'")
            output_variables_size_input = input("Enter output variable sizes separated by spaces, corresponding to each ID (e.g., 20 25 30): ").strip().strip('"').strip("'")

            # Convert to lists of integers
            output_variables_ID = [int(var_id) for var_id in output_variables_ID_input.split()]
            output_variables_size = [int(var_size) for var_size in output_variables_size_input.split()]

            create_session(source_model_ID, destination_model_ID, 
                           initiator_id, inviter_id,
                           len(input_variables_ID), input_variables_ID, input_variables_size, len(output_variables_ID), output_variables_ID, output_variables_size)
        elif choice == '2':
            get_all_session_statuses()
        elif choice == '3':  # Assuming '6' is the exit option now
            session_id = input("Enter session ID to join: ")
            join_session(session_id)
        elif choice == '4':
            session_id = input("Enter session ID to get variable flags: ")
            get_flags(session_id)
        elif choice == '5':
            session_id = input("Enter session ID: ")
            var_id = int(input("Enter variable ID: "))
            data_array = list(range(300, 320))  # Example data array
            send_data(session_id, var_id, data_array)
        elif choice == '6':
            session_id = input("Enter session ID: ")
            var_id = int(input("Enter variable ID: "))
            receive_data(session_id, var_id)
        elif choice == '7':
            session_id = input("Enter session ID to end: ")
            end_session(session_id)
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")
