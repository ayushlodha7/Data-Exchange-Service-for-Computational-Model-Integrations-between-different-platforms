from cyberwater_library import *
import time 

# Function to check and send data with retry logic and feedback using specific flag
def check_and_send_data(session_id, var_id, data_array, max_retries=5):
    retry_count = 0
    while retry_count < max_retries:
        flag = get_variable_flag(session_id, var_id)
        print ("------------------------------", flag, "------------------------------")
        if flag == 0:
            send_data(session_id, var_id, data_array)
            return
        else:
            time.sleep(3)
            print(f"---- Trying to send for the variable: {var_id} | retries: {retry_count}")
            retry_count += 1
    print(f"Failed to send data for var_id {var_id} after {max_retries} attempts: Flag is not in the expected state.")

# Function to check and receive data with retry logic and feedback using specific flag
def check_and_receive_data(session_id, var_id, max_retries=5):
    retry_count = 0
    while retry_count < max_retries:
        flag = get_variable_flag(session_id, var_id)
        print ("------------------------------", flag, "------------------------------")
        if flag == 1:
            receive_data(session_id, var_id)
            return
        else:
            time.sleep(3)
            print(f"---- Trying to receive for the variable: {var_id} | retries: {retry_count}")
            retry_count += 1
    print(f"Failed to receive data for var_id {var_id} after {max_retries} attempts: Flag is not in the expected state.")

# source_model_ID = 1
# destination_model_ID = 2
# initiator_id = 1
# inviter_id = 2
# input_variables_ID = [1]  # Example
# input_variables_size = [20]  # Example
# output_variables_ID = [4]  # Example
# output_variables_size = [20]  # Example

# # Start session
# session_response = create_session(source_model_ID, destination_model_ID, 
#                                     initiator_id, inviter_id, 
#                                     len(input_variables_ID), input_variables_ID, input_variables_size, 
#                                     len(output_variables_ID), output_variables_ID, output_variables_size)
# session_id = session_response.get('session_id')

# Join session
session_id = "199"
join_session(session_id)

get_flags(session_id)

print ("------ Sleeping for 10 seconds ------")
# Pause for setup
time.sleep(10)

# Example data to send
var_send_id = 4  # Placeholder variable ID
data_array = list(range(300, 320))
check_and_send_data(session_id, var_send_id, data_array)
print ("------ Sleeping for 10 seconds ------")
time.sleep(10)


# Receive data
var_receive_id = 1
print ("------ Sleeping for 10 seconds ------")
check_and_receive_data(session_id, var_receive_id)

# Pause before ending session
time.sleep(10)

# End session
# end_session(session_id)
