from .imghandler import ImageUploader



# une seule interface pour choisir le provider de img upload
# TODO : ajouter un fallback si un provide ne fonctionne pas 
# ou ben basculement vers un autre clé

__all__ = [
    'ImageUploader'
]