from cyberwater_library import *
import time 

# SERVER_URL = "http://0.0.0.0:8080"

# client_id  = "ClientB"

# source_model_ID = 1
# destination_model_ID = 2
# initiator_id = 1
# inviter_id = 2
# input_variables_ID = [1]  # Example
# input_variables_size = [20]  # Example
# output_variables_ID = [4]  # Example
# output_variables_size = [20]  # Example

# Start session
# session_response = create_session(source_model_ID, destination_model_ID, 
#                                     initiator_id, inviter_id, 
#                                     len(input_variables_ID), input_variables_ID, input_variables_size, 
#                                     len(output_variables_ID), output_variables_ID, output_variables_size)
# session_id = session_response.get('session_id')

# Join session
session_id = "2001_2005_35_36_1"
join_session(session_id)

get_flags(session_id)

# Pause for setup
time.sleep(10)

# Example data to send
var_send_id = 4  # Placeholder variable ID
data_array = list(range(300, 320))
send_data(session_id, var_send_id, data_array)

time.sleep(10)


# Receive data
var_receive_id = 1
receive_data(session_id, var_receive_id)

# Pause before ending session
time.sleep(10)

# End session
# end_session(session_id)
