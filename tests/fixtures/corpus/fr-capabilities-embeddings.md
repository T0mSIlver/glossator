---
url: https://docs.mistral.ai/fr/capabilities/embeddings
title: Embeddings
breadcrumbs:
  - Capacités
  - Embeddings
kind: doc
locale: fr
source_path: src/content/fr/docs/capabilities/embeddings/page.mdx
source_commit: 2e094f7
---

# Embeddings

Un embedding transforme un texte en un vecteur de nombres dont la géométrie
reflète le sens : deux textes qui parlent de la même chose se retrouvent proches
l'un de l'autre, quels que soient les mots employés. C'est ce qui permet à la
recherche sémantique de fonctionner là où la recherche par mots-clés échoue.

## Les modèles {#les-modeles}

`mistral-embed` produit des vecteurs de 1024 dimensions et accepte jusqu'à 8192
tokens en entrée. Le modèle est multilingue : un texte français et sa traduction
anglaise se placent au même endroit de l'espace, ce qui permet d'interroger en
français un corpus rédigé en anglais.

`mistral-embed-dim128-2510` renvoie 128 dimensions pour le même texte. L'index
occupe huit fois moins de place, au prix d'une perte de finesse sur les
distinctions les plus subtiles.

## Appeler l'API {#appeler-l-api}

L'endpoint accepte une liste de textes et renvoie un vecteur par texte, dans
l'ordre de la requête.

```python
from mistralai import Mistral

client = Mistral(api_key=api_key)
reponse = client.embeddings.create(
    model="mistral-embed",
    inputs=["Comment diffuser une réponse ?", "Quels modèles gèrent la vision ?"],
)
vecteurs = [donnee.embedding for donnee in reponse.data]
```

Une requête peut contenir jusqu'à 512 textes. Au-delà, l'API renvoie un code 400
et aucun vecteur n'est facturé.

## Choisir la taille des passages {#choisir-la-taille-des-passages}

Un passage trop long dilue le sujet dans le vecteur ; un passage trop court perd
le contexte qui le rend interprétable. Pour de la documentation technique, une
section de titre avec son corps est la bonne unité : elle porte un seul sujet et
reste sous la limite de tokens.

## Tarification {#tarification}

`mistral-embed` est facturé 0,10 USD par million de tokens en entrée. Il n'y a
pas de coût de sortie : la réponse ne contient que des vecteurs.
