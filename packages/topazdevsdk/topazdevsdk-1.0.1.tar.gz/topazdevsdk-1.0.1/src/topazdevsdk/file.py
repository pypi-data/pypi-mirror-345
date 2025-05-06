import os
import json

# •••••••••••••••••••••••••••••••••••••••
# ••••••••••••• FICHIERS ••••••••••••••••
# •••••••••••••••••••••••••••••••••••••••
def exist(path):
	"""
	Permet de vérifier l'existante d'un fichier ou d'un dossier.

	:param str path: Lien du fichier ou dossier.
	"""
	if os.path.exists(path):
		return True
	else:
		return False

# •••••••••••••••••••••••••••••••••••••••
def open_read(path, encoding='utf-8'):
	"""
	Ouvre un fichier en mode lecture et retourne ce fichier sous forme d'objet.

	:param str path: Lien du fichier.
	"""
	if exist(path):
		file = open(path, 'r', errors="ignore", encoding=encoding)
		return file
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def read(path, encoding='utf-8'):
	"""
	Ouvre un fichier en mode lecture et retourne ce fichier sous forme d'octet/texte.

	:param str path: Lien du fichier.
	"""
	if exist(path):
		file = open_read(path, encoding=encoding)
		return file.read()
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def write_check(path, data):
	"""
	Permet l'écriture d'un fichier par écrassement avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à écrire dans le fichier.
	"""
	if exist(path):
		file = open(path, 'w', encoding="utf-8")
		file.write(data)
		file.close()
		return True
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def write(path, data, encoding='utf-8'):
	"""
	Permet l'écriture d'un fichier par écrassement sans vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à écrire dans le fichier.
	"""
	file = open(path, 'w', encoding=encoding)
	file.write(data)
	file.close()
	return True

# •••••••••••••••••••••••••••••••••••••••
def add(path, data, encoding='utf-8'):
	"""
	Permet l'écriture d'un fichier par ajout avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à ajouter dans le fichier.
	"""
	if exist(path):
		file = open(path, 'a', encoding=encoding)
		file.write(data)
		file.close()
		return True
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def replace(path, value, line: int, encoding='utf-8'):
	"""
	Permet l'écriture d'un fichier par ajout avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à ajouter dans le fichier.
	"""
	if exist(path):
		file = open(path, 'r', encoding=encoding)
		data = file.readlines()
		file.close()

		data[line] = value

		file = open(path, 'w', encoding=encoding) 
		file.writelines(data)
		file.close()
		return True
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def replace_last(path, value, line: int = 1, encoding='utf-8'):
	"""
	Permet l'écriture d'un fichier par ajout avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à ajouter dans le fichier.
	"""
	if exist(path):
		file = open(path, 'r', encoding=encoding)
		data = file.readlines()
		file.close()
		l = len(data)-line

		data[l] = value

		file = open(path, 'w', encoding=encoding) 
		file.writelines(data)
		file.close()
		return True
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def check_in_line(path, value, line: int, encoding='utf-8'):
	"""
	"""
	if exist(path):
		file = open(path, 'r', encoding=encoding)
		data = file.readlines()
		file.close()
		if value in data[line]:
			return True
		else:
			return False
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def check_line(path, value, line: int, encoding='utf-8'):
	"""
	"""
	if exist(path):
		file = open(path, 'r', encoding=encoding)
		data = file.readlines()
		file.close()
		if value == data[line]:
			return True
		else:
			return False
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def create(path, encoding='utf-8'):
	"""
	Permet la création d'un fichier.

	:param str path: Lien du fichier.
	"""
	file = open(path, 'w', encoding=encoding)
	file.close()
	return True

# •••••••••••••••••••••••••••••••••••••••
def delete(path):
	"""
	Permet la suppression d'un fichier avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	"""
	if exist(path):
		os.remove(path)
		return True
	else:
		print(f"Impossible de supprimer le fichier {path} car il n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def copy(source, destination):
	"""
	Permet la copie d'un fichier avec vérification de l'existance du fichier.

	:param str source: Lien du fichier source.
	:param str destination: Lien du fichier destination.
	"""
	if exist(source):
		if not exist(destination):
			os.system(f'copy "{source}" "{destination}"')
			return True
		else:
			print(f"Le fichier {destination} existe déjà")
			return False
	else:
		print(f"Le fichier {source} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
# ••••••••••••• DOSSIERS ••••••••••••••••
# •••••••••••••••••••••••••••••••••••••••
def createdir(path):
	"""
	Permet la création d'un dossier avec vérification de l'existance de ce dossier.

	:param str path: Lien du fichier.
	"""
	if not os.path.exists(path):
		os.makedirs(path)
		return True
	return False

# •••••••••••••••••••••••••••••••••••••••
def listdirs(dirs, path):
	"""
	Permet de lister les fichiers et dossiers du dossier sélectionner.

	:param str path: Lien du dossier.
	"""
	for file in os.listdir(path):
		d = os.path.join(path, file)
		if os.path.isdir(d):
			dirs.append(d)
			listdirs(dirs, d)
	return dirs

# •••••••••••••••••••••••••••••••••••••••
def currentdir():
	"""
	Retourne le dossier courant

	:return: Chemin du dossier courant + Nom du dossier courant
	"""
	# récupérer le chemin du répertoire courant
	path = os.getcwd()
	# récupérer le nom du répertoire courant
	repn = os.path.basename(path)
	return path, repn

# •••••••••••••••••••••••••••••••••••••••
def copy_dir(source, destination):
	"""
	Permet la copie d'un dossier avec vérification de l'existance du dossier.

	:param str source: Lien du dossier source.
	:param str destination: Lien du dossier destination.
	"""
	if exist(source):
		if not exist(destination):
			os.system(f'xcopy "{source}" "{destination}" /E /I')
			return True
		else:
			print(f"Le dossier {destination} existe déjà")
			return False
	else:
		print(f"Le dossier {source} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
# ••••••••••••••• JSON ••••••••••••••••••
# •••••••••••••••••••••••••••••••••••••••
def json_read(path):
	"""
	Permet la lecture d'un fichier json et restitution des données sous la forme d'un objet.

	:param str path: Lien du fichier.
	"""
	if exist(path):
		file = open_read(path=path)
		data = json.load(file)
		file.close()
		return data
	else:
		print(f"Le fichier {path} n'existe pas")
		return False
	
# •••••••••••••••••••••••••••••••••••••••
def json_write(path, data):
	"""
	Permet l'écriture d'un fichier json par écrassement avec vérification de l'existance du fichier.

	:param str path: Lien du fichier.
	:param data: Données à écrire dans le fichier.
	"""
	if exist(path):
		file = open(path, 'w', encoding='utf-8')
		json.dump(data, file, indent=4, ensure_ascii=False)
		file.close()
		return True
	else:
		print(f"Le fichier {path} n'existe pas")
		return False

# •••••••••••••••••••••••••••••••••••••••
def json_loads(data):
	"""
	Permet de transformer des données brute en objet json.
	
	:param data: Données à mettre en forme.
	"""
	return json.loads(data)