import requests
import zipfile
import os.path
from os.path import abspath
import pathlib


def download_grand_piano():

	"""Download the dataset if it's missing"""

	try:

		cwd = pathlib.Path(__file__).parent.resolve()

		file_paths = [os.path.join(cwd, f"bitKlavierGrand_PianoBar/{i}v8.wav") for i in range(88)]

		if os.path.isfile(file_paths[0]):
			return

		bitKlavierURL = 'https://ccrma.stanford.edu/~braun/assets/bitKlavierGrand_PianoBar.zip'
		
		# download the file contents in binary format
		print(f'Downloading: {bitKlavierURL}')
		r = requests.get(bitKlavierURL)

		path_to_zip_file = os.path.join(cwd, "bitKlavierGrand_PianoBar.zip")
		print(f'Saving zip to path: {path_to_zip_file}')
		with open(path_to_zip_file, "wb") as zip:
		    zip.write(r.content)

		print(f'Unzipping to directory: {cwd}')
		with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
		    zip_ref.extractall(cwd)

		os.remove(path_to_zip_file)
		print(f'Removed zip: {path_to_zip_file}')

	except Exception as e:
		print('Something went wrong downloading the bitKlavier Grand Piano data.')
		raise e

if __name__ == "__main__":
	download_grand_piano()