############################################################################################################
  ##### Código de nome "continuo.py", tem como objetivo ajustar o contínuo de cada objeto da amostra. #####
#   Devida algumas particularidades de alguns espectros, houve a necessidade de se impor valores iniciais mais espeíficos.
# Isso possibilitou o código "achar" um ajuste de forma mais rápida e sem erro. Outras particularidades são da estética do 
# gráfico plotado. Para impor limites para alguns espectros em especiais, também utilizamos de particularidades como: 
# - exclusão de comprimentos de onda que havia problemas instrumentais;
# - regiões de S/N muito elevado com consequentemente com picos.

                        ########  Instruções de como rodar o código:  ########  
#		                        		 'python plot.py <numero>'
# 	         <numero> indica a linha do arquivo 'sample_list.txt' que você deseja trabalhar.
#############################################################################################################

##### bibliotecas utilizadas ####
#coding: utf-8
import math as mat
import numpy as np
import matplotlib.pyplot as plt
import lineid_plot
import statistics
import copy
import sys
import os
from lmfit import Model
from lmfit import Parameters
import seaborn as sns
pal=sns.color_palette("colorblind",20)
#####################################

#inicialização e upload de arquivos
nun=int(sys.argv[1])	# argumento do terminal 

# variaveis do código que são importante ser declaradas
X, Y, x = [], [], []		
l=a=q=k=cont=0
d=20
flux=[None]*d
label,wave=[],[]

continuox, continuoy = [], []
wavegx, wavegy = [], []

wgx, wgy, YMAX = [], [], []
centro, alpha = [], []

n_contx,n_conty=[],[]

#reconhecendo cabeçalho do arquivo que ira entrar
data=np.genfromtxt('sample_list.txt', delimiter='\t', dtype=None, encoding=None, names=('FILE','AGN','redshift','RA','DEC','telescope','instrument','E(B-V)g','index'))

z=data['redshift']
index=data['index']
name=data['AGN']
arquivo=data['FILE']

#os.chdir('/home/usuario/INPE/agns/trabalho/sample/entrada')
os.chdir('/home/denimara/Documentos/agns/trabalho/sample/entrada/teste')
file=np.genfromtxt(arquivo[nun])

#lendo arquivo dos dados  

X=file[:,0]		#X=comprimendo de onda
Y=file[:,1]#/1e-15	#Y=fluxo

			#linha que desejamos identificar
line_wave = [8446,8498,9531,9999,10049,10500,10830,10938,11126,12820,14300,18750,19446,21654]#,22230,22470] 
line_label1 = ['O I','Ca II','[SIII]','FeII','HI','FeII','HeI','HI','FeII','HI','[SiX]','HI','HI', 'HI']#,'H$_2$','H$_2$']

		#####################################################
#			Identificando linhas no espectro
		#####################################################

#comprimento do arquivo em coluna y
n=len(Y)	

######	Primeiro for: 
#contém a subdivisão de valores 'd' partes, onde para 'd' se tira uma mediana do cálculo do fluxo. Deste modo valores abaixo da mediana são guardados, e valores acima servem para identificar as linhas 'd' regiao.

for i in range (d):
	y=[]

	for j in range (n//d):
		y.append(Y[q])
		q+=1

	y1=copy.copy(y)

	#fazendo uma mediana do que sera um valor de fluxo 
	flux[i]=statistics.median(y1)

	# loop para "delimitar" o fluxo relevante para identificação das linhas, depois armazena-los 
for z in range(d):

	for i in range (n//d):

			#guarda valor da possivel posição de x que irá conter a linha
			if Y[k]> (flux[z]) and Y[k]>Y[k-1]:
				x.append(X[k])	
				n_contx.append(X[k])
				n_conty.append(Y[k])

			#se for menor, identifica como possivel valor de continuo
			elif Y[k]<flux[z]:

				#Avaliando regiões não interessantes para contio de alguns    
				# espectros em particular. Por ex, se for alguma do flamingos,
				# não inclua os 500A finais no continuo.		      
				if 8400<X[k]<8600 or 9440<X[k]<9600 or 9900<X[k]<10230 or 10740<X[k]<11030:
					pass

				else:
					if nun==13 or nun==14 or nun==62 or nun==67 or nun==68:
						if X[k]< (max(X)-500):
							continuox.append(X[k])
							continuoy.append(Y[k])
				
					elif nun==58:
						if  X[k]>9810 and X[k]< (max(X)-900):
							continuox.append(X[k])
							continuoy.append(Y[k])
					elif nun==26: 
						if X[k]>7950:
							continuox.append(X[k])
							continuoy.append(Y[k])
					elif nun==71: 
						if X[k]>9000:
							continuox.append(X[k])
							continuoy.append(Y[k])
					elif nun==57:
						if X[k]<7676 or X[k]>7705:
							continuox.append(X[k])
							continuoy.append(Y[k])
					elif nun==31:
						if X[k]<17000 or X[k]>18430 or X[k]>23670:
							continuox.append(X[k])
							continuoy.append(Y[k])
					elif nun==24:
						if X[k]<16100 or X[k]>17000:
							continuox.append(X[k])
							continuoy.append(Y[k])
					else:
						continuox.append(X[k])
						continuoy.append(Y[k])
			k+=1

#quantos valores de linhas para possíveis fluxos foram identificadas
N=len(x)

######################	Salvando regiões de linhas em um arquivo ##############
#os.chdir('/home/usuario/INPE/agns/trabalho/sample/scripts/fluxo')
#os.chdir('/home/denimara/Documentos/agns/trabalho/sample/scripts/fluxo')
#np.savetxt('linhas.txt',np.c_[n_contx,n_conty],delimiter=' ', newline='\n')
###############################################################################


#######	Loop grande:
# destinado a identificar linhas dentre os fluxos previamente identificados

for j in range (N):
	for l in range (len(line_wave)):
	#separação fina por um delta de comprimendo de onda aceitável para 'caber' tal linha
		if (line_wave[l]-6)< x[j] < (line_wave[l]+6):
			cont+=1

			if cont==1:
				wave.append(line_wave[l])
				label.append(line_label1[l])

			#não estava plotando em cima da onde achou a linha e sim da catalogada, então aqui se fez um 'shift' para melhor traçar a identificação
			elif wave[-1]!=line_wave[l]:
				if label[-1]!=line_label1[l] and (l-1)>=0:
					wave.append(x[j])
					label.append(line_label1[l])
					qts=l

				else:
					if label[-1]==line_label1[l] and x[j]-wave[-1]>20:
						wave.append(x[j])
						label.append(line_label1[l])

			
		#########################################################
#			Identificação de valor obrigatório de CONTINUO 		
#				(retirado de Rifell et. all 2006)	
		#########################################################
for i in range (len(X)):

	if 8000<=X[i]<=8100 and nun!=58 and nun !=26 and nun!=71:#continuo que eu adicionei para forçar no inicio do espectro
		continuox.append(X[i])
		continuoy.append(Y[i])		
		
	elif 9700<=X[i]<=9800 and nun!=58:#original
		continuox.append(X[i])
		continuoy.append(Y[i])

	elif 12299<X[i]<12301: #original
		continuox.append(X[i])
		continuoy.append(Y[i])

	elif 16600<=X[i]<=16700 and nun!=24:	#original
		continuox.append(X[i])
		continuoy.append(Y[i])
	
	elif 20900<=X[i]<=21000:		#original
		continuox.append(X[i])
		continuoy.append(Y[i])

	elif 8400<X[i]<22000 and nun!=58:	#motivo estético para o plot
		YMAX.append(Y[i])
	elif 9810<X[i]<22000 and nun==58:
		YMAX.append(Y[i])


########################### Saida com valor do contínuo ########################
#arq=np.genfromtxt(arquivo[nun])
#os.chdir('/home/usuario/INPE/agns/trabalho/sample/scripts/fluxo')
#os.chdir('/home/denimara/Documentos/agns/trabalho/sample/scripts/fluxo')
#np.savetxt(arquivo[nun],np.c_[continuox,continuoy],delimiter=' ', newline='\n')


		################################
#			Pré ajuste
		################################

#Parametros de cada modelo a serem fitados
params = Parameters()
params.add(name='scala',value=statistics.median(Y))
params.add(name='reference',value=10000)

###############################################################################################
#	valores bons para temperatura inicial, obtidos a partir de tentativa e erro
#	obs: nem todos espectros precisam
###############################################################################################
if   nun==22 or nun==2 or nun==64 or nun==69  or nun==3 or nun==20 or  nun==36 or nun==59 or nun==37 or nun==43  or nun==65:
	params.add('T',value=980,min=500,max=1500)

elif nun==10 or nun==11 or nun==13 or nun==15 or nun==42 or nun==46 or nun==48 or nun==71  or nun==70 or nun==23  or nun==66 or nun==16 or nun==29 or nun==0 or nun==4 or nun==17 or nun==21 or nun==24 or nun==25 or nun==30 or nun==40 or nun==44 or nun==52  or nun==18  or nun==27 or nun==35 or nun==54 :
	params.add('T',value=1255,min=500,max=1500)

elif nun==41 or nun==16  or nun==58  :
	params.add('T',value=1350,min=500,max=1500 )

elif nun==56 or nun==45 or nun==38 or nun==39 :
	params.add('T',value=1499,min=500,max=1500)

else:
	params.add('T',value=0,min=500,max=1500)


	#######################################################################
#		Funções de componentes que irão ser ajustadas
	#######################################################################

#POWER LAW
def PowerLow(wavelenght,scala,reference,Index):
	return (scala*((wavelenght/reference)**Index))

#BLACK BODY
def Black_Body(wavelenght,T,alfa,reference):
	c1 = 1.438786e+8
	fator=c1/T
	top=(reference**5)*(np.exp(fator/reference)-1)
	bot=(np.power(wavelenght,5))*(np.exp(fator/wavelenght)-1)
	return alfa*(top/bot)

#FIT DO CONTINUO :pw+bb 
def SOMA(wavelenght, T, alfa, reference, scala, Index):
	bb=Black_Body(wavelenght,T,alfa,reference)
	pl=PowerLow(wavelenght,scala,reference,Index)
	return bb+pl

			###############################
#				Início do ajuste
			##############################

contador=0.001
while (contador<1.0):
	if nun==71 or nun==0 or nun==58 or nun==18:
		params.add(name='Index',value=index[nun],min=-3.0001,max=0.00009)
	else:
		params.add(name='Index',value=index[nun])

	if  nun==11 or nun==10 or nun==12 or nun==16 or nun==25 or nun==19 or nun==24 or nun==29 or nun==30 or nun==31 or nun==36 or nun==37  or nun==41 or nun==43 or nun==45 or nun==54 or nun==56 or nun==27 or nun==57 or nun==58 or nun==59 or nun==60 or nun==61 or nun==62 or nun==63 or nun==65 or nun==67 or nun==3:
		params.add('alfa',value=contador, min=0,max=1e-10)
	else:
		params.add('alfa',value=contador)

	try:
		modeloSOMA=Model(SOMA,independent_vars=['wavelenght'],param_names=['T','alfa','reference','scala','Index'])
		resultSOMA=modeloSOMA.fit(continuoy,params,wavelenght=continuox)

		s1=resultSOMA.params['T'].value
		s2=resultSOMA.params['alfa'].value
		s3=resultSOMA.params['reference'].value
		s4=resultSOMA.params['scala'].value
		s5=resultSOMA.params['Index'].value
		fluxo_continuo=SOMA(X,s1,s2,s3,s4,s5)

		#imprimindo INFORMAÇÕES sobre o  FIT
		#print(resultSOMA.fit_report())
		#print('\n\n')
		print (s1,s2,s5)
		contador=1.0

	except:
		contador+=0.001

		###################################################################
#			guardando informações (T,fluxo em 2.2microns na banda K)
		###################################################################

fluxoK=[]
BB =Black_Body(X,s1,s2,s3)
K=0
for i in range(len(X)):
	if X[i]==22000:
		fluxoK=BB[i]		
		K=1
	else:
		if K==0:
			if 21998<X[i]<22002:
				fluxoK=BB[i]		
				K=1

			elif 21997 <=  X[i] <= 22003:
				fluxoK=BB[i]	
				K=1
			elif max(X)<22000:
				fluxoK=0		

	######	Fluxo integrado	#####
Fluxo_IntegradoBB = np.trapz(Black_Body(X,s1,s2,s3), x=X)
#print(Fluxo_IntegradoBB)

	######	saída dos valores	######
#os.chdir('/home/denimara/Documentos/agns/trabalho/sample/scripts/continuo')
#os.chdir('/home/usuario/INPE/agns/trabalho/sample/scripts/continuo')
#arq=open('entrada_dust.txt','a')
#np.savetxt(arq,np.c_[fluxoK,s1],delimiter=' ', newline='\n')
#print(fluxoK,s1)
os.chdir('/home/denimara/Documentos/agns/trabalho/sample/scripts/continuo/saida_ajuste_continuo')
arqs=open('saida_ajuste_continuo.txt','a')
#np.savetxt(arqs,np.c_[s1,s2,s3,s4,s5,Fluxo_IntegradoBB,resultSOMA.params['T'].stderr,resultSOMA.params['Index'].stderr],delimiter=' ', newline='\n')
par=open('parametros.txt', 'a')
np.savetxt(par,np.c_[s1,s2,s5], delimiter =' ', newline= '\n')

		###########################
#			LABELS da figura
		###########################

#YMAX=YMAX/1e-15
Y=Y/1e-15
#plt.gcf().clear()
plt.rc('font', weight='bold') #bold fonte 
plt.rc('axes', linewidth=1.8) #broader eixos
fig = plt.figure(1,figsize=(16,8))
plt.tight_layout()
plt.rcParams.update({'font.size': 15})
ax2=fig.add_axes([0.085,0.1,0.901,0.7])
ax2.set_ylabel(r'Flux [x 10$^{-15}$ erg / s / cm$^{2}$ / $\mathdefault{\AA}$]',fontweight='bold',fontsize=23)
ax2.set_xlabel('Wavelength [$\mathdefault{\AA}$]',fontweight='bold',fontsize=20)
ax2.set_title(name[nun],fontweight='bold',fontsize=20,y=1.17)

#delimitando extremidades dos plots especiais
if nun==11 or nun==24 or  nun==26 or nun==47 or nun==49 or nun==52 or nun==63 or nun==64 or nun==65 or nun==66 or nun==69 or nun==70:
	ax2.set_xlim(8000,max(X))

elif nun==58:
	ax2.set_xlim(9880,(max(X)-500))

elif nun==54:
	ax2.set_xlim(9000,max(X))

elif nun==57:
	ax2.set_xlim(8000,max(X))

else: 
	ax2.set_xlim(min(X),max(X))

#valores adicionados ou subtraidos, são para dar margem ao plot
if(min(Y)<0):
	ax2.set_ylim(0,(max(YMAX)+max(YMAX)/10)/1e-15)
else:
	ax2.set_ylim(0,(max(YMAX)+max(YMAX)/10)/1e-15)

if nun==64:
	ax2.set_ylim(min(Y)-min(Y)/2,max(Y)/3)

elif nun==69:
	ax2.set_ylim(min(Y)-min(Y)/2,max(Y/5))

ax2.plot(X,Y,'-k',linewidth=2.8)

#____________________________fits_________________________________________
line1,=ax2.plot(X,fluxo_continuo/1e-15,linestyle='-',color='blue',linewidth=3,label="continnum")
line2,=ax2.plot(X,PowerLow(X,s4,s3,s5)/1e-15,'--',color=pal[3],linewidth=3,label="power-law")
line3,=ax2.plot(X,Black_Body(X,s1,s2,s3)/1e-15,'--',color=pal[2],linewidth=3,label="blackbody")
ax2.tick_params(axis='x', which='both',direction='in', length=4,width=1.7)
ax2.tick_params(axis='y', which='both',direction='in', length=4, width=1.7)

#mostrar continuo
#ax2.plot(continuox,continuoy,".",linewidth=20,color='orange')
#ax2.patch.set_facecolor('gray')
#ax2.patch.set_alpha(0.1)

lineid_plot.plot_line_ids(X, Y, wave, label,ax=ax2,max_iter=1000)
fig.set_facecolor('w')
legend_properties = {'weight':'bold'}
plt.legend(handles=[line1,line2,line3],loc="upper right",prop=legend_properties)

	####	box superior	####
ax1=fig.add_axes([0.085,0.800,0.901,0.10])
ax1.set_xticks([])
ax1.set_yticks([])
ax1.plot()
ax1.patch.set_facecolor('gray')
ax1.patch.set_alpha(0.05)

#os.chdir('/home/usuario/INPE/agns/trabalho/sample/plots')
os.chdir('/home/denimara/Documentos/agns/trabalho/sample/scripts/continuo/plots')
plt.savefig(name[nun]+'.png',facecolor=fig.get_facecolor(), edgecolor='none')

#Para exibir na tela e não salvar, 'descomente'
#plt.show(block=True)

