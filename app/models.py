class ad:
	def __init__(self, id=None, nome="", descricao="", categoria="", imagem="", preco=0.0):
		self.id = id if id is not None else self._generate_id()
		self.nome = nome
		self.descricao = descricao
		self.categoria = categoria
		self.imagem = imagem
		self.preco = preco

	_next_id = 1
	@classmethod
	def _generate_id(cls):
		current_id = cls._next_id
		cls._next_id += 1
		return current_id

# lista em memoria para armazenar os anuncios
_ads_data = []

def get_ads():
	"""retorna todos os anuncios."""
	return _ads_data

def add_ad(ad):
	"""adiciona um novo anuncio a lista."""
	_ads_data.append(ad)
