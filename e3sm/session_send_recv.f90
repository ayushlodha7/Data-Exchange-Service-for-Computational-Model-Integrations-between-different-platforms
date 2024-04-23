module session_send_recv

  use http_client_interface

  implicit none

    character(len=256), parameter :: url = "http://128.55.151.75:8080"
contains

  subroutine start_session()

    implicit none

    ! Declare variables related to session management and data transmission.
    integer, dimension(:), allocatable :: input_variables_ID, input_variables_size
    integer, dimension(:), allocatable :: output_variables_ID, output_variables_size
    real(c_double), dimension(:), allocatable :: arr_send, arr_receive

    ! Session and model information variables.
    integer :: source_model_ID, destination_model_ID
    integer :: initiator_id, inviter_id
    integer :: no_of_input_variables, no_of_output_variables
    integer :: arr_length, i
    integer :: status_send, status_receive

    ! URL and ID strings for various API endpoints.
    !character(len=256) :: url
    character(len=256) :: session_id
    character(len=100) :: client_id = "ClientA"
    ! Variable identifiers for sending and receiving.
    integer :: var_send, var_receive

    ! Session Variables
    source_model_ID = 2001
    destination_model_ID = 2005
    initiator_id = 35
    inviter_id = 36

    ! Initialize session information and input/output variable arrays.
    no_of_input_variables = 3
    no_of_output_variables = 3
    allocate(input_variables_ID(no_of_input_variables))
    allocate(input_variables_size(no_of_input_variables))
    allocate(output_variables_ID(no_of_output_variables))
    allocate(output_variables_size(no_of_output_variables))

    input_variables_ID = [1, 2, 3]
    input_variables_size = [20, 20, 20]
    output_variables_ID = [4, 5, 6]
    output_variables_size = [20, 20, 20]

    ! Create a session with the server.
    call create_session_c(trim(url), source_model_ID, destination_model_ID, trim(client_id), &
                          initiator_id, inviter_id, input_variables_ID, input_variables_size, &
                          no_of_input_variables, output_variables_ID, output_variables_size, &
                          no_of_output_variables)
    ! Clean up the ID and size arrays to free memory.
    deallocate(input_variables_ID, input_variables_size, output_variables_ID, output_variables_size)

  end subroutine start_session


  !===============================================================================


  subroutine send_data_test()
    use http_client_interface
    use iso_c_binding, only: c_double
    implicit none

    real(c_double), dimension(:), allocatable :: arr_send
    integer :: arr_length, i, flag, retries, max_retries, status_send
    character(len=256) :: session_id
    integer :: var_send
    integer :: sleep_off_time

    session_id = "2001_2005_35_36_1"
    var_send = 1   ! Example variable ID for sending data
    sleep_off_time = 3
    max_retries = 5
    retries = 0

    ! Check the status of all sessions.
    call get_all_session_statuses(trim(url))

    ! Retrieve session flags.
    session_id = "2001_2005_35_36_1"
    call get_flags(trim(url), trim(session_id))

    ! Prepare and send data to the server.
    var_send = 1
    arr_length = get_variable_size_c(trim(url), trim(session_id), var_send)
    print *, 'Array length send :', arr_length
    allocate(arr_send(arr_length))
    arr_send = [(real(i, kind=c_double), i = 1, arr_length)]

    ! Check flag and attempt to send data with retries
    do while (retries < max_retries)
      flag = get_variable_flag_c(trim(url), trim(session_id), var_send)
      print *, "Flag :",flag 
      if (flag ==0) then 
        status_send = send_data_to_server(trim(url), trim(session_id), var_send, arr_send, arr_length)
        if (status_send == 1) then
            print *, "Data successfully sent."
            exit
        else
            print *, "Failed to send data, will retry..."
        endif
      else
        print *, "Flag is not set for sending, retrying..."
        retries = retries + 1
        call sleep(sleep_off_time)
      end if
    end do

    if (retries >= max_retries) then
        print *, "Failed to send data for var_id", var_send, "after", max_retries, "attempts: Flag is not in the expected state."
    endif

    deallocate(arr_send)  ! Free the allocated memory for arr_send.

  end subroutine send_data_test


  !===============================================================================


  subroutine recv_data_test()

    real(c_double), dimension(:), allocatable :: arr_receive
    integer :: arr_length, i, flag, retries, max_retries, status_send
    integer :: status_receive
    character(len=256) :: session_id
    integer :: var_receive
    integer :: sleep_time, base_sleep_time

    base_sleep_time = 5
    max_retries = 4
    retries = 0

    ! Retrieve session flags.
    session_id = "2001_2005_35_36_1"
    call get_flags(trim(url), trim(session_id))

    ! ! Receive data from the server.
    var_receive = 4
    arr_length = get_variable_size_c(trim(url), trim(session_id), var_receive) 
    allocate(arr_receive(arr_length))

    ! Check flag and attempt to receive data with retries
    do while (retries < max_retries)
      sleep_time = base_sleep_time *(2**retries)  ! Exponential back-off
      flag = get_variable_flag_c(trim(url), trim(session_id), var_receive)
      print *, "Flag :",flag 
      if (flag ==1) then 
        print *, "Got the Flag ---- waiting to receive data "
        status_receive = receive_data_from_server(trim(url), trim(session_id), var_receive, arr_receive, arr_length)
        if (status_receive == 1) then
            print *, "Data received successfully:"
            do i = 1, arr_length
                print *, "arr_receive(", i, ") = ", arr_receive(i)
            end do
            exit
        else
            print *, "Failed to fetch data, will retry..."
        endif
      else
        print *, "Flag is not set for receiving, retrying..."
        retries = retries + 1
        call sleep(sleep_time)
      end if
    end do

    if (retries >= max_retries) then
        print *, "Failed to receive data for var_id: ", var_receive, "after", &
             max_retries, "attempts: Flag is not in the expected state."
    endif

    ! Clean up...
    deallocate(arr_receive)

  end subroutine recv_data_test


  !===============================================================================

  subroutine end_session()

    character(len=256) :: session_id
    character(len=100) :: client_id = "ClientA"
    session_id = "2001_2005_35_36_1"

    ! End the session with the server.
    call end_session_c(trim(url), trim(session_id), trim(client_id))

  end subroutine end_session

end module session_send_recv