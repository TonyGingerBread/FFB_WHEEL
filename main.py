import network
import socket
import time
from machine import Timer
from machine import Pin
import machine
import select
import utime

current_freq = machine.freq()
new_freq = 130000000  # For example, setting it to 250 MHz
machine.freq(new_freq)
led_pin = machine.Pin('LED', machine.Pin.OUT)
flag_for_changing_motor_state = 0;
flag_for_motor_state = 99;
EN_ACTIVE = 1
pwm_pin_7 = machine.Pin(7)
pwm_pin_10 = machine.Pin(10)
EN1_pin = machine.Pin(6, machine.Pin.OUT)
EN2_pin = machine.Pin(8, machine.Pin.OUT)
last_speed = 0
last_direction = 0

pwm_7 = machine.PWM(pwm_pin_7)
pwm_10 = machine.PWM(pwm_pin_10)

# Set PWM frequency (e.g., 1000 Hz)
pwm_7.freq(20000)
pwm_10.freq(20000)

def Motor_bring_to_speed(speed, direction):
    global last_speed
    global last_direction
    #if(speed != 0):
        #print(f'last_speed: {last_speed}')
        #print(f'last_direction: {last_direction}')
        #print(f'speed: {speed}')
        #print(f'direction: {direction}')
    if( direction != last_direction):
        if (last_direction == 1):
            for PWM_SPEED in range(last_speed, 0, -300):
                #print(PWM_SPEED)
                pwm_7.duty_u16(PWM_SPEED)
                pwm_10.duty_u16(0)
                utime.sleep_ms(5)
            last_direction = 0
            last_speed = 0
                                     
        if (last_direction == 2):
            for PWM_SPEED in range(last_speed, 0, -300):
                #print(PWM_SPEED)
                pwm_7.duty_u16(0)
                pwm_10.duty_u16(PWM_SPEED)
                utime.sleep_ms(5)
            last_direction = 0
            last_speed = 0
            
                
    if (direction == last_direction or last_direction == 0):
        if (direction == 1):
            if (last_speed > speed):
                for PWM_SPEED in range(last_speed, speed, -500):
                    #print(PWM_SPEED)
                    pwm_7.duty_u16(PWM_SPEED)
                    pwm_10.duty_u16(0)
                    utime.sleep_ms(5)
            if (last_speed < speed):
                for PWM_SPEED in range(last_speed, speed, 500):
                    #print(PWM_SPEED)
                    pwm_7.duty_u16(PWM_SPEED)
                    pwm_10.duty_u16(0)
                    utime.sleep_ms(5)
                
        if (direction == 2):
            if (last_speed > speed):
                for PWM_SPEED in range(last_speed, speed, -500):
                    #print(PWM_SPEED)
                    pwm_7.duty_u16(0)
                    pwm_10.duty_u16(PWM_SPEED)
                    utime.sleep_ms(5)
            if (last_speed < speed):
                for PWM_SPEED in range(last_speed, speed, 500):
                    #print(PWM_SPEED)
                    pwm_7.duty_u16(0)
                    pwm_10.duty_u16(PWM_SPEED)
                    utime.sleep_ms(5)
    
    
    #for duty_cycle_percent in range(0, 80):
     #   duty_cycle_value = int((60 / 100.0) * 65534)
     #   pwm_7.duty_u16(duty_cycle_value) # 32768 for 50%
     #   pwm_9.duty_u16(0) # 32768 for 50%
      #  utime.sleep_ms(100)  # Sleep for 1 second
    
    last_speed = speed
    last_direction = direction
    
    

wlan = network.WLAN(network.STA_IF)
def wlan_connect():
    ssid = 'VID4037'
    password = 'Anmpv021'

    if wlan.isconnected():
        print("Wi-Fi already connected")
        return

    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print(status[0])
                
wlan_connect()
UDP_IP = "10.0.0.194"
UDP_PORT = 5006
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind(('', UDP_PORT))
MESSAGE = b"HEY, MCU_PC"

EN1_pin.value(1)
EN2_pin.value(1)

while(True):
    #time.sleep(0.01);
    
    readable, _, _ = select.select([sock], [], [], 0)
    if sock in readable:
        data, addr = sock.recvfrom(1024)  
        
        try:
            INT_DATA = int(data.decode())
            INT_DATA = INT_DATA + 90
            INT_DATA %= 360
            if INT_DATA > 180:
                INT_DATA = INT_DATA - 360
            #print(INT_DATA)
            PWM_SIGNAL = ((200 * (abs(INT_DATA))) ^ 2) + 1500
            #PWM_SIGNAL %= 20000
            #print(PWM_SIGNAL)
            #print(f"Received from {addr}: {INT_DATA}")
            #print(INT_DATA)
            #if INT_DATA != 0 and EN_ACTIVE != 1:
            #    EN1_pin.value(1)
            #    EN2_pin.value(1)
            
            if int(INT_DATA) > 6: #and flag_for_motor_state != 1
                #flag_for_motor_state = 1
                #print("bigger than 0")
                led_pin.toggle()
                Motor_bring_to_speed(PWM_SIGNAL, 1)
                
            if int(INT_DATA) < -6: #and flag_for_motor_state != 2
                #flag_for_motor_state = 2
                #print("smaller than 0")
                led_pin.toggle()
                Motor_bring_to_speed(PWM_SIGNAL, 2)
            
            if int(INT_DATA) >= -6 and int(INT_DATA) <= 6:
                EN_ACTIVE = 0
                #flag_for_motor_state = 0
                led_pin.toggle()
                Motor_bring_to_speed(0, 0)
                #pwm_7.duty_u16(0)
                #pwm_10.duty_u16(0)
                
        except Exception as E:
            print(E)
            print("couldnt do the motor stuff")
            


sock.close()
wlan.deinit()


