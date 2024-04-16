program e3sm

  use session_send_recv

  implicit none

  call start_session() 

  print *, "------ Sleeping for 10 seconds ------"
  
  call sleep(10)

  call send_data_test()

  print *, "------ Sleeping for 10 seconds ------"

  call sleep(10)

  call recv_data_test()

  print *, "------ Sleeping for 10 seconds ------"

  call sleep(10)

  ! call end_session()

end program e3sm
