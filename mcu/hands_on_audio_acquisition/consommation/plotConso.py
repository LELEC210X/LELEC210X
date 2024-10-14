#Plot the consomation of the board depending on time
import matplotlib.pyplot as plt
import numpy as np

#datas dans le csv situé à consommation/scopy.csv
# Sample,Time(S),CH1(V)
# Les datas commencent à la 9ieme ligne
data = np.genfromtxt('consommation/scopyv2.csv', delimiter=',', skip_header=9)

#On récupère les valeurs de temps et de consommation
time = data[:,1]
conso = data[:,2]**2/27*1000

## print moyenne de la consommation entre 1.8 et 1.9s en mW
print("Consommation moyenne entre 1.8 et 1.9s en mW:", np.mean(conso[(time>1.8) & (time<1.9)]))
## print moyenne de la consommation entre 2 et 3d en mW
print("Consommation moyenne entre 2 et 3s en mW:", np.mean(conso[(time>2) & (time<3)]))
## print moyenne de la consommation entre 3.8 et 0.19s
print("Consommation moyenne entre 3.8 et 3.9s en mW:", np.mean(conso[(time>3.8) & (time<3.9)]))
## print moyenne de la consommation entre 5 et 7s
print("Consommation moyenne entre 5 et 7s en mW:", np.mean(conso[(time>5) & (time<7)]))
## print moyenne de la consommation entre 9 et 10s
print("Consommation moyenne entre 9 et 10s en mW:", np.mean(conso[(time>9) & (time<10)]))

#On plot les valeurs
plt.plot(time, conso)
plt.xlabel('Time (s)')
plt.ylabel('Consumption (mW)')
plt.title('Consumption of the board depending on time')
#plt.savefig('consommation/conso.pdf', format='pdf')
plt.show()

#Créer un pie chart pour montrer la consommation moyenne
conso_moy = [0.1625*10**-3*0.20,  0.7688*10**-3*0.80]

#On plot le pie chart
plt.pie(conso_moy, labels=['Recording datas into \n the buffer after the ADC','LED ON and sending \n datas to UART'])
plt.gca().patches[0].set_color('green')
plt.gca().patches[1].set_color('magenta')
plt.legend(loc='lower right', labels=[
    'Recording datas into the buffer after the ADC - {:.1f}%'.format(conso_moy[0] / sum(conso_moy) * 100),
    'LED ON and sending datas to UART - {:.1f}%'.format(conso_moy[1] / sum(conso_moy) * 100)
])
plt.title('Energy consomption of the system.')
#plt.savefig('consommation/conso_moy_pie_chart.pdf', format='pdf')
plt.show()