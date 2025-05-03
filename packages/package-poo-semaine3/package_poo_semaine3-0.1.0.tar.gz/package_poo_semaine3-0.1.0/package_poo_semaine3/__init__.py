"""
Mon package - Une bibliothèque pour simplifeir les opérations complexes.
"""

# Version du package
__version__ = '0.1.0'

# Importation des éléments que nous voulons rendre disponibles directement
from .module1 import fonction_principale, ClassePrincipale
from .module2 import fonction_utilitaire


# Liste des éléments exposés (utile pour l'importation with import *)
__all__ = [
  'fonction_principale', 'ClassePrincipale', 'fonction_utilitaire'
]
