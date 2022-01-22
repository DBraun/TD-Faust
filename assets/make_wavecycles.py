import numpy as np
from scipy.io import wavfile


def additive_synthesis(name, phases, amplitudes, length=4096):

	alldata = np.zeros(length)

	for i, (phase, amplitude) in enumerate(zip(phases, amplitudes)):

		# if i != 3:
		# 	amplitude *= 0.

		alldata += amplitude*np.sin(phase + (i+1)*np.pi*2.*np.arange(length)/length)

	alldata = alldata.reshape(1, -1)

	wavfile.write(f'{name}.wav', 44100, alldata.transpose())


def make_wavecycles():

	# make sine wave cycles
	for num in [4, 16, 4096]:

		data = np.sin(np.pi*2.*np.arange(num)/num)

		data = data.reshape(1, -1)

		wavfile.write(f'wave_cycle_sine_{num}_samples.wav', 44100, data.transpose())

	# make sawtooth wave cycles
	for num in [3, 4, 16]:

		data = (np.arange(num) / num)*2
		data -= 2.*np.floor(data)
		print(data)
		data = data.reshape(1, -1)
		

		wavfile.write(f'wave_cycle_saw_{num}_samples.wav', 44100, data.transpose())



def make_additive_synthesis_examples():

	for i in range(4):

		num_harmonics = 20

		name = f'additive_synthesis_{i}'
		phases = np.random.rand(num_harmonics)*np.pi*2.
		amplitudes = np.random.rand(num_harmonics)*.25

		additive_synthesis(name, phases, amplitudes)


def main():

	make_wavecycles()
	make_additive_synthesis_examples()


if __name__ == "__main__":
	main()