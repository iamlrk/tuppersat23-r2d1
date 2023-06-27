import machine
import time

i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

sensor_address = 0x77


coefficients = [] #[P sensitivity, P offset, T coeff of P sensitivity, T coeff of P offset, reference T, T coeff of temperature]

for i in range(8):
    i2c.writeto(sensor_address, bytes([0xA0+i*2]))
    data = i2c.readfrom(sensor_address, 2)
    value = int.from_bytes(data, 'big')
    coefficients.append(value)

#CALL PRESSURE 
# Send command to start pressure conversion with oversampling rate of 4096 (OSR=4096)
i2c.writeto(sensor_address, bytes([0x48]))

# Wait for pressure conversion to finish (9.04 ms for OSR=4096)
time.sleep_ms(10)


# Send command to read ADC result 
i2c.writeto(sensor_address, bytes([0x00]))

# Read three bytes of data 
data = i2c.readfrom(sensor_address, 3)

# Convert data to integer value 
value = int.from_bytes(data, 'big')

# define pressure
D1 = value # Raw pressure value

#CALL TEMPERATURE 
# Send command to start temperature conversion with oversampling rate of 4096 (OSR=4096)
i2c.writeto(sensor_address, bytes([0x58]))

# Wait for temperature conversion to finish (9.04 ms for OSR=4096)
time.sleep_ms(10)

# Send command to read ADC result 
i2c.writeto(sensor_address, bytes([0x00]))

# Read three bytes of data 
data = i2c.readfrom(sensor_address, 3)

# Convert data to integer value 
value = int.from_bytes(data, 'big')

#define temperature 
D2 = value # Raw temperature value

C1 = coefficients[1]
C2 = coefficients[2]
C3 = coefficients[3]
C4 = coefficients[4]
C5 = coefficients[5]
C6 = coefficients[6]

# Calculate difference between actual and reference temperature 
dT = D2 - C5 * pow(2,8)
temp = 2000 + ((dT * C6) / pow(2,23))

# Calculate actual temperature (-40...85°C with 0.01°C resolution) 
#temperature_actual = 2000 + dT * C6 / pow(2,23) 

# Calculate offset at actual temperature 
OFF = C2 * pow(2,16) + ((C4 * dT) / pow(2,7) )

# Calculate sensitivity at actual temperature 
SENS = C1 * pow(2,15) + ((C3 * dT) / pow(2,8) )

# Calculate second order corrections based on actual temperature range  
if temp < 2000:  
   Tcorr   = pow(dT , 2) / pow(2 , 31)  
   OFFcorr   = 5 * pow((temp -2000), 2)/2 
   SENScorr   =(29*pow((temp -2000),2))/2
   if temp < -1500:  
       #Tcorr   =(11*pow(dT , 3))/pow((34359738368),12);  
       OFFcorr =OFFcorr + 7*pow((temp+1500),2)
       SENScorr =SENScorr + 11*pow((temp+1500),2)/2 

else:   
   Tcorr=OFFcorr=SENScorr=0

TEMP = temp-Tcorr
OFF = OFF-OFFcorr
SENS = SENS -SENScorr


Pressure = (D1*(SENS)/pow(2,21)-(OFF))/pow(2,15) #output is in pascal
print(Pressure/100)
