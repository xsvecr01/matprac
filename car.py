#importování knihoven
import socket
import machine
import time

#přiřazení a nastavení pinů
servo = machine.PWM(machine.Pin(4), freq=50)
fwd = machine.PWM(machine.Pin(12), freq=50)
bwd = machine.PWM(machine.Pin(14), freq=50)

#funkce pro rychlost a směr motoru
def speed(i):
    if i > 300:
        i = i-300
        fwd.duty(i)
        bwd.duty(0)
    elif i < -300:
        i = i*(-1)
        i = i-300
        fwd.duty(0)
        bwd.duty(i)
    else:
        fwd.duty(0)
        bwd.duty(0)

#s = socket.socket()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s.bind(addr)
s.listen(1)

while True:
    vcc = machine.ADC(1).read()/1024    #přečtení hodnoty napětí na pinu ADC
    if vcc < 3.2:                       #porovnání hodnoty proměnné "vcc", jestli je menší než 3.2
        speed(0)                        #pokud podmínka platí, model se na 10 sekund zastaví
        time.sleep(10)
    cl, addr = s.accept()               #přiřazení adresy a portu pro připojení
    request = cl.recv(1024)             #příjem požadavků
    request = str(request)              #převedení požadavků na proměnnou typu string
    ix = request.find('X')              #hledání znaku "X" a přiřazení jeho pozice do proměnné "ix"
    iy = request.find('Y')
    iz = request.find('Z')
    if ix > 0:                          #porovnání, jestli přišel požadavek
        cl.sendall('HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n') #odeslání HTTP hlavičky klientovi
        ie = request.find(' ', ix)      #hledání mezery a proměnné "ix"
        ValX = int(request[ix+1:iy])    #přiřazení hodnoty mezi "ix" a "iy" do proměnné ValX
        ValY = int(request[iy+1:iz])
        servo.duty(ValX)                #odeslání hodnoty "ValX" na servo
        speed(ValY)                     #provedení funkce speed s danou hodnotou
    else:
        cl.sendall('HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Type: text/html\r\n\r\n')
        html = open('html.html', 'r')   #přečtení souboru html.html a přiřazení do proměnné
        cl.sendall(html.read())         #poslání html stránky klientovi
        html.close()                    #zavření souboru
        del html                        #smazání proměnné
        time.sleep_ms(500)              #čekání 500ms pro správné poslání html
    cl.close()                          #ukončení komunikace
