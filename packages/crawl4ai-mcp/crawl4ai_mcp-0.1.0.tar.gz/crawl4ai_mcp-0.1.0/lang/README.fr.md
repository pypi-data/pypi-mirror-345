# Web Crawler MCP

[![English](https://img.shields.io/badge/lang-en-blue.svg)](../README.md) [![中文](https://img.shields.io/badge/lang-zh-blue.svg)](README.zh.md) [![हिंदी](https://img.shields.io/badge/lang-hi-blue.svg)](README.hi.md) [![Español](https://img.shields.io/badge/lang-es-blue.svg)](README.es.md) [![Français](https://img.shields.io/badge/lang-fr-blue.svg)](README.fr.md) [![العربية](https://img.shields.io/badge/lang-ar-blue.svg)](README.ar.md) [![বাংলা](https://img.shields.io/badge/lang-bn-blue.svg)](README.bn.md) [![Русский](https://img.shields.io/badge/lang-ru-blue.svg)](README.ru.md) [![Português](https://img.shields.io/badge/lang-pt-blue.svg)](README.pt.md) [![Bahasa Indonesia](https://img.shields.io/badge/lang-id-blue.svg)](README.id.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

Un puissant outil de crawling web qui s'intègre avec des assistants IA via le MCP (Machine Conversation Protocol). Ce projet vous permet de crawler des sites web et de sauvegarder leur contenu [...]

## 📋 Fonctionnalités

- Crawling de sites web avec profondeur configurable
- Support pour liens internes et externes
- Génération de fichiers Markdown structurés
- Intégration native avec les assistants IA via MCP
- Statistiques détaillées des résultats de crawl
- Gestion des erreurs et des pages non trouvées

## 🚀 Installation

### Prérequis

- Python 3.9 ou supérieur

### Étapes d'installation

1. Cloner ce dépôt:

```bash
git clone laurentvv/crawl4ai-mcp
cd crawl4ai-mcp
```

2. Créer et activer un environnement virtuel:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python -m venv .venv
source .venv/bin/activate
```

3. Installer les dépendances requises:

```bash
pip install -r requirements.txt
```

## 🔧 Configuration

### Configuration MCP pour les Assistants IA

Pour utiliser ce crawler avec des assistants IA comme VScode Cline, configurez votre fichier `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "crawl": {
      "command": "PATH\\TO\\YOUR\\ENVIRONMENT\\.venv\\Scripts\\python.exe",
      "args": [
        "PATH\\TO\\YOUR\\PROJECT\\crawl_mcp.py"
      ],
      "disabled": false,
      "autoApprove": [],
      "timeout": 600
    }
  }
}
```

Remplacez `PATH\\TO\\YOUR\\ENVIRONMENT` et `PATH\\TO\\YOUR\\PROJECT` par les chemins appropriés sur votre système.

#### Exemple concret (Windows)

```json
{
  "mcpServers": {
    "crawl": {
      "command": "C:\\Python\\crawl4ai-mcp\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\Python\\crawl4ai-mcp\\crawl_mcp.py"
      ],
      "disabled": false,
      "autoApprove": [],
      "timeout": 600
    }
  }
}
```

## 🖥️ Utilisation

### Utilisation avec un Assistant IA (via MCP)

Une fois configuré dans votre assistant IA, vous pouvez utiliser le crawler en demandant à l'assistant d'effectuer un crawl en utilisant la syntaxe suivante:

```
Pouvez-vous crawler le site web https://example.com avec une profondeur de 2?
```

L'assistant utilisera le protocole MCP pour exécuter l'outil de crawling avec les paramètres spécifiés.

### Exemples d'utilisation avec Claude

Voici des exemples de demandes que vous pouvez faire à Claude après avoir configuré l'outil MCP:

- **Crawl simple**: "Pouvez-vous crawler le site example.com et me donner un résumé?"
- **Crawl avec options**: "Pouvez-vous crawler https://example.com avec une profondeur de 3 et inclure les liens externes?"
- **Crawl avec sortie personnalisée**: "Pouvez-vous crawler le blog example.com et sauvegarder les résultats dans un fichier nommé 'blog_analysis.md'?"

## 📁 Structure des résultats

Les résultats du crawl sont sauvegardés dans le dossier `crawl_results` à la racine du projet. Chaque fichier de résultat est au format Markdown avec la structure suivante:

```markdown
# https://example.com/page

## Métadonnées
- Profondeur: 1
- Horodatage: 2023-07-01T12:34:56

## Contenu
Contenu extrait de la page...

---
```

## 🛠️ Paramètres disponibles

L'outil de crawl accepte les paramètres suivants:

| Paramètre | Type | Description | Valeur par défaut |
|-----------|------|-------------|---------------|
| url | chaîne | URL à crawler (requis) | - |
| max_depth | entier | Profondeur maximale de crawling | 2 |
| include_external | booléen | Inclure les liens externes | false |
| verbose | booléen | Activer la sortie détaillée | true |
| output_file | chaîne | Chemin du fichier de sortie | généré automatiquement |

## 📊 Format des résultats

L'outil renvoie un résumé avec:
- URL crawlée
- Chemin vers le fichier généré
- Durée du crawl
- Statistiques sur les pages traitées (réussies, échouées, non trouvées, accès interdit)

Les résultats sont sauvegardés dans le répertoire `crawl_results` de votre projet.

## 🤝 Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.