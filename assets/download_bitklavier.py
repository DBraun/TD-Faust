import requests
import zipfile
import os.path
from os.path import abspath

def download_grand_piano():

	"""Download the dataset if it's missing"""

	try:

		file_paths = [f"bitKlavierGrand_PianoBar/{i}v8.wav" for i in range(88)]

		if os.path.isfile(file_paths[0]):
			return

		bitKlavierURL = 'https://ccrma.stanford.edu/~braun/assets/bitKlavierGrand_PianoBar.zip'
		
		# download the file contents in binary format
		print(f'Downloading: {bitKlavierURL}')
		r = requests.get(bitKlavierURL)

		path_to_zip_file = abspath("bitKlavierGrand_PianoBar.zip")
		print(f'Saving to path: {path_to_zip_file}')
		with open(path_to_zip_file, "wb") as zip:
		    zip.write(r.content)

		print(f'Unzipping: {path_to_zip_file}')
		with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
		    zip_ref.extractall("./")

		os.remove(path_to_zip_file)
		print(f'Removed zip: {path_to_zip_file}')

	except Exception as e:
		print('Something went wrong downloading the bitKlavier Grand Piano data.')
		raise e

if __name__ == "__main__":
	download_grand_piano()