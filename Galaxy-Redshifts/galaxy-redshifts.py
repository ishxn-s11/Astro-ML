#Extracting Galaxy Redshifts From Real Data 
'''
To Determine The Redshift Of A Galaxy By Fitting A Model To 
The Spectral Features In Its Observed Spectrum And Comparing The
Wavelength Of These Features When They Were Created By The Galaxy.
'''

#Importing Necessary Libraries
import numpy as np, matplotlib.pyplot as plt
import scipy.signal as signal
from scipy.optimize import curve_fit
from astropy.io import fits

#Defining Gaussian Function 
def gauss(x,a,mean,sigma):
    return (a/(sigma*np.sqrt(2*np.pi)))*np.exp((-pow((x-mean),2.0)/(2*pow(sigma,2.0))))

#Testing The Gaussian Function
x_test=np.linspace(0,20,100)
test=gauss(x_test,1.0,5,1.0)
plt.plot(x_test,test)
plt.show()

#Function To Combine Two Gaussians At Different Linecenters Into One Simulated Spectrum
def combined_gauss(x,a1,a2,m1,m2,w1,cont):
    return cont+gauss(x,a1,m1,w1)+gauss(x,a2,m2,w1)

print()

#Function To Fit The Combined Gaussian To The Simulated Spectrum
def fit_data(wave,spec_flux,a1,a2,m1,m2,w1,cont):
    #Least Squares Fit 
    popt,pcov=curve_fit(combined_gauss,wave,spec_flux,p0=[a1,a2,m1,m2,w1,cont])
    err=np.sqrt(np.diag(pcov))
    print("Best Fit Parameters And 1 std Errors:")
    print(f'Line 1 Amplitude:{popt[0]:.2f} ± {err[0]:.2f}\n')
    print(f'Line 2 Amplitude:{popt[1]:.2f} ± {err[1]:.2f}\n')
    print(f'Line 1 Wavelength:{popt[2]:.2f} ± {err[2]:.2f}\n')
    print(f'Line 2 Wavelength:{popt[3]:.2f} ± {err[3]:.2f}\n')
    print(f'Line Width:{popt[4]:.2f} ± {err[4]:.2f}\n')
    print(f'Continuum Level:{popt[5]:.2f} ± {err[5]:.2f}\n')
    print()
    #Plotting The Observed And Modeled Data
    y_mod=combined_gauss(wave,*popt) #Unpacking
    plt.plot(wave,spec_flux,label='Observed Spectrum')
    plt.plot(wave,y_mod,label='Modeled Spectrum')
    plt.vlines(popt[2],ymin=0.0,ymax=spec_flux.max(),linestyle='--',alpha=0.75,linewidth=1.0)
    plt.vlines(popt[3],ymin=0.0,ymax=spec_flux.max(),linestyle='--',alpha=0.75,linewidth=1.0)
    plt.legend()
    plt.show()
    return popt,pcov

#Testing
wave_test=np.linspace(0,20,100)
pure_mod=combined_gauss(wave_test,20.0,40.0,5,10,1.0,0.25)
test_func=pure_mod+np.random.normal(loc=pure_mod,size=len(pure_mod))
plt.plot(wave_test,test_func)
plt.show()
out_popt,out_pcov=fit_data(wave_test,test_func,18,33,4.5,9.5,1.5,0.5)

#Defining The Function For Calculating Redshift From The Fitted Line Centers
def calc_redshift(wave_obs,wave_rest):
    return (wave_obs-wave_rest)/wave_rest

#Reading The FITS File Containing The Galaxy Spectrum
hdul=fits.open('galaxy_spec.fits')
print(hdul[1].columns)

spec=hdul[1].data['flux']
waves=10**hdul[1].data['log-wavelen']

plt.figure(figsize=(10,6)) 
plt.plot(waves,spec)
plt.show()

#Preparing Inputs To The Fitting Function
sub_i=np.where((waves>6450)&(waves<6600))
sub_spec=spec[sub_i]
sub_wave=waves[sub_i]

plt.figure(figsize=(10,6)) 
plt.plot(sub_wave,sub_spec)
plt.show()

spec_peaks=signal.find_peaks(sub_spec,height=35)
print(sub_wave[spec_peaks])

#Fitting The Data 
popt_,pcov_=fit_data(sub_wave,sub_spec,40,130,*sub_wave[spec_peaks],5.0,4.0)

#Calculating The Redshift
03_4959_e=4958.911
03_5007_e=5006.843
src_redshift=calc_redshift(popt_[2],03_4959_e)
print(f"Redshift From 4959 Line:{src_redshift:.4f}\n")
print() 
src_redshift=calc_redshift(popt_[3],03_5007_e)
print(f"Redshift From 5007 Line:{src_redshift:.4f}\n")
