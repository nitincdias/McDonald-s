#!/bin/env python3

#Created by Nitin Dias
#git clone https://github.com/nitincdias/McDonald-s
#Dependent file: stores.csv, saved at /var/home/nd842u/stores.csv


import netmiko
import ipaddress
import sys
import csv
import getpass
import datetime

try:
    user = str(input('\nEnter AT&T username: '))
    pwd = getpass.getpass('Enter AT&T password: ')       
except KeyboardInterrupt:
    print()
    sys.exit()


def getstoreip(ele):
    devip = ''
    with open('/var/home/nd842u/stores.csv') as f:
        read1 = csv.reader(f)
        for row in read1:
            if row[0] == ele:
                devip = (row[1])
                break
    return devip

def getstorenum(contents):
    store = []
    for row in contents:
        try:
            if row == '':
                continue
            elif len(row) > 5:
                stname = row.split()
                fstore = stname[1]
            elif len(row) == 5:
                fstore = row
            elif len(row) == 4:
                fstore = '0'+row
            elif len(row) == 3:
                fstore = '00'+row
            elif len(row) == 2:
                fstore = '000'+row
            elif len(row) == 1:
                fstore = '0000'+row
            store.append(fstore)
        except:
            store.append('')
            continue
    return store

def xy(value):

    if (value[15] == '.') & (value[17] == '.'):
        x=value[14]
        y=value[16]
    elif (value[15] == '.') & (value[18] == '.'):
        x=value[14]
        y=value[16]+value[17]
    elif (value[15] == '.') & (value[19] == '.'):
        x=value[14]
        y=value[16]+value[17]+value[18]

    elif (value[16] == '.') & (value[18] == '.'):
        x=value[14]+value[15]
        y=value[17]
    elif (value[16] == '.') & (value[19] == '.'):
        x=value[14]+value[15]
        y=value[17]+value[18]
    elif (value[16] == '.') & (value[20] == '.'):
        x=value[14]+value[15]
        y=value[17]+value[18]+value[19]

    elif (value[17] == '.') & (value[19] == '.'):
        x=value[14]+value[15]+value[16]
        y=value[18]
    elif (value[17] == '.') & (value[20] == '.'):
        x=value[14]+value[15]+value[16]
        y=value[18]+value[19]
    else:
        x=value[14]+value[15]+value[16]
        y=value[18]+value[19]+value[20]


    bos='10.'+x+'.'+y+'.24'
    pos='10.'+x+'.'+y+'.25'
    bos1='10.'+x+'.'+y+'.51'

    return bos, pos, bos1

def health():

    print('\n************************************************')
    print('*     Health Check for McDonalds Restaurant    *')
    print('************************************************')

    deviceip = ''
    attempt = 0

    while True:
        try:
            if attempt <= 2:
                store1 = input('\nEnter the McDonalds store number: ')
                if len(store1) >= 5:
                    store = store1
                elif len(store1) == 4:
                    store = '0'+store1
                elif len(store1) == 3:
                    store = '00'+store1
                elif len(store1) == 2:
                    store = '000'+store1
                else: store = '0000'+store1

                deviceip = getstoreip(store)
                if deviceip != '':
                    break
                else:
                    print('\nInvalid store number')
                    attempt+=1 

            else:
                print('\n**** Attempting to connect using IP address ****')
                while True:
                    try:
                        deviceip = input('\nEnter the IP address of the controller: ')
                        if ipaddress.ip_address(deviceip) == True:
                            break
                        break
                    except ValueError:
                        print("\nNot a valid IP address. Try again!")
                break

        except KeyboardInterrupt:
            print('\n')
            sys.exit()


    try:
        device = netmiko.ConnectHandler(device_type='aruba_os', ip=deviceip, username=user, password=pwd)
    except netmiko.NetMikoTimeoutException:
        print('\nCannot connect to this device')
        sys.exit()
    except netmiko.NetMikoAuthenticationException:
        print('\nAuthentication Error. Cannot connect to this device')
        sys.exit()
    except KeyboardInterrupt:
        print('\n')
        sys.exit()
    except:
        print('\nAn error occured')

    host = device.send_command('show hostname')
    host1 = host.split()


    try:
        print('\n({}) #show uplink'.format(host1[2]))
        print(device.send_command('show uplink'))
        print('\n({}) #show crypto ipsec sa'.format(host1[2]))
        print(device.send_command('show crypto ipsec sa'))
        print('\n({}) #ping 66.111.155.132 source 410'.format(host1[2]))
        TS1= device.send_command('ping 66.111.155.132 source 410')
        print(TS1)
        print('({}) #ping 152.140.225.56 source 410'.format(host1[2]))
        TS2= device.send_command('ping 152.140.225.56 source 410')
        print(TS2)
        value = device.send_command('show ip route | i VLAN410')

        val = xy(value)

        bosip = ('ping {}'.format(val[0]))
        posip= ('ping {}'.format(val[1]))
        bos1ip = ('ping {}'.format(val[2]))

        print('({}) #ping {}'.format(host1[2], val[0]))
        B24 = (device.send_command(bosip))
        print(B24)
        print('({}) #ping {}'.format(host1[2], val[1]))
        P25 = (device.send_command(posip))
        print(P25)
        print('({}) #ping {}'.format(host1[2], val[2]))
        B51 = (device.send_command(bos1ip))
        print(B51)
        print('({}) #ping prod.dw.us.fdcnet.biz'.format(host1[2]))
        cash =(device.send_command('ping prod.dw.us.fdcnet.biz'))
        print(cash)


        print('\n**********************************************')
        print('*                 SUMMARY                    *')
        print('**********************************************\n')


        uplink= device.send_command ('show uplink | begin 4094')

        usplit=uplink.split('40')
        for _ in range(0,4):
            usplit[_]=usplit[_].replace('Waiting for link', 'Waiting_for_link')


        u4094 = usplit[1].split()
        u4081 = usplit[2].split()
        u4082 = usplit[3].split()

        print('\n1. Uplink 101 is {} and {}'.format(u4094[3],u4094[4]))
        print('\n2. Uplink 102 is {} and {}'.format(u4081[3],u4081[4]))
        print('\n3. Uplink 103 is {} and {}'.format(u4082[3],u4082[4]))

        ipsec = device.send_command ('show crypto ipsec sa | begin Total')
        ipsec1=ipsec.split()
        print('\n4. Total IPSEC tunnels: {}'.format(ipsec1[3]))

        TS11 = TS1.split('Success')
        TS111 = TS11[1].split()
        if TS111[2] == '0':
            TS1R = 'No'
        else:
            TS1R = 'Yes'
        print('\n5. Terminal Server 66.111.155.132')
        print('\tReachable:    {}'.format(TS1R))
        print('\tSuccess Rate: {} %'.format(TS111[2]))

        TS22 = TS2.split('Success')
        TS222 = TS22[1].split()
        if TS222[2] == '0':
            TS2R = 'No'
        else:
            TS2R = 'Yes'
        print('\n6. Terminal Server 152.140.225.56')
        print('\tReachable:    {}'.format(TS2R))
        print('\tSuccess Rate: {} %'.format(TS222[2]))

        B24s = B24.split('Success')
        B24ss = B24s[1].split()
        if B24ss[2] == '0':
            B24R = 'No'
        else:
            B24R = 'Yes'
        print('\n7. BOS (.24)')
        print('\tReachable:    {}'.format(B24R))
        print('\tSuccess Rate: {} %'.format(B24ss[2]))

        B51s = B51.split('Success')
        B51ss = B51s[1].split()
        if B51ss[2] == '0':
            B51R = 'No'
        else:
            B51R = 'Yes'
        print('\n8. BOS (.51)')
        print('\tReachable:    {}'.format(B51R))
        print('\tSuccess Rate: {} %'.format(B51ss[2]))

        P25s = P25.split('Success')
        P25ss = P25s[1].split()
        if P25ss[2] == '0':
            P25R = 'No'
        else:
            P25R = 'Yes'
        print('\n9. POS (.25)')
        print('\tReachable:    {}'.format(P25R))
        print('\tSuccess Rate: {} %'.format(P25ss[2]))

        cashs = cash.split('Success')
        cashss = cashs[1].split()
        if cashss[2] == '0':
            cashR = 'No'
        else:
            cashR = 'Yes'
        print('\n10. Cashless Connectivity')
        print('\tReachable:    {}'.format(cashR))
        print('\tSuccess Rate: {} %'.format(cashss[2]))
        print('\n')

    except KeyboardInterrupt:
        print('\n')
        sys.exit()
    except:
        print('\nAn error occured')


    print('Any additional commands to run?  (Use Ctrl+C to exit)')
    while True:
        try:
            command = input('\nEnter the command: ')
            print(device.send_command(command))
            continue
        except KeyboardInterrupt:
            print('\n')
            device.disconnect()
            sys.exit()

    device.disconnect()
    sys.exit()

def cashless():

    command = []
    passed = []
    failed = []
    contents = []

    print("\nEnter the store numbers:  (Use Ctrl-D to save and run)\n")

    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            print('\n')
            sys.exit()
        except:
            break
        contents.append(line)

    storenumbers = getstorenum(contents)
    print(storenumbers)


    print('\n       ********************* CASHLESS CHECK ********************\n')

    while True:
        try:
            text_file = open("output.txt", "w")

            for ele in storenumbers:
                deviceip = getstoreip(ele)
                if deviceip == '':
                    print("\n               ##############  McDonald's {}  #############".format(ele))
                    print('\nInvalid store number')
                    failed.append(ele)
                    continue
                else:
                    print("\n               ##############  McDonald's {}  #############".format(ele))
                    try:
                        device = netmiko.ConnectHandler(device_type='aruba_os', ip=deviceip, username=user, password=pwd)
                    except netmiko.NetMikoTimeoutException:
                        print('\nCannot connect to this device \nCashless check failed for this store')
                        failed.append(ele)
                        continue
                    except netmiko.NetMikoAuthenticationException:
                        print('\nAuthentication Error. Cannot connect to this device')
                        failed.append(ele)
                        continue
                    except KeyboardInterrupt:
                        print('\n')
                        sys.exit()
                    except:
                        print('\nAn error occured')
                        failed.append(ele)
                        continue

                try:
                    host = device.send_command('show hostname')
                    host1 = host.split()
                    now = datetime.datetime.now()

                    TS1= device.send_command('ping 66.111.155.132 source 410')
                    TS2= device.send_command('ping 152.140.225.56 source 410')

                    value = device.send_command('show ip route | i VLAN410')

                    val = xy(value)

                    bosip = ('ping {}'.format(val[0]))
                    posip= ('ping {}'.format(val[1]))
                    bos1ip = ('ping {}'.format(val[2]))

                    B24 = (device.send_command(bosip))
                    P25 = (device.send_command(posip))
                    B51 = (device.send_command(bos1ip))
                    cash =(device.send_command('ping prod.dw.us.fdcnet.biz'))

                    TS11 = TS1.split('Success')
                    TS111 = TS11[1].split()
                    if TS111[2] == '0':
                        TS1R = 'Unreachable'
                    else:
                        TS1R = 'Reachable'
                    print('\nTS1: 66.111.155.132      {0} - {1}%'.format(TS1R, TS111[2]))


                    TS22 = TS2.split('Success')
                    TS222 = TS22[1].split()
                    if TS222[2] == '0':
                        TS2R = 'Unreachable'
                    else:
                        TS2R = 'Reachable'
                    print('TS2: 152.140.225.56      {0} - {1}%'.format(TS2R, TS222[2]))


                    B24s = B24.split('Success')
                    B24ss = B24s[1].split()
                    if B24ss[2] == '0':
                        B24R = 'Unreachable'
                    else:
                        B24R = 'Reachable'
                    print('BOS (.24)                {0} - {1}%'.format(B24R, B24ss[2]))


                    B51s = B51.split('Success')
                    B51ss = B51s[1].split()
                    if B51ss[2] == '0':
                        B51R = 'Unreachable'
                    else:
                        B51R = 'Reachable'
                    print('BOS (.51)                {0} - {1}%'.format(B51R, B51ss[2]))


                    P25s = P25.split('Success')
                    P25ss = P25s[1].split()
                    if P25ss[2] == '0':
                        P25R = 'Unreachable'
                    else:
                        P25R = 'Reachable'
                    print('POS (.25)                {0} - {1}%'.format(P25R, P25ss[2]))


                    cashs = cash.split('Success')
                    cashss = cashs[1].split()
                    if cashss[2] == '0':
                        cashR = 'Unreachable'
                    else:
                        cashR = 'Reachable'
                    print('Cashless URL             {0} - {1}%'.format(cashR, cashss[2]))


                    if (TS1R+TS2R+B24R+B51R+P25R+cashR) == (6*'Reachable'):
                        print('\nCashless Test:      PASSED')
                        passed.append(ele)

                        text_file.write("\n\n               ##############  McDonald's {}  #############".format(ele))
                        text_file.write('\n#Cashless \n\nThis Venue is not part of the Cashless Down/Venue Down tracking report. The POS, BOS, TS and cashless are all reachable.\n')
                        text_file.write(now.strftime('Output as of %m-%d-%Y %H:%M:%S %ZGMT'))
                        text_file.write('\n\n({}) #ping 66.111.155.132 source 410'.format(host1[2]))
                        text_file.write(TS1)
                        text_file.write('({}) #ping 152.140.225.56 source 410'.format(host1[2]))
                        text_file.write(TS2)
                        text_file.write('({}) #ping {}'.format(host1[2], val[0]))
                        text_file.write(B24)
                        text_file.write('({}) #ping {}'.format(host1[2], val[1]))
                        text_file.write(P25)
                        text_file.write('({}) #ping {}'.format(host1[2], val[2]))
                        text_file.write(B51)
                        text_file.write('({}) #ping prod.dw.us.fdcnet.biz'.format(host1[2]))
                        text_file.write(cash)

                    else:
                        print('\nCashless Test:      FAILED')
                        failed.append(ele)

                    device.disconnect()

                except:
                    print('\nCashless check failed for this store')
                    failed.append(ele)
                    continue

            text_file.close()

            print('\n\n    ********* SUMMARY ********')
            print('\nCashless test PASSED for the below sites:\n{}'.format(passed))
            print('\nCashless test FAILED for the below sites:\n{}'.format(failed))
            print('\n**** All outputs are saved in output.txt file ****\n')

            break

        except KeyboardInterrupt:
            print('\n')
            text_file.close()
            sys.exit()
        except:
            print('\nAn error occured')
            text_file.close()
            sys.exit()

    sys.exit()

def check():

    command = []

    print("\nEnter the store numbers:  (Use Ctrl-D to save and run)\n")
    contents = []
    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            print('\n')
            sys.exit()
        except:
            break
        contents.append(line)

    storenumbers = getstorenum(contents)
    print(storenumbers)


    while True:
        try:
            command.append(input('\nEnter the command to run: '))
            sure = input('\nDo you want to enter more commands? Answer [y or n]: ')
            if (sure== 'y') or (sure=='Y'):
                continue
            elif (sure== 'n') or (sure=='N'):
                break
            else:
                print('Invalid input')
                break
        except KeyboardInterrupt:
            print('\n')
            sys.exit()

    print('\nExecuting the following commands for the list of stores: \n\n{}'.format(command))


    while True:
        try:
            text_file = open("output.txt", "w")
            for ele in storenumbers:
                deviceip = getstoreip(ele)
                if deviceip == '':
                    print("\n               ##############  McDonald's {}  #############".format(ele))
                    print('\nInvalid store number')
                    text_file.write("\n\n\n               ##############  McDonald's {}  #############".format(ele))
                    text_file.write('\n\nInvalid store number')
                    continue
                else:
                    print("\n               ##############  McDonald's {}  #############".format(ele))
                    text_file.write("\n\n\n               ##############  McDonald's {}  #############".format(ele))

                    try:
                        device = netmiko.ConnectHandler(device_type='aruba_os', ip=deviceip, username=user, password=pwd)
                    except netmiko.NetMikoTimeoutException:
                        print('\nCannot connect to this device')
                        continue
                    except netmiko.NetMikoAuthenticationException:
                        print('\nAuthentication Error. Cannot connect to this device')
                        continue
                    except KeyboardInterrupt:
                        print('\n')
                        sys.exit()
                    except:
                        print('\nAn error occured')
                        continue

                    host = device.send_command('show hostname')
                    host1 = host.split()

                    for _ in command:
                        try:
                            if _ == '':
                                continue
                            else:
                                print('\n({0}) #{1}'.format(host1[2],_))
                                text_file.write('\n\n({0}) #{1}\n'.format(host1[2],_))
                                zz = (device.send_command(_))
                                print(zz)
                                text_file.write(zz)
                                print('\n')
                                text_file.write('\n')
                        except:
                            print('\nAn error occured')
                            continue

                    device.disconnect()
            text_file.close()
            print('\n**** All outputs are saved in output.txt file ****\n')
            break

        except KeyboardInterrupt:
            print('\n')
            text_file.close()
            sys.exit()
        except:
            print('\nAn error occured')
            text_file.close()
            sys.exit()

    device.disconnect()

def main():
    print('\n************************************************')
    print("*                  McDonald's                  *")
    print('************************************************')
    print('\n\tSelect from the options below:\n')
    print('\t1. Health Check\n\t2. Cashless Check\n\t3. Run commands on single/multiple sites')

    while True:
        try:
            option = input('\nEnter the option number: ')
            if option == '1':
                health()
                break
            elif option == '2':
                cashless()
                break
            elif option == '3':
                check()
                break
            else: 
                print('Invalid input, Try again')

        except KeyboardInterrupt:
            print('\n')
            sys.exit()

if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print()
        quit()