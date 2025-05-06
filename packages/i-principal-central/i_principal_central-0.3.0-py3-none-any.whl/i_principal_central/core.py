













import os

from pathlib import Path





class i_class:


    def __init__(i_self):


        i_self.i = {}

        i_self.i["i am you"] = False

        i_self.i["i develope"] = False


    def i_am_you(i_self):


        i_self.i["i am you"] = True


    def i_develope(i_self):

        i_self.i["i develope"] = True


    def i_function(i_self, i_function):


        if ((i_self.i["i am you"] == True) and (i_self.i["i develope"] == True)):


            if (i_function == "make file-s of send-ing and receive-ing"):

                print("i_hello .")

                i_self.i["i_Economic_Partner_official_receiver_0"] = """
















global i

i = {}


i["pricipal-central"] = "i am here"


i["i am you"] = True


if (i["i am you"] == True):


    # i_Economic_Partner_official_receiver_0.py




    import os

    import socket

    import time

    import traceback

    from pathlib import Path





    i["i_cwd"] = os.getcwd() + "/"



    def i_get_ip_of_wifi():


        i_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:

            i_s.connect(("8.8.8.8", 80))

            i_ip = i_s.getsockname()[0]

        except Exception:

            i_ip = "NULL"

        finally:

            i_s.close()

        return i_ip




    i["i_ip_of_wifi_of_receiver"] = i_get_ip_of_wifi()

    print("i . i_ip_of_wifi_of_receiver = ", i["i_ip_of_wifi_of_receiver"])


    i["i_semaphore"] = False



    try:


        try:

            i["i_folder_for_receive"] = i["i_cwd"] + "i_folder_for_receive/"

            os.mkdir(i["i_folder_for_receive"])


        except Exception as i_e:


            i["i_semaphore_1"] = True




        try:

            i["i_folder_of_history"] = i["i_cwd"] + "i_folder_for_receive/i_folder_of_history/"

            os.mkdir(i["i_folder_for_receive"])


        except Exception as i_e:


            i["i_semaphore_1"] = True



        try:


            i["i_folder_for_send"] = i["i_cwd"] + "i_folder_for_send/"

            os.mkdir(i["i_folder_for_send"])


        except Exception as i_e:


            i["i_semaphore_1"] = True





        i["server_socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        i["server_socket"].bind((i["i_ip_of_wifi_of_receiver"], 12345))
        
        i["server_socket"].listen(1)
        

        print("i . start server success .")



        i["client_socket"], i["client_address"] = i["server_socket"].accept()

        print("i . connect with client ", i["client_address"]," success .")


        i["i_t1"] = time.time()
        










        i["i_number_of_file-s_byte-s"] = i["client_socket"].recv(8)

        i["i_number_of_file-s"] = int.from_bytes(i["i_number_of_file-s_byte-s"], 'big')






        i["i_counter"] = 0


        while (i["i_counter"] < i["i_number_of_file-s"]):



            i["i_length_of_name_file_in_byte-s"] = i["client_socket"].recv(8)

            i["i_length_of_name_file"] = int.from_bytes(i["i_length_of_name_file_in_byte-s"], 'big')



            i["i_name_of_file"] = ""

            while len(i["i_name_of_file"]) < i["i_length_of_name_file"]:

                i["chunk"] = i["client_socket"].recv(1).decode('utf-8')
                
                if not i["chunk"]:

                    break

                i["i_name_of_file"] += i["chunk"]

                

            i["i_size_of_file_in_byte-s"] = i["client_socket"].recv(8)

            i["i_size_of_file"] = int.from_bytes(i["i_size_of_file_in_byte-s"], 'big')

            print("📦 i['i_size_of_file'] = ", i["i_size_of_file"])


            i["i_received_data"] = b''

            while len(i["i_received_data"]) < i["i_size_of_file"]:



                if (len(i["i_received_data"]) < i["i_size_of_file"] - 10_000_000):

                    i["chunk"] = i["client_socket"].recv(10_000_000)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 1_000_000):

                    i["chunk"] = i["client_socket"].recv(1_000_000)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 100_000):

                    i["chunk"] = i["client_socket"].recv(100_000)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 10_000):

                    i["chunk"] = i["client_socket"].recv(10_000)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 1_000):

                    i["chunk"] = i["client_socket"].recv(1_000)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 100):

                    i["chunk"] = i["client_socket"].recv(100)


                elif (len(i["i_received_data"]) < i["i_size_of_file"] - 10):

                    i["chunk"] = i["client_socket"].recv(10)

                else:

                    i["chunk"] = i["client_socket"].recv(1)
                
                if not i["chunk"]:

                    break

                i["i_received_data"] += i["chunk"]


            i["i_file"] = i["i_folder_for_receive"] + i["i_name_of_file"]

            i["d"] = Path(i["i_file"])

            i["d"].write_bytes(i["i_received_data"])


            i["i_counter"] += 1





        i["i_t2"] = time.time()


        print("i . message receive-ed with success . i_time = ", i["i_t2"] - i["i_t1"])



        i["client_socket"].close()

        i["server_socket"].close()

        print("i . close server .")


    except Exception as i_e:


        i["i_semaphore"] = True

        print("i . i_e = ", i_e)

        traceback.print_exc()

        i_e_ = str(traceback.format_exc())

        print("i . i_e_ = ", i_e_)



    print("i['i_semaphore'] = ", i["i_semaphore"])













                """




                i_self.i["i_Economic_Partner_official_sender_0"] = """

















global i

i = {}



i["pricipal-central"] = "i am here"


i["i am you"] = True


if (i["i am you"] == True):


    # i_Economic_Partner_official_sender_0.py


    import os

    import socket

    import traceback

    from pathlib import Path

    import time





    # the place of modify

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------

    i["i_ip_of_wifi_of_receiver"] = ""

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------




    i["i_cwd"] = os.getcwd() + "/"

    i["i_semaphore"] = False




    try:



        try:

            i["i_folder_for_receive"] = i["i_cwd"] + "i_folder_for_receive/"

            os.mkdir(i["i_folder_for_receive"])


        except Exception as i_e:


            i["i_semaphore_1"] = True




        try:

            i["i_folder_of_history"] = i["i_cwd"] + "i_folder_for_receive/i_folder_of_history/"

            os.mkdir(i["i_folder_for_receive"])


        except Exception as i_e:


            i["i_semaphore_1"] = True



        try:


            i["i_folder_for_send"] = i["i_cwd"] + "i_folder_for_send/"

            os.mkdir(i["i_folder_for_send"])


        except Exception as i_e:


            i["i_semaphore_1"] = True








        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client_socket.connect((i["i_ip_of_wifi_of_receiver"], 12345))


        print("i . connect to server success .")

        i["i_t1"] = time.time()

        i["i_file-s"] = []


        for root, dirs, i["i_file-s"] in os.walk(i["i_folder_for_send"]):

            break



        client_socket.sendall(len(i["i_file-s"]).to_bytes(8, 'big'))



        i["i_counter"] = 0

        while (i["i_counter"] < len(i["i_file-s"])):

                

            i["i_path_of_file"] = i["i_cwd"] + i["i_file-s"][i["i_counter"]]

            i["i_name_of_file"] = i["i_file-s"][i["i_counter"]]

            print("i . length of name of file : ", len(i["i_name_of_file"]))




            client_socket.sendall(len(i["i_name_of_file"].encode('utf-8')).to_bytes(8, 'big'))


            client_socket.send(i["i_name_of_file"].encode('utf-8'))



            i["d"] = Path(i["i_folder_for_send"] + i["i_name_of_file"])


            i["d_bytes"] = i["d"].read_bytes()



            client_socket.sendall(len(i["d_bytes"]).to_bytes(8, 'big'))


            client_socket.sendall(i["d_bytes"])


            os.remove(i["i_folder_for_send"] + i["i_file-s"][i["i_counter"]])


            i["i_counter"] += 1




        i["i_counter"] = 0

        while (i["i_counter"] < len(i["i_file-s"])):


            i["i_counter"] += 1            



        i["i_t2"] = time.time()


        print("i . send-ed to server success . i_time = ", i["i_t2"] - i["i_t1"])



        client_socket.close()


        print("i . close success .")

    
    except Exception as i_e:


        i["i_semaphore"] = True

        print("i . i_e = ", i_e)


        traceback.print_exc()

        i_e_ = str(traceback.format_exc())


        print("i . i_e_ = ", i_e_)




    print("i . i['i_semaphore'] = ", i["i_semaphore"])
















                """





                i_self.i["i_cwd"] = os.getcwd() + "/"

                i_self.i["file"] = i_self.i["i_cwd"] + "i_Economic_Partner_official_receiver_0.py"

                i_self.i["d"] = Path(i_self.i["file"])

                i_self.i["d"].write_text(i_self.i["i_Economic_Partner_official_receiver_0"])




                i_self.i["file"] = i_self.i["i_cwd"] + "i_Economic_Partner_official_sender_0.py"

                i_self.i["d"] = Path(i_self.i["file"])

                i_self.i["d"].write_text(i_self.i["i_Economic_Partner_official_sender_0"])

                






