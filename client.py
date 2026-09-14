#!/usr/bin/env python3
"""
SWAEV Genomics TUI Client
Interactive, rich terminal client designed for researchers to submit genomic sequences
and visualize chromatin contact map outputs with dynamic phage ASCII animations.
"""

import os
import sys
import time
import json
import math
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Ensure rich is installed
try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.align import Align
    from rich.rule import Rule
    from rich.layout import Layout
    from rich.padding import Padding
except ImportError:
    print("Error: The 'rich' library is required to run this TUI client.")
    print("Please install it by running: pip install rich")
    sys.exit(1)

console = Console()

# Configuration Path
CONFIG_PATH = os.path.expanduser("~/.goldbeam.json")
DEFAULT_API_URL = "https://gateway.swaev.com"
GITHUB_RAW = "https://raw.githubusercontent.com/CK5515/SWAEV_TUI/main"
__version__ = "2026-09-14"

# -----------------------------------------------------------------------------
# Color Themes & Localization Configuration
# -----------------------------------------------------------------------------
THEME_CONFIGS = {
    "multi_colour": {
        "name": "Retro Multi Colour",
        "desc": "A vibrant vintage high-contrast experience with classic retro terminal colors.",
        "primary": "#4285F4",
        "primary_bold": "bold #4285F4",
        "secondary": "#EA4335",
        "secondary_bold": "bold #EA4335",
        "accent": "#FBBC05",
        "accent_bold": "bold #FBBC05",
        "success": "#34A853",
        "success_bold": "bold #34A853",
        "warning": "#FBBC05",
        "warning_bold": "bold #FBBC05",
        "error": "#EA4335",
        "error_bold": "bold #EA4335",
        "text": "white",
        "text_bold": "bold white",
        "border": "#4285F4",
        "title": "#4285F4",
        "art_primary": "#4285F4",
        "art_primary_bold": "bold #4285F4",
        "art_limbs": "#34A853",
        "art_limbs_bold": "bold #34A853",
    },
    "swaev_blue": {
        "name": "SWAEV Blue",
        "desc": "High-readability light mode matching SWAEV website branding (#057db5 brand text, slate text).",
        "primary": "#057db5",
        "primary_bold": "bold #057db5",
        "secondary": "#0ea5e9",
        "secondary_bold": "bold #0ea5e9",
        "accent": "#0ea5e9",
        "accent_bold": "bold #0ea5e9",
        "success": "#047857",
        "success_bold": "bold #047857",
        "warning": "#b45309",
        "warning_bold": "bold #b45309",
        "error": "#b91c1c",
        "error_bold": "bold #b91c1c",
        "text": "#0f172a",
        "text_bold": "bold #0f172a",
        "border": "#057db5",
        "title": "#057db5",
        "art_primary": "#057db5",
        "art_primary_bold": "bold #057db5",
        "art_limbs": "#0ea5e9",
        "art_limbs_bold": "bold #0ea5e9",
    },
    "swaev_lime": {
        "name": "SWAEV Lime",
        "desc": "Sleek cyber-green experience matching SWAEV website dark-mode accent (#deff9a).",
        "primary": "chartreuse1",
        "primary_bold": "bold chartreuse1",
        "secondary": "green",
        "secondary_bold": "bold green",
        "accent": "spring_green1",
        "accent_bold": "bold spring_green1",
        "success": "chartreuse1",
        "success_bold": "bold chartreuse1",
        "warning": "yellow",
        "warning_bold": "bold yellow",
        "error": "red",
        "error_bold": "bold red",
        "text": "white",
        "text_bold": "bold white",
        "border": "chartreuse1",
        "title": "chartreuse1",
        "art_primary": "chartreuse1",
        "art_primary_bold": "bold chartreuse1",
        "art_limbs": "bright_green",
        "art_limbs_bold": "bold bright_green",
    },
    "cyberpunk_neon": {
        "name": "Cyberpunk Neon",
        "desc": "Retro-futuristic aesthetic with hot pink and deep violet accents.",
        "primary": "hot_pink",
        "primary_bold": "bold hot_pink",
        "secondary": "dark_violet",
        "secondary_bold": "bold dark_violet",
        "accent": "magenta",
        "accent_bold": "bold magenta",
        "success": "hot_pink",
        "success_bold": "bold hot_pink",
        "warning": "magenta",
        "warning_bold": "bold magenta",
        "error": "red",
        "error_bold": "bold red",
        "text": "white",
        "text_bold": "bold white",
        "border": "hot_pink",
        "title": "hot_pink",
        "art_primary": "hot_pink",
        "art_primary_bold": "bold hot_pink",
        "art_limbs": "magenta",
        "art_limbs_bold": "bold magenta",
    },
    "retro_amber": {
        "name": "Retro Amber",
        "desc": "Monochrome phosphor cathode ray terminal experience.",
        "primary": "orange3",
        "primary_bold": "bold orange3",
        "secondary": "orange3",
        "secondary_bold": "bold orange3",
        "accent": "orange3",
        "accent_bold": "bold orange3",
        "success": "orange3",
        "success_bold": "bold orange3",
        "warning": "orange3",
        "warning_bold": "bold orange3",
        "error": "orange3",
        "error_bold": "bold orange3",
        "text": "orange3",
        "text_bold": "bold orange3",
        "border": "orange3",
        "title": "orange3",
        "art_primary": "orange3",
        "art_primary_bold": "bold orange3",
        "art_limbs": "orange3",
        "art_limbs_bold": "bold orange3",
    }
}

TRANSLATIONS = {
    "en": {
        "title_security_check": "SECURITY CHECK",
        "title_security_approved": "SECURITY APPROVED",
        "title_access_denied": "ACCESS DENIED",
        "title_offline_mode": "OFFLINE MODE",
        "title_onboarding": "WELCOME WIZARD",
        
        "welcome_banner": "» SECURE B2B AUTHENTICATION",
        "welcome_desc": "To interact with the GoldBEAM genomic prediction engine, please\nauthenticate using your secure API access token.",
        "welcome_tip": "Generate your key at: [underline cyan]swaev.com/#portal[/underline cyan]",
        "welcome_sandbox": "[bold white]Or press ENTER with an empty key to enter Offline Sandbox Mode.[/bold white]",
        "prompt_key": "Paste your X-API-Key: ",
        "verifying_key": "» VERIFYING ACCESS CREDENTIALS...",
        "verifying_gateway": "Contacting secure B2B gateway...",
        
        "sandbox_title": "» OFFLINE SANDBOX PROFILE SETUP",
        "sandbox_desc": "Please specify a research username for your local\noffline sandbox workspace session:",
        "prompt_username": "Enter username: ",
        "offline_configured": "[bold green]✓[/bold green] OFFLINE PROFILE CONFIGURED",
        "welcome_local": "Welcome [brown]{username}[/brown] to SWAEV local workstation.",
        "init_sandbox": "Initializing sandbox sequence workspace...",
        
        "auth_success": "[bold green]✓[/bold green] AUTHENTICATION SUCCESSFUL",
        "welcome_back": "Welcome back, [brown]{username}[/brown]!",
        "key_registered": "Your secure API key has been locally registered.",
        "invalid_token": "[bold red]✗[/bold red] Invalid access token. Check the key and try again.",
        "gateway_unreachable": "[bold red]✗[/bold red] GATEWAY UNREACHABLE",
        "gateway_unreachable_desc": "Cannot verify key because the authentication server is offline.",
        
        
        "label_user": "User",
        "label_tier": "Tier",
        "label_mode": "Mode",
        "label_core": "Core",
        "status_active": "Active",
        "status_online": "Online",
        "status_offline": "Offline",
        "settings_title": "USER SETTINGS",
        "settings_current_name": "Current Name",
        "settings_current_theme": "Current Theme",
        "settings_current_lang": "Current Language",
        "settings_api_conn": "API Connection",
        "settings_current_fasta": "FASTA Index Folder",
        "settings_opt_name": "Change Researcher Name",
        "settings_opt_theme": "Change Color Theme",
        "settings_opt_lang": "Change Localization Language",
        "settings_opt_api": "Configure API Key / Gateway Connection",
        "settings_opt_dirs": "Configure Working Directories",
        "settings_opt_back": "Back to Workspace",
        "settings_prompt": "Select an option [1-6]: ",
        "settings_user_config_title": "USER CONFIG",
        "settings_online": "Online",
        "settings_offline": "Offline Sandbox",
        "title_dir_config": "DIRECTORY CONFIG",
        "dir_title": "CONFIGURE WORKING DIRECTORIES",
        "dir_desc": "Enter the folder that holds your FASTA files. (e.g. '.', './fasta')",
        "title_name_config": "NAME CONFIG",
        "title_theme_config": "THEME CONFIG",
        "title_lang_config": "LANGUAGE CONFIG",
        "title_api_config": "API CONFIG",
        "title_api_config_error": "API CONFIG ERROR",
        "theme_title": "SELECT COLOR THEME",
        "theme_desc": "Choose a theme that matches your workstation branding:",
        "theme_prompt": "Choose theme [1-5]: ",
        "theme_classic": "(Classic Retro)",
        "theme_blue_desc": "(Branded light mode accent)",
        "theme_lime_desc": "(Branded dark mode accent)",
        "theme_neon_desc": "(Hot Pink & Violet)",
        "theme_amber_desc": "(CRT Phosphor monochrome)",
        "theme_apply_note": "The client border, titles, and bacteriophage art will adapt immediately.",
        "theme_applied_success": "THEME APPLIED",
        "theme_changed_to": "Theme changed to",
        "initializing_workspace_styling": "Initializing workspace styling...",
        "onboarding_lang_prompt": "Choose language [1-4] (default 1): ",
        "onboarding_theme_prompt": "Choose theme [1-5] (default 3): ",
        "lang_select_title": "SELECT YOUR LANGUAGE / SELECCIONE IDIOMA",
        "lang_select_desc": "Select your preferred localization language:",
        "lang_choice_prompt": "Choose language [1-4]: ",
        "onboarding_offline_fallback": "Proceeding in Offline Sandbox mode under: [brown]{username}[/brown]",
    },
    "es": {
        "title_security_check": "CONTROL DE SEGURIDAD",
        "title_security_approved": "SEGURIDAD APROBADA",
        "title_access_denied": "ACCESO DENEGADO",
        "title_offline_mode": "MODO OFFLINE",
        "title_onboarding": "ASISTENTE DE BIENVENIDA",
        
        "welcome_banner": "» AUTENTICACIÓN SEGURA B2B",
        "welcome_desc": "Para interactuar con el motor de predicción genómica GoldBEAM,\nautentíquese utilizando su token de acceso API seguro.",
        "welcome_tip": "Genere su clave en: [underline cyan]swaev.com/#portal[/underline cyan]",
        "welcome_sandbox": "[bold white]O presione ENTER con una clave vacía para el Modo Sandbox Offline.[/bold white]",
        "prompt_key": "Pegue su X-API-Key: ",
        "verifying_key": "» VERIFICANDO CLAVE DE CREDENCIALES...",
        "verifying_gateway": "Contactando con la pasarela segura para autorizar...",
        
        "sandbox_title": "» CONFIGURACIÓN DE PERFIL SANDBOX OFFLINE",
        "sandbox_desc": "Especifique un nombre de usuario de investigación para su sesión\nde espacio de trabajo sandbox local offline:",
        "prompt_username": "Ingrese nombre de usuario: ",
        "offline_configured": "[bold green]✓[/bold green] PERFIL OFFLINE CONFIGURADO",
        "welcome_local": "Bienvenido [brown]{username}[/brown] a la estación de trabajo local SWAEV.",
        "init_sandbox": "Inicializando el espacio de trabajo sandbox...",
        
        "auth_success": "[bold green]✓[/bold green] AUTENTICACIÓN EXITOSA",
        "welcome_back": "¡Bienvenido de nuevo, [brown]{username}[/brown]!",
        "key_registered": "Su clave API segura ha sido registrada localmente.",
        "invalid_token": "[bold red]✗[/bold red] Token de acceso no válido. Verifique la clave e intente nuevamente.",
        "gateway_unreachable": "[bold red]✗[/bold red] PASARELA INALCANZABLE",
        "gateway_unreachable_desc": "No se puede verificar la clave porque el servidor de autenticación está fuera de línea.",
        
        
        "label_user": "Usuario",
        "label_tier": "Plan",
        "label_mode": "Modo",
        "label_core": "Núcleo",
        "status_active": "Activo",
        "status_online": "En línea",
        "status_offline": "Desconectado",
        "settings_title": "AJUSTES DE USUARIO",
        "settings_current_name": "Nombre actual",
        "settings_current_theme": "Tema actual",
        "settings_current_lang": "Idioma actual",
        "settings_api_conn": "Conexión API",
        "settings_current_fasta": "Carpeta de índice FASTA",
        "settings_opt_name": "Cambiar nombre de investigador",
        "settings_opt_theme": "Cambiar tema de color",
        "settings_opt_lang": "Cambiar idioma de localización",
        "settings_opt_api": "Configurar clave API / Conexión de pasarela",
        "settings_opt_dirs": "Configurar carpetas de trabajo",
        "settings_opt_back": "Volver al espacio de trabajo",
        "settings_prompt": "Seleccione una opción [1-6]: ",
        "settings_user_config_title": "CONFIG DE USUARIO",
        "settings_online": "En línea",
        "settings_offline": "Sandbox fuera de línea",
        "title_dir_config": "CONFIG DE CARPETAS",
        "dir_title": "CONFIGURAR CARPETAS DE TRABAJO",
        "dir_desc": "Ingrese la carpeta que contiene sus archivos FASTA. (ej. '.', './fasta')",
        "title_name_config": "CONFIG DE NOMBRE",
        "title_theme_config": "CONFIG DE TEMA",
        "title_lang_config": "CONFIG DE IDIOMA",
        "title_api_config": "CONFIG DE API",
        "title_api_config_error": "ERROR CONFIG API",
        "theme_title": "SELECCIONAR TEMA DE COLOR",
        "theme_desc": "Elija un tema que coincida con la marca de su estación de trabajo:",
        "theme_prompt": "Elija tema [1-5]: ",
        "theme_classic": "(Clásico Retro)",
        "theme_blue_desc": "(Acento de marca en modo claro)",
        "theme_lime_desc": "(Acento de marca en modo oscuro)",
        "theme_neon_desc": "(Rosa caliente y Violeta)",
        "theme_amber_desc": "(Fósforo CRT monocromo)",
        "theme_apply_note": "El borde del cliente, los títulos y el arte del bacteriófago se adaptarán de inmediato.",
        "theme_applied_success": "TEMA APLICADO",
        "theme_changed_to": "Tema cambiado a",
        "initializing_workspace_styling": "Inicializando estilo del espacio de trabajo...",
        "onboarding_lang_prompt": "Elija idioma [1-4] (por defecto 1): ",
        "onboarding_theme_prompt": "Elija tema [1-5] (por defecto 3): ",
        "lang_select_title": "SELECT YOUR LANGUAGE / SELECCIONE IDIOMA",
        "lang_select_desc": "Seleccione su idioma de localización preferido:",
        "lang_choice_prompt": "Elija idioma [1-4]: ",
        "onboarding_offline_fallback": "Procediendo en modo Sandbox fuera de línea como: [brown]{username}[/brown]",
    },
    "fr": {
        "title_security_check": "CONTRÔLE DE SÉCURITÉ",
        "title_security_approved": "SÉCURITÉ APPROUVÉE",
        "title_access_denied": "ACCÈS REFUSÉ",
        "title_offline_mode": "MODE HORS LIGNE",
        "title_onboarding": "ASSISTANT DE CONFIGURATION",
        
        "welcome_banner": "» AUTHENTIFICATION SÉCURISÉE B2B",
        "welcome_desc": "Pour interagir with le moteur de prédiction génomique GoldBEAM,\nveuillez vous authentifier à l'aide de votre clé d'accès API.",
        "welcome_tip": "Générez votre clé sur: [underline cyan]swaev.com/#portal[/underline cyan]",
        "welcome_sandbox": "[bold white]Ou appuyez sur ENTRÉE avec une clé vide pour le Mode Sandbox Hors Ligne.[/bold white]",
        "prompt_key": "Saisissez votre clé X-API-Key: ",
        "verifying_key": "» VÉRIFICATION DE LA CLÉ D'ACCÈS...",
        "verifying_gateway": "Connexion à la passerelle de sécurité pour vérification...",
        
        "sandbox_title": "» CONFIGURATION DU PROFIL SANDBOX HORS LIGNE",
        "sandbox_desc": "Veuillez spécifier un nom d'utilisateur pour votre session\nsandbox locale hors ligne:",
        "prompt_username": "Entrez votre nom d'utilisateur: ",
        "offline_configured": "[bold green]✓[/bold green] PERFIL HORS LIGNE CONFIGURÉ",
        "welcome_local": "Bienvenue [brown]{username}[/brown] sur la station de travail locale SWAEV.",
        "init_sandbox": "Initialisation de l'espace de travail sandbox...",
        
        "auth_success": "[bold green]✓[/bold green] AUTHENTIFICATION RÉUSSIE",
        "welcome_back": "Ravi de vous revoir, [brown]{username}[/brown]!",
        "key_registered": "Votre clé API sécurisée a été enregistrée localement.",
        "invalid_token": "[bold red]✗[/bold red] Clé d'accès invalide. Veuillez vérifier et réessayer.",
        "gateway_unreachable": "[bold red]✗[/bold red] PASSERELLE INACCESSIBLE",
        "gateway_unreachable_desc": "Impossible de vérifier la clé car le serveur d'authentification est hors ligne.",
        
        
        "label_user": "Utilisateur",
        "label_tier": "Forfait",
        "label_mode": "Mode",
        "label_core": "Noyau",
        "status_active": "Actif",
        "status_online": "En ligne",
        "status_offline": "Hors ligne",
        "settings_title": "PARAMÈTRES UTILISATEUR",
        "settings_current_name": "Nom actuel",
        "settings_current_theme": "Thème actuel",
        "settings_current_lang": "Langue actuelle",
        "settings_api_conn": "Connexion API",
        "settings_current_fasta": "Dossier d'index FASTA",
        "settings_opt_name": "Modifier le nom du chercheur",
        "settings_opt_theme": "Modifier le thème de couleur",
        "settings_opt_lang": "Modifier la langue de localisation",
        "settings_opt_api": "Configurer la clé API / Connexion passerelle",
        "settings_opt_dirs": "Configurer les dossiers de travail",
        "settings_opt_back": "Retour à l'espace de travail",
        "settings_prompt": "Sélectionnez une option [1-6]: ",
        "settings_user_config_title": "CONFIG UTILISATEUR",
        "settings_online": "En ligne",
        "settings_offline": "Sandbox hors ligne",
        "title_dir_config": "CONFIG DOSSIERS",
        "dir_title": "CONFIGURER LES DOSSIERS DE TRAVAIL",
        "dir_desc": "Saisissez le dossier contenant vos fichiers FASTA. (ex. '.', './fasta')",
        "title_name_config": "CONFIG NOM",
        "title_theme_config": "CONFIG THÈME",
        "title_lang_config": "CONFIG LANGUE",
        "title_api_config": "CONFIG API",
        "title_api_config_error": "ERREUR CONFIG API",
        "theme_title": "SÉLECTIONNER LE THÈME DE COULEUR",
        "theme_desc": "Choisissez un thème qui correspond à l'image de votre station de travail:",
        "theme_prompt": "Choisissez le thème [1-5]: ",
        "theme_classic": "(Classique Rétro)",
        "theme_blue_desc": "(Accent de marque mode clair)",
        "theme_lime_desc": "(Accent de marque mode sombre)",
        "theme_neon_desc": "(Rose vif et Violet)",
        "theme_amber_desc": "(Phosphore CRT monochrome)",
        "theme_apply_note": "La bordure du client, les titres et l'art du bactériophage s'adapteront immédiatement.",
        "theme_applied_success": "THÈME APPLIQUÉ",
        "theme_changed_to": "Thème modifié en",
        "initializing_workspace_styling": "Initialisation du style de l'espace de travail...",
        "onboarding_lang_prompt": "Choisissez la langue [1-4] (par défaut 1): ",
        "onboarding_theme_prompt": "Choisissez le thème [1-5] (par défaut 3): ",
        "lang_select_title": "SELECT YOUR LANGUAGE / SELECCIONE IDIOMA",
        "lang_select_desc": "Sélectionnez votre langue de localisation préférée:",
        "lang_choice_prompt": "Choisissez la langue [1-4]: ",
        "onboarding_offline_fallback": "Poursuite en mode Sandbox hors ligne sous: [brown]{username}[/brown]",
    },
    "de": {
        "title_security_check": "SICHERHEITSPRÜFUNG",
        "title_security_approved": "ZUGRIFF ERLAUBT",
        "title_access_denied": "ZUGRIFF VERWEIGERT",
        "title_offline_mode": "OFFLINE-MODUS",
        "title_onboarding": "WILLKOMMENS-ASSISTENT",
        
        "welcome_banner": "» SICHERE B2B-AUTHENTIFIZIERUNG",
        "welcome_desc": "Um auf die GoldBEAM-Genomvorhersage-Engine zuzugreifen,\nauthentifizieren Sie sich bitte mit Ihrem sicheren API-Zugriffstoken.",
        "welcome_tip": "Erstellen Sie Ihren Schlüssel unter: [underline cyan]swaev.com/#portal[/underline cyan]",
        "welcome_sandbox": "[bold white]Oder drücken Sie EINGABE mit leerem Schlüssel für den Offline-Sandbox-Modus.[/bold white]",
        "prompt_key": "Fügen Sie Ihren X-API-Key ein: ",
        "verifying_key": "» ÜBERPRÜFE ÜBERGEBENEN SCHLÜSSEL...",
        "verifying_gateway": "Verbindung zum sicheren Gateway zur Autorisierung wird hergestellt...",
        
        "sandbox_title": "» OFFLINE-SANDBOX-PROFIL-EINRICHTUNG",
        "sandbox_desc": "Bitte geben Sie einen Forschernamen für Ihre lokale\nOffline-Sandbox-Arbeitsbereich-Sitzung ein:",
        "prompt_username": "Benutzername eingeben: ",
        "offline_configured": "[bold green]✓[/bold green] OFFLINE-PROFIL KONFIGUIERT",
        "welcome_local": "Willkommen [brown]{username}[/brown] an Ihrem lokalen SWAEV-Arbeitsplatz.",
        "init_sandbox": "Sandbox-Arbeitsbereich wird initialisiert...",
        
        "auth_success": "[bold green]✓[/bold green] AUTHENTIFIZIERUNG ERFOLGREICH",
        "welcome_back": "Willkommen zurück, [brown]{username}[/brown]!",
        "key_registered": "Ihr sicherer API-Schlüssel wurde lokal registriert.",
        "invalid_token": "[bold red]✗[/bold red] Ungültiges Zugriffstoken. Prüfen Sie den Schlüssel und versuchen Sie es erneut.",
        "gateway_unreachable": "[bold red]✗[/bold red] GATEWAY NICHT ERREICHBAR",
        "gateway_unreachable_desc": "Schlüsselprüfung nicht möglich, da der Authentifizierungsserver offline ist.",
        
        
        "label_user": "Benutzer",
        "label_tier": "Stufe",
        "label_mode": "Modus",
        "label_core": "Kern",
        "status_active": "Aktiv",
        "status_online": "Online",
        "status_offline": "Offline",
        "settings_title": "BENUTZER-EINSTELLUNGEN",
        "settings_current_name": "Aktueller Name",
        "settings_current_theme": "Aktuelles Theme",
        "settings_current_lang": "Aktuelle Sprache",
        "settings_api_conn": "API-Verbindung",
        "settings_current_fasta": "FASTA-Index-Ordner",
        "settings_opt_name": "Forschernamen ändern",
        "settings_opt_theme": "Farb-Theme ändern",
        "settings_opt_lang": "Lokalisierungssprache ändern",
        "settings_opt_api": "API-Schlüssel / Gateway-Verbindung konfigurieren",
        "settings_opt_dirs": "Arbeitsverzeichnisse konfigurieren",
        "settings_opt_back": "Zurück zum Arbeitsbereich",
        "settings_prompt": "Option auswählen [1-6]: ",
        "settings_user_config_title": "BENUTZERKONFIGURATION",
        "settings_online": "Online",
        "settings_offline": "Offline-Sandbox",
        "title_dir_config": "ORDNER-KONFIGURATION",
        "dir_title": "ARBEITSVERZEICHNISSE KONFIGURIEREN",
        "dir_desc": "Geben Sie den Ordner mit Ihren FASTA-Dateien ein. (z. B. '.', './fasta')",
        "title_name_config": "NAMENSKONFIGURATION",
        "title_theme_config": "THEMENKONFIGURATION",
        "title_lang_config": "SPRACHKONFIGURATION",
        "title_api_config": "API-KONFIGURATION",
        "title_api_config_error": "API-KONFIGURATION FEHLER",
        "theme_title": "FARB-THEME AUSWÄHLEN",
        "theme_desc": "Wählen Sie ein Theme, das zu Ihrem Arbeitsplatz-Branding passt:",
        "theme_prompt": "Theme wählen [1-5]: ",
        "theme_classic": "(Klassisches Retro)",
        "theme_blue_desc": "(Branded Light-Mode-Akzent)",
        "theme_lime_desc": "(Branded Dark-Mode-Akzent)",
        "theme_neon_desc": "(Hot Pink & Violett)",
        "theme_amber_desc": "(CRT-Phosphor einfarbig)",
        "theme_apply_note": "Der Client-Rand, die Titel und das Bakteriophagen-Design passen sich sofort an.",
        "theme_applied_success": "THEME ANGEWENDET",
        "theme_changed_to": "Theme geändert zu",
        "initializing_workspace_styling": "Arbeitsbereich-Styling wird initialisiert...",
        "onboarding_lang_prompt": "Sprache wählen [1-4] (Standard 1): ",
        "onboarding_theme_prompt": "Theme wählen [1-5] (Standard 3): ",
        "lang_select_title": "SELECT YOUR LANGUAGE / SELECCIONE IDIOMA"
    }
}

TRANSLATIONS_EXTENSION = {
    "en": {
        "bg_opt_title": "SWAEV Blue Theme Optimizer",
        "bg_opt_desc1": "SWAEV Blue is styled after the SWAEV website branding.",
        "bg_opt_desc2": "To ensure text is perfectly readable, please select your terminal background mode:",
        "bg_opt_dark": "Dark Background (converts body text to bright high-contrast colors)",
        "bg_opt_light": "Light/White Background (keeps body text as dark slate #0f172a)",
        "bg_prompt": "Choose background mode [1-2] (default 1): ",
        "dir_val_title": "Directory Validation",
        "dir_val_selected_fasta": "Selected FASTA Path: [bold cyan]{path}[/bold cyan]",
        "dir_val_exists": "[bold green]✓ Directory exists.[/bold green]",
        "dir_val_found_fasta": "[bold green]✓ Found {count} FASTA files inside.[/bold green]",
        "dir_val_not_exists": "[bold yellow]⚠ Directory does not exist yet (it will be created automatically).[/bold yellow]",
        "dir_val_empty_fasta": "[bold red]⚠ Contains 0 FASTA files currently.[/bold red]",
        "dir_val_confirm": "Confirm selection? (y/n, default y): ",
        "prompt_new_fasta_dir": "Enter new FASTA folder path (or ENTER to keep): ",
        "title_security_check": "SECURITY CHECK",
        "title_security_approved": "SECURITY APPROVED",
        "title_access_denied": "ACCESS DENIED",
        "title_offline_mode": "OFFLINE MODE",
        "predict_detached_clean": "\n[yellow]Genomic prediction worker detached. Goodbye![/yellow]",
    },
    "es": {
        "bg_opt_title": "Optimización del tema SWAEV Blue",
        "bg_opt_desc1": "SWAEV Blue está diseñado según la marca del sitio web SWAEV.",
        "bg_opt_desc2": "Para garantizar que el texto sea perfectamente legible, seleccione el modo de fondo de su terminal:",
        "bg_opt_dark": "Fondo oscuro (convierte el texto del cuerpo en colores brillantes de alto contraste)",
        "bg_opt_light": "Fondo claro/blanco (mantiene el texto del cuerpo como pizarra oscura #0f172a)",
        "bg_prompt": "Elija el modo de fondo [1-2] (predeterminado 1): ",
        "dir_val_title": "Validación de carpetas",
        "dir_val_selected_fasta": "Ruta FASTA seleccionada: [bold cyan]{path}[/bold cyan]",
        "dir_val_exists": "[bold green]✓ La carpeta existe.[/bold green]",
        "dir_val_found_fasta": "[bold green]✓ Se encontraron {count} archivos FASTA dentro.[/bold green]",
        "dir_val_not_exists": "[bold yellow]⚠ La carpeta aún no existe (se creará automáticamente).[/bold yellow]",
        "dir_val_empty_fasta": "[bold red]⚠ Actualmente contiene 0 archivos FASTA.[/bold red]",
        "dir_val_confirm": "¿Confirmar selección? (s/n, por defecto s): ",
        "prompt_new_fasta_dir": "Ingrese nueva ruta de carpeta FASTA (o ENTER para mantener): ",
        "title_security_check": "CONTROL DE SEGURIDAD",
        "title_security_approved": "SEGURIDAD APROBADA",
        "title_access_denied": "ACCESO DENEGADO",
        "title_offline_mode": "MODO SIN CONEXIÓN",
        "predict_detached_clean": "\n[yellow]Trabajador de predicción genómica desconectado. ¡Adiós![/yellow]",
    },
    "fr": {
        "bg_opt_title": "Optimiseur de thème SWAEV Blue",
        "bg_opt_desc1": "SWAEV Blue est conçu d'après la marque du site Web SWAEV.",
        "bg_opt_desc2": "Pour que le texte soit parfaitement lisible, veuillez sélectionner le mode de fond de votre terminal :",
        "bg_opt_dark": "Arrière-plan sombre (convertit le texte en couleurs vives à contraste élevé)",
        "bg_opt_light": "Arrière-plan clair/blanc (conserve le texte en gris foncé #0f172a)",
        "bg_prompt": "Choisissez le mode d'arrière-plan [1-2] (défaut 1) : ",
        "dir_val_title": "Validation du répertoire",
        "dir_val_selected_fasta": "Chemin FASTA sélectionné : [bold cyan]{path}[/bold cyan]",
        "dir_val_exists": "[bold green]✓ Le répertoire existe.[/bold green]",
        "dir_val_found_fasta": "[bold green]✓ Trouvé {count} fichiers FASTA à l'intérieur.[/bold green]",
        "dir_val_not_exists": "[bold yellow]⚠ Le répertoire n'existe pas encore (il sera créé automatiquement).[/bold yellow]",
        "dir_val_empty_fasta": "[bold red]⚠ Contient actuellement 0 fichier FASTA.[/bold red]",
        "dir_val_confirm": "Confirmer la sélection ? (y/n, défaut y) : ",
        "prompt_new_fasta_dir": "Entrez le nouveau chemin du dossier FASTA (ou ENTRÉE pour conserver) : ",
        "title_security_check": "CONTRÔLE DE SÉCURITÉ",
        "title_security_approved": "SÉCURITÉ APPROUVÉE",
        "title_access_denied": "ACCÈS REFUSÉ",
        "title_offline_mode": "MODE HORS LIGNE",
        "predict_detached_clean": "\n[yellow]Serveur de prédiction génomique détaché. Au revoir ![/yellow]",
    },
    "de": {
        "bg_opt_title": "SWAEV Blue Design-Optimierer",
        "bg_opt_desc1": "SWAEV Blue ist dem Branding der SWAEV-Website nachempfunden.",
        "bg_opt_desc2": "Um eine perfekte Lesbarkeit des Textes zu gewährleisten, wählen Sie bitte den Hintergrundmodus Ihres Terminals:",
        "bg_opt_dark": "Dunkler Hintergrund (konvertiert Fließtext in helle, kontrastreiche Farben)",
        "bg_opt_light": "Heller/Weißer Hintergrund (belässt Fließtext in dunklem Schiefer #0f172a)",
        "bg_prompt": "Hintergrundmodus wählen [1-2] (Standard 1): ",
        "dir_val_title": "Verzeichnis-Validierung",
        "dir_val_selected_fasta": "Ausgewählter FASTA-Pfad: [bold cyan]{path}[/bold cyan]",
        "dir_val_exists": "[bold green]✓ Verzeichnis existiert.[/bold green]",
        "dir_val_found_fasta": "[bold green]✓ {count} FASTA-Dateien darin gefunden.[/bold green]",
        "dir_val_not_exists": "[bold yellow]⚠ Verzeichnis existiert noch nicht (es wird automatisch erstellt).[/bold yellow]",
        "dir_val_empty_fasta": "[bold red]⚠ Enthält derzeit 0 FASTA-Dateien.[/bold red]",
        "dir_val_confirm": "Auswahl bestätigen? (y/n, Standard y): ",
        "prompt_new_fasta_dir": "Geben Sie den neuen FASTA-Ordnerpfad ein (oder EINGABETASTE zum Behalten): ",
        "predict_detached_clean": "\n[yellow]Genomischer Vorhersage-Worker getrennt. Auf Wiedersehen![/yellow]",
    }
}

for lang, keys_dict in TRANSLATIONS_EXTENSION.items():
    if lang in TRANSLATIONS:
        TRANSLATIONS[lang].update(keys_dict)

CURRENT_THEME = "multi_colour"
CURRENT_LANG = "en"


def t_style(style_key: str) -> str:
    """Returns the style color or tag for the given style key based on the current theme."""
    theme_dict = THEME_CONFIGS.get(CURRENT_THEME, THEME_CONFIGS["multi_colour"])
    return theme_dict.get(style_key, style_key)


def format_theme_style(text_str: str) -> str:
    """Replaces hardcoded colors with theme-specific colors dynamically."""
    sb = t_style("success_bold")
    s = t_style("success")
    eb = t_style("error_bold")
    e = t_style("error")
    wb = t_style("warning_bold")
    w = t_style("warning")
    pb = t_style("primary_bold")
    p = t_style("primary")
    tb = t_style("text_bold")
    txt = t_style("text")
    
    return (text_str
            .replace("[bold green]", f"[{sb}]")
            .replace("[/bold green]", f"[/{sb}]")
            .replace("[green]", f"[{s}]")
            .replace("[/green]", f"[/{s}]")
            .replace("[bold red]", f"[{eb}]")
            .replace("[/bold red]", f"[/{eb}]")
            .replace("[red]", f"[{e}]")
            .replace("[/red]", f"[/{e}]")
            .replace("[bold yellow]", f"[{wb}]")
            .replace("[/bold yellow]", f"[/{wb}]")
            .replace("[yellow]", f"[{w}]")
            .replace("[/yellow]", f"[/{w}]")
            .replace("[bold cyan]", f"[{pb}]")
            .replace("[/bold cyan]", f"[/{pb}]")
            .replace("[cyan]", f"[{p}]")
            .replace("[/cyan]", f"[/{p}]")
            .replace("[bold white]", f"[{tb}]")
            .replace("[/bold white]", f"[/{tb}]")
            .replace("[white]", f"[{txt}]")
            .replace("[/white]", f"[/{txt}]")
            )


def t(key: str, apply_theme: bool = True, **kwargs) -> str:
    """Returns the localized string for key using the active language."""
    lang_dict = TRANSLATIONS.get(CURRENT_LANG, TRANSLATIONS["en"])
    text_val = lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        text_val = text_val.format(**kwargs)
    if apply_theme:
        return format_theme_style(text_val)
    return text_val


def format_phage_style(art_str: str) -> str:
    """Replaces hardcoded rich styles in phage art with theme styles."""
    apb = t_style("art_primary_bold")
    ap = t_style("art_primary")
    alb = t_style("art_limbs_bold")
    
    return (art_str
            .replace("[bold cyan]", f"[{apb}]")
            .replace("[/bold cyan]", f"[/{apb}]")
            .replace("[dim cyan]", f"[{ap}]")
            .replace("[/dim cyan]", f"[/{ap}]")
            .replace("[bold white]", f"[{alb}]")
            .replace("[/bold white]", f"[/{alb}]")
            .replace("[bold red]", f"[{t_style('error_bold')}]")
            .replace("[/bold red]", f"[/{t_style('error_bold')}]")
            .replace("[bold green]", f"[{t_style('success_bold')}]")
            .replace("[/bold green]", f"[/{t_style('success_bold')}]")
            .replace("[bold yellow]", f"[{t_style('accent_bold')}]")
            .replace("[/bold yellow]", f"[/{t_style('accent_bold')}]")
            .replace("[bold magenta]", f"[{t_style('secondary_bold')}]")
            .replace("[/bold magenta]", f"[/{t_style('secondary_bold')}]")
            .replace("[dim]", f"[{t_style('secondary')}]")
            .replace("[/dim]", f"[/{t_style('secondary')}]")
            )

def update_theme_and_lang_globals(config: Dict[str, Any]):
    global CURRENT_THEME, CURRENT_LANG
    CURRENT_THEME = config.get("theme", "swaev_lime")
    CURRENT_LANG = config.get("language", "en")


# -----------------------------------------------------------------------------
# Terminal Wiping Utility (Wipes screen & scrollback buffer for single-phage rule)
# -----------------------------------------------------------------------------
def clear_screen_completely():
    """Clears the terminal screen and completely purges the scrollback buffer."""
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()


# -----------------------------------------------------------------------------
# Configuration & Local Storage
# -----------------------------------------------------------------------------
def load_config() -> Dict[str, Any]:
    config = {"api_url": DEFAULT_API_URL, "api_key": "", "username": "", "theme": "swaev_lime", "language": "en", "onboarded": False, "fasta_dir": ".", "terminal_background": "dark"}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                loaded = json.load(f)
                config.update(loaded)
        except Exception:
            pass
            
    # Auto-migration: replace stale/dev URLs with the stable custom domain
    _saved_url = config.get("api_url", "")
    if not _saved_url or "a.run.app" in _saved_url or "127.0.0.1" in _saved_url or "localhost" in _saved_url:
        config["api_url"] = DEFAULT_API_URL
        try:
            save_config(config)
        except Exception:
            pass

    # Apply dynamic Dual-Mode Slate/White Adapter for SWAEV Blue theme
    if config.get("terminal_background", "dark") == "light":
        THEME_CONFIGS["swaev_blue"]["text"] = "#0f172a"
        THEME_CONFIGS["swaev_blue"]["text_bold"] = "bold #0f172a"
    else:
        THEME_CONFIGS["swaev_blue"]["text"] = "white"
        THEME_CONFIGS["swaev_blue"]["text_bold"] = "bold white"
        
    return config


def save_config(config: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        console.print(f"[red]Failed to save configuration locally: {e}[/red]")


# -----------------------------------------------------------------------------
# Onboarding Preferences Wizard & Settings Menu
# -----------------------------------------------------------------------------
def run_onboarding_wizard(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stunning step-by-step onboarding preference configuration wizard for first launch.
    Collects Name, Language, Theme, and API access key with real-time feedback.
    """
    # Step 1: Language Selection (Instantly localizes subsequent steps!)
    clear_screen_completely()
    lang_content = [
        f"[bold cyan]» {t('lang_select_title')}[/bold cyan]",
        "",
        t("lang_select_desc"),
        "",
        "  [bold yellow][1][/bold yellow] English (UK/US)",
        "  [bold yellow][2][/bold yellow] Español (Spanish)",
        "  [bold yellow][3][/bold yellow] Français (French)",
        "  [bold yellow][4][/bold yellow] Deutsch (German)",
        "",
        "[dim]Subsequent screens will be translated into your chosen language.[/dim]"
    ]
    header_group = Group(*lang_content)
    choice = animated_input(t("onboarding_lang_prompt"), state="typing", header_renderable=header_group, main_title=t("title_onboarding"), single_char=True)
    
    lang = "en"
    if choice == "2":
        lang = "es"
    elif choice == "3":
        lang = "fr"
    elif choice == "4":
        lang = "de"
        
    config["language"] = lang
    global CURRENT_LANG
    CURRENT_LANG = lang

    # Step 2: Username Input
    clear_screen_completely()
    user_content = [
        f"[bold yellow]» {t('sandbox_title')}[/bold yellow]",
        "",
        t("sandbox_desc"),
        ""
    ]
    header_group = Group(*user_content)
    username = animated_input(t("prompt_username"), state="idle", header_renderable=header_group, main_title=t("title_onboarding"))
    if not username:
        username = "Sandbox User"
    config["username"] = username
    USER_STATE["name"] = username

    # Step 3: Theme Selection
    theme_error = ""
    while True:
        clear_screen_completely()
        theme_content = [
            f"[bold yellow]» {t('theme_title')}[/bold yellow]",
            "",
            t("theme_desc"),
            "",
            f"  [bold yellow][1][/bold yellow] [bold cyan]Multi Colour[/bold cyan] {t('theme_classic')}",
            f"  [bold yellow][2][/bold yellow] [bold #0ea5e9]SWAEV Blue[/bold #0ea5e9] {t('theme_blue_desc')}",
            f"  [bold yellow][3][/bold yellow] [bold chartreuse1]SWAEV Lime[/bold chartreuse1] {t('theme_lime_desc')}",
            f"  [bold yellow][4][/bold yellow] [bold hot_pink]Cyberpunk Neon[/bold hot_pink] {t('theme_neon_desc')}",
            f"  [bold yellow][5][/bold yellow] [bold orange3]Retro Amber[/bold orange3] {t('theme_amber_desc')}",
            "",
            f"[dim]{t('theme_apply_note')}[/dim]"
        ]
        header_group = Group(*theme_content)
        theme_choice = animated_input(t("onboarding_theme_prompt"), state="idle", header_renderable=header_group, main_title=t("title_onboarding"), error_msg=theme_error, single_char=True)
        
        theme_map = {
            "1": "multi_colour",
            "2": "swaev_blue",
            "3": "swaev_lime",
            "4": "cyberpunk_neon",
            "5": "retro_amber"
        }
        
        selected_theme_key = theme_map.get(theme_choice, "swaev_lime") if theme_choice else "swaev_lime"
        config["theme"] = selected_theme_key
        
        # SWAEV Blue Background Optimization Prompt
        if selected_theme_key == "swaev_blue":
            clear_screen_completely()
            bg_content = [
                f"[bold yellow]» {t('bg_opt_title')}[/bold yellow]",
                "",
                t('bg_opt_desc1'),
                t('bg_opt_desc2'),
                "",
                f"  [bold yellow][1][/bold yellow] {t('bg_opt_dark')}",
                f"  [bold yellow][2][/bold yellow] {t('bg_opt_light')}",
                ""
            ]
            bg_choice = animated_input(t('bg_prompt'), state="idle", header_renderable=Group(*bg_content), main_title="BACKGROUND CONFIG", single_char=True)
            if bg_choice == "2":
                config["terminal_background"] = "light"
            else:
                config["terminal_background"] = "dark"
                
        # Re-load config to apply overrides
        if config.get("terminal_background", "dark") == "light":
            THEME_CONFIGS["swaev_blue"]["text"] = "#0f172a"
            THEME_CONFIGS["swaev_blue"]["text_bold"] = "bold #0f172a"
        else:
            THEME_CONFIGS["swaev_blue"]["text"] = "white"
            THEME_CONFIGS["swaev_blue"]["text_bold"] = "bold white"
            
        global CURRENT_THEME
        CURRENT_THEME = selected_theme_key
        
        # Flash a quick preview success
        clear_screen_completely()
        preview_content = [
            f"[bold green]✓ {t('theme_applied_success')}[/bold green]",
            "",
            f"{t('theme_changed_to')}: [brown]{THEME_CONFIGS[selected_theme_key]['name']}[/brown]",
            THEME_CONFIGS[selected_theme_key]["desc"],
            "",
            t("initializing_workspace_styling")
        ]
        grid = build_dashboard_grid("success", 0, Group(*preview_content), border_style="green", main_title=t("title_onboarding"))
        console.print(grid)
        time.sleep(1.5)
        break

    # Step 4: API Key Setup & Verification
    api_error = ""
    while True:
        clear_screen_completely()
        api_content = [
            f"[bold yellow]» {t('welcome_banner')}[/bold yellow]",
            "",
            t("welcome_desc"),
            "",
            t("welcome_tip"),
            "",
            t("welcome_sandbox"),
            ""
        ]
        if config.get("api_key"):
            api_content.append(f"[bold green]✓ Stored API Key detected ({config['api_key'][:4]}...{config['api_key'][-4:]})[/bold green]")
            api_content.append("[bold white]Press ENTER without typing to keep your existing key.[/bold white]")
            api_content.append("")
            
        header_group = Group(*api_content)
        key = animated_input(t("prompt_key"), state="warning", header_renderable=header_group, main_title=t("title_onboarding"), error_msg=api_error)
        
        if not key:
            if config.get("api_key"):
                key = config["api_key"]
            else:
                config["api_key"] = ""
                USER_STATE["name"] = config["username"]
                USER_STATE["subscription_tier"] = "sandbox"
                USER_STATE["online"] = False
                
                clear_screen_completely()
                success_content = [
                    f"[bold green]✓ {t('offline_configured')}[/bold green]",
                    "",
                    t("welcome_local", username=config["username"]),
                    t("init_sandbox")
                ]
                grid = build_dashboard_grid("success", 0, Group(*success_content), border_style="green", main_title=t("title_onboarding"))
                console.print(grid)
                time.sleep(1.5)
                break
                
        # Paste a key - let's verify it!
        clear_screen_completely()
        verifying_content = [
            f"[bold cyan]» {t('verifying_key')}[/bold cyan]",
            "",
            t("verifying_gateway")
        ]
        grid = build_dashboard_grid("processing", 0, Group(*verifying_content), main_title=t("title_security_check"))
        console.print(grid)
        
        status = verify_and_register_key(key, config)
        if status == "success":
            config["api_key"] = key
            config["username"] = USER_STATE["name"]
            
            clear_screen_completely()
            success_content = [
                f"[bold green]✓ {t('auth_success')}[/bold green]",
                "",
                t("welcome_back", username=USER_STATE["name"]),
                t("key_registered")
            ]
            grid = build_dashboard_grid("success", 0, Group(*success_content), border_style="green", main_title=t("title_onboarding"))
            console.print(grid)
            time.sleep(1.5)
            break
        elif status == "invalid":
            api_error = t("invalid_token")
            continue
        else:
            # Offline gateway unreachable
            clear_screen_completely()
            offline_unreachable_content = [
                f"[bold red]✗ {t('gateway_unreachable')}[/bold red]",
                "",
                t("gateway_unreachable_desc"),
                "",
                t("onboarding_offline_fallback", username=config['username'])
            ]
            config["api_key"] = ""
            USER_STATE["name"] = config["username"]
            USER_STATE["subscription_tier"] = "sandbox"
            USER_STATE["online"] = False
            
            grid = build_dashboard_grid("warning", 0, Group(*offline_unreachable_content), border_style="yellow", main_title=t("title_onboarding"))
            console.print(grid)
            time.sleep(2.5)
            break

    return config


def run_settings_menu(config: Dict[str, Any]) -> None:
    """
    Provides an interactive user preferences dashboard within the sequence browser loop.
    Allows changing Name, Theme, Language, and API Keys at any time with live previews.
    """
    while True:
        clear_screen_completely()
        
        # Dynamically align parameter colons across languages
        p_name = t('settings_current_name', apply_theme=False) + ":"
        p_theme = t('settings_current_theme', apply_theme=False) + ":"
        p_lang = t('settings_current_lang', apply_theme=False) + ":"
        p_conn = t('settings_api_conn', apply_theme=False) + ":"
        p_fasta = t('settings_current_fasta', apply_theme=False) + ":"
        
        max_len = max(len(p_name), len(p_theme), len(p_lang), len(p_conn), len(p_fasta))
        
        pad_name = p_name.ljust(max_len)
        pad_theme = p_theme.ljust(max_len)
        pad_lang = p_lang.ljust(max_len)
        pad_conn = p_conn.ljust(max_len)
        pad_fasta = p_fasta.ljust(max_len)
        
        settings_content = [
            f"[bold yellow]» {t('settings_title')}[/bold yellow]",
            "",
            f"  {format_theme_style(pad_name)}  [brown]{config.get('username')}[/brown]",
            f"  {format_theme_style(pad_theme)}  [brown]{THEME_CONFIGS.get(config.get('theme'), {}).get('name', 'Classic')}[/brown]",
            f"  {format_theme_style(pad_lang)}  [brown]{config.get('language', 'en').upper()}[/brown]",
            f"  {format_theme_style(pad_conn)}  [brown]{t('settings_online') if USER_STATE.get('online') else t('settings_offline')}[/brown]",
            f"  {format_theme_style(pad_fasta)}  [brown]{config.get('fasta_dir', '.')}[/brown]",
            "",
            f"  [bold yellow][1][/bold yellow] {t('settings_opt_name')}",
            f"  [bold yellow][2][/bold yellow] {t('settings_opt_theme')}",
            f"  [bold yellow][3][/bold yellow] {t('settings_opt_lang')}",
            f"  [bold yellow][4][/bold yellow] {t('settings_opt_api')}",
            f"  [bold yellow][5][/bold yellow] {t('settings_opt_dirs')}",
            f"  [bold yellow][6][/bold yellow] {t('settings_opt_back')}",
            ""
        ]
        header_group = Group(*settings_content)
        choice = animated_input(t("settings_prompt"), state="idle", header_renderable=header_group, main_title=t("settings_user_config_title"), single_char=True)
        
        if choice == "1":
            clear_screen_completely()
            name_content = [
                f"[bold yellow]» {t('sandbox_title')}[/bold yellow]",
                "",
                t("sandbox_desc"),
                ""
            ]
            header_group = Group(*name_content)
            new_name = animated_input(t("prompt_username"), state="typing", header_renderable=header_group, main_title=t("title_name_config"))
            if new_name:
                config["username"] = new_name
                save_config(config)
                USER_STATE["name"] = new_name
                
        elif choice == "2":
            clear_screen_completely()
            theme_content = [
                f"[bold yellow]» {t('theme_title')}[/bold yellow]",
                "",
                t("theme_desc"),
                "",
                f"  [bold yellow][1][/bold yellow] [bold cyan]Multi Colour[/bold cyan] {t('theme_classic')}",
                f"  [bold yellow][2][/bold yellow] [bold #0ea5e9]SWAEV Blue[/bold #0ea5e9] {t('theme_blue_desc')}",
                f"  [bold yellow][3][/bold yellow] [bold chartreuse1]SWAEV Lime[/bold chartreuse1] {t('theme_lime_desc')}",
                f"  [bold yellow][4][/bold yellow] [bold hot_pink]Cyberpunk Neon[/bold hot_pink] {t('theme_neon_desc')}",
                f"  [bold yellow][5][/bold yellow] [bold orange3]Retro Amber[/bold orange3] {t('theme_amber_desc')}",
                ""
            ]
            header_group = Group(*theme_content)
            theme_choice = animated_input(t("theme_prompt"), state="idle", header_renderable=header_group, main_title=t("title_theme_config"), single_char=True)
            theme_map = {
                "1": "multi_colour",
                "2": "swaev_blue",
                "3": "swaev_lime",
                "4": "cyberpunk_neon",
                "5": "retro_amber"
            }
            if theme_choice in theme_map:
                selected_theme_key = theme_map[theme_choice]
                config["theme"] = selected_theme_key
                if selected_theme_key == "swaev_blue":
                    clear_screen_completely()
                    bg_content = [
                        f"[bold yellow]» {t('bg_opt_title')}[/bold yellow]",
                        "",
                        t('bg_opt_desc1'),
                        t('bg_opt_desc2'),
                        "",
                        f"  [bold yellow][1][/bold yellow] {t('bg_opt_dark')}",
                        f"  [bold yellow][2][/bold yellow] {t('bg_opt_light')}",
                        ""
                    ]
                    bg_choice = animated_input(t('bg_prompt'), state="idle", header_renderable=Group(*bg_content), main_title="BACKGROUND CONFIG", single_char=True)
                    if bg_choice == "2":
                        config["terminal_background"] = "light"
                    else:
                        config["terminal_background"] = "dark"
                save_config(config)
                # Re-load config to apply overrides
                config = load_config()
                global CURRENT_THEME
                CURRENT_THEME = selected_theme_key
                
        elif choice == "3":
            clear_screen_completely()
            lang_content = [
                f"[bold cyan]» {t('lang_select_title')}[/bold cyan]",
                "",
                t("lang_select_desc"),
                "",
                "  [bold yellow][1][/bold yellow] English (UK/US)",
                "  [bold yellow][2][/bold yellow] Español (Spanish)",
                "  [bold yellow][3][/bold yellow] Français (French)",
                "  [bold yellow][4][/bold yellow] Deutsch (German)",
                ""
            ]
            header_group = Group(*lang_content)
            lang_choice = animated_input(t("lang_choice_prompt"), state="typing", header_renderable=header_group, main_title=t("title_lang_config"), single_char=True)
            lang_map = {"1": "en", "2": "es", "3": "fr", "4": "de"}
            if lang_choice in lang_map:
                selected_lang = lang_map[lang_choice]
                config["language"] = selected_lang
                save_config(config)
                global CURRENT_LANG
                CURRENT_LANG = selected_lang
                
        elif choice == "4":
            clear_screen_completely()
            api_content = [
                f"[bold yellow]» {t('welcome_banner')}[/bold yellow]",
                "",
                t("welcome_desc"),
                "",
                t("welcome_tip"),
                "",
                t("welcome_sandbox"),
                ""
            ]
            header_group = Group(*api_content)
            key = animated_input(t("prompt_key"), state="warning", header_renderable=header_group, main_title=t("title_api_config"))
            if key is not None:
                clear_screen_completely()
                verifying_content = [
                    f"[bold cyan]» {t('verifying_key')}[/bold cyan]",
                    "",
                    t("verifying_gateway")
                ]
                grid = build_dashboard_grid("processing", 0, Group(*verifying_content), main_title=t("title_security_check"))
                console.print(grid)
                
                status = verify_and_register_key(key, config)
                if status == "success":
                    config["api_key"] = key
                    config["username"] = USER_STATE["name"]
                    save_config(config)
                elif status == "invalid":
                    clear_screen_completely()
                    grid = build_dashboard_grid("error", 0, t("invalid_token"), border_style="red", main_title=t("title_api_config_error"))
                    console.print(grid)
                    time.sleep(2.0)
                else:
                    clear_screen_completely()
                    offline_unreachable_content = [
                        f"[bold red]✗ {t('gateway_unreachable')}[/bold red]",
                        "",
                        t("gateway_unreachable_desc")
                    ]
                    config["api_key"] = ""
                    save_config(config)
                    USER_STATE["name"] = config["username"]
                    USER_STATE["subscription_tier"] = "sandbox"
                    USER_STATE["online"] = False
                    grid = build_dashboard_grid("warning", 0, Group(*offline_unreachable_content), border_style="yellow", main_title=t("title_api_config"))
                    console.print(grid)
                    time.sleep(2.0)
                    
        elif choice == "5":
            clear_screen_completely()
            dir_content = [
                f"[bold yellow]» {t('dir_title')}[/bold yellow]",
                "",
                t("dir_desc"),
                "",
                f"  FASTA Folder   : [brown]{config.get('fasta_dir', '.')}[/brown]",
                ""
            ]
            header_group = Group(*dir_content)
            new_fasta_dir = animated_input(t("prompt_new_fasta_dir"), state="typing", header_renderable=header_group, main_title=t("title_dir_config"))
            if new_fasta_dir:
                has_dir = os.path.isdir(new_fasta_dir)
                num_fasta = 0
                if has_dir:
                    try:
                        num_fasta = len(scan_fasta_files(new_fasta_dir))
                    except Exception:
                        pass
                
                clear_screen_completely()
                val_content = [
                    f"[bold yellow]» {t('dir_val_title')}[/bold yellow]",
                    "",
                    t('dir_val_selected_fasta', path=new_fasta_dir),
                    ""
                ]
                if has_dir:
                    val_content.append(t('dir_val_exists'))
                    val_content.append(t('dir_val_found_fasta', count=num_fasta))
                else:
                    val_content.append(t('dir_val_not_exists'))
                    val_content.append(t('dir_val_empty_fasta'))
                val_content.append("")
                
                confirm_choice = animated_input(t('dir_val_confirm'), state="typing", header_renderable=Group(*val_content), main_title="CONFIRM PATH")
                if confirm_choice.lower() != "n":
                    config["fasta_dir"] = new_fasta_dir
                    os.makedirs(new_fasta_dir, exist_ok=True)
                    save_config(config)
                
        elif choice == "6" or not choice:
            break


# Global user state for premium visualizations
USER_STATE = {
    "name": "Anonymous",
    "email": "offline@swaev.com",
    "subscription_tier": "sandbox",
    "megabase_limit": 1.0,
    "megabases_used": 0.0,
    "concurrent_limit": 1,
    "active_jobs": 0,
    "online": False
}

# Stores metadata about the last loaded sequence for cross-function access
_LAST_SEQUENCE_INFO: Dict[str, Any] = {"filename": "", "path": "", "tokens": []}


def fetch_user_usage(config: Dict[str, Any]) -> None:
    """
    Attempts to retrieve current user parameters and limits from the gateway.
    Falls back to configured/offline sandbox values on connection failure.
    """
    api_url = config.get("api_url", DEFAULT_API_URL)
    api_key = config.get("api_key")
    
    if not api_key:
        USER_STATE["name"] = config.get("username", "Offline Sandbox")
        USER_STATE["online"] = False
        return
    
    try:
        response = requests.get(
            f"{api_url}/v1/user/usage",
            headers={"X-API-Key": api_key},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            local_user = config.get("username")
            USER_STATE.update({
                "name": local_user if local_user else data.get("name", "Unknown Scientist"),
                "email": data.get("email", ""),
                "subscription_tier": data.get("subscription_tier", "sandbox"),
                "megabase_limit": float(data.get("megabase_limit", 1.0)),
                "megabases_used": float(data.get("megabases_used", 0.0)),
                "concurrent_limit": int(data.get("concurrent_limit", 1)),
                "active_jobs": int(data.get("active_jobs", 0)),
                "online": True
            })
        else:
            USER_STATE["name"] = config.get("username", "Offline Sandbox")
            USER_STATE["online"] = False
    except Exception:
        USER_STATE["name"] = config.get("username", "Offline Sandbox")
        USER_STATE["online"] = False


def verify_and_register_key(api_key: str, config: Dict[str, Any]) -> str:
    """
    Validates an API key against the gateway `/v1/user/usage` endpoint.
    If valid, updates USER_STATE and returns "success".
    If invalid (401/403/404), returns "invalid".
    If unreachable/offline, returns "offline".
    """
    api_url = config.get("api_url", DEFAULT_API_URL)
    try:
        response = requests.get(
            f"{api_url}/v1/user/usage",
            headers={"X-API-Key": api_key},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            local_user = config.get("username")
            USER_STATE.update({
                "name": local_user if local_user else data.get("name", "Unknown Scientist"),
                "email": data.get("email", ""),
                "subscription_tier": data.get("subscription_tier", "sandbox"),
                "megabase_limit": float(data.get("megabase_limit", 1.0)),
                "megabases_used": float(data.get("megabases_used", 0.0)),
                "concurrent_limit": int(data.get("concurrent_limit", 1)),
                "active_jobs": int(data.get("active_jobs", 0)),
                "online": True
            })
            return "success"
        elif response.status_code in (401, 403, 404):
            USER_STATE["online"] = False
            return "invalid"
        else:
            USER_STATE["online"] = False
            return "offline"
    except Exception:
        USER_STATE["online"] = False
        return "offline"


# -----------------------------------------------------------------------------
# Phage ASCII Frames & State Machinery
# -----------------------------------------------------------------------------
def is_friday_after_5() -> bool:
    now = datetime.now()
    return now.weekday() == 4 and now.hour >= 17


def make_head_line(head_char: str, style: str = "bold cyan") -> str:
    """
    Mathematically centers the eye characters precisely within a 7-character head interior.
    This guarantees that the head is centered and completely jitter-free.
    """
    target_len = 7
    char_len = len(head_char)
    if char_len >= target_len:
        interior = f"[{style}]{head_char}[/{style}]"
    else:
        left_pad = (target_len - char_len) // 2
        right_pad = target_len - char_len - left_pad
        interior = " " * left_pad + f"[{style}]{head_char}[/{style}]" + " " * right_pad
        
    return f"   [{style}]|[/{style}]{interior}[{style}]|[/{style}]   "


def _get_phage_art_raw(state: str, frame: int = 0) -> str:
    """
    Returns specific, highly-polished bacteriophage ASCII states.
    Available states: 'idle', 'zoom', 'weights', 'typing', 'victory', 'sleep', 'success', 'error', 'processing', 'warning', 'land_compress', 'land_stretch'
    Every single frame is mathematically aligned to exactly 15 characters wide and 8 lines high.
    This guarantees zero horizontal and vertical layout jitter.
    """
    # Capsid eyes depending on the state
    head_char = "o o"
    if state == "success":
        head_char = "> v <"
    elif state == "error":
        head_char = "x x"  # Dizzy/crossed eyes for error state
    elif state == "processing":
        head_char = "o ."  # Puzzled/thinking eyes for processing state
    elif state == "warning":
        head_char = "@ @"
    elif state == "land_compress":
        if frame == 0:
            head_char = "> <"
        else:
            head_char = "o o"
    
    # Idle, Dancing & Thinking Blink & Wink override
    if state in ["idle", "dancing", "thinking"]:
        if state == "thinking":
            if frame % 16 == 8:  # Smooth blink interval while thinking
                head_char = "- -"
            else:
                head_char = "o o"
        else:
            if frame % 128 == 64:  # Rare easter egg wink
                head_char = "o -"
            elif frame % 24 == 12:  # Regular blink less frequent
                head_char = "- -"
            else:
                head_char = "o o"

    # Easter Egg check
    if is_friday_after_5():
        state = "sleep"

    if state in ["idle", "dancing", "success", "error", "processing", "warning", "thinking"]:
        head_line = make_head_line(head_char, "bold cyan")
        
        # Resolve the active walking/dancing limb fiber styling (The Phage Dance)
        if state in ("idle", "thinking"):
            legs_line = "    [bold white]/ / \\ \\ [/bold white]   "
        else:
            if frame % 3 == 0:
                legs_line = "    [bold white]/ / \\ \\ [/bold white]   "
            elif frame % 3 == 1:
                legs_line = "    [bold white]/ | | \\ [/bold white]   "
            else:
                legs_line = "    [bold white]\\ \\ / / [/bold white]   "
            
        # Bob up (alternating frames) or bob down inside the constant 8-line boundary
        if state == "thinking":
            dots_frames = [
                "       .       ",
                "      . .      ",
                "     . . .     ",
                "               "
            ]
            dots_line = dots_frames[frame % 4]
            lines = [
                dots_line,
                "     [bold cyan]_____[/bold cyan]     ",
                "    [bold cyan]/     \\ [/bold cyan]   ",
                head_line,
                "    [bold cyan]\\_____/[/bold cyan]    ",
                "       [bold white]|[/bold white]       ",
                "     [bold white]--|--[/bold white]     ",
                legs_line
            ]
        else:
            if frame % 2 == 1: # Bob up
                lines = [
                    "     [bold cyan]_____[/bold cyan]     ",
                    "    [bold cyan]/     \\ [/bold cyan]   ",
                    head_line,
                    "    [bold cyan]\\_____/[/bold cyan]    ",
                    "       [bold white]|[/bold white]       ",
                    "     [bold white]--|--[/bold white]     ",
                    legs_line,
                    "               "
                ]
            else: # Bob down / land
                lines = [
                    "               ",
                    "     [bold cyan]_____[/bold cyan]     ",
                    "    [bold cyan]/     \\ [/bold cyan]   ",
                    head_line,
                    "    [bold cyan]\\_____/[/bold cyan]    ",
                    "       [bold white]|[/bold white]       ",
                    "     [bold white]--|--[/bold white]     ",
                    legs_line
                ]
        return "\n".join(lines)

    elif state == "land_compress":
        head_line = make_head_line(head_char, "bold cyan")
        lines = [
            "               ",
            "               ",
            "     [bold cyan]_____[/bold cyan]     ",
            "    [bold cyan]/     \\ [/bold cyan]   ",
            head_line,
            "    [bold cyan]\\_____/[/bold cyan]    ",
            "     [bold white]--|--[/bold white]     ",
            "   [bold white]/_/   \\_\\ [/bold white]  "
        ]
        return "\n".join(lines)

    elif state == "land_stretch":
        head_line = make_head_line(head_char, "bold cyan")
        lines = [
            "     [bold cyan]_____[/bold cyan]     ",
            "    [bold cyan]/     \\ [/bold cyan]   ",
            head_line,
            "    [bold cyan]\\_____/[/bold cyan]    ",
            "       [bold white]|[/bold white]       ",
            "       [bold white]|[/bold white]       ",
            "     [bold white]--|--[/bold white]     ",
            "    [bold white]/ / \\ \\ [/bold white]   "
        ]
        return "\n".join(lines)

    elif state == "sleep":
        # Snoozing state has static u u eyes and rising zZ snoring particles flowing outward!
        snore_head_char = "u u"
        head_line = make_head_line(snore_head_char, "dim cyan")
        
        # Rising zZ snoring particles flowing outward at line index 0 (15 characters wide)
        if frame % 3 == 0:
            snore_particles = "        [bold yellow]z[/bold yellow]      "
        elif frame % 3 == 1:
            snore_particles = "          [bold yellow]zZ[/bold yellow]   "
        else:
            snore_particles = "            [bold yellow]~zZ[/bold yellow]"
            
        # Keep the phage completely still while snoozing to prevent vertical jumping
        lines = [
            snore_particles,
            "     [dim cyan]_____[/dim cyan]     ",
            "    [dim cyan]/     \\ [/dim cyan]   ",
            head_line,
            "    [dim cyan]\\_____/[/dim cyan]    ",
            "       [dim]|[/dim]       ",
            "     [dim]--|--[/dim]     ",
            "    [dim]/ / \\ \\ [/dim]    "
        ]
        return "\n".join(lines)

    elif state == "zoom":
        if frame == 0:
            lines = [
                "               ",
                "               ",
                "               ",
                "               ",
                "               ",
                "               ",
                "       [bold cyan].[/bold cyan]       ",
                "      [bold white]/|\\ [/bold white]     "
            ]
        elif frame == 1:
            lines = [
                "               ",
                "               ",
                "               ",
                "      [bold cyan]___[/bold cyan]      ",
                "     [bold cyan]|o o|[/bold cyan]     ",
                "     [bold cyan]\\___/[/bold cyan]     ",
                "       [bold white]|[/bold white]       ",
                "      [bold white]/ \\ [/bold white]     "
            ]
        else:
            lines = [
                "               ",
                "     [bold cyan]_____[/bold cyan]     ",
                "    [bold cyan]/     \\ [/bold cyan]   ",
                "   [bold cyan]|  o o  |[/bold cyan]   ",
                "    [bold cyan]\\_____/[/bold cyan]    ",
                "       [bold white]|[/bold white]       ",
                "     [bold white]--|--[/bold white]     ",
                "    [bold white]/ / \\ \\ [/bold white]   "
            ]
        return "\n".join(lines)

    elif state == "weights":
        if frame % 2 == 0:
            # Lifted UP: Head & body are perfectly anchored and centered.
            # Arms extend outwards and upwards to hold the barbell above the head without crossing head boundaries.
            lines = [
                " [bold red]O===========O[/bold red] ",
                "  \\  [bold cyan]_____[/bold cyan]  /  ",
                "   \\\\[bold cyan]/     \\\\[/bold cyan]/   ",
                "   [bold cyan]|  > <  |[/bold cyan]   ",
                "    [bold cyan]\\_____/[/bold cyan]    ",
                "       [bold white]|[/bold white]       ",
                "     [bold white]--|--[/bold white]     ",
                "    [bold white]/ / \\ \\ [/bold white]   "
            ]
        else:
            # Resting DOWN: Barbell rests at shoulder level.
            lines = [
                "               ",
                "     [bold cyan]_____[/bold cyan]     ",
                "    [bold cyan]/     \\ [/bold cyan]   ",
                "   [bold cyan]|  u u  |[/bold cyan]   ",
                "    [bold cyan]\\_____/[/bold cyan]    ",
                "       [bold white]|[/bold white]       ",
                " [bold green]O===--|--===O[/bold green] ",
                "    [bold white]/ / \\ \\ [/bold white]   "
            ]
        return "\n".join(lines)

    elif state == "typing":
        arm_line = "     --|--     " if frame % 2 == 0 else "     /\\|/\\     "
        lines = [
            "               ",
            "     [bold cyan]_____[/bold cyan]     ",
            "    [bold cyan]/     \\ [/bold cyan]   ",
            "   [bold cyan]|  u u  |[/bold cyan]   ",
            "    [bold cyan]\\_____/[/bold cyan]    ",
            "       [bold white]|[/bold white]       ",
            f"[bold white]{arm_line}[/bold white]",
            "    [bold white]/ / \\ \\ [/bold white]   "
        ]
        return "\n".join(lines)

    elif state == "victory":
        if frame % 2 == 0:
            lines = [
                " [bold yellow]*[/bold yellow]  [bold magenta]A[/bold magenta]  [bold cyan]*[/bold cyan]  [bold green]T[/bold green]  [bold yellow]*[/bold yellow] ",
                "  \\ [bold cyan]_____[/bold cyan] /   ",
                "   \\ [bold cyan]/     \\ [/bold cyan]/  ",
                "  [bold cyan]|  ^ ^  |[/bold cyan]   ",
                "   [bold cyan]\\_____/[/bold cyan]    ",
                "      [bold white]|[/bold white]       ",
                "    [bold white]\\--|--/[/bold white]    ",
                "    [bold white]/ / \\ \\ [/bold white]   "
            ]
        else:
            lines = [
                " [bold green]*[/bold green]  [bold yellow]G[/bold yellow]  [bold magenta]*[/bold magenta]  [bold cyan]C[/bold cyan]  [bold green]*[/bold green] ",
                "     [bold cyan]_____[/bold cyan]     ",
                "    [bold cyan]/     \\ [/bold cyan]   ",
                "   [bold cyan]|  > <  |[/bold cyan]   ",
                "    [bold cyan]\\_____/[/bold cyan]    ",
                "       [bold white]|[/bold white]       ",
                "    [bold white]\\--|--/[/bold white]    ",
                "    [bold white]\\ \\ / /[/bold white]    "
            ]
        return "\n".join(lines)

    return ""


def get_phage_art(state: str, frame: int = 0) -> str:
    """Wraps _get_phage_art_raw with format_phage_style to support custom themes."""
    raw_art = _get_phage_art_raw(state, frame)
    return format_phage_style(raw_art)


def get_dna_horizontal_line(width: int) -> Text:
    """Generates a basic, premium horizontal divider line that goes across the terminal."""
    return Text("─" * width, style=f"dim {t_style('text')}")


def build_dashboard_grid(state: str, frame: int, main_content: Any, border_style: str = "cyan", main_title: str = "WORKSPACE", anchor_bottom: bool = False) -> Table:
    """
    Constructs a premium, left-aligned, side-by-side terminal dashboard using Table grid.
    The panels fill the terminal height; the phage sidebar is hidden on narrow
    terminals so the workspace keeps a usable width.

    anchor_bottom: when the workspace content is taller than the panel, keep its
    last lines (e.g. an input prompt) visible instead of its first lines.
    """
    width, height = console.size
    safe_width = max(20, width - 2)
    show_sidebar = safe_width >= 64

    # Header + divider take 2 rows; leave 1 row so Live/print never scrolls
    panel_height = max(8, height - 3)
    
    # 1. Resolve default border style using the active theme
    if border_style == "cyan":
        border_style = t_style("border")
        
    # 2. Phage core art (exactly 8 lines)
    phage_art = get_phage_art(state, frame)
    
    # 3. Dynamic status text under phage to fit panel_height precisely without expanding it
    inner_height = panel_height - 2
    phage_height = 8
    status_budget = inner_height - phage_height  # How many lines we can use for status
    
    status_text = Text()
    status_lines = []
    
    # Translate and format sidebar stats
    user_name_disp = USER_STATE.get("name", "Sarah Jenkins")
    if len(user_name_disp) > 11:
        user_name_disp = user_name_disp[:10] + "…"
    
    tier_disp = USER_STATE.get("subscription_tier", "sandbox").upper()
    if len(tier_disp) > 11:
        tier_disp = tier_disp[:10] + "…"
        
    is_online = USER_STATE.get("online", False)
    mode_disp = t("status_online", apply_theme=False) if is_online else t("status_offline", apply_theme=False)
    mode_style = "white" if is_online else "dim white"
    
    status_lines.append((" ● ", "dim white", f"{t('label_user', apply_theme=False)}: {user_name_disp}", "white"))
    status_lines.append((" ● ", "dim white", f"{t('label_tier', apply_theme=False)}: {tier_disp}", "white"))
    status_lines.append((" ● ", "dim white", f"{t('label_mode', apply_theme=False)}: {mode_disp}", mode_style))
    status_lines.append((" ● ", "dim white", f"{t('label_core', apply_theme=False)}: {t('status_active', apply_theme=False)}", "white"))

    if status_budget > 0:
        num_to_show = min(status_budget, len(status_lines))
        padding = status_budget - num_to_show
        if padding > 0:
            status_text.append("\n" * padding)
        
        for i in range(num_to_show):
            bullet_char, bullet_style, label_text, label_style = status_lines[i]
            status_text.append(bullet_char, style=bullet_style)
            status_text.append(label_text, style=label_style)
            if i < num_to_show - 1:
                status_text.append("\n")
    
    sidebar_group = Group(
        phage_art,
        status_text
    )
    
    # Sidebar Panel (width = 19 interior + 2 border = 21, height = panel_height)
    core_title = t("label_core", apply_theme=False).upper()
    core_title_style = "bold white"
    sidebar_panel = Panel(
        sidebar_group,
        border_style=border_style,
        title=f"[{core_title_style}]{core_title}[/{core_title_style}]",
        title_align="left",
        width=21,
        height=panel_height
    )
    
    # Translate main workspace title dynamically
    title_key = f"title_{main_title.replace(' ', '_').lower()}"
    translated_title = t(title_key)
    if translated_title == title_key:
        translated_title = main_title  # fallback if key not defined
        
    main_title_style = t_style("title")
    if anchor_bottom:
        from rich.segment import Segment, Segments
        inner_w = max(1, safe_width - (23 if show_sidebar else 0) - 4)
        rendered = console.render_lines(main_content, console.options.update(width=inner_w), pad=False)
        avail = panel_height - 2
        if len(rendered) > avail:
            # Drop blank spacer lines first, then keep the tail (the prompt)
            excess = len(rendered) - avail
            kept = []
            for line in rendered:
                if excess > 0 and not "".join(seg.text for seg in line).strip():
                    excess -= 1
                    continue
                kept.append(line)
            segs: List[Segment] = []
            for line in kept[-avail:]:
                segs.extend(line)
                segs.append(Segment.line())
            main_content = Segments(segs[:-1])

    # Main Workspace Panel
    main_panel = Panel(
        main_content,
        border_style=border_style,
        title=f"[{main_title_style}]{translated_title}[/{main_title_style}]",
        title_align="left",
        height=panel_height,
        expand=True
    )
    
    # 3. Side-by-side body table
    body_table = Table.grid(expand=True)
    if show_sidebar:
        body_table.add_column(width=21)
        body_table.add_column(width=2)  # spacer
        body_table.add_column()         # main workspace
        body_table.add_row(sidebar_panel, "", main_panel)
    else:
        body_table.add_column()
        body_table.add_row(main_panel)
    
    # 4. Header & Divider
    _h_prefix  = " » SWAEV Genomics "
    _h_sep     = "│ "
    _h_sub     = "SWAEV B2B Structural Genomics Client"
    header = Text(no_wrap=True, overflow="ellipsis")
    header.append(_h_prefix, style=f"bold {t_style('title')}")
    header.append(_h_sep, style=f"dim {t_style('text')}")
    header.append(_h_sub, style=f"{t_style('text_bold')}")

    fixed_len = len(_h_prefix) + len(_h_sep) + len(_h_sub)
    if safe_width > fixed_len + 25:
        spaces = " " * (safe_width - fixed_len - 25)
        header.append(spaces)
        header.append("SECURE TERMINAL: ONLINE", style=f"{t_style('success_bold')}")
        
    divider = get_dna_horizontal_line(safe_width)
    
    # 5. Main container
    container = Table.grid()
    container.width = safe_width
    container.add_column()
    container.add_row(header)
    container.add_row(divider)
    container.add_row(body_table)
    
    return container


def animated_input(prompt: str, state: str = "idle", header_renderable: Optional[Any] = None, main_title: str = "WORKSPACE", error_msg: str = "", single_char: bool = False) -> str:
    """
    Reads a string from stdin non-blocking while keeping the phage animation alive in real-time.
    Maintains termios raw/cbreak mode safely and restores terminal settings on exit.
    Gracefully falls back to standard console.input() if stdin is not a TTY.
    """
    if not sys.stdin.isatty():
        clear_screen_completely()
        right_content = []
        if header_renderable is not None:
            right_content.append(header_renderable)
            right_content.append("")
        if error_msg:
            right_content.append(error_msg)
            right_content.append("")
        grid = build_dashboard_grid(state, 0, Group(*right_content) if right_content else "", main_title=main_title)
        console.print(grid)
        return console.input(prompt).strip()

    import termios
    import tty
    import select

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    buffer = ""
    frame = 0
    last_update = time.time()
    
    try:
        tty.setcbreak(fd)
        with Live(auto_refresh=False, console=console, transient=True) as live:
            while True:
                cursor = "▮" if int(time.time() * 2) % 2 == 0 else " "
                
                # Combine header_renderable with input prompt
                right_content = []
                
                active_header = header_renderable
                if len(buffer) > 0 and header_renderable is not None and hasattr(header_renderable, "renderables"):
                    filtered_renderables = []
                    for r in header_renderable.renderables:
                        r_str = str(r) if r is not None else ""
                        if "Tip" in r_str or "Tip:" in r_str:
                            continue
                        if isinstance(r, Panel):
                            title_str = str(r.title) if r.title is not None else ""
                            if "ACCOUNT QUOTA" in title_str:
                                continue
                        filtered_renderables.append(r)
                    active_header = Group(*filtered_renderables)

                if active_header is not None:
                    right_content.append(active_header)
                    right_content.append("")  # spacing spacer
                
                if error_msg and len(buffer) == 0:
                    right_content.append(error_msg)
                    right_content.append("")
                
                # Render prompt and input buffer nicely using the active theme
                right_content.append(Text.assemble(
                    (prompt, t_style("text_bold")),
                    (buffer, t_style("primary_bold")),
                    (cursor, t_style("text_bold"))
                ))
                
                # If the user has typed characters, the phage starts dancing!
                active_state = "dancing" if (len(buffer) > 0 and state != "thinking") else state
                
                # Build unified side-by-side dashboard grid
                grid = build_dashboard_grid(active_state, frame, Group(*right_content), main_title=main_title, anchor_bottom=True)
                
                live.update(grid)
                live.refresh()
                
                # Check for input characters non-blocking
                now = time.time()
                timeout = max(0.01, 0.35 - (now - last_update))
                
                rlist, _, _ = select.select([fd], [], [], timeout)
                if rlist:
                    char = os.read(fd, 1).decode("utf-8", errors="replace")
                    if char in ("\x03", "\x04"):  # Ctrl+C / Ctrl+D
                        raise KeyboardInterrupt()

                     # Backspace
                    if char in ("\x7f", "\x08"):
                        if len(buffer) > 0:
                            buffer = buffer[:-1]
                    elif char in ("\r", "\n"):  # Enter
                        break
                    elif char == "\x1b":  # Escape sequences — drain completely
                        while True:
                            _dr, _, _ = select.select([fd], [], [], 0.1)
                            if _dr:
                                _c = os.read(fd, 1).decode("utf-8", errors="replace")
                                if _c in ("A", "B", "C", "D", "H", "F", "M", "m", "~", "l", "h"):
                                    break
                            else:
                                break
                    elif ord(char) >= 32:
                        buffer += char
                        if single_char:
                            break

                if time.time() - last_update >= 0.35:
                     frame += 1
                     last_update = time.time()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        clear_screen_completely()
        
    return buffer.strip()


# -----------------------------------------------------------------------------
# FASTA Loading & Parsing
# -----------------------------------------------------------------------------
def scan_fasta_files(fasta_dir: str = ".") -> List[str]:
    """Scans custom directory for genomic FASTA files."""
    fasta_files = []
    if not os.path.isdir(fasta_dir):
        return []
    for entry in os.listdir(fasta_dir):
        if entry.lower().endswith((".fa", ".fasta", ".fna")):
            fasta_files.append(entry)
    return sorted(fasta_files)


def parse_fasta(file_path: str) -> List[int]:
    """
    Parses FASTA file, translating characters into integer base-pair tokens:
    0=A, 1=C, 2=G, 3=T, 4=N
    """
    tokens = []
    base_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'U': 3, 'N': 4}
    
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">") or not line:
                continue
            for char in line.upper():
                if char in base_map:
                    tokens.append(base_map[char])
                else:
                    tokens.append(4)
    return tokens


        

# -----------------------------------------------------------------------------
# Genomic Matrix Heatmap Simulators & Visualizers
# -----------------------------------------------------------------------------
def generate_simulated_matrix(matrix_type: str, size: int = 24) -> List[List[float]]:
    """
    Generates a highly realistic, publication-grade genomic interaction matrix of given size.
    Features a diagonal proximity decay, TAD domains, and CTCF loop anchors.
    """
    import math
    matrix = [[0.0 for _ in range(size)] for _ in range(size)]
    
    bin_36_ratio = 36.0 / 256.0
    bin_219_ratio = 219.0 / 256.0
    
    idx_36 = int(size * bin_36_ratio)
    idx_219 = int(size * bin_219_ratio)
    
    if idx_36 == 0:
        idx_36 = 1
        
    for i in range(size):
        for j in range(size):
            dist = abs(i - j)
            # Base diagonal decay (proximity-based folding)
            base = 1.0 / (dist + 1.5)**0.7
            
            # Sub-diagonal chromatin domains/TADs
            in_same_domain = False
            if (i < idx_36 and j < idx_36) or (idx_36 <= i < idx_219 and idx_36 <= j < idx_219) or (i >= idx_219 and j >= idx_219):
                in_same_domain = True
            
            if in_same_domain:
                base += 0.15 / (dist + 1.0)**0.3
            
            # Prominent WT loop anchor at idx_36 interacting with an upstream anchor
            loop_i, loop_j = idx_36, max(0, idx_36 - int(size * 0.15))
            dist_to_loop_wt = math.sqrt((i - loop_i)**2 + (j - loop_j)**2)
            dist_to_loop_wt_sym = math.sqrt((j - loop_i)**2 + (i - loop_j)**2)
            loop_wt_val = 0.5 * math.exp(- (min(dist_to_loop_wt, dist_to_loop_wt_sym))**2 / 1.5)
            base += loop_wt_val
            
            if matrix_type == "wt":
                matrix[i][j] = base
            elif matrix_type == "experimental_hic":
                # WT predicted matrix + coordinate-based deterministic noise to prevent flickering
                noise = 0.05 * math.sin(i * 31.0 + j * 17.0) + 0.02 * math.cos(i * 7.0 - j * 13.0)
                matrix[i][j] = max(0.01, base + noise)
            elif matrix_type == "deletion_mutant":
                is_near_deletion = (abs(i - idx_36) < 2 or abs(j - idx_36) < 2)
                if is_near_deletion:
                    base = base * 0.3
                else:
                    base -= loop_wt_val * 0.8
                matrix[i][j] = max(0.01, base)
            elif matrix_type == "deletion_diff":
                is_near_deletion = (abs(i - idx_36) < 2 or abs(j - idx_36) < 2)
                val = 0.0
                if is_near_deletion:
                    val = -0.45 * math.exp(- (min(abs(i-idx_36), abs(j-idx_36)))**2 / 2.0)
                else:
                    dist_to_loop_wt = math.sqrt((i - loop_i)**2 + (j - loop_j)**2)
                    dist_to_loop_wt_sym = math.sqrt((j - loop_i)**2 + (i - loop_j)**2)
                    val = -0.4 * math.exp(- (min(dist_to_loop_wt, dist_to_loop_wt_sym))**2 / 1.5)
                matrix[i][j] = val
            elif matrix_type == "insertion_mutant":
                loop_i2, loop_j2 = idx_219, min(size - 1, idx_219 + int(size * 0.12))
                dist_to_loop_ins = math.sqrt((i - loop_i2)**2 + (j - loop_j2)**2)
                dist_to_loop_ins_sym = math.sqrt((j - loop_i2)**2 + (i - loop_j2)**2)
                loop_ins_val = 0.65 * math.exp(- (min(dist_to_loop_ins, dist_to_loop_ins_sym))**2 / 1.2)
                matrix[i][j] = base + loop_ins_val
            elif matrix_type == "insertion_diff":
                loop_i2, loop_j2 = idx_219, min(size - 1, idx_219 + int(size * 0.12))
                dist_to_loop_ins = math.sqrt((i - loop_i2)**2 + (j - loop_j2)**2)
                dist_to_loop_ins_sym = math.sqrt((j - loop_i2)**2 + (i - loop_j2)**2)
                val = 0.65 * math.exp(- (min(dist_to_loop_ins, dist_to_loop_ins_sym))**2 / 1.2)
                if abs(i - idx_219) < 1 or abs(j - idx_219) < 1:
                    val += 0.15 * math.exp(- (abs(i - j))**2 / 4.0)
                matrix[i][j] = val
                
    return matrix


def get_chromatin_color(value: float, min_v: float, max_v: float) -> Tuple[int, int, int]:
    """Teal/green gradient: deep slate/navy -> teal -> vibrant green."""
    if max_v == min_v:
        return 5, 10, 15
    norm = max(0.0, min(1.0, (value - min_v) / (max_v - min_v)))
    if norm < 0.5:
        p = norm / 0.5
        r = int(10 + p * (20 - 10))
        g = int(15 + p * (150 - 15))
        b = int(35 + p * (180 - 35))
    else:
        p = (norm - 0.5) / 0.5
        r = int(20 + p * (50 - 20))
        g = int(150 + p * (255 - 150))
        b = int(180 + p * (100 - 180))
    return r, g, b


def get_difference_color(value: float, max_abs: float) -> Tuple[int, int, int]:
    """Diverging blue-to-red color map: Negative = Loss (Blue), Positive = Gain (Red), Neutral = Dark Slate."""
    if max_abs <= 0:
        return 15, 17, 26
    norm = max(-1.0, min(1.0, value / max_abs))
    if norm < 0:
        p = -norm
        r = int(15 - p * 5)
        g = int(17 + p * 30)
        b = int(26 + p * 200)
    else:
        p = norm
        r = int(15 + p * 220)
        g = int(17 - p * 10)
        b = int(26 - p * 15)
    return r, g, b


def render_matrix_double_res(matrix_data: Optional[List[List[float]]], map_type: str, max_height: Optional[int] = None, max_width: Optional[int] = None) -> Group:
    """
    Renders a 2D matrix using half-block terminal graphics for double vertical resolution.
    The grid is sized to max_width × max_height cells (terminal size when omitted).
    """
    width, height = console.size
    # 5 columns go to the row labels and the two box sides
    max_w_size = (max_width - 5) if max_width else width - 12
    if max_height is not None:
        # Subtract 3 lines: 2 for top/bottom borders of the graph box, 1 for the kb labels at the bottom.
        # Each vertical cell is a half-block (takes 1 character height for 2 rows).
        max_h_size = max(4, (max_height - 3) * 2)
    else:
        max_h_size = (height - 12) * 2
    grid_size = min(80, max_w_size, max_h_size)
    grid_size = max(12, grid_size)
    
    if grid_size % 2 != 0:
        grid_size -= 1
        
    if matrix_data is None or len(matrix_data) == 0:
        matrix_data = generate_simulated_matrix(map_type, size=grid_size)
    elif len(matrix_data) != grid_size:
        src_n = len(matrix_data)
        resized: List[List[float]] = []
        for _ri in range(grid_size):
            src_i = int(_ri * src_n / grid_size)
            resized_row: List[float] = []
            for _ci in range(grid_size):
                src_j = int(_ci * src_n / grid_size)
                resized_row.append(matrix_data[src_i][src_j])
            resized.append(resized_row)
        matrix_data = resized
    flat_vals = [val for row in matrix_data for val in row]
    min_v = min(flat_vals) if flat_vals else 0.0
    max_v = max(flat_vals) if flat_vals else 1.0
    max_abs = max(abs(min_v), abs(max_v)) if flat_vals else 1.0
    
    lines = []
    lines.append("   [dim]┌[/]" + "[dim]─[/]" * grid_size + "[dim]┐[/]")
    
    for y in range(grid_size // 2):
        row_str = f" [dim]{y*2:2d}[/dim][dim]│[/]"
        for x in range(grid_size):
            val_top = matrix_data[2*y][x]
            val_bottom = matrix_data[2*y + 1][x]
            
            if map_type in ("wt", "deletion_mutant", "insertion_mutant", "experimental_hic"):
                r_top, g_top, b_top = get_chromatin_color(val_top, min_v, max_v)
                r_bot, g_bot, b_bot = get_chromatin_color(val_bottom, min_v, max_v)
            else:
                r_top, g_top, b_top = get_difference_color(val_top, max_abs)
                r_bot, g_bot, b_bot = get_difference_color(val_bottom, max_abs)
                
            row_str += f"[#{r_top:02x}{g_top:02x}{b_top:02x} on #{r_bot:02x}{g_bot:02x}{b_bot:02x}]▄[/]"
        row_str += "[dim]│[/]"
        lines.append(row_str)
        
    lines.append("   [dim]└[/]" + "[dim]─[/]" * grid_size + "[dim]┘[/]")
    
    # Initialize a character array starting at offset index 4 for proportional labels
    lbl_arr = [" "] * (4 + grid_size + 10)
    labels = ["0k", "256k", "512k", "768k", "1024k"]
    fracs = [0.0, 0.25, 0.5, 0.75, 1.0]
    if grid_size < 30:  # too narrow for five labels without overlap
        labels, fracs = ["0k", "1024k"], [0.0, 1.0]
    for frac, label in zip(fracs, labels):
        grid_col = int(round(frac * (grid_size - 1)))
        char_idx = 4 + grid_col
        for idx, char in enumerate(label):
            if char_idx + idx < len(lbl_arr):
                lbl_arr[char_idx + idx] = char
    lbl_line = "".join(lbl_arr).rstrip()
    lines.append(f"[dim]{lbl_line}[/dim]")
    
    return Group(*[Text.from_markup(line) for line in lines])


# -----------------------------------------------------------------------------
# Sequence Analytics: Statistics, Composition & Motif Search
# -----------------------------------------------------------------------------

def compute_sequence_stats(tokens: List[int]) -> Dict[str, Any]:
    """Computes biophysical and compositional statistics for a token sequence."""
    n = len(tokens)
    counts: Dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for tok in tokens:
        counts[tok] = counts.get(tok, 0) + 1

    a, c, g, t_count, n_count = counts[0], counts[1], counts[2], counts[3], counts[4]
    valid = n - n_count
    gc = c + g
    at = a + t_count

    gc_pct = (gc / valid * 100) if valid > 0 else 0.0
    at_skew = (a - t_count) / (a + t_count) if (a + t_count) > 0 else 0.0
    gc_skew = (g - c) / (g + c) if (g + c) > 0 else 0.0

    # Marmur-Doty melting temperature
    if n < 14:
        tm = 2 * at + 4 * gc
    else:
        tm = 64.9 + 41.0 * (gc - 16.4) / n

    # CpG dinucleotide count (C=1 followed by G=2)
    cpg_count = sum(1 for i in range(len(tokens) - 1) if tokens[i] == 1 and tokens[i + 1] == 2)
    cpg_oe = (cpg_count * n) / (c * g) if (c > 0 and g > 0) else 0.0

    return {
        "length": n, "valid": valid,
        "a": a, "c": c, "g": g, "t": t_count, "n_count": n_count,
        "gc_pct": gc_pct, "at_skew": at_skew, "gc_skew": gc_skew,
        "tm": tm, "cpg_count": cpg_count, "cpg_oe": cpg_oe,
    }


# ============================================================
# GOLDBEAM INTERPRETABILITY SUITE — Core Analysis Engine
# ============================================================

def get_contact_matrix(tokens: List[int]) -> Tuple[List[List[float]], str]:
    """
    Central model seam. Returns (matrix, provenance_string).
    Swap the body with a real API call once GoldBEAM model is trained.
    Hook: replace generate_simulated_matrix with call_goldbeam_api(tokens).
    """
    matrix = generate_simulated_matrix("wt", size=40)
    return matrix, "SIMULATED — GoldBEAM model in training. Illustrative only."


def compute_insulation_score(matrix: List[List[float]], diamond_size: int = 5) -> List[float]:
    """Computes normalized insulation score per diagonal bin. Local minima = TAD boundaries."""
    n = len(matrix)
    d = diamond_size
    raw: List[float] = []
    for i in range(n):
        total = 0.0
        count = 0
        for r in range(max(0, i - d), i):
            for c in range(i + 1, min(n, i + d + 1)):
                total += matrix[r][c]
                count += 1
        raw.append(total / count if count > 0 else 0.0)
    lo = min(raw) if raw else 0.0
    hi = max(raw) if raw else 1.0
    rng = hi - lo
    return [(s - lo) / (rng + 1e-10) for s in raw]


def call_tad_boundaries(
    insulation_scores: List[float], min_valley_depth: float = 0.12
) -> List[Dict[str, Any]]:
    """Returns local minima of insulation profile as TAD boundary dicts."""
    n = len(insulation_scores)
    boundaries: List[Dict[str, Any]] = []
    for i in range(1, n - 1):
        left = insulation_scores[i - 1]
        here = insulation_scores[i]
        right_s = insulation_scores[i + 1]
        if here < left and here < right_s:
            depth = min(left, right_s) - here
            if depth >= min_valley_depth:
                boundaries.append({"bin": i, "insulation_score": here, "boundary_strength": depth})
    return boundaries


def compute_oe_matrix(matrix: List[List[float]]) -> List[List[float]]:
    """Observed/expected contact matrix (row/column marginal normalization)."""
    n = len(matrix)
    row_sums = [sum(matrix[i]) for i in range(n)]
    total = sum(row_sums)
    if total < 1e-10:
        return [[0.0] * n for _ in range(n)]
    oe = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            expected = (row_sums[i] * row_sums[j]) / total
            oe[i][j] = matrix[i][j] / expected if expected > 1e-10 else 0.0
    return oe


def _power_iteration(sym_matrix: List[List[float]], n_iter: int = 80) -> List[float]:
    """Dominant eigenvector via power iteration (for 256x256 or smaller matrices)."""
    import random as _rng
    n = len(sym_matrix)
    v = [_rng.gauss(0.0, 1.0) for _ in range(n)]
    for _ in range(n_iter):
        nv = [sum(sym_matrix[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in nv))
        if norm < 1e-10:
            break
        v = [x / norm for x in nv]
    return v


def compute_ab_compartments(matrix: List[List[float]]) -> Tuple[List[str], List[float]]:
    """
    A/B compartment calling via first eigenvector of O/E Pearson correlation matrix.
    Positive eigenvector component = A (active/open), negative = B (inactive/closed).
    """
    oe = compute_oe_matrix(matrix)
    n = len(oe)
    row_means = [sum(oe[i]) / n for i in range(n)]
    corr = [[0.0] * n for _ in range(n)]
    for i in range(n):
        di = [oe[i][k] - row_means[i] for k in range(n)]
        norm_i = math.sqrt(sum(x * x for x in di))
        for j in range(i, n):
            dj = [oe[j][k] - row_means[j] for k in range(n)]
            norm_j = math.sqrt(sum(x * x for x in dj))
            if norm_i > 1e-10 and norm_j > 1e-10:
                c = sum(di[k] * dj[k] for k in range(n)) / (norm_i * norm_j)
            else:
                c = 0.0
            corr[i][j] = c
            corr[j][i] = c
    eigvec = _power_iteration(corr)
    return ["A" if v >= 0 else "B" for v in eigvec], eigvec


def find_loop_anchors(
    matrix: List[List[float]], min_dist: int = 6, top_n: int = 25
) -> List[Tuple[int, int, float]]:
    """Returns the top off-diagonal contact pairs as predicted loop anchor candidates."""
    n = len(matrix)
    candidates = [(matrix[i][j], i, j) for i in range(n) for j in range(i + min_dist, n)]
    candidates.sort(reverse=True)
    return [(i, j, v) for v, i, j in candidates[:top_n]]


def _perturb_matrix_near_bins(
    base_matrix: List[List[float]], bins: List[int], strength: float = 0.35
) -> List[List[float]]:
    """Creates a perturbed contact matrix to simulate a structural variant effect."""
    import random as _rng
    n = len(base_matrix)
    mut = [row[:] for row in base_matrix]
    for pb in bins:
        pb = max(0, min(n - 1, pb))
        for i in range(n):
            for j in range(n):
                dist = min(abs(i - pb), abs(j - pb))
                if dist <= 3:
                    amplitude = strength * (1.0 - dist / 4.0)
                    delta = _rng.gauss(0, amplitude * max(0.05, base_matrix[i][j]))
                    mut[i][j] = max(0.0, mut[i][j] + delta)
    for i in range(n):
        for j in range(i, n):
            avg = (mut[i][j] + mut[j][i]) * 0.5
            mut[i][j] = avg
            mut[j][i] = avg
    return mut


def compute_delta_matrix(
    wt_matrix: List[List[float]], mut_matrix: List[List[float]]
) -> List[List[float]]:
    """Element-wise delta: mutant − wildtype."""
    n = len(wt_matrix)
    return [[mut_matrix[i][j] - wt_matrix[i][j] for j in range(n)] for i in range(n)]


def compute_delta_stats(delta: List[List[float]]) -> Dict[str, float]:
    flat = [delta[i][j] for i in range(len(delta)) for j in range(len(delta[i]))]
    if not flat:
        return {"mean_abs_delta": 0.0, "max_gain": 0.0, "max_loss": 0.0}
    return {
        "mean_abs_delta": sum(abs(v) for v in flat) / len(flat),
        "max_gain": max(flat),
        "max_loss": min(flat),
    }


def generate_simulated_saliency(tokens: List[int], n_bins: int = 40) -> List[float]:
    """
    Per-bin attribution/saliency stub: peaks over GC-rich regions with signal variation.
    Hook: replace with real gradient-based attribution when GoldBEAM model is trained.
    """
    n = len(tokens)
    if n == 0:
        return [0.0] * n_bins
    bin_size = max(1, n // n_bins)
    scores: List[float] = []
    for b in range(n_bins):
        sl = tokens[b * bin_size: b * bin_size + bin_size]
        if not sl:
            scores.append(0.0)
            continue
        gc = sum(1 for tok in sl if tok in (1, 2)) / len(sl)
        sig = gc + math.sin(b * 0.45) * 0.12 + math.cos(b * 0.2) * 0.07
        scores.append(max(0.0, min(1.0, sig + 0.08)))
    return scores


# ── Export utilities ─────────────────────────────────────────────────────────

def _make_export_dir() -> str:
    p = os.path.expanduser("~/goldbeam_exports")
    os.makedirs(p, exist_ok=True)
    return p


def _provenance_header_lines(provenance: str, tool: str) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    warn = "Simulated data. Not real model output." if "SIMULATED" in provenance else "Real model output."
    return (
        f"# provenance: {provenance}\n"
        f"# tool: GoldBEAM {tool}\n"
        f"# generated: {ts}\n"
        f"# WARNING: {warn}\n"
    )


def export_tad_bed(
    boundaries: List[Dict[str, Any]],
    chrom: str,
    start_bp: int,
    bin_size: int,
    provenance: str,
    output_path: Optional[str] = None,
) -> str:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(_make_export_dir(), f"goldbeam_tad_boundaries_{ts}.bed")
    with open(output_path, "w") as fh:
        fh.write(_provenance_header_lines(provenance, "TAD Boundary Caller"))
        fh.write(f'track name="GoldBEAM_TAD" description="Predicted TAD boundaries ({provenance})"\n')
        for b in boundaries:
            b_start = start_bp + b["bin"] * bin_size
            score = int(b["boundary_strength"] * 1000)
            fh.write(f"{chrom}\t{b_start}\t{b_start + bin_size}\tTAD_boundary_{b['bin']}\t{score}\t.\n")
    return output_path


def export_compartment_bed(
    assignments: List[str],
    eigvec: List[float],
    chrom: str,
    start_bp: int,
    bin_size: int,
    provenance: str,
    output_path: Optional[str] = None,
) -> str:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(_make_export_dir(), f"goldbeam_ab_compartments_{ts}.bed")
    with open(output_path, "w") as fh:
        fh.write(_provenance_header_lines(provenance, "A/B Compartment Caller"))
        fh.write(f'track name="GoldBEAM_AB" description="Predicted A/B compartments ({provenance})"\n')
        for i, (comp, val) in enumerate(zip(assignments, eigvec)):
            b_start = start_bp + i * bin_size
            score = int(abs(val) * 1000)
            fh.write(f"{chrom}\t{b_start}\t{b_start + bin_size}\t{comp}_compartment_{i}\t{score}\t.\n")
    return output_path


def export_loop_tsv(
    anchors: List[Tuple[int, int, float]],
    chrom: str,
    start_bp: int,
    bin_size: int,
    provenance: str,
    output_path: Optional[str] = None,
) -> str:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(_make_export_dir(), f"goldbeam_loop_anchors_{ts}.tsv")
    with open(output_path, "w") as fh:
        fh.write(_provenance_header_lines(provenance, "Loop Anchor Registry"))
        fh.write("chrom\tanchor1_start\tanchor1_end\tanchor2_start\tanchor2_end\tcontact_score\n")
        for bin1, bin2, score in anchors:
            a1s = start_bp + bin1 * bin_size
            a2s = start_bp + bin2 * bin_size
            fh.write(f"{chrom}\t{a1s}\t{a1s + bin_size}\t{a2s}\t{a2s + bin_size}\t{score:.6f}\n")
    return output_path


def export_saliency_bedgraph(
    scores: List[float],
    chrom: str,
    start_bp: int,
    bin_size: int,
    provenance: str,
    output_path: Optional[str] = None,
) -> str:
    if output_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(_make_export_dir(), f"goldbeam_saliency_{ts}.bedGraph")
    with open(output_path, "w") as fh:
        fh.write(_provenance_header_lines(provenance, "Saliency / Attribution"))
        fh.write(f'track type=bedGraph name="GoldBEAM_Saliency" description="Per-bin attribution ({provenance})"\n')
        for i, score in enumerate(scores):
            b_start = start_bp + i * bin_size
            fh.write(f"{chrom}\t{b_start}\t{b_start + bin_size}\t{score:.6f}\n")
    return output_path


# ── Session history ───────────────────────────────────────────────────────────
# One entry per sequence source (a FASTA path or a UCSC coordinate), newest
# first, with the variants simulated and files exported while it was loaded.
# Kept in its own file so saving history can never overwrite settings.

HISTORY_PATH = os.path.expanduser("~/.goldbeam_history.json")
_HISTORY_LIMIT = 50          # sessions kept
_HISTORY_DETAIL_LIMIT = 20   # variants / exports kept per session


def load_session_history() -> List[Dict[str, Any]]:
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("source") in ("file", "ucsc") and e.get("locator")]


def save_session_history(history: List[Dict[str, Any]]) -> None:
    tmp_path = HISTORY_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(history[:_HISTORY_LIMIT], fh, indent=2)
        os.replace(tmp_path, HISTORY_PATH)
    except OSError:
        pass


def record_sequence_session(
    source: str,
    locator: str,
    name: str,
    tokens: List[int],
    cell_line: str,
    synthetic: bool = False,
) -> str:
    """
    Adds a history entry for a loaded sequence — or moves the existing entry for
    the same source to the top, keeping its variants and exports. Returns its id.
    """
    history = load_session_history()
    entry = next((e for e in history if e["source"] == source and e["locator"] == locator), None)
    if entry is None:
        entry = {"id": f"{time.time():.6f}", "variants": [], "exports": []}
    else:
        history.remove(entry)
    gc_count = sum(1 for tok in tokens if tok in (1, 2))
    entry.update({
        "source": source,
        "locator": locator,
        "name": name,
        "length": len(tokens),
        "gc_pct": round(gc_count / len(tokens) * 100, 2) if tokens else 0.0,
        "cell_line": cell_line,
        "synthetic": synthetic,
        "last_opened": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    history.insert(0, entry)
    save_session_history(history)
    return entry["id"]


def update_session_history(
    entry_id: str,
    cell_line: Optional[str] = None,
    variant: Optional[Dict[str, Any]] = None,
    exports: Optional[List[str]] = None,
) -> None:
    """Attaches a cell-line change, a simulated variant or exported files to a session."""
    if not entry_id:
        return
    history = load_session_history()
    entry = next((e for e in history if e.get("id") == entry_id), None)
    if entry is None:
        return
    if cell_line:
        entry["cell_line"] = cell_line
    if variant:
        entry["variants"] = (entry.get("variants", []) + [variant])[-_HISTORY_DETAIL_LIMIT:]
    if exports:
        entry["exports"] = (entry.get("exports", []) + list(exports))[-_HISTORY_DETAIL_LIMIT:]
    save_session_history(history)


def remove_session_history(entry_id: str) -> None:
    save_session_history([e for e in load_session_history() if e.get("id") != entry_id])


# ── Real genomic sequence fetch via UCSC REST API ─────────────────────────────

def _parse_genomic_coord(coord_str: str) -> Optional[Tuple[str, int, int]]:
    """Parses 'chr22:34000000-35000000' and variants (commas, no-chr-prefix)."""
    import re
    s = coord_str.strip().replace(",", "").replace(" ", "")
    m = re.match(r"^(chr[0-9XYMT]+|[0-9XYMT]+):(\d+)-(\d+)$", s, re.IGNORECASE)
    if not m:
        return None
    chrom_raw = m.group(1)
    if not chrom_raw.lower().startswith("chr"):
        chrom_raw = "chr" + chrom_raw
    return chrom_raw.lower(), int(m.group(2)), int(m.group(3))


def fetch_ucsc_sequence(
    chrom: str, start: int, end: int, assembly: str = "hg38"
) -> Optional[List[int]]:
    """
    Fetches a real DNA sequence from UCSC REST API (0-based coords).
    Returns ACGT token list (0=A,1=C,2=G,3=T,4=N) or None on failure.
    Endpoint: https://api.genome.ucsc.edu/getData/sequence
    """
    url = (
        f"https://api.genome.ucsc.edu/getData/sequence"
        f"?genome={assembly};chrom={chrom};start={start};end={end}"
    )
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            return None
        data = resp.json()
        dna = data.get("dna", "")
        if not dna:
            return None
        tok_map: Dict[str, int] = {"a": 0, "c": 1, "g": 2, "t": 3}
        return [tok_map.get(b.lower(), 4) for b in dna]
    except Exception:
        return None


# ── Interpretability suite rendering helpers ──────────────────────────────────

def _group_track(values: List[float], max_rows: int) -> Tuple[List[float], List[int]]:
    """
    Fits a per-bin track into max_rows rows: one row per bin when it fits,
    otherwise consecutive bins are averaged. Returns (row values, first bin of each row).
    """
    n = len(values)
    if n <= max_rows or max_rows <= 0:
        return list(values), list(range(n))
    step = -(-n // max_rows)  # ceiling division
    starts = list(range(0, n, step))
    return [sum(values[s:s + step]) / len(values[s:s + step]) for s in starts], starts


def _render_bar_chart_1d(
    scores: List[float],
    width: int = 50,
    markers: Optional[List[int]] = None,
    high_color: str = "chartreuse1",
    marker_color: str = "red",
    max_rows: int = 0,
) -> List[str]:
    """
    Compact 1D bar chart as markup lines, with optional marker annotations.
    With max_rows, bins are averaged into at most that many rows; a row is
    marked when any bin inside it is a marker.
    """
    lines: List[str] = []
    max_v = max(scores) if scores else 1.0
    if max_v < 1e-10:
        max_v = 1.0
    marker_set = set(markers or [])
    rows, starts = _group_track(scores, max_rows) if max_rows else (list(scores), list(range(len(scores))))
    step = starts[1] - starts[0] if len(starts) > 1 else 1
    for start, v in zip(starts, rows):
        bar_len = int(v / max_v * width)
        filled = f"[{high_color}]{'█' * bar_len}[/{high_color}]"
        empty = f"[dim]{'░' * (width - bar_len)}[/dim]"
        marked = any(b in marker_set for b in range(start, start + step))
        mark = f" [{marker_color}]◄[/{marker_color}]" if marked else ""
        lines.append(f"  {start:3d} {filled}{empty} {v:.3f}{mark}")
    return lines


def _render_delta_matrix_text(delta: List[List[float]], max_size: int = 22) -> List[str]:
    """Renders ΔContact matrix as text heatmap: red=gain, blue=loss."""
    n = len(delta)
    step = max(1, n // max_size)
    flat = [delta[i][j] for i in range(n) for j in range(n)]
    max_abs = max(abs(v) for v in flat) if flat else 1.0
    if max_abs < 1e-10:
        max_abs = 1.0
    lines: List[str] = []
    cells = len(range(0, n, step))
    lines.append(f"   [dim]┌{'─' * cells}┐[/dim]")
    for i in range(0, n, step):
        row_str = f" {i:2d}[dim]│[/dim]"
        for j in range(0, n, step):
            v = delta[i][j]
            intensity = min(1.0, abs(v) / max_abs)
            level = int(intensity * 4)
            ch = " ░▒▓█"[level]
            if v > 0.005:
                row_str += f"[bold red]{ch}[/bold red]"
            elif v < -0.005:
                row_str += f"[bold #0ea5e9]{ch}[/bold #0ea5e9]"
            else:
                row_str += f"[dim]{ch}[/dim]"
        row_str += "[dim]│[/dim]"
        lines.append(row_str)
    lines.append(f"   [dim]└{'─' * cells}┘[/dim]")
    lines.append("   [dim][bold red]■[/bold red]=contact gain  [bold #0ea5e9]■[/bold #0ea5e9]=contact loss  ■=neutral[/dim]")
    return lines


# ── Interpretability Suite Dashboard ─────────────────────────────────────────

def run_interpretability_suite(
    tokens: List[int],
    filename: str,
    config: Dict[str, Any],
    on_export: Optional[Any] = None,
) -> None:
    """
    Launches the GoldBEAM Interpretability Suite — 7 analysis tabs.
    All outputs carry provenance stamps (SIMULATED until model is wired).
    Hook: swap get_contact_matrix() body to connect real model output.
    on_export(file_names) is called after each successful export.
    """
    clear_screen_completely()

    # Pre-compute all analyses on entry
    matrix, provenance = get_contact_matrix(tokens)
    n_bins = len(matrix)
    insulation = compute_insulation_score(matrix)
    boundaries = call_tad_boundaries(insulation)
    compartments, eigvec = compute_ab_compartments(matrix)
    loop_anchors = find_loop_anchors(matrix)
    saliency = generate_simulated_saliency(tokens, n_bins=n_bins)

    seq_len = len(tokens)
    chrom = "chrUnknown"
    start_bp = 0
    bin_size_bp = max(1, seq_len // n_bins) if seq_len > 0 else 4096
    locus_name = filename or "loaded sequence"

    # Variant modeller state
    vt_matrix: List[List[float]] = [row[:] for row in matrix]
    vt_delta: List[List[float]] = [[0.0] * n_bins for _ in range(n_bins)]
    vt_stats: Dict[str, float] = {"mean_abs_delta": 0.0, "max_gain": 0.0, "max_loss": 0.0}
    vt_desc: str = "No variant applied.  Commands: snp <pos> <REF>><ALT>  |  del <start> <end>"
    vt_applied: bool = False

    current_tab = "1"
    toast_msg: Optional[str] = None
    toast_expire: float = 0.0

    TAB_NAMES: Dict[str, str] = {
        "1": "TAD Architecture",
        "2": "A/B Compartments",
        "3": "Insulation Profile",
        "4": "Loop Registry",
        "5": "Saliency",
        "6": "Variant Modeller",
        "7": "Export",
    }

    while True:
        clear_screen_completely()
        width, height = console.size
        now = time.time()
        narrow = width < 110

        # Build tab bar (first word of each tab name on narrow terminals)
        tabs_fmt = [
            (f"[bold chartreuse1]⬢ [{k}] {name.split()[0] if narrow else name}[/bold chartreuse1]"
             if current_tab == k else f"[dim]  [{k}] {name.split()[0] if narrow else name}[/dim]")
            for k, name in TAB_NAMES.items()
        ]
        nav_rows: List[Text] = []
        for tab_markup in tabs_fmt:
            tab_text = Text.from_markup(tab_markup)
            if nav_rows and nav_rows[-1].cell_len + 3 + tab_text.cell_len <= width - 4:
                nav_rows[-1].append(" │ ", style="dim")
                nav_rows[-1].append_text(tab_text)
            else:
                nav_rows.append(tab_text)
        nav_text = Text("\n", justify="center").join(nav_rows)
        nav_lines = len(nav_rows)

        # Screen rows: provenance (1) + workspace + tab bar (+2 border) + hint (1) + prompt (1)
        ws_h = max(8, height - nav_lines - 5)
        ws_inner_h = ws_h - 2
        ws_inner_w = max(20, width - 4)
        # Content width/height inside a nested panel within the workspace
        sub_w = max(16, ws_inner_w - 4)
        sub_h = max(4, ws_inner_h - 2)

        workspace_content: List[Any] = []
        workspace_border = "chartreuse1"

        if current_tab == "1":
            # ── TAD Architecture ──────────────────────────────────────────────
            side_by_side = ws_inner_w >= 70
            n_listed = max(1, min(10, (ws_inner_h if side_by_side else ws_inner_h // 2) - 9))
            tad_lines = [
                "[bold chartreuse1]TAD Architecture[/bold chartreuse1]\n",
                f"[bold white]Boundaries found:[/bold white] [chartreuse1]{len(boundaries)}[/chartreuse1]",
            ]
            if len(boundaries) >= 2:
                gaps = [boundaries[i + 1]["bin"] - boundaries[i]["bin"] for i in range(len(boundaries) - 1)]
                avg_gap = sum(gaps) / len(gaps)
                tad_lines.append(f"[bold white]Avg TAD size:[/bold white] [chartreuse1]~{avg_gap:.1f} bins[/chartreuse1]")
            tad_lines.extend(["", "[bold white]Boundary bins:[/bold white]"])
            for i, b in enumerate(boundaries[:n_listed]):
                bp_pos = start_bp + b["bin"] * bin_size_bp
                tad_lines.append(
                    f"  [{i+1}] bin {b['bin']:3d}  "
                    f"str [chartreuse1]{b['boundary_strength']:.3f}[/chartreuse1]"
                    + (f"  ({bp_pos/1000:.0f} kb)" if seq_len > 0 else "")
                )
            if len(boundaries) > n_listed:
                tad_lines.append(f"  [dim]...+{len(boundaries)-n_listed} more[/dim]")
            tad_lines.extend([
                "", "[dim]Insulation score minima = TAD boundary positions.[/dim]",
                "[dim]Marks where adjacent chromatin domains separate.[/dim]",
            ])
            side_panel = Panel(
                Text.from_markup("\n".join(tad_lines)),
                border_style="dim chartreuse1",
                padding=(0, 1),
                height=ws_inner_h if side_by_side else None,
            )
            if side_by_side:
                map_group = render_matrix_double_res(matrix, "wt", max_height=ws_inner_h,
                                                     max_width=(ws_inner_w - 2) * 3 // 5)
                grid_t = Table.grid(expand=True)
                grid_t.add_column(ratio=3)
                grid_t.add_column(width=2)
                grid_t.add_column(ratio=2)
                grid_t.add_row(map_group, "", side_panel)
                workspace_content.append(grid_t)
            else:
                map_group = render_matrix_double_res(
                    matrix, "wt", max_height=max(8, ws_inner_h // 2 + 2), max_width=ws_inner_w)
                side_panel.height = max(3, ws_inner_h - len(map_group.renderables))
                workspace_content.append(map_group)
                workspace_content.append(side_panel)

        elif current_tab == "2":
            # ── A/B Compartments ──────────────────────────────────────────────
            workspace_border = "#0ea5e9"
            a_count = compartments.count("A")
            b_count = compartments.count("B")
            tot = len(compartments)
            bar_cols = max(8, sub_w - 2)
            ab_bar_chars = "".join(
                "[bold chartreuse1]█[/bold chartreuse1]"
                if compartments[min(tot - 1, c * tot // bar_cols)] == "A"
                else "[bold #0ea5e9]█[/bold #0ea5e9]"
                for c in range(bar_cols)
            )
            max_ev = max(abs(v) for v in eigvec) or 1.0
            ev_bar_w = max(10, min(60, sub_w - 20))
            ev_lines: List[str] = [
                "[bold #0ea5e9]First Eigenvector (PC1)[/bold #0ea5e9]",
                "[dim]Positive=A (active)   Negative=B (inactive)[/dim]",
                "",
            ]
            # One row per bin, or averaged groups of bins when the panel is short
            ev_rows, ev_labels = _group_track(eigvec, max(3, sub_h - 7))
            for label, v in zip(ev_labels, ev_rows):
                norm_v = v / max_ev
                bar_len = int(abs(norm_v) * (ev_bar_w // 2))
                half = ev_bar_w // 2
                if v >= 0:
                    bar_part = " " * half + "[chartreuse1]" + "█" * bar_len + "[/chartreuse1]"
                else:
                    bar_part = " " * (half - bar_len) + "[#0ea5e9]" + "█" * bar_len + "[/#0ea5e9]"
                bar_part += " " * (ev_bar_w - half - (bar_len if v >= 0 else 0))
                comp_label = "[chartreuse1]A[/chartreuse1]" if v >= 0 else "[#0ea5e9]B[/#0ea5e9]"
                ev_lines.append(f"  {label:>3} {bar_part} {comp_label}  {v:+.3f}")
            ev_lines.extend([
                "",
                f"[chartreuse1]A active: {a_count}/{tot} ({a_count/tot*100:.0f}%)[/chartreuse1]  "
                f"[#0ea5e9]B inactive: {b_count}/{tot} ({b_count/tot*100:.0f}%)[/#0ea5e9]",
            ])
            workspace_content.append(Panel(
                Group(
                    Text.from_markup(f"{ab_bar_chars}\n"),
                    *[Text.from_markup(l) for l in ev_lines],
                ),
                border_style="#0ea5e9",
                title="[bold #0ea5e9] A/B COMPARTMENTS [/bold #0ea5e9]",
                padding=(0, 1),
                height=ws_inner_h,
            ))

        elif current_tab == "3":
            # ── Insulation Profile ────────────────────────────────────────────
            workspace_border = "yellow"
            bnd_set = {b["bin"] for b in boundaries}
            chart = _render_bar_chart_1d(
                insulation,
                width=max(10, min(60, sub_w - 20)),
                markers=list(bnd_set),
                high_color="yellow",
                marker_color="red",
                max_rows=max(3, sub_h - 6),
            )
            sal_lines = [
                "[bold yellow]Insulation Score Profile[/bold yellow]",
                "[dim]Lower score = higher insulation → likely TAD boundary[/dim]",
                "[dim red]◄ markers = called TAD boundaries[/dim red]",
                "",
            ] + chart + [
                "",
                f"[bold white]min:[/bold white] {min(insulation):.3f}  "
                f"[bold white]max:[/bold white] {max(insulation):.3f}  "
                f"[bold white]mean:[/bold white] {sum(insulation)/len(insulation):.3f}  "
                f"[bold white]n_boundaries:[/bold white] {len(boundaries)}",
            ]
            workspace_content.append(Panel(
                Group(*[Text.from_markup(l) for l in sal_lines]),
                border_style="yellow",
                title="[bold yellow] INSULATION SCORE [/bold yellow]",
                padding=(0, 1),
                height=ws_inner_h,
            ))

        elif current_tab == "4":
            # ── Loop Anchor Registry ──────────────────────────────────────────
            workspace_border = "#bb9af7"
            tbl_l = Table(
                show_header=True,
                header_style="bold #bb9af7",
                border_style="dim",
                title="[bold #bb9af7]Predicted CTCF Loop Anchors[/bold #bb9af7]",
            )
            wide_tbl = ws_inner_w >= 90
            tbl_l.add_column("Rank", width=5 if wide_tbl else None, justify="right", no_wrap=True)
            tbl_l.add_column("Anchor 1", width=10 if wide_tbl else None, justify="right", no_wrap=True)
            tbl_l.add_column("Anchor 2", width=10 if wide_tbl else None, justify="right", no_wrap=True)
            tbl_l.add_column("Distance", width=10 if wide_tbl else None, justify="right", no_wrap=True)
            tbl_l.add_column("Contact Score" if wide_tbl else "Score", width=14 if wide_tbl else None,
                             justify="right", no_wrap=True)
            if wide_tbl:
                tbl_l.add_column("Est. Locus", width=22, no_wrap=True)
            # title + borders/header (4) + totals (4)
            n_listed = max(1, ws_inner_h - 9)
            for rank, (bin1, bin2, score) in enumerate(loop_anchors[:n_listed], 1):
                dist = bin2 - bin1
                pos_str = (
                    f"{(start_bp + bin1*bin_size_bp)/1000:.0f}k–{(start_bp + bin2*bin_size_bp)/1000:.0f}k"
                    if seq_len > 0 else "—"
                )
                sc = "chartreuse1" if score > 0.7 else "#bb9af7" if score > 0.4 else "dim"
                row = [
                    str(rank), str(bin1), str(bin2),
                    f"{dist} bins",
                    f"[{sc}]{score:.4f}[/{sc}]",
                ]
                if wide_tbl:
                    row.append(f"[dim]{pos_str}[/dim]")
                tbl_l.add_row(*row)
            workspace_content.append(tbl_l)
            if loop_anchors:
                dists = [b2 - b1 for b1, b2, _ in loop_anchors]
                mean_d = sum(dists) / len(dists)
                shown = "" if n_listed >= len(loop_anchors) else f" (top {n_listed} shown)"
                workspace_content.append(Text.from_markup(
                    f"\n  [bold white]Total:[/bold white] [#bb9af7]{len(loop_anchors)}{shown}[/#bb9af7]  "
                    f"[bold white]Mean loop dist:[/bold white] [#bb9af7]{mean_d:.1f} bins[/#bb9af7]"
                    + (f" (~{mean_d*bin_size_bp/1000:.0f} kb)" if seq_len > 0 else "")
                ))
            workspace_content.append(Text.from_markup(
                "\n  [dim]High-intensity off-diagonal contacts = predicted CTCF-mediated loops.[/dim]"
            ))

        elif current_tab == "5":
            # ── Saliency / Attribution ────────────────────────────────────────
            workspace_border = "#f7768e"
            top_idx = sorted(range(len(saliency)), key=lambda i: saliency[i], reverse=True)[:5]
            chart_s = _render_bar_chart_1d(
                saliency,
                width=max(10, min(60, sub_w - 20)),
                markers=top_idx,
                high_color="#f7768e",
                marker_color="yellow",
                max_rows=max(3, sub_h - 16),
            )
            sal_lines2 = [
                "[bold #f7768e]Nucleotide Attribution / Saliency Landscape[/bold #f7768e]",
                "[dim]Per-bin sequence importance for contact map prediction[/dim]",
                "[dim yellow]◄ top-5 most influential bins[/dim yellow]",
                "",
            ] + chart_s + [
                "", "[bold white]Top influential regions:[/bold white]",
            ]
            for i, idx in enumerate(top_idx, 1):
                bp_pos = start_bp + idx * bin_size_bp
                sal_lines2.append(
                    f"  {i}. bin {idx:3d}  saliency [bold #f7768e]{saliency[idx]:.4f}[/bold #f7768e]"
                    + (f"  ({bp_pos/1000:.0f} kb)" if seq_len > 0 else "")
                )
            sal_lines2.extend([
                "",
                "[dim]Hook: swap generate_simulated_saliency() with real gradient-based[/dim]",
                "[dim]attribution when GoldBEAM model is trained.[/dim]",
            ])
            workspace_content.append(Panel(
                Group(*[Text.from_markup(l) for l in sal_lines2]),
                border_style="#f7768e",
                title="[bold #f7768e] SALIENCY / ATTRIBUTION [/bold #f7768e]",
                padding=(0, 1),
                height=ws_inner_h,
            ))

        elif current_tab == "6":
            # ── Variant Modeller ──────────────────────────────────────────────
            workspace_border = "#ff9e64"
            side_by_side = ws_inner_w >= 70
            right_w = (ws_inner_w - 2) * 2 // 5 if side_by_side else ws_inner_w
            if vt_applied:
                delta_size = max(6, min(n_bins, 20, right_w - 10,
                                        (ws_inner_h if side_by_side else ws_inner_h // 2) - 12))
                delta_lines = _render_delta_matrix_text(vt_delta, max_size=delta_size)
                right_lines = [
                    "[bold #ff9e64]ΔContact Map (Mutant − WT)[/bold #ff9e64]",
                    f"[dim]{vt_desc}[/dim]",
                    "",
                ] + delta_lines + [
                    "",
                    f"[bold white]Mean |ΔContact|:[/bold white] [#ff9e64]{vt_stats['mean_abs_delta']:.4f}[/#ff9e64]",
                    f"[bold white]Max gain:[/bold white] [bold red]+{vt_stats['max_gain']:.4f}[/bold red]   "
                    f"[bold white]Max loss:[/bold white] [bold #0ea5e9]{vt_stats['max_loss']:.4f}[/bold #0ea5e9]",
                    "",
                    "[dim]Type 'reset' to restore wildtype.[/dim]",
                ]
            else:
                right_lines = [
                    "[bold #ff9e64]Variant Effect Predictor[/bold #ff9e64]",
                    "[dim]Apply a variant to see the predicted ΔContact map.[/dim]",
                    "",
                    "  [bold white]Commands:[/bold white]",
                    "  [chartreuse1]snp <pos_bp> <REF>><ALT>[/chartreuse1]",
                    "    e.g.  snp 500000 G>A",
                    "",
                    "  [chartreuse1]del <start_bp> <end_bp>[/chartreuse1]",
                    "    e.g.  del 200000 210000",
                    "",
                    "  [chartreuse1]reset[/chartreuse1]  — restore wildtype",
                    "",
                    "[dim]Enter command at the prompt below.[/dim]",
                ]
            delta_panel = Panel(
                Group(*[Text.from_markup(l) for l in right_lines]),
                border_style="#ff9e64",
                padding=(0, 1),
                height=ws_inner_h if side_by_side else None,
            )
            if side_by_side:
                wt_map = render_matrix_double_res(matrix, "wt", max_height=ws_inner_h,
                                                  max_width=(ws_inner_w - 2) * 3 // 5)
                vt_grid = Table.grid(expand=True)
                vt_grid.add_column(ratio=3)
                vt_grid.add_column(width=2)
                vt_grid.add_column(ratio=2)
                vt_grid.add_row(wt_map, "", delta_panel)
                workspace_content.append(vt_grid)
            else:
                wt_map = render_matrix_double_res(
                    matrix, "wt", max_height=max(8, ws_inner_h // 2), max_width=ws_inner_w)
                delta_panel.height = max(3, ws_inner_h - len(wt_map.renderables))
                workspace_content.append(wt_map)
                workspace_content.append(delta_panel)

        elif current_tab == "7":
            # ── Export Center ─────────────────────────────────────────────────
            workspace_border = "dim"
            export_dir = _make_export_dir()
            exp_lines = [
                "[bold chartreuse1]Export Center[/bold chartreuse1]",
                f"[dim]Output directory: {export_dir}[/dim]",
                f"[dim]Locus: {locus_name}[/dim]",
                "",
                "[bold white]Available exports:[/bold white]",
                "",
                "  [chartreuse1]e1[/chartreuse1]  TAD boundaries         → .bed   (IGV/Juicebox compatible)",
                "  [chartreuse1]e2[/chartreuse1]  A/B compartments       → .bed   (per-bin A/B assignment)",
                "  [chartreuse1]e3[/chartreuse1]  Loop anchor registry   → .tsv   (ranked CTCF loop pairs)",
                "  [chartreuse1]e4[/chartreuse1]  Saliency / attribution → .bedGraph",
                "  [chartreuse1]ea[/chartreuse1]  Export ALL of the above",
                "",
                "[dim]All exported files carry provenance headers stamped with:[/dim]",
                f"[dim]  {provenance}[/dim]",
            ]
            if toast_msg and now < toast_expire:
                exp_lines.extend(["", f"[bold chartreuse1]✓ {toast_msg}[/bold chartreuse1]"])
            workspace_content.append(Panel(
                Group(*[Text.from_markup(l) for l in exp_lines]),
                border_style="dim",
                title="[bold chartreuse1] EXPORT CENTER [/bold chartreuse1]",
                padding=(0, 2),
                height=ws_inner_h,
            ))

        # ── Assemble layout ───────────────────────────────────────────────────
        workspace_panel = Panel(
            Group(*workspace_content),
            title=f"[bold chartreuse1] {TAB_NAMES.get(current_tab, '')} [/bold chartreuse1]",
            border_style=workspace_border,
            padding=(0, 1),
            height=ws_h,
        )
        nav_panel = Panel(
            nav_text,
            title="[bold chartreuse1] ⬡ SWAEV GENOMICS INTERPRETABILITY SUITE [/bold chartreuse1]",
            border_style="chartreuse1",
        )
        prov_text = Text.from_markup(
            f"  [dim reverse] ⚠ {provenance} [/dim reverse]"
            f"  [dim]locus: {locus_name}  │  bins: {n_bins}  │  seq: {seq_len:,} bp[/dim]"
        )
        prov_text.no_wrap = True
        prov_text.overflow = "ellipsis"
        main_layout = Table.grid(expand=True)
        main_layout.add_row(prov_text)
        main_layout.add_row(workspace_panel)
        main_layout.add_row(nav_panel)
        console.print(main_layout)

        # Tabs are listed in the bar above; tab 6 lists its commands and tab 7
        # its export codes, so the hint only names what isn't already on screen
        if current_tab in ("6", "7"):
            hint = "  [dim]? help │ q exit[/dim]"
        else:
            hint = "  [dim]snp/del: variant modeller │ ? help │ q exit[/dim]"
        console.print(hint, no_wrap=True, overflow="ellipsis")

        choice = console.input(Text("» interpret> ", style="bold chartreuse1")).strip()

        if not choice or choice.lower() in ("q", "quit", "exit", "back"):
            break

        lc = choice.lower()

        if lc in ("?", "help", "h"):
            run_suite_help(current_tab)
            continue

        if lc in TAB_NAMES:
            current_tab = lc
            continue

        # Variant modeller commands
        if lc == "reset":
            vt_matrix = [row[:] for row in matrix]
            vt_delta = [[0.0] * n_bins for _ in range(n_bins)]
            vt_stats = {"mean_abs_delta": 0.0, "max_gain": 0.0, "max_loss": 0.0}
            vt_desc = "Variant reset — showing wildtype"
            vt_applied = False
            current_tab = "6"
            continue

        if lc.startswith("snp "):
            parts = choice.split()
            if len(parts) == 3 and ">" in parts[2]:
                try:
                    pos_bp = int(parts[1])
                    ref_b, alt_b = parts[2].upper().split(">", 1)
                    alt_b = alt_b[0]
                    token_pos = min(pos_bp, max(0, seq_len - 1))
                    bin_idx = token_pos * n_bins // max(1, seq_len)
                    vt_matrix = _perturb_matrix_near_bins(matrix, [bin_idx], strength=0.3)
                    vt_delta = compute_delta_matrix(matrix, vt_matrix)
                    vt_stats = compute_delta_stats(vt_delta)
                    vt_desc = f"SNP pos {pos_bp:,}  {ref_b}>{alt_b}  (bin {bin_idx})"
                    vt_applied = True
                    current_tab = "6"
                    continue
                except (ValueError, IndexError):
                    pass

        if lc.startswith("del "):
            parts = choice.split()
            if len(parts) == 3:
                try:
                    del_start = int(parts[1])
                    del_end = int(parts[2])
                    del_center = ((del_start + del_end) // 2) * n_bins // max(1, seq_len)
                    vt_matrix = _perturb_matrix_near_bins(matrix, [del_center], strength=0.5)
                    vt_delta = compute_delta_matrix(matrix, vt_matrix)
                    vt_stats = compute_delta_stats(vt_delta)
                    vt_desc = f"DEL {del_start:,}–{del_end:,} ({del_end - del_start:,} bp)"
                    vt_applied = True
                    current_tab = "6"
                    continue
                except (ValueError, IndexError):
                    pass

        # Export commands
        if lc in ("e1", "e2", "e3", "e4", "ea"):
            exported: List[str] = []
            try:
                if lc in ("e1", "ea"):
                    p = export_tad_bed(boundaries, chrom, start_bp, bin_size_bp, provenance)
                    exported.append(f"TAD → {os.path.basename(p)}")
                if lc in ("e2", "ea"):
                    p = export_compartment_bed(compartments, eigvec, chrom, start_bp, bin_size_bp, provenance)
                    exported.append(f"AB → {os.path.basename(p)}")
                if lc in ("e3", "ea"):
                    p = export_loop_tsv(loop_anchors, chrom, start_bp, bin_size_bp, provenance)
                    exported.append(f"Loops → {os.path.basename(p)}")
                if lc in ("e4", "ea"):
                    p = export_saliency_bedgraph(saliency, chrom, start_bp, bin_size_bp, provenance)
                    exported.append(f"Saliency → {os.path.basename(p)}")
                toast_msg = "  ".join(exported)
                if on_export:
                    on_export([item.split(" → ", 1)[1] for item in exported])
            except Exception as e_exp:
                toast_msg = f"Export error: {e_exp}"
            toast_expire = time.time() + 6.0
            current_tab = "7"
            continue

    clear_screen_completely()


# ---------------------------------------------------------------------------
# Contextual Help Overlays
# ---------------------------------------------------------------------------

_SUITE_TAB_HELP: Dict[str, Any] = {
    "1": {
        "title": "TAD Architecture",
        "subtitle": "Topologically Associating Domains",
        "sections": [
            ("What are TADs?",
             "TADs are self-interacting chromosomal domains typically 100 kb–3 Mb in size. "
             "DNA sequences within a TAD preferentially interact with each other over sequences "
             "in adjacent domains. They are fundamental units of 3D genome organisation — "
             "genes and enhancers inside the same TAD are far more likely to interact than "
             "those separated by a TAD boundary."),
            ("Reading the contact map",
             "Warmer colours (yellow/red) = higher contact frequency. "
             "TAD blocks appear as bright triangles along the diagonal. "
             "The stronger the triangle, the more self-contained the domain. "
             "Stripes extending off-diagonal indicate loop extrusion activity."),
            ("Boundary annotations",
             "The right-hand table lists predicted TAD boundaries. "
             "Insulation Score shows the local contact minimum (lower = stronger boundary). "
             "Boundary Strength is the depth of the insulation valley normalised to [0, 1]."),
            ("Biological significance",
             "Loss of a TAD boundary can bring an oncogene into contact with an active "
             "enhancer — this is the CTCF-boundary disruption mechanism seen in many cancers. "
             "GoldBEAM lets you test this directly with the Variant Modeller (Tab 6)."),
        ],
    },
    "2": {
        "title": "A/B Compartments",
        "subtitle": "Chromatin activity states at megabase scale",
        "sections": [
            ("What are A/B compartments?",
             "Compartments are the largest-scale feature of genome organisation. "
             "Type A compartments are gene-rich, open chromatin, transcriptionally active "
             "(associated with H3K27ac, H3K4me3). "
             "Type B compartments are gene-poor, compact heterochromatin, "
             "transcriptionally silent (associated with H3K9me3, laminB)."),
            ("How GoldBEAM calls them",
             "1. Compute O/E matrix (observed contacts ÷ expected from distance decay). "
             "2. Pearson-correlate each bin's contact profile across all other bins. "
             "3. Extract the first eigenvector of the correlation matrix via power iteration. "
             "4. Sign: positive eigenvector bins → A; negative → B. "
             "Sign is ambiguous (eigenvectors can be negated) — GoldBEAM uses the convention "
             "that the higher-GC half is A."),
            ("Reading the display",
             "[green]Green bars[/green] = A compartment (active). "
             "[blue]Blue bars[/blue] = B compartment (inactive). "
             "Bar height = eigenvector magnitude (strength of compartment identity). "
             "Sharp sign changes mark compartment transitions."),
            ("Export",
             "Tab 7 → e2 exports a BED file with A/B assignments and eigenvector values "
             "for downstream analysis in IGV, UCSC Browser, or deeptools."),
        ],
    },
    "3": {
        "title": "Insulation Profile",
        "subtitle": "1D summary of TAD boundary strength",
        "sections": [
            ("What is the insulation score?",
             "For each genomic bin, we sum all contacts in a diamond-shaped window centred "
             "on that bin along the diagonal (Crawford et al. 2016 method). "
             "Bins at TAD boundaries receive fewer contacts than bins inside TADs — "
             "they are 'insulated' from cross-domain interactions. "
             "A local minimum in the insulation score indicates a boundary."),
            ("Reading the chart",
             "X-axis = genomic bins left to right. "
             "Y-axis = insulation score (0 = strongest boundary; 1 = no insulation). "
             "Yellow tick marks (▲) = called TAD boundaries. "
             "Wider valleys = more prominent, biologically stronger boundaries."),
            ("Limitations",
             "Resolution is limited by bin size. At 4 kb bins (default) the score is "
             "sensitive to individual CTCF binding. At 40 kb it reflects domain-level "
             "architecture. GoldBEAM's bin count is determined by the model's output grid."),
        ],
    },
    "4": {
        "title": "Loop Anchor Registry",
        "subtitle": "Predicted CTCF-mediated chromatin loops",
        "sections": [
            ("What are chromatin loops?",
             "Loops are point interactions between distant loci mediated by cohesin-extrusion "
             "and blocked by convergent CTCF motifs. They appear as bright off-diagonal dots "
             "in the contact map. Loops connect enhancers to gene promoters and help establish "
             "TAD boundaries."),
            ("How GoldBEAM identifies them",
             "We take the top-N off-diagonal contact scores (requiring a minimum genomic "
             "separation of 6 bins to exclude diagonal noise). These are the highest-confidence "
             "predicted loop interactions. After model training, this will be replaced with "
             "a stripes + dot detector using the observed/expected map."),
            ("Reading the table",
             "Rank: ordered by contact score (1 = strongest). "
             "Bin 1 / Bin 2: zero-indexed genomic bin coordinates. "
             "Distance: separation in bins (multiply by bin_size_bp for base pairs). "
             "Contact Score: raw contact frequency in the predicted map."),
            ("Export",
             "Tab 7 → e3 exports a TSV with genomic coordinates. "
             "Compatible with CTCF ChIP-seq peak overlap analysis in bedtools."),
        ],
    },
    "5": {
        "title": "Sequence Saliency",
        "subtitle": "Per-bin input attribution landscape",
        "sections": [
            ("What is saliency?",
             "Saliency measures how much each input DNA window contributes to the model's "
             "output. High saliency = those bases strongly influence the predicted contact map. "
             "In trained deep learning models this is computed as the gradient of the output "
             "with respect to the input (∂output/∂input)."),
            ("Current status (SIMULATED)",
             "Before model training, saliency is approximated by GC content per bin — "
             "a weak but non-trivial proxy since GC-rich regions correlate with active "
             "chromatin. After training, real gradient-based attribution (integrated gradients "
             "or GradCAM) will be wired through generate_simulated_saliency()."),
            ("Reading the chart",
             "X-axis = genomic bins. Y-axis = attribution score. "
             "Gold/yellow markers (◆) = top-5 highest-attribution bins. "
             "These are the sequence windows most influential for the predicted structure."),
            ("Use cases",
             "Identify transcription factor binding sites driving domain organisation. "
             "Design CRISPR experiments at high-saliency positions. "
             "Explain why a variant in a particular bin disrupts a TAD boundary."),
        ],
    },
    "6": {
        "title": "Variant Modeller",
        "subtitle": "In silico mutagenesis — predict structural consequences of variants",
        "sections": [
            ("What it does",
             "Apply a sequence variant (SNP or deletion), re-predict the contact map, "
             "and visualise the change as a ΔContact heatmap. "
             "This is the core clinical/research workflow: given a patient VCF variant, "
             "does it disrupt a TAD boundary or create a neo-loop?"),
            ("Commands",
             "snp <pos> <REF>><ALT>   — point mutation at base position (1-indexed)\n"
             "  Example:  snp 500000 G>A\n\n"
             "del <start> <end>       — deletion from start to end bp\n"
             "  Example:  del 450000 520000\n\n"
             "reset                   — restore wildtype"),
            ("Reading the ΔContact map",
             "[red]Red cells[/red] = contact gain (the variant creates new interactions). "
             "[blue]Blue cells[/blue] = contact loss (the variant disrupts existing interactions). "
             "Diagonal red/blue striping = TAD boundary shift. "
             "Off-diagonal red dot = neo-loop formation."),
            ("Biological interpretation",
             "Contact loss at a boundary position = boundary weakening (TAD fusion risk). "
             "This is the CTCF-disruption cancer mechanism. "
             "Contact gain between an oncogene and an active enhancer = activation risk. "
             "Mean |Δ| > 0.15 is considered a structurally significant variant."),
        ],
    },
    "7": {
        "title": "Export Centre",
        "subtitle": "Genomics-standard file formats for downstream analysis",
        "sections": [
            ("Export commands",
             "e1  →  TAD boundaries (.bed)\n"
             "e2  →  A/B compartments (.bed with eigenvector scores)\n"
             "e3  →  Loop anchors (.tsv with genomic coordinates)\n"
             "e4  →  Saliency track (.bedGraph for IGV/UCSC Browser)\n"
             "ea  →  All four formats at once"),
            ("File locations",
             "All exports land in ~/goldbeam_exports/ with timestamped filenames. "
             "Each file includes a provenance header documenting the locus, timestamp, "
             "GoldBEAM version, and a SIMULATED stamp until the model is trained."),
            ("BED format (e1, e2)",
             "chrom  chromStart  chromEnd  name  score  strand\n"
             "Compatible with UCSC Browser, IGV, bedtools, deeptools."),
            ("bedGraph format (e4)",
             "chrom  chromStart  chromEnd  value\n"
             "Load directly into IGV as a quantitative track. "
             "Use bedtools genomecov or deeptools bamCoverage for normalisation."),
        ],
    },
}


def _run_scroll_view(
    build: Any,
    title: str,
    border_style: str,
    exit_label: str = "back",
) -> None:
    """
    Full-screen scrollable page for long help content.

    build(width) returns the renderables for a given content width; it is
    re-run whenever the terminal width changes, so text re-wraps on resize.
    Keys: ↑↓ / j k line · PgUp PgDn / Space page · Home End · Enter / Esc / q close.
    """
    if not sys.stdin.isatty():
        console.print(Panel(Group(*build(max(10, console.size.width - 6))),
                            title=title, border_style=border_style, padding=(0, 2)))
        return

    import termios, tty, select as _sel
    from rich.segment import Segment, Segments

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    offset = 0
    built_for_width = -1
    lines: List[List[Segment]] = []

    try:
        tty.setcbreak(fd)
        with Live(console=console, screen=True, auto_refresh=False) as live:
            while True:
                term_w, term_h = console.size
                inner_w = max(10, term_w - 6)  # border + 2-cell padding each side
                view_h = max(1, term_h - 2)
                if term_w != built_for_width:
                    lines = console.render_lines(
                        Group(*build(inner_w)),
                        console.options.update(width=inner_w),
                        pad=True,
                    )
                    built_for_width = term_w
                max_offset = max(0, len(lines) - view_h)
                offset = max(0, min(offset, max_offset))

                segs: List[Segment] = []
                for line in lines[offset:offset + view_h]:
                    segs.extend(line)
                    segs.append(Segment.line())
                if len(lines) > view_h:
                    status = (f" {offset + 1}–{min(len(lines), offset + view_h)} of {len(lines)}"
                              f"  ↑↓ PgUp PgDn scroll  ⏎ {exit_label} ")
                else:
                    status = f" ⏎ {exit_label} "
                live.update(Panel(
                    Segments(segs[:-1]),
                    title=title,
                    subtitle=Text(status, style="dim"),
                    subtitle_align="right",
                    border_style=border_style,
                    padding=(0, 2),
                    height=term_h,
                ))
                live.refresh()

                ready, _, _ = _sel.select([fd], [], [], 0.25)
                if not ready:
                    continue
                ch = os.read(fd, 1)
                if ch in (b"\r", b"\n", b"q", b"Q", b"\x03", b"\x04"):
                    break
                if ch == b"\x1b":
                    seq = b""
                    while True:
                        more, _, _ = _sel.select([fd], [], [], 0.05)
                        if not more:
                            break
                        seq += os.read(fd, 1)
                        if seq[-1:] in b"ABCDHF~":
                            break
                    if not seq:  # bare Esc
                        break
                    if seq.endswith(b"A"):
                        offset -= 1
                    elif seq.endswith(b"B"):
                        offset += 1
                    elif seq.endswith(b"5~"):
                        offset -= view_h - 1
                    elif seq.endswith(b"6~"):
                        offset += view_h - 1
                    elif seq.endswith(b"H") or seq.endswith(b"1~"):
                        offset = 0
                    elif seq.endswith(b"F") or seq.endswith(b"4~"):
                        offset = max_offset
                elif ch == b" ":
                    offset += view_h - 1
                elif ch == b"k":
                    offset -= 1
                elif ch == b"j":
                    offset += 1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _help_body(body: str, indent: int) -> List[Any]:
    """Help paragraphs as indented, width-wrapped renderables (one per source line)."""
    return [Padding(Text.from_markup(raw_line), (0, 0, 0, indent)) for raw_line in body.split("\n")]


def run_suite_help(current_tab: str) -> None:
    """Full-screen contextual help for the current interpretability suite tab."""
    info = _SUITE_TAB_HELP.get(current_tab, {})
    title = info.get("title", f"Tab {current_tab}")
    subtitle = info.get("subtitle", "")
    sections = info.get("sections", [])

    def _build(width: int) -> List[Any]:
        lines: List[Any] = []
        lines.append(Text.from_markup(
            f"[bold chartreuse1]Interpretability Suite — {title}[/bold chartreuse1]"
            f"  [dim]{subtitle}[/dim]"
        ))
        lines.append(Rule(style="chartreuse1"))

        for sec_title, sec_body in sections:
            lines.append(Text.from_markup(f"[bold yellow]{sec_title}[/bold yellow]"))
            lines.extend(_help_body(sec_body, 2))
            lines.append(Text(""))

        # Suite navigation reminder
        lines.append(Rule(style="dim"))
        tab_list = "  ".join(
            f"[bold chartreuse1][{k}][/bold chartreuse1]" if k == current_tab
            else f"[dim][{k}][/dim]"
            for k in "1234567"
        )
        lines.append(Text.from_markup(f"Tabs: {tab_list}"))
        lines.append(Text.from_markup(
            "[dim]1 TAD Architecture  2 A/B Compartments  3 Insulation  "
            "4 Loop Registry  5 Saliency  6 Variant Modeller  7 Export[/dim]"
        ))
        return lines

    _run_scroll_view(_build, "[bold chartreuse1] ⬡ Interpretability Suite — Help [/bold chartreuse1]",
                     "chartreuse1")
    clear_screen_completely()


# ── Flight Simulator Help ─────────────────────────────────────────────────────

_FS_TOOL_HELP: Dict[str, Dict[str, Any]] = {
    "1": {
        "icon": "◐",
        "name": "Sequence Analytics",
        "tagline": "GC skew · Shannon entropy · nucleotide composition",
        "sections": [
            ("GC SKEW  (G−C)/(G+C)",
             "Measures strand asymmetry per genomic bin. Positive values = G-strand "
             "enrichment. Reversal points mark replication origins and transcription "
             "start sites. CpG islands appear as local skew inflections."),
            ("SHANNON ENTROPY  H = −Σ p·log₂p",
             "Sequence complexity per bin. Low entropy = repetitive / low-complexity "
             "sequence (tandem repeats, microsatellites, homopolymers). High entropy = "
             "complex DNA with strong combinatorial information content."),
            ("COMPOSITION STATS",
             "GC% — fraction of G/C bases. "
             "Tm — estimated melting temperature (Wallace rule: 2°C per AT pair, 4°C per GC). "
             "CpG O/E — CpG dinucleotide observed/expected ratio; mammalian norm 0.60–0.80 "
             "due to methylation-driven depletion. "
             "Complexity — Shannon entropy of 3-mer distribution (Wootton–Federhen, 1993)."),
        ],
    },
    "2": {
        "icon": "⌦",
        "name": "Virtual Deletion Probe",
        "tagline": "In silico mutagenesis · SDI readout · ΔContact map",
        "sections": [
            ("ENTERING SIMULATION MODE",
             "Press M to toggle OBSERVATION → SIMULATION. A red command bar appears "
             "at the bottom of the HUD. Type a command and press Enter to apply it."),
            ("COMMANDS",
             "snp <pos> <REF>><ALT>   point mutation (1-indexed base position)\n"
             "  Example:  snp 500000 G>A\n"
             "\n"
             "del <start> <end>       deletion from start bp to end bp\n"
             "  Example:  del 450000 520000\n"
             "\n"
             "reset                   restore wildtype baseline"),
            ("SDI — STRUCTURAL DISRUPTION INDEX",
             "SDI = mean absolute ΔContact across the full predicted matrix. "
             "SDI ≥ 0.15 = structurally significant (TAD boundary disruption threshold). "
             "SDI ≥ 0.30 = severe structural rearrangement. "
             "A red ⚠ warning appears when this threshold is exceeded."),
            ("READING THE DELTA MAP",
             "Red cells = contact gain (new interactions created by the variant). "
             "Blue cells = contact loss (existing interactions disrupted). "
             "Diagonal red/blue striping = TAD boundary shift. "
             "Off-diagonal red dot = neo-loop formation event."),
            ("CTCF SCANNER SHORTCUT",
             "Press C to open the CTCF Motif Scanner overlay. Navigate with ↑↓ "
             "to an anchor of interest, then press Enter — it pre-fills this tool's "
             "deletion sandbox with that anchor's coordinates automatically."),
        ],
    },
    "3": {
        "icon": "⬡",
        "name": "Biophysical Profiler",
        "tagline": "Helical twist · bendability · CpG island track",
        "sections": [
            ("HELICAL TWIST  (Calladine & Drew 1984)",
             "Intrinsic rotational angle between consecutive base pairs derived from "
             "dinucleotide lookup tables. Range ≈ 33–35.5°/step. Low twist = wider "
             "minor groove (more accessible to proteins and transcription factors). "
             "CTCF preferentially binds at specific twist profiles."),
            ("BENDABILITY  (Brukner 1995 dinucleotide tables)",
             "DNA mechanical flexibility from dinucleotide rigidity parameters. "
             "High bendability = flexible DNA that wraps nucleosomes easily. "
             "Low bendability = stiff linker DNA. "
             "Nucleosome positioning correlates with alternating stiff/flexible regions."),
            ("CpG OBSERVED / EXPECTED",
             "CpG dinucleotide frequency relative to random expectation (p_C × p_G). "
             "Mammalian genome norm: 0.60–0.80 (methylation depletes CpGs over evolution). "
             "Bins with O/E > 0.6 are flagged ▲ as CpG island candidates — "
             "these are typically gene promoters and CTCF binding sites."),
        ],
    },
    "4": {
        "icon": "≋",
        "name": "Insulation Scoring",
        "tagline": "TAD barrier profiles and boundary table",
        "sections": [
            ("DIAMOND INSULATION SCORE  (Crawford 2016)",
             "For each genomic bin, sums all contacts within a diamond-shaped window "
             "centred on the diagonal. Bins at TAD boundaries receive fewer cross-domain "
             "contacts than bins inside domains — local minima = boundary positions."),
            ("READING THE CHART",
             "X-axis = genomic bins left to right. Y-axis = insulation score "
             "(0 = strongest barrier; 1 = no insulation). "
             "Red tick marks ▲ = called TAD boundaries. "
             "Wider and deeper valleys = more prominent, biologically stronger boundaries."),
            ("BOUNDARY TABLE",
             "Ranks all called boundaries by insulation valley depth. "
             "Insulation Score = raw minimum value at the boundary bin. "
             "Boundary Strength = valley depth normalised to [0, 1]. "
             "Press E to export as a .BED file for IGV or UCSC Browser."),
        ],
    },
    "5": {
        "icon": "⊞",
        "name": "Multi-Scale Dilation Check",
        "tagline": "d1/d2/d4/d8 contact head diagnostics",
        "sections": [
            ("DILATED CONVOLUTIONAL HEADS",
             "GoldBEAM uses 4 parallel dilated convolutional heads to capture contacts "
             "at different genomic scales in a single forward pass:\n"
             "  d1  0–100 kb        loops and CTCF-mediated point contacts\n"
             "  d2  100 kb–500 kb   sub-domain scale interactions\n"
             "  d4  500 kb–2 Mb     TAD-scale architecture\n"
             "  d8  2 Mb+           macro-domain and compartment scale"),
            ("EXPECTED RANGES",
             "Healthy mean contact per head: [0.05, 0.35]. "
             "Outside this range during training indicates head collapse or gradient issues. "
             "Pre-training stubs show SIMULATED values — range check will flag them, "
             "which is expected before real weights are loaded."),
            ("CONTACT DECAY CURVE  P(s)",
             "Contact probability as a function of genomic distance s. "
             "Should decrease monotonically — a universal feature of genome organisation. "
             "Flat decay = matrix artefact. Sharp early drop = strong domain insulation. "
             "After training this will reflect true GoldBEAM model predictions."),
        ],
    },
    "6": {
        "icon": "◍",
        "name": "Species-Embedding Bias",
        "tagline": "CpG depletion · repeat density · GC bias heuristics",
        "sections": [
            ("SPECIES INFERENCE HEURISTIC",
             "GoldBEAM is trained on mammalian genomes. This panel checks whether the "
             "loaded sequence matches the expected compositional fingerprint:\n"
             "  CpG O/E < 0.45 + GC% > 35%  →  methylated mammalian DNA ✓\n"
             "  CpG O/E > 1.0               →  invertebrate or prokaryote\n"
             "  GC% > 55%                   →  GC-rich organism (plant / bacteria)"),
            ("CpG DEPLETION PROFILE",
             "Mammalian methylation depletes CpG dinucleotides to ~60–80% of the "
             "expectation from random composition. Bins with high CpG O/E are active "
             "promoters or CpG islands — these are the sites most likely to harbour "
             "CTCF binding motifs and architectural protein occupancy."),
            ("REPEAT DENSITY",
             "Fraction of each bin consisting of tandem repeats (runs ≥ 4 identical "
             "consecutive bases). High repeat density = microsatellite or "
             "centromeric-like sequence. The model's attention will focus on the "
             "flanking unique sequence in these regions rather than the repeat itself."),
        ],
    },
    "7": {
        "icon": "⊡",
        "name": "Boundary Anchor Scan",
        "tagline": "CTCF density profile + predicted loop anchors",
        "sections": [
            ("CTCF DENSITY PROFILE",
             "Counts of CTCF core motif hits (CCGCGNGGG) per genomic bin. "
             "Peaks mark likely insulator positions. Top-5 density peaks are flagged ▲. "
             "Press C to open the full CTCF Motif Scanner overlay — it scans all six "
             "motif classes with genomic coordinates and one-click sandbox integration."),
            ("LOOP ANCHOR PAIRS",
             "Top 20 off-diagonal contact scores from the predicted matrix, "
             "requiring a minimum 6-bin separation to exclude diagonal noise. "
             "These are the highest-confidence predicted chromatin loop interactions. "
             "After model training, these will reflect true cohesin-extruded loops."),
            ("EXPORT",
             "Press E to export the anchor table as a .tsv file with genomic "
             "coordinates. Use bedtools intersect against CTCF ChIP-seq peaks "
             "to validate predicted loop anchors against experimental data."),
        ],
    },
    "8": {
        "icon": "⬛",
        "name": "Structural Disruption Map",
        "tagline": "24-bit true-colour ANSI chromatin contact matrix",
        "sections": [
            ("CONTACT MATRIX",
             "Full 40×40 predicted contact frequency map rendered at 2× vertical "
             "resolution using Unicode half-block characters (▄). "
             "Colour scale: purple → yellow → white = low → high contact frequency. "
             "Bright triangular blocks along the diagonal = TADs. "
             "Off-diagonal bright spots = chromatin loops."),
            ("DELTA OVERLAY  (Simulation Mode)",
             "Switch to SIMULATION mode (press M) and apply a variant using tool [2]. "
             "This panel overlays the ΔContact map: red = contact gain, blue = contact loss. "
             "The SDI score quantifies total structural perturbation. "
             "Panel border turns red when a variant is active."),
            ("CELL-LINE CONTEXT  (⇥ Tab)",
             "Press Tab to cycle the chromatin context applied to the contact matrix:\n"
             "  GM12878 — lymphoblastoid B-cell · sharp TAD boundaries · ENCODE tier 1\n"
             "  H1-hESC — embryonic stem cell · diffuse open chromatin\n"
             "  IMR90   — lung fibroblast · intermediate compaction\n"
             "The CELLULAR CONTEXT line in the header updates to reflect the active context."),
        ],
    },
    "9": {
        "icon": "⬡",
        "name": "GoldBEAM Prediction",
        "tagline": "O(N) chromatin contact predictor · model status · mission control",
        "sections": [
            ("MODEL ARCHITECTURE",
             "GoldBEAM is SWAEV's O(N) DNA-to-3D-contact-map predictor. "
             "The encoder maps raw nucleotide tokens to multi-scale latent representations; "
             "multiple prediction heads decode these into contact frequency matrices at "
             "resolutions d1, d2, d4, and d8 (matching Akita's dilation scheme). "
             "Current status: pre-training phase — weights frozen at encoder init."),
            ("BENCHMARK",
             "Akita (DeepMind / Bionano, 2021) achieves 0.832 Pearson correlation "
             "on held-out sequences for genome-wide contact prediction. "
             "GoldBEAM targets this as its primary training benchmark. "
             "All predictions shown in this build are SIMULATED outputs from a "
             "deterministic surrogate — not trained model weights."),
            ("GOLD SEQUENCE RADAR",
             "When tool [9] is active, the side-panel Sequence Radar turns amber/gold "
             "to signal GoldBEAM mission mode. The DNA helix colours shift from the "
             "active theme to #ffaa00 (amber) for GC-rich regions and #cc8800 for AT-rich. "
             "CTCF motif links retain their aquamarine colour as a structural landmark."),
            ("TRAINING PIPELINE  (upcoming)",
             "Model training is the next milestone after TUI MVP. "
             "The frozen encoder will be unfrozen in stages with Pearson correlation loss "
             "on each head. Simulated outputs will be replaced by live inference once "
             "weights are trained on ENCODE Hi-C datasets."),
        ],
    },
}


def run_fs_help(current_tool: str) -> None:
    """Full-screen contextual help for the Flight Simulator (all 9 tools + new features)."""
    info = _FS_TOOL_HELP.get(current_tool, {})
    icon = info.get("icon", "◈")
    name = info.get("name", f"Tool {current_tool}")
    tagline = info.get("tagline", "")
    sections = info.get("sections", [])

    def _build(width: int) -> List[Any]:
        lines: List[Any] = []

        # ── Active tool header ────────────────────────────────────────────────
        title_row = Text()
        title_row.append(f" {icon} [{current_tool}] {name} ", style=f"bold #000000 on {t_style('primary')}")
        title_row.append(f"  {tagline}", style="dim")
        lines.append(title_row)
        lines.append(Rule(style=t_style("border")))
        lines.append(Text(""))

        # ── Tool-specific sections ────────────────────────────────────────────
        for sec_title, sec_body in sections:
            lines.append(Text(sec_title, style=t_style("primary_bold")))
            lines.extend(_help_body(sec_body, 2))
            lines.append(Text(""))

        lines.append(Rule(style=f"dim {t_style('border')}"))
        lines.append(Text(""))

        # ── New features ──────────────────────────────────────────────────────
        lines.append(Text("NEW FEATURES", style=t_style("primary_bold")))
        lines.append(Text(""))
        new_features = [
            ("G  LIVE UCSC FETCHER",
             "Press G · type a UCSC coordinate · press Enter to fetch in the background.\n"
             "Format:  chr7:114200000-115240000  or  chr1:1000000-2000000\n"
             "The sequence loads from UCSC hg38. Fallback: synthetic sequence if offline.\n"
             "Esc cancels. The fetched sequence replaces the current one and triggers the\n"
             "victory animation. Works from any tool, in any mode."),
            ("C  CTCF MOTIF SCANNER",
             "Press C to scan the loaded sequence for structural anchor motifs.\n"
             "Six motif classes: CTCF_core (CCCTCCTGG) · CTCF_core_rc · CTCF_alt ·\n"
             "CTCF_alt_rc · SP1_GC_box (GGGCGG) · CpG_cluster (CCGCGCGG).\n"
             "Navigate results with ↑ ↓ arrow keys. Press Enter to send the selected\n"
             "anchor's coordinates to the deletion sandbox (tool [2]) automatically.\n"
             "Press C again to close the overlay."),
            ("⇥  CELL-LINE SHIFTER  (Tab key)",
             "Cycles the active chromatin context through three tissue types:\n"
             "  GM12878 — lymphoblastoid B-cell · sharp compartment boundaries (purple)\n"
             "  H1-hESC — embryonic stem cell · diffuse, open chromatin (blue)\n"
             "  IMR90   — lung fibroblast · intermediate compaction (amber)\n"
             "Applies a deterministic distance-based bias to the contact matrix.\n"
             "Resets any applied variant and invalidates insulation / boundary caches."),
        ]
        for feat_title, feat_body in new_features:
            lines.append(Text(f"  {feat_title}", style=t_style("primary_bold")))
            lines.extend(_help_body(feat_body, 4))
            lines.append(Text(""))

        lines.append(Rule(style=f"dim {t_style('border')}"))
        lines.append(Text(""))

        # ── Simulation mode commands ──────────────────────────────────────────
        lines.append(Text("SIMULATION MODE  (press M to enter, then type a command + Enter · Esc clears)",
                          style=t_style("primary_bold")))
        sim_tbl = Table(show_header=False, box=None, padding=(0, 3, 0, 0))
        sim_tbl.add_column(style=t_style("primary_bold"), no_wrap=True)
        sim_tbl.add_column(style="dim")
        sim_tbl.add_row("snp <pos> <REF>><ALT>", "Point mutation  —  e.g.  snp 500000 G>A")
        sim_tbl.add_row("del <start> <end>",      "Deletion range  —  e.g.  del 450000 520000")
        sim_tbl.add_row("reset",                  "Restore wildtype baseline")
        lines.append(sim_tbl)
        lines.append(Text(""))

        # ── Global keyboard reference ─────────────────────────────────────────
        lines.append(Text("GLOBAL CONTROLS", style=t_style("primary_bold")))
        kb_pairs = [
            ("1 – 9", "Switch active tool"),
            ("L",     "Load new sequence (FASTA)"),
            ("G",     "GOTO UCSC coordinate"),
            ("⇥",     "Cycle cell-line context"),
            ("H",     "Session history — reload past sequences"),
            ("?",     "This help screen"),
            ("M",     "Toggle OBSERVATION / SIMULATION"),
            ("I",     "Launch Interpretability Suite"),
            ("C",     "CTCF Motif Scanner overlay"),
            ("E",     "Export active tool output"),
            ("S",     "Settings (Observation mode)"),
            ("Q",     "Quit flight simulator"),
        ]
        # Two key/description pairs per row when the page is wide enough
        per_row = 2 if width >= 80 else 1
        kb_tbl = Table(show_header=False, box=None, padding=(0, 3, 0, 0))
        for _ in range(per_row):
            kb_tbl.add_column(style=t_style("primary_bold"), no_wrap=True, width=6)
            kb_tbl.add_column(style="dim")
        half = len(kb_pairs) // 2
        for i in range(half if per_row == 2 else len(kb_pairs)):
            if per_row == 2:
                kb_tbl.add_row(*kb_pairs[i], *kb_pairs[i + half])
            else:
                kb_tbl.add_row(*kb_pairs[i])
        lines.append(kb_tbl)
        lines.append(Text(""))

        # ── Tool index ────────────────────────────────────────────────────────
        lines.append(Rule(style=f"dim {t_style('border')}"))
        lines.append(Text("TOOL INDEX", style=t_style("primary_bold")))
        for k in "123456789":
            ti = _FS_TOOL_HELP.get(k, {})
            is_cur = k == current_tool
            t_icon = ti.get("icon", "◈")
            t_name = ti.get("name", f"Tool {k}")
            t_tag = ti.get("tagline", "")
            row = Text()
            if is_cur:
                row.append(f" {t_icon} [{k}] ", style=f"bold #000000 on {t_style('primary')}")
                row.append(f" {t_name}", style=t_style("primary_bold"))
            else:
                row.append(f"  [{k}] {t_icon}", style="dim")
                row.append(f" {t_name}", style="dim")
            row.append(f"  —  {t_tag}", style="dim")
            lines.append(row)
        return lines

    _pstyle = t_style("primary_bold")
    _run_scroll_view(
        _build,
        f"[{_pstyle}] ◈ SWAEV Genomics Client — Help [/{_pstyle}]",
        t_style("border"),
        exit_label="back to flight simulator",
    )
    clear_screen_completely()


# -----------------------------------------------------------------------------
# Main TUI Loop
# -----------------------------------------------------------------------------
def check_and_apply_update() -> None:
    """Fetch version.txt from GitHub; if newer, replace this script and exec-restart."""
    try:
        resp = requests.get(f"{GITHUB_RAW}/version.txt", timeout=3)
        if resp.status_code != 200:
            return
        latest = resp.text.strip()
        if latest <= __version__:
            return
        console.print(f"[dim]» Updating GoldBEAM TUI {__version__} → {latest}...[/dim]")
        dl = requests.get(f"{GITHUB_RAW}/client.py", timeout=20)
        if dl.status_code != 200:
            return
        self_path = os.path.abspath(__file__)
        tmp_path = self_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            fh.write(dl.text)
        os.replace(tmp_path, self_path)
        console.print(f"[bold green]✓ Updated to {latest}. Restarting...[/bold green]")
        time.sleep(0.8)
        os.execv(sys.executable, [sys.executable, self_path] + sys.argv[1:])
    except Exception:
        pass


def run_tui():
    check_and_apply_update()
    config = load_config()
    
    # Check if first launch onboarding is required
    if not config.get("onboarded", False):
        config = run_onboarding_wizard(config)
        config["onboarded"] = True
        save_config(config)
        
    update_theme_and_lang_globals(config)
    fetch_user_usage(config)

    # 1. We have an existing API key in config - verify it!
    if config.get("api_key"):
        clear_screen_completely()
        right_content = [
            f"[bold cyan]» {t('verifying_key')}[/bold cyan]",
            "",
            t("verifying_gateway"),
            f"[dim]Endpoint: {config.get('api_url', DEFAULT_API_URL)}[/dim]"
        ]
        grid = build_dashboard_grid("processing", 0, Group(*right_content), main_title="SECURITY CHECK")
        console.print(grid)
        
        status = verify_and_register_key(config["api_key"], config)
        
        if status == "success":
            clear_screen_completely()
            success_content = [
                f"[bold green]✓ {t('auth_success')}[/bold green]",
                "",
                f"Subscription Tier: [bold yellow]{USER_STATE['subscription_tier'].upper()}[/bold yellow]",
                t("init_sandbox")
            ]
            grid = build_dashboard_grid("success", 0, Group(*success_content), border_style="green", main_title="SECURITY APPROVED")
            console.print(grid)
            time.sleep(1.2)
            clear_screen_completely()
        elif status == "invalid":
            config["api_key"] = ""
            save_config(config)
            clear_screen_completely()
            invalid_content = [
                f"[bold red]✗ {t('title_access_denied')}[/bold red]",
                "",
                t("invalid_token")
            ]
            grid = build_dashboard_grid("error", 0, Group(*invalid_content), border_style="red", main_title="ACCESS DENIED")
            console.print(grid)
            time.sleep(2.0)
            clear_screen_completely()
        else:
            username = config.get("username", "Sandbox User")
            USER_STATE["name"] = username
            USER_STATE["subscription_tier"] = "sandbox"
            USER_STATE["online"] = False
            
            clear_screen_completely()
            offline_content = [
                f"[bold yellow]» {t('gateway_unreachable')}[/bold yellow]",
                "",
                t("gateway_unreachable_desc"),
                f"Resuming offline workspace session under: [cyan]{username}[/cyan]"
            ]
            grid = build_dashboard_grid("warning", 0, Group(*offline_content), border_style="yellow", main_title="OFFLINE MODE")
            console.print(grid)
            time.sleep(2.0)
            clear_screen_completely()
    else:
        # No API Key - offline Sandbox profile has been configured
        username = config.get("username", "Sandbox User")
        USER_STATE["name"] = username
        USER_STATE["subscription_tier"] = "sandbox"
        USER_STATE["online"] = False

    # ── Launch Genomic Flight Simulator immediately (L to load sequence) ────────
    run_goldbeam_flight_simulator([], "", config)


# =============================================================================
#
#   ██████╗  ██████╗ ██╗     ██████╗ ██████╗ ███████╗ █████╗ ███╗   ███╗
#  ██╔════╝ ██╔═══██╗██║     ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗ ████║
#  ██║  ███╗██║   ██║██║     ██║  ██║██████╔╝█████╗  ███████║██╔████╔██║
#  ██║   ██║██║   ██║██║     ██║  ██║██╔══██╗██╔══╝  ██╔══██║██║╚██╔╝██║
#  ╚██████╔╝╚██████╔╝███████╗██████╔╝██████╔╝███████╗██║  ██║██║ ╚═╝ ██║
#   ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
#
#  GENOMIC FLIGHT SIMULATOR  ->  GoldBEAM Immersive Analysis Platform
#  3-Panel: HUD Workspace  ·  Toolkit Registry  ·  Sequence Radar
#
# =============================================================================

# ── Biophysical dinucleotide reference tables ─────────────────────────────────
# Calladine & Drew helical twist values (degrees per dinucleotide step)
# Tokens: A=0 C=1 G=2 T=3 N=4
_DINUC_TWIST: Dict[Tuple[int, int], float] = {
    (0, 0): 35.1, (0, 1): 34.0, (0, 2): 35.0, (0, 3): 33.6,
    (1, 0): 35.0, (1, 1): 33.0, (1, 2): 35.5, (1, 3): 35.0,
    (2, 0): 34.9, (2, 1): 35.5, (2, 2): 33.0, (2, 3): 35.0,
    (3, 0): 33.6, (3, 1): 35.0, (3, 2): 34.0, (3, 3): 35.1,
}

# Brukner 1995 bendability scores (higher = more easily bent)
_DINUC_BEND: Dict[Tuple[int, int], float] = {
    (0, 0): 0.60, (0, 1): 0.90, (0, 2): 0.80, (0, 3): 1.40,
    (1, 0): 1.10, (1, 1): 0.90, (1, 2): 1.00, (1, 3): 0.80,
    (2, 0): 1.10, (2, 1): 1.20, (2, 2): 0.90, (2, 3): 1.00,
    (3, 0): 1.20, (3, 1): 1.10, (3, 2): 1.10, (3, 3): 0.60,
}

# CTCF core motif (JASPAR MA0139.1 simplified): CCGCGNGGG
_CTCF_CORE: List[int] = [1, 1, 2, 1, 2, 4, 2, 2, 2]


# ── Per-bin sequence analysis primitives ──────────────────────────────────────

def _gc_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """GC content per genomic bin [0, 1]."""
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.5] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        chunk = tokens[b * bin_size: min((b + 1) * bin_size, seq_len)]
        if not chunk:
            out.append(0.5)
        else:
            out.append(sum(1 for t in chunk if t in (1, 2)) / len(chunk))
    return out


def _n_density_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """Fraction of unknown bases (N) per bin [0, 1]."""
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.0] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        chunk = tokens[b * bin_size: min((b + 1) * bin_size, seq_len)]
        if not chunk:
            out.append(0.0)
        else:
            out.append(sum(1 for t in chunk if t == 4) / len(chunk))
    return out


def _ctcf_density_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """CTCF core motif hits per bin, normalised to [0, 1]."""
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.0] * n_bins
    pat = _CTCF_CORE
    pat_len = len(pat)
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        start = b * bin_size
        end = min(start + bin_size, seq_len)
        chunk = tokens[start:end]
        hits = 0
        for i in range(len(chunk) - pat_len + 1):
            if all(pat[j] == 4 or chunk[i + j] == pat[j] for j in range(pat_len)):
                hits += 1
        capacity = max(1, (end - start) - pat_len + 1)
        out.append(min(1.0, hits / capacity * 30))
    return out


def _gc_skew_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """(G−C)/(G+C) per bin, in [−1, 1]."""
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.0] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        chunk = tokens[b * bin_size: min((b + 1) * bin_size, seq_len)]
        g = sum(1 for t in chunk if t == 2)
        c = sum(1 for t in chunk if t == 1)
        out.append((g - c) / (g + c + 1e-9))
    return out


def _entropy_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """Shannon entropy per bin, normalised to [0, 1] (max = log2(4) = 2 bits)."""
    from collections import Counter
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.0] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        chunk = tokens[b * bin_size: min((b + 1) * bin_size, seq_len)]
        if not chunk:
            out.append(0.0)
            continue
        counts = Counter(chunk)
        total = len(chunk)
        ent = -sum((c / total) * math.log2(c / total + 1e-12) for c in counts.values())
        out.append(min(1.0, ent / 2.0))
    return out


def _twist_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """Mean dinucleotide helical twist per bin, normalised to [0, 1]."""
    seq_len = len(tokens)
    if seq_len < 2:
        return [0.5] * n_bins
    bin_size = max(1, seq_len // n_bins)
    default_twist = 34.5
    min_t, max_t = 33.0, 35.5
    out = []
    for b in range(n_bins):
        start = b * bin_size
        end = min(start + bin_size, seq_len)
        chunk = tokens[start:end]
        twists = [
            _DINUC_TWIST.get((chunk[i], chunk[i + 1]), default_twist)
            for i in range(len(chunk) - 1)
            if chunk[i] < 4 and chunk[i + 1] < 4
        ]
        mean_t = sum(twists) / len(twists) if twists else default_twist
        out.append((mean_t - min_t) / (max_t - min_t))
    return out


def _bend_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """Mean dinucleotide bendability per bin, normalised to [0, 1]."""
    seq_len = len(tokens)
    if seq_len < 2:
        return [0.5] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        start = b * bin_size
        end = min(start + bin_size, seq_len)
        chunk = tokens[start:end]
        bends = [
            _DINUC_BEND.get((chunk[i], chunk[i + 1]), 1.0)
            for i in range(len(chunk) - 1)
            if chunk[i] < 4 and chunk[i + 1] < 4
        ]
        mean_b = sum(bends) / len(bends) if bends else 1.0
        out.append(min(1.0, max(0.0, (mean_b - 0.60) / (1.40 - 0.60))))
    return out


def _cpg_oe_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """CpG observed/expected per bin. Expected ~0.6–0.8 for mammalian genomes."""
    seq_len = len(tokens)
    if seq_len < 2:
        return [0.65] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        start = b * bin_size
        end = min(start + bin_size, seq_len)
        chunk = tokens[start:end]
        n = len(chunk)
        if n < 2:
            out.append(0.65)
            continue
        cpg = sum(1 for i in range(n - 1) if chunk[i] == 1 and chunk[i + 1] == 2)
        c_f = sum(1 for t in chunk if t == 1) / n
        g_f = sum(1 for t in chunk if t == 2) / n
        expected = c_f * g_f * n
        oe = (cpg / expected) if expected > 0.001 else 0.65
        out.append(min(2.0, max(0.0, oe)))
    return out


def _repeat_density_per_bin(tokens: List[int], n_bins: int) -> List[float]:
    """Tandem repeat density per bin: fraction of bases in runs ≥ 4 of same token."""
    seq_len = len(tokens)
    if seq_len == 0:
        return [0.0] * n_bins
    bin_size = max(1, seq_len // n_bins)
    out = []
    for b in range(n_bins):
        start = b * bin_size
        end = min(start + bin_size, seq_len)
        chunk = tokens[start:end]
        n = len(chunk)
        if n == 0:
            out.append(0.0)
            continue
        in_run = 0
        run_len = 1
        for i in range(1, n):
            if chunk[i] == chunk[i - 1]:
                run_len += 1
            else:
                if run_len >= 4:
                    in_run += run_len
                run_len = 1
        if run_len >= 4:
            in_run += run_len
        out.append(in_run / n)
    return out


# ── Color utilities ───────────────────────────────────────────────────────────

def _matrix_val_to_rgb(v: float) -> Tuple[int, int, int]:
    """
    Maps contact matrix value [0, 1] to a 24-bit RGB colour ramp:
    near-zero → deep navy → royal blue → cyan → magenta → gold (diagonal peak)
    """
    v = max(0.0, min(1.0, v))
    if v < 0.20:
        t = v / 0.20
        return (0, int(t * 30), int(60 + t * 100))              # black → navy
    elif v < 0.40:
        t = (v - 0.20) / 0.20
        return (0, int(30 + t * 60), int(160 + t * 70))         # navy → blue
    elif v < 0.58:
        t = (v - 0.40) / 0.18
        return (int(t * 120), int(90 + t * 100), int(230 - t * 50))  # blue → cyan
    elif v < 0.76:
        t = (v - 0.58) / 0.18
        return (int(120 + t * 135), int(190 - t * 190), int(180 - t * 180))  # cyan → magenta
    else:
        t = (v - 0.76) / 0.24
        return (255, int(t * 210), 0)                            # magenta → gold


def _delta_val_to_rgb(v: float) -> Tuple[str, int, int, int]:
    """
    Maps delta matrix value [−1, 1] to (sign_label, R, G, B).
    Positive (contact gain) → red spectrum; negative (loss) → blue spectrum.
    """
    if v >= 0:
        t = min(1.0, v / 0.4)
        return ("gain", int(60 + t * 195), int(20 - 0), int(20 - 0))
    else:
        t = min(1.0, abs(v) / 0.4)
        return ("loss", int(20), int(20), int(80 + t * 175))


def _sdi_color(sdi: float) -> str:
    """Return Rich markup colour for Structural Disruption Index."""
    if sdi < 0.05:
        return "dim white"
    if sdi < 0.10:
        return "bold yellow"
    if sdi < 0.15:
        return "bold dark_orange"
    return "bold red"


def _profile_chart(
    vals: List[float],
    width: int,
    height: int,
    color: str,
    markers: Optional[List[int]] = None,
    marker_color: str = "#ff4444",
) -> List[Text]:
    """
    Vertical ASCII bar chart. Each of `width` columns shows one sample bar.
    Markers are overlaid as ▲ ticks at the base.
    Returns a list of `height` Text lines.
    """
    n = len(vals)
    if n == 0 or width <= 0 or height <= 0:
        return [Text("─" * width, style="dim")] * height

    # Downsample or upsample vals to `width` columns
    cols: List[float] = []
    for x in range(width):
        src = int(x / width * n)
        cols.append(max(0.0, min(1.0, vals[min(src, n - 1)])))

    marker_set = set(markers) if markers else set()
    rows: List[Text] = []
    for row in range(height):
        threshold = 1.0 - (row + 1) / height
        line = Text()
        for xi, v in enumerate(cols):
            src_bin = int(xi / width * n)
            is_marker = src_bin in marker_set
            if v >= threshold:
                if is_marker:
                    line.append("█", style=f"bold {marker_color}")
                else:
                    line.append("█", style=f"bold {color}")
            else:
                if is_marker and row == height - 1:
                    line.append("▲", style=f"bold {marker_color}")
                else:
                    line.append(" ", style="")
        rows.append(line)
    return rows


# ── Sequence Radar — DNA Double Helix ────────────────────────────────────────

def render_sequence_helix(
    tokens: List[int],
    frame: int,
    panel_width: int,
    panel_height: int,
    pulse_frames: int = 0,
    helix_tint: str = "",
) -> Panel:
    """
    Renders the motif-aware DNA double helix Sequence Radar.

    The helix strands follow sinusoidal paths; horizontal link characters
    encode local sequence properties:
      ≡  bold gold        — high-GC region (>60 %, triple-bond character)
      ─  chartreuse       — mid-GC (40–60 %, double bond)
      ╌  steel blue       — AT-rich (<40 %)
      ═  aquamarine bold  — CTCF core motif detected
      ·  dim purple       — assembly gap (N-run >30 %)

    Front-strand ◆ is bold; back-strand ◇ is dim, simulating depth.
    """
    usable_w = max(14, panel_width - 4)
    usable_h = max(6, panel_height - 4)  # leave room for legend

    n_bins = usable_h
    gc_b = _gc_per_bin(tokens, n_bins) if tokens else [0.45] * n_bins
    n_b = _n_density_per_bin(tokens, n_bins) if tokens else [0.0] * n_bins
    ctcf_b = _ctcf_density_per_bin(tokens, n_bins) if tokens else [0.0] * n_bins

    center = usable_w // 2
    amp = max(4, usable_w // 5)
    freq = 0.52

    pulsing = pulse_frames > 0

    lines: List[Any] = []

    for row in range(usable_h):
        phase = row * freq + frame * 0.10
        sin_v = math.sin(phase)

        s1_x = int(center + sin_v * amp)
        s2_x = int(center - sin_v * amp)
        s1_x = max(0, min(usable_w - 1, s1_x))
        s2_x = max(0, min(usable_w - 1, s2_x))

        left_x, right_x = min(s1_x, s2_x), max(s1_x, s2_x)
        front_is_s1 = sin_v >= 0

        # Depth-cued strand colours
        if pulsing and pulse_frames % 6 < 3:
            front_style = "bold #ffffff"
            back_style = "bold #aaaaff"
        elif helix_tint == "gold":
            front_style = "bold #ffaa00"
            back_style = "dim #cc6600"
        else:
            front_style = t_style("art_primary_bold")
            back_style = f"dim {t_style('art_primary')}"

        s1_style = front_style if front_is_s1 else back_style
        s2_style = back_style if front_is_s1 else front_style

        # Per-bin sequence context
        bin_idx = min(n_bins - 1, row)
        gc = gc_b[bin_idx]
        n_frac = n_b[bin_idx]
        ctcf = ctcf_b[bin_idx]

        # Link character selection
        gap = right_x - left_x
        if gap < 2:
            # Strands at crossing point — no link
            link_char, link_style, link_len = "", "", 0
        elif n_frac > 0.30:
            link_char, link_style, link_len = "·", "dim #334466", max(0, gap - 2)
        elif ctcf > 0.05:
            link_char, link_style, link_len = "═", "bold #00ffcc", max(0, gap - 2)
        elif gc >= 0.60:
            link_char, link_style, link_len = "≡", "bold #ffd700", max(0, gap - 2)
        elif gc >= 0.40:
            link_char, link_style, link_len = "─", ("#ffaa00" if helix_tint == "gold" else "#00ee88"), max(0, gap - 2)
        else:
            link_char, link_style, link_len = "╌", ("#cc8800" if helix_tint == "gold" else "#4488bb"), max(0, gap - 2)

        if pulsing and pulse_frames % 6 < 3 and link_len > 0:
            link_style = "bold #00ffff"

        # Build row
        buf: List[Tuple[str, str]] = [(" ", "")] * usable_w

        # Draw the link first (background)
        for lx in range(left_x + 1, right_x):
            if 0 <= lx < usable_w and link_len > 0:
                buf[lx] = (link_char, link_style)

        # Draw strands on top
        s1_char = "◆" if front_is_s1 else "◇"
        s2_char = "◇" if front_is_s1 else "◆"
        if 0 <= s1_x < usable_w:
            buf[s1_x] = (s1_char, s1_style)
        if 0 <= s2_x < usable_w:
            buf[s2_x] = (s2_char, s2_style)

        row_text = Text()
        for ch, sty in buf:
            row_text.append(ch, style=sty) if sty else row_text.append(ch)
        lines.append(row_text)

    # Legend
    legend = Text()
    legend.append("≡", style="bold #ffd700")
    legend.append(" GC>60  ", style="dim")
    legend.append("═", style="bold #00ffcc")
    legend.append(" CTCF  ", style="dim")
    legend.append("·", style="dim #334466")
    legend.append(" gap", style="dim")
    lines.append(Rule(style="dim #334466"))
    lines.append(legend)

    if pulsing:
        title_str = "[bold #00ffff blink]◈ SEQUENCE LOADED ◈[/bold #00ffff blink]"
        border_col = t_style("border")
    elif helix_tint == "gold":
        title_str = "[bold #ffaa00]⬡ GOLDBEAM SEQUENCE ⬡[/bold #ffaa00]" if tokens else "[dim #886600]⬡ GOLDBEAM SEQUENCE ⬡[/dim #886600]"
        border_col = "#cc8800" if tokens else "dim #664400"
    else:
        title_str = (
            f"[{t_style('primary_bold')}]◈ SEQUENCE RADAR ◈[/{t_style('primary_bold')}]"
            if tokens
            else "[dim]◈ SEQUENCE RADAR ◈[/dim]"
        )
        border_col = t_style("border") if tokens else f"dim {t_style('border')}"

    return Panel(
        Group(*lines),
        title=title_str,
        border_style=border_col,
        padding=(0, 1),
    )


# ── 24-bit true-colour contact matrix ────────────────────────────────────────

def render_matrix_24bit(
    matrix: List[List[float]],
    display_n: int,
    height_chars: int,
    delta: Optional[List[List[float]]] = None,
) -> Text:
    """
    Renders a contact (or delta) matrix as a 24-bit true-colour block using
    upper/lower half-block characters (▀ / ▄) for 2× vertical resolution.

    Args:
        matrix     : square 2D contact matrix, values in [0, 1]
        display_n  : number of output columns
        height_chars: number of terminal character rows (each = 2 matrix rows)
        delta      : optional delta overlay (if present, renders as red/blue signed map)

    Rows and columns are sampled proportionally, so the whole matrix is shown
    at any display size (downsampled or upscaled).
    """
    n = len(matrix)
    if n == 0 or display_n <= 0 or height_chars <= 0:
        return Text("  [no matrix]", style="dim")

    actual_rows = height_chars * 2
    src_rows = [min(n - 1, r * n // actual_rows) for r in range(actual_rows)]
    src_cols = [min(n - 1, c * n // display_n) for c in range(display_n)]

    result = Text()

    for char_row in range(height_chars):
        r_top = src_rows[char_row * 2]
        r_bot = src_rows[char_row * 2 + 1]

        for c in src_cols:
            if delta is not None:
                _, tr, tg, tb = _delta_val_to_rgb(delta[r_top][c])
                _, br, bg, bb = _delta_val_to_rgb(delta[r_bot][c])
            else:
                tr, tg, tb = _matrix_val_to_rgb(matrix[r_top][c])
                br, bg, bb = _matrix_val_to_rgb(matrix[r_bot][c])

            result.append(
                "▀",
                style=f"rgb({tr},{tg},{tb}) on rgb({br},{bg},{bb})",
            )

        if char_row < height_chars - 1:
            result.append("\n")

    return result


def _fit_matrix_dims(n: int, avail_w: int, avail_h: int) -> Tuple[int, int]:
    """
    Largest square-looking (columns, character rows) for an n×n matrix inside
    avail_w × avail_h cells. Half-blocks give 2 matrix rows per character row,
    so a square map needs columns == 2 × rows.
    """
    cols = max(2, min(avail_w, 2 * avail_h))
    cols -= cols % 2
    return cols, cols // 2


def render_matrix_color_legend(width: int) -> Text:
    """Renders a horizontal 24-bit colour legend bar for the contact matrix."""
    steps = max(6, width)
    t = Text()
    t.append("0 ", style="dim")
    for i in range(steps - 4):
        v = i / (steps - 5)
        r, g, b = _matrix_val_to_rgb(v)
        t.append("█", style=f"rgb({r},{g},{b})")
    t.append(" 1", style="dim")
    return t


# ── Responsive geometry & shared panel helpers ───────────────────────────────

_FS_MIN_COLS = 40
_FS_MIN_ROWS = 16


def _fs_geometry(term_w: int, term_h: int, footer_h: int) -> Dict[str, Any]:
    """
    Single source of truth for the flight simulator's panel geometry.

    Panels are dropped progressively as the terminal narrows so the HUD
    workspace is never the narrowest panel:
      ≥140 cols  HUD · toolkit · sequence radar
      ≥100 cols  HUD · toolkit
       <100 cols HUD only, with a one-line tool strip above it
    The header shrinks from the full phage banner to a compact or one-line
    variant as the terminal gets shorter.
    """
    too_small = term_w < _FS_MIN_COLS or term_h < _FS_MIN_ROWS

    if term_h >= 36 and term_w >= 90:
        header_mode, header_h = "full", 10
    elif term_h >= 24:
        header_mode, header_h = "compact", 4
    else:
        header_mode, header_h = "mini", 3

    if term_w >= 150:
        toolkit_w = 37
    elif term_w >= 100:
        toolkit_w = 30
    else:
        toolkit_w = 0
    helix_w = 26 if term_w >= 140 else 0
    strip_h = 0 if toolkit_w else 1

    body_h = max(1, term_h - header_h - footer_h)
    hud_outer_w = max(1, term_w - toolkit_w - helix_w)
    hud_outer_h = max(1, body_h - strip_h)

    return {
        "too_small": too_small,
        "term_w": term_w,
        "term_h": term_h,
        "header_mode": header_mode,
        "header_h": header_h,
        "footer_h": footer_h,
        "toolkit_w": toolkit_w,
        "helix_w": helix_w,
        "strip_h": strip_h,
        "body_h": body_h,
        "hud_outer_h": hud_outer_h,
        # Interior content area of the HUD panel (minus border and padding)
        "hud_w": max(1, hud_outer_w - 4),
        "hud_h": max(1, hud_outer_h - 2),
        "key": (too_small, header_h, footer_h, toolkit_w, helix_w, strip_h),
    }


def _fs_build_layout(geo: Dict[str, Any]) -> Layout:
    """Builds the Rich Layout tree for a geometry from _fs_geometry()."""
    layout = Layout(name="root")
    if geo["too_small"]:
        return layout
    layout.split_column(
        Layout(name="header", size=geo["header_h"]),
        Layout(name="body"),
        Layout(name="footer", size=geo["footer_h"]),
    )
    if geo["toolkit_w"]:
        cols = [Layout(name="hud"), Layout(name="toolkit", size=geo["toolkit_w"])]
        if geo["helix_w"]:
            cols.append(Layout(name="helix", size=geo["helix_w"]))
        layout["body"].split_row(*cols)
    else:
        layout["body"].split_column(
            Layout(name="strip", size=geo["strip_h"]),
            Layout(name="hud"),
        )
    return layout


def _fs_too_small_panel(term_w: int, term_h: int) -> Panel:
    msg = Text(justify="center")
    msg.append("TERMINAL TOO SMALL\n\n", style=t_style("primary_bold"))
    msg.append(f"Resize to at least {_FS_MIN_COLS}×{_FS_MIN_ROWS}\n", style="dim")
    msg.append(f"(currently {term_w}×{term_h})", style="dim")
    return Panel(Align.center(msg, vertical="middle"), border_style=t_style("border"))


def _fs_key_items(context: str, mode: str = "OBSERVATION") -> List[Tuple[str, str]]:
    """
    Every keyboard hint the flight simulator shows, per input context.
    Rendered once in the footer key bar — panels do not repeat these.
    """
    if context == "browser":
        return [("↑↓", "select"), ("⏎", "load"), ("/", "type path"),
                ("G", "UCSC fetch"), ("L/Esc", "close")]
    if context == "path":
        return [("⏎", "load"), ("Esc", "cancel")]
    if context == "history":
        return [("↑↓", "select"), ("⏎", "reload"), ("x/Del", "remove"), ("H/Esc", "close")]
    if context == "ctcf":
        return [("↑↓", "select"), ("⏎", "deletion sandbox"), ("C/Esc", "close")]
    if context == "goto":
        return [("⏎", "fetch"), ("Esc", "cancel")]
    if context == "simcmd":
        return [("⏎", "run command"), ("⌫", "edit"), ("Esc", "clear")]
    items = [
        ("1-9", "tool"), ("L", "load"), ("G", "goto"), ("C", "ctcf"),
        ("⇥", "cell line"), ("M", "observe" if mode == "SIMULATION" else "simulate"),
        ("I", "suite"), ("H", "history"), ("E", "export"),
        ("S", "settings"), ("?", "help"), ("Q", "quit"),
    ]
    if mode == "SIMULATION":
        # s starts an snp command in Simulation mode, so Settings is Observation-only
        items = [item for item in items if item[0] != "S"]
        items.insert(0, ("s/d/r", "type snp · del · reset"))
    return items


def _render_key_bar(items: List[Tuple[str, str]], width: int, max_lines: int = 4) -> Tuple[Group, int]:
    """Greedily wraps key hints into as few full-width lines as possible."""
    from rich.cells import cell_len

    rows: List[Text] = []
    cur = Text(" ", no_wrap=True, overflow="ellipsis")
    for key, label in items:
        chunk_len = cell_len(key) + 1 + cell_len(label)
        if cur.cell_len > 1 and cur.cell_len + 3 + chunk_len > width:
            rows.append(cur)
            cur = Text(" ", no_wrap=True, overflow="ellipsis")
        elif cur.cell_len > 1:
            cur.append("   ")
        cur.append(key, style=t_style("primary_bold"))
        cur.append(f" {label}", style="dim")
    rows.append(cur)
    rows = rows[:max_lines]
    return Group(*rows), len(rows)


def _fs_panel_height(item: Any) -> Optional[int]:
    """Best-effort line count of a HUD renderable (None if unknown)."""
    if isinstance(item, Text):
        return item.plain.count("\n") + 1
    if isinstance(item, Rule):
        return 1
    if isinstance(item, Table):
        return item.row_count + (1 if item.show_header else 0)
    return None


def _fs_panel(
    lines: List[Any],
    title: Any,
    border_style: Optional[str] = None,
    max_h: int = 0,
) -> Panel:
    """
    Wraps HUD lines in a panel. Text lines never wrap (long ones end in …) so
    one long line can't push the rest of the panel out of view. When the
    content is taller than max_h, blank spacer lines are removed first.
    """
    for item in lines:
        if isinstance(item, Text):
            item.no_wrap = True
            item.overflow = "ellipsis"
    if max_h:
        heights = [_fs_panel_height(i) or 1 for i in lines]
        excess = sum(heights) - max_h
        if excess > 0:
            kept: List[Any] = []
            for item in lines:
                if excess > 0 and isinstance(item, Text) and not item.plain.strip():
                    excess -= 1
                    continue
                kept.append(item)
            lines = kept
    return Panel(
        Group(*lines),
        title=title,
        border_style=border_style or t_style("border"),
        padding=(0, 1),
    )


def _fs_stat_table(
    pairs: List[Tuple[str, str]],
    width: int,
    label_w: int,
) -> Tuple[Table, int]:
    """Label/value grid: two pairs per row when the width allows, else one."""
    val_w = max((len(v) for _, v in pairs), default=0)
    per_row = 2 if width >= 2 * (label_w + val_w + 4) else 1
    if per_row == 1:
        label_w = max(6, min(label_w, width - val_w - 2))
    tbl = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    for _ in range(per_row):
        tbl.add_column(style="dim", no_wrap=True, width=label_w, overflow="ellipsis")
        tbl.add_column(style=t_style("primary_bold"), no_wrap=True, overflow="ellipsis")
    rows = 0
    for i in range(0, len(pairs), per_row):
        cells: List[str] = []
        for lbl, val in pairs[i:i + per_row]:
            cells += [lbl, val]
        cells += [""] * (2 * per_row - len(cells))
        tbl.add_row(*cells)
        rows += 1
    return tbl, rows


def _axis_labels(left: str, right: str, width: int, style: str = "dim") -> Text:
    """One line with a left-aligned and a right-aligned label spanning width."""
    gap = max(1, width - len(left) - len(right))
    return Text(f"{left}{' ' * gap}{right}", style=style)


# ── Flight Simulator Header ───────────────────────────────────────────────────


_FS_TOOLKIT_LABELS = {
    1: "Sequence Analytics",
    2: "Virtual Deletion Probe",
    3: "Biophysical Profiler",
    4: "Insulation Scoring",
    5: "Multi-Scale Dilation Check",
    6: "Species-Embedding Bias",
    7: "Boundary Anchor Scan",
    8: "Structural Disruption",
    9: "GoldBEAM Prediction",
}

_FS_TOOLKIT_ICONS = {
    1: "◈", 2: "⌖", 3: "⟁", 4: "⊟",
    5: "⊠", 6: "⊛", 7: "⊕", 8: "⊞", 9: "⬡",
}

_FS_TOOLKIT_DESC = {
    1: "GC skew · Shannon entropy · k-mer profile",
    2: "In silico fragment deletion · SDI readout",
    3: "Helical twist · Bendability · CpG islands",
    4: "TAD barrier insulation profiles",
    5: "d1/d2/d4/d8 head diagnostic monitor",
    6: "CpG depletion · repeat bias · GC skew",
    7: "CTCF/cohesin motif density scan",
    8: "24-bit ANSI true-colour 2D matrix map",
    9: "O(N) contact prediction · model status · SIMULATED",
}


def render_flight_header(
    tokens: List[int],
    filename: str,
    config: Dict[str, Any],
    frame: int,
    active_tool: int,
    mode: str,
    phage_state: str = "idle",
    cell_line_idx: int = 0,
    goto_mode: bool = False,
    goto_buffer: str = "",
    fetch_running: bool = False,
    header_mode: str = "full",
) -> Panel:
    """
    Top header panel: animated phage mascot + TPU metrics + file context +
    active-tool badge + mode indicator.  All chrome uses the active theme.

    header_mode: "full"    — phage art + 6 metric lines + badges (8 rows)
                 "compact" — badges + one-line sequence summary (2 rows)
                 "mini"    — badges only (1 row)
    Keyboard hints live in the footer key bar, not here.
    """
    seq_len = len(tokens)
    if seq_len >= 1_000_000:
        len_str = f"{seq_len / 1_000_000:.3f} Mb"
    elif seq_len >= 1_000:
        len_str = f"{seq_len / 1_000:.1f} kb"
    else:
        len_str = f"{seq_len:,} bp"

    n_bins_display = min(256, max(1, seq_len // 4096)) if seq_len > 0 else 256
    fname = (filename or "NO SEQUENCE LOADED")[-36:]
    tier = (config.get("subscription_tier") or USER_STATE.get("subscription_tier") or "sandbox").upper()
    username = (config.get("username") or USER_STATE.get("name") or "researcher").lower()
    usage_mb = USER_STATE.get("megabases_used", 0.0)
    quota_mb = USER_STATE.get("megabase_limit", 1.0)

    # GC bar (20 chars) — themed primary colour
    if tokens:
        gc_vals = _gc_per_bin(tokens, 1)
        gc_pct = gc_vals[0] * 100
        gc_bar_n = int(gc_vals[0] * 20)
        gc_text = f"{gc_pct:.1f}%"
    else:
        gc_bar_n = 0
        gc_text = "--.--%"

    tool_label = _FS_TOOLKIT_LABELS.get(active_tool, "")
    tool_icon = _FS_TOOLKIT_ICONS.get(active_tool, "◈")
    mode_style = "bold #00ffcc" if mode == "SIMULATION" else t_style("primary_bold")
    mode_icon = "◉"

    _cl_name, _cl_desc, _cl_color = _CELL_LINES[cell_line_idx % len(_CELL_LINES)]

    username_disp = username[:16] + "…" if len(username) > 16 else username
    badges = Text(no_wrap=True, overflow="ellipsis")
    if goto_mode:
        _cursor = "▮" if int(time.time() * 2) % 2 == 0 else " "
        if fetch_running:
            _spin = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(time.time() * 10) % 10]
            badges.append(f" {_spin} FETCHING UCSC hg38 — hold tight…", style=t_style("primary_bold"))
        else:
            badges.append(" GOTO> ", style=t_style("primary_bold"))
            badges.append(goto_buffer, style="bold #00ffcc")
            badges.append(_cursor, style="bold #00ffcc")
            badges.append("  e.g. chr7:114200000-115240000", style="dim")
    else:
        badges.append(f" {mode_icon} {mode} MODE ", style=f"{mode_style} on #111111")
        badges.append("  ")
        badges.append(f" {tool_icon} [{active_tool}] {tool_label} ", style=f"bold #111111 on {t_style('primary')}")
        badges.append("  ")
        badges.append(f" {tier} ", style="bold #111111 on #0EA5E9")
        badges.append(f"  @{username_disp}", style="dim")

    title = f"[{t_style('primary_bold')}]SWAEV Genomics Client[/{t_style('primary_bold')}]"

    if header_mode == "mini":
        return Panel(badges, title=title, title_align="left",
                     border_style=t_style("border"), padding=(0, 1))

    if header_mode == "compact":
        summary = Text(no_wrap=True, overflow="ellipsis")
        summary.append(f" {fname}", style="bold #00ffcc")
        summary.append(f"  {len_str}", style=t_style("primary_bold"))
        summary.append("  GC ", style="dim")
        summary.append(gc_text, style=t_style("primary_bold"))
        summary.append("  ·  ", style="dim")
        summary.append(f"{_cl_name} · hg38", style=f"bold {_cl_color}")
        summary.append("  ·  ", style="dim")
        summary.append(f"{usage_mb:.2f}/{quota_mb:.1f} Mb", style=t_style("primary_bold"))
        return Panel(Group(badges, summary), title=title, title_align="left",
                     border_style=t_style("border"), padding=(0, 1))

    # Full-size phage via get_phage_art (15 chars × 8 lines) — theme-aware
    phage_art = Text.from_markup(get_phage_art(phage_state, frame))

    def _metric(label: str) -> Text:
        return Text(f"{label:<20}", style="dim", no_wrap=True, overflow="ellipsis")

    m_accel = _metric("MAPPED ACCELERATOR")
    m_accel.append("16× v6e TPU Pod Cluster", style=t_style("primary_bold"))
    m_cell = _metric("CELLULAR CONTEXT")
    m_cell.append(f"{_cl_name} · hg38", style=f"bold {_cl_color}")
    m_file = _metric("STREAMING FILE")
    m_file.append(fname, style="bold #00ffcc")
    m_res = _metric("WINDOW RESOLUTION")
    m_res.append(f"{len_str}  [{n_bins_display} bins @ 4 kb/bin]", style=t_style("primary_bold"))
    m_gc = _metric("GC CONTENT")
    m_gc.append("█" * gc_bar_n, style=t_style("primary_bold"))
    m_gc.append("░" * (20 - gc_bar_n), style="dim")
    m_gc.append(f"  {gc_text}", style=t_style("primary_bold"))
    m_usage = _metric("USAGE")
    m_usage.append(f"{usage_mb:.2f}/{quota_mb:.1f} Mb  ", style=t_style("primary_bold"))
    quota_pct = min(1.0, usage_mb / max(0.001, quota_mb))
    quota_bar_n = int(quota_pct * 16)
    m_usage.append("█" * quota_bar_n, style=t_style("primary_bold"))
    m_usage.append("░" * (16 - quota_bar_n), style="dim")

    header_grid = Table.grid(padding=(0, 1))
    header_grid.add_column(width=16)
    header_grid.add_column()
    header_grid.add_row(
        phage_art,
        Group(m_accel, m_cell, m_file, m_res, m_gc, m_usage, Text(""), badges),
    )

    return Panel(
        header_grid,
        title=title,
        title_align="left",
        border_style=t_style("border"),
        padding=(0, 1),
    )


# ── Toolkit Registry (centre panel) ──────────────────────────────────────────

def render_toolkit_menu(active_tool: int, panel_h: int = 0) -> Panel:
    """
    Renders the vertical toolkit registry, fitted to panel_h rows.
    Active item is highlighted with the current theme primary; others are dim.
    Spacing and the heading are dropped first when the panel is short.
    Pass active_tool=0 to render every entry dimmed (boot sequence).
    """
    inner_h = panel_h - 2 if panel_h else 99
    has_active = 1 <= active_tool <= 9
    list_h = 9 + (1 if has_active else 0)
    spaced = inner_h >= list_h + 3 + 9
    heading = inner_h >= list_h + 2

    lines: List[Any] = []
    if heading:
        lines.append(Text("TOOLKIT REGISTRY", style=f"bold dim {t_style('primary')}"))
        lines.append(Rule(style=f"dim {t_style('border')}"))
    if spaced:
        lines.append(Text(""))

    for k in range(1, 10):
        icon = _FS_TOOLKIT_ICONS[k]
        label = _FS_TOOLKIT_LABELS[k]
        desc = _FS_TOOLKIT_DESC[k]
        is_active = k == active_tool

        key_text = Text(no_wrap=True, overflow="ellipsis")
        if k == 9:
            # GoldBEAM gets gold/amber styling
            if is_active:
                key_text.append(f" [9] {icon} ", style="bold #111111 on #ffaa00")
                key_text.append(f" {label}", style="bold #ffaa00")
            else:
                key_text.append(f" [9] {icon} ", style="dim #886600")
                key_text.append(label, style="dim #886600")
            desc_style = "dim #cc8800"
        elif is_active:
            key_text.append(f" [{k}] {icon} ", style=f"bold #111111 on {t_style('primary')}")
            key_text.append(f" {label}", style=t_style("primary_bold"))
            desc_style = "dim"
        else:
            key_text.append(f" [{k}] {icon} ", style="dim")
            key_text.append(label, style="dim")
            desc_style = "dim"
        lines.append(key_text)
        if is_active and inner_h >= 10:
            lines.append(Text(f"     {desc}", style=desc_style, no_wrap=True, overflow="ellipsis"))
        if spaced:
            lines.append(Text(""))

    return Panel(
        Group(*lines),
        title=Text("◈ TOOLS ◈", style=t_style("primary_bold")),
        border_style=t_style("border"),
        padding=(0, 1),
    )


def render_tool_strip(active_tool: int) -> Text:
    """One-line toolkit selector used when the terminal is too narrow for the toolkit panel."""
    strip = Text(no_wrap=True, overflow="ellipsis")
    for k in range(1, 10):
        icon = _FS_TOOLKIT_ICONS[k]
        if k == active_tool:
            bg = "#ffaa00" if k == 9 else t_style("primary")
            strip.append(f" {k} {icon} {_FS_TOOLKIT_LABELS[k]} ", style=f"bold #111111 on {bg}")
        else:
            strip.append(f" {k}{icon} ", style="dim #886600" if k == 9 else "dim")
    return strip


# ── HUD Tool Content Renderers ────────────────────────────────────────────────
# hud_w / hud_h are the interior content size of the HUD panel (cells).

def render_hud_1_analytics(
    tokens: List[int],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[1] Sequence Analytics — GC skew, Shannon entropy, composition stats."""
    title = f"[{t_style('primary_bold')}]◈ [1] SEQUENCE ANALYTICS ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "analytics" not in cache:
        n_bins = min(60, max(8, hud_w - 2))
        cache["analytics"] = {
            "gc":      _gc_per_bin(tokens, n_bins),
            "skew":    _gc_skew_per_bin(tokens, n_bins),
            "entropy": _entropy_per_bin(tokens, n_bins),
            "n_bins":  n_bins,
        }
        stats = compute_sequence_stats(tokens)
        cache["analytics"]["stats"] = stats

    d = cache["analytics"]
    stats = d["stats"]

    n = stats["length"]
    len_str = f"{n / 1_000_000:.3f} Mb" if n >= 1_000_000 else f"{n / 1_000:.1f} kb" if n >= 1_000 else f"{n:,} bp"
    tbl, tbl_rows = _fs_stat_table([
        ("Length", len_str), ("GC%", f"{stats['gc_pct']:.2f}%"),
        ("AT%", f"{100 - stats['gc_pct']:.2f}%"), ("CpG O/E", f"{stats.get('cpg_oe', 0.65):.3f}"),
        ("Tm (est.)", f"~{stats.get('tm', 0):.1f}°C"), ("N-content", f"{stats.get('n_pct', 0):.2f}%"),
        ("Complexity", f"{stats.get('complexity', 0):.3f}"), ("Tokens", f"{n:,}"),
    ], hud_w, 14)

    chart_w = max(8, hud_w)
    # table + rule + 3 chart titles + skew axis + 2 spacers
    chart_h = max(1, (hud_h - tbl_rows - 7) // 3)

    lines: List[Any] = [tbl, Rule(style=f"dim {t_style('border')}")]

    # GC skew chart
    lines.append(Text("GC SKEW  (G−C)/(G+C)", style="dim #aaddaa"))
    lines.append(Text(f"{'─' * (chart_w // 2)}┼{'─' * (chart_w - chart_w // 2 - 1)}", style="dim"))
    lines.extend(_profile_chart(
        [(v + 1) / 2 for v in d["skew"]],  # shift [-1,1] to [0,1]
        chart_w, chart_h,
        color="#00ff88",
    ))
    lines.append(Text(""))

    # Shannon entropy chart
    lines.append(Text("SHANNON ENTROPY  H = −Σ p·log₂p", style="dim #aaddaa"))
    lines.extend(_profile_chart(d["entropy"], chart_w, chart_h, color="#0EA5E9"))
    lines.append(Text(""))

    # GC profile
    lines.append(Text("GC CONTENT PROFILE", style="dim #aaddaa"))
    lines.extend(_profile_chart(d["gc"], chart_w, chart_h, color="#ffd700"))

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_2_deletion_probe(
    tokens: List[int],
    sim_state: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[2] Virtual Deletion Probe — in silico mutagenesis with SDI readout."""
    lines: List[Any] = []

    applied = sim_state.get("applied", False)
    vt_desc = sim_state.get("desc", "No variant applied — showing wildtype")
    sdi = sim_state.get("sdi", 0.0)
    wt_matrix = sim_state.get("wt_matrix", [])
    vt_matrix = sim_state.get("vt_matrix", [])
    delta = sim_state.get("delta", None)
    rule = f"dim {t_style('border')}"

    # Status banner
    status_style = "bold #ff4444" if applied else "dim"
    lines.append(Text(f"  STATUS  {vt_desc}", style=status_style))

    if applied:
        sdi_col = _sdi_color(sdi)
        _sdi_bar_w = max(4, min(40, hud_w - 18))
        sdi_bar_n = min(_sdi_bar_w, int(sdi / 0.30 * _sdi_bar_w))
        sdi_bar = Text()
        sdi_bar.append("  SDI   ", style="dim")
        sdi_bar.append("█" * sdi_bar_n, style=sdi_col)
        sdi_bar.append("░" * (_sdi_bar_w - sdi_bar_n), style="dim")
        sdi_bar.append(f"  {sdi:.4f}", style=sdi_col)
        lines.append(sdi_bar)
        if sdi >= 0.15:
            lines.append(Text("  ⚠ STRUCTURAL SIGNIFICANCE THRESHOLD EXCEEDED", style="bold red"))

    lines.append(Rule(style=rule))

    # Everything below the matrices: delta stats (when applied) and command reference
    tail: List[Any] = []
    if applied:
        ds = sim_state.get("delta_stats", {})
        stat_tbl = Table(show_header=False, box=None, padding=(0, 3, 0, 0))
        stat_tbl.add_column(style="dim", no_wrap=True)
        stat_tbl.add_column(style=t_style("primary_bold"), no_wrap=True)
        stat_tbl.add_row("Mean |ΔContact|", f"{ds.get('mean_abs_delta', 0):.4f}")
        stat_tbl.add_row("Max gain", f"+{ds.get('max_gain', 0):.4f}")
        stat_tbl.add_row("Max loss", f"−{abs(ds.get('max_loss', 0)):.4f}")
        tail += [Rule(style=rule), stat_tbl]

    used = len(lines) + sum(_fs_panel_height(i) or 1 for i in tail)
    if hud_h - used >= 4 + 6:
        hints = Text()
        hints.append("  snp <pos> <REF>><ALT>", style=t_style("primary_bold"))
        hints.append("   e.g. snp 500000 G>A\n", style="dim")
        hints.append("  del <start> <end>    ", style=t_style("primary_bold"))
        hints.append("   e.g. del 450000 520000\n", style="dim")
        hints.append("  reset                ", style=t_style("primary_bold"))
        hints.append("   restore wildtype", style="dim")
        tail += [Rule(style=rule), hints]
        used += 4

    if wt_matrix:
        n = len(wt_matrix)
        avail_h = max(1, hud_h - used - 1)
        side = _fit_matrix_dims(n, (hud_w - 2) // 2, avail_h)
        stacked = _fit_matrix_dims(n, hud_w, max(1, (avail_h - 1) // 2))

        if applied and vt_matrix:
            def _mut(c: int, r: int) -> Text:
                return render_matrix_24bit(vt_matrix, c, r)
        elif applied and delta:
            def _mut(c: int, r: int) -> Text:
                return render_matrix_24bit(wt_matrix, c, r, delta=delta)
        else:
            def _mut(c: int, r: int) -> Text:
                return Text("wildtype", style="dim", no_wrap=True, overflow="ellipsis")

        if side[0] >= stacked[0]:
            cols, rows = side
            lines.append(Text(f"{'WILDTYPE':<{max(cols + 2, 10)}}MUTANT / DELTA", style="dim"))
            side_grid = Table.grid()
            side_grid.add_column(width=cols)
            side_grid.add_column(width=2)
            side_grid.add_column(width=cols)
            side_grid.add_row(render_matrix_24bit(wt_matrix, cols, rows), Text("  "), _mut(cols, rows))
            lines.append(side_grid)
        else:
            cols, rows = stacked
            lines.append(Text("WILDTYPE", style="dim"))
            lines.append(render_matrix_24bit(wt_matrix, cols, rows))
            lines.append(Text("MUTANT / DELTA", style="dim"))
            lines.append(_mut(cols, rows))
    else:
        lines.append(Text("  No sequence loaded.", style="dim"))

    lines.extend(tail)

    return _fs_panel(
        lines,
        f"[{t_style('primary_bold')}]◈ [2] VIRTUAL DELETION PROBE ◈[/{t_style('primary_bold')}]",
        border_style="#ff4444" if applied else None,
    )


def render_hud_3_biophysical(
    tokens: List[int],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[3] Biophysical Profiler — helical twist, bendability, CpG island track."""
    title = f"[{t_style('primary_bold')}]◈ [3] BIOPHYSICAL PROFILER ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "biophysical" not in cache:
        n_bins = min(60, max(8, hud_w - 2))
        cache["biophysical"] = {
            "twist":   _twist_per_bin(tokens, n_bins),
            "bend":    _bend_per_bin(tokens, n_bins),
            "cpg_oe":  _cpg_oe_per_bin(tokens, n_bins),
            "n_bins":  n_bins,
        }

    d = cache["biophysical"]
    chart_w = max(8, hud_w)

    # Summary stats
    twist_vals = d["twist"]
    bend_vals = d["bend"]
    cpg_vals = d["cpg_oe"]

    mean_twist_norm = sum(twist_vals) / len(twist_vals)
    mean_twist_deg = 33.0 + mean_twist_norm * 2.5  # denormalise
    mean_bend = sum(bend_vals) / len(bend_vals)
    mean_bend_real = 0.60 + mean_bend * 0.80       # denormalise to brukner range
    mean_cpg = sum(cpg_vals) / len(cpg_vals)
    cpg_island_bins = sum(1 for v in cpg_vals if v > 0.6)

    tbl, tbl_rows = _fs_stat_table([
        ("Mean helical twist", f"{mean_twist_deg:.2f}°/step"),
        ("Mean bendability", f"{mean_bend_real:.3f}"),
        ("CpG O/E mean", f"{mean_cpg:.3f}"),
        ("CpG island bins", f"{cpg_island_bins} / {d['n_bins']}"),
    ], hud_w, 20)
    # table + rule + 3 titles + 2 axis lines + 2 spacers + legend
    chart_h = max(1, (hud_h - tbl_rows - 9) // 3)

    lines: List[Any] = [tbl, Rule(style=f"dim {t_style('border')}")]

    # Helical Twist
    lines.append(Text("HELICAL TWIST  (Calladine & Drew, °/step  ≈ 33–35.5°)", style="dim #aaddaa"))
    lines.extend(_profile_chart(twist_vals, chart_w, chart_h, color="#ffd700"))
    lines.append(_axis_labels("min 33.0°", "max 35.5°", chart_w))
    lines.append(Text(""))

    # Bendability
    lines.append(Text("BENDABILITY  (Brukner 1995; higher = more flexible)", style="dim #aaddaa"))
    lines.extend(_profile_chart(bend_vals, chart_w, chart_h, color="#00ee88"))
    lines.append(_axis_labels("rigid 0.60", "flexible 1.40", chart_w))
    lines.append(Text(""))

    # CpG O/E
    lines.append(Text("CpG OBSERVED/EXPECTED  (mammalian norm ≈ 0.6–0.8)", style="dim #aaddaa"))
    # Mark bins where O/E > 0.6 (putative CpG islands)
    cpg_markers = [i for i, v in enumerate(cpg_vals) if v > 0.60]
    cpg_norm = [min(1.0, v / 2.0) for v in cpg_vals]
    lines.extend(_profile_chart(cpg_norm, chart_w, chart_h, color="#0EA5E9",
                                markers=cpg_markers, marker_color="#00ffcc"))
    lines.append(Text("  ▲ = CpG island candidate (O/E > 0.6)", style="dim #00ffcc"))

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_4_insulation(
    tokens: List[int],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[4] Insulation Scoring — TAD barrier profiles and boundary table."""
    title = f"[{t_style('primary_bold')}]◈ [4] INSULATION SCORING ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "insulation" not in cache:
        matrix, _ = get_contact_matrix(tokens)
        ins = compute_insulation_score(matrix)
        bounds = call_tad_boundaries(ins)
        cache["insulation"] = {
            "insulation": ins,
            "boundaries": bounds,
            "matrix": matrix,
        }

    d = cache["insulation"]
    ins = d["insulation"]
    bounds = d["boundaries"]
    chart_w = max(8, hud_w)

    # Summary
    n_tads = len(bounds)
    mean_ins = sum(ins) / len(ins) if ins else 0.5
    tbl, tbl_rows = _fs_stat_table([
        ("TAD boundaries called", str(n_tads)),
        ("Mean insulation score", f"{mean_ins:.4f}"),
        ("Bins scored", str(len(ins))),
        ("Min insulation", f"{min(ins) if ins else 0:.4f}"),
    ], hud_w, 22)

    # table + rule + chart title + legend + rule + table title + table header
    remaining = hud_h - tbl_rows - 6
    n_rows = min(8, len(bounds), max(1, remaining // 3))
    chart_h = max(2, remaining - n_rows)

    lines: List[Any] = [tbl, Rule(style=f"dim {t_style('border')}")]

    # Insulation profile
    boundary_bins = [b["bin"] for b in bounds]
    lines.append(Text("INSULATION SCORE  (↓ valleys = TAD boundaries  ▲ markers)", style="dim #aaddaa"))
    lines.extend(_profile_chart(
        ins, chart_w, chart_h,
        color="#0EA5E9",
        markers=boundary_bins,
        marker_color="#ff4444",
    ))
    lines.append(Text("  ▲ = TAD boundary  (insulation valley)", style="dim #ff4444"))
    lines.append(Rule(style=f"dim {t_style('border')}"))

    # Boundary table
    lines.append(Text("PREDICTED TAD BOUNDARIES", style="dim #aaddaa"))
    btbl = Table(
        show_header=True,
        header_style=t_style("primary_bold"),
        border_style="dim",
        box=None,
        padding=(0, 2, 0, 0),
    )
    wide = hud_w >= 42
    btbl.add_column("Rank" if wide else "#", width=5 if wide else 3, justify="right", no_wrap=True)
    btbl.add_column("Bin", width=6 if wide else 4, justify="right", no_wrap=True)
    btbl.add_column("Insulation" if wide else "Insul.", width=12 if wide else 8, justify="right", no_wrap=True)
    if wide:
        btbl.add_column("Strength", width=10, justify="right", no_wrap=True)
    for rank, b in enumerate(bounds[:n_rows], 1):
        row = [str(rank), str(b["bin"]), f"{b['insulation_score']:.4f}"]
        if wide:
            row.append(f"{b.get('boundary_strength', 0):.3f}")
        btbl.add_row(*row)
    lines.append(btbl)

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_5_multiscale(
    tokens: List[int],
    cache: Dict[str, Any],
    frame: int,
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[5] Multi-Scale Dilation Check — d1/d2/d4/d8 contact head diagnostics."""
    title = f"[{t_style('primary_bold')}]◈ [5] MULTI-SCALE DILATION CHECK ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "multiscale" not in cache:
        matrix, _ = get_contact_matrix(tokens)
        n = len(matrix)
        scales = {
            "d1_loop":     (1,  8,   "0–100 kb loops"),
            "d2_domain":   (8,  20,  "100 kb–500 kb domains"),
            "d4_TAD":      (20, 60,  "500 kb–2 Mb TADs"),
            "d8_macroTAD": (60, n,   "2 Mb+ macro-domains"),
        }
        head_data = {}
        for name, (lo, hi, label) in scales.items():
            hi_clamped = min(n, hi)
            vals = [
                matrix[r][c]
                for r in range(n)
                for c in range(lo, min(hi_clamped, r))
                if abs(r - c) >= lo and abs(r - c) < hi_clamped
            ]
            mean_v = sum(vals) / len(vals) if vals else 0.0
            max_v = max(vals) if vals else 0.0
            head_data[name] = {
                "label": label,
                "mean": mean_v,
                "max": max_v,
                "n_contacts": len(vals),
                "expected_mean_range": (0.05, 0.35),
            }
        cache["multiscale"] = {"heads": head_data, "matrix": matrix}

    d = cache["multiscale"]["heads"]
    # Short terminals show 2 lines per head instead of 4
    detailed = hud_h >= 30
    bar_w = max(4, hud_w - 4 - 24)

    lines: List[Any] = []
    lines.append(Text("GOLDBEAM MULTISCALE CONTACT HEAD MONITOR", style="dim #aaddaa"))
    lines.append(Text("  Architecture: 4 dilated convolutional heads (d1/d2/d4/d8)", style="dim"))
    lines.append(Rule(style=f"dim {t_style('border')}"))

    for head_name, hd in d.items():
        is_ok = hd["expected_mean_range"][0] <= hd["mean"] <= hd["expected_mean_range"][1]
        status_style = t_style("success_bold") if is_ok else t_style("error_bold")
        status_icon = "✓" if is_ok else "⚠"

        head_line = Text()
        head_line.append(f"  {status_icon} ", style=status_style)
        head_line.append(f"{head_name:14s}", style=t_style("primary_bold"))
        head_line.append(f"  {hd['label']}", style="dim")
        if not is_ok:
            head_line.append("  [PRE-TRAINING — SIMULATED]", style="dim red")
        lines.append(head_line)

        bar_val = min(1.0, hd["mean"] / 0.35)
        bar_n = int(bar_val * bar_w)
        bar_line = Text()
        bar_line.append("    ")
        bar_line.append("█" * bar_n, style=status_style)
        bar_line.append("░" * (bar_w - bar_n), style="dim")
        bar_line.append(f"  μ={hd['mean']:.4f}  max={hd['max']:.4f}", style="dim")
        lines.append(bar_line)

        if detailed:
            exp_lo, exp_hi = hd["expected_mean_range"]
            lines.append(Text(f"    Expected range: [{exp_lo:.2f}, {exp_hi:.2f}]  "
                              f"Contacts sampled: {hd['n_contacts']:,}", style="dim"))
            lines.append(Text(""))

    lines.append(Rule(style=f"dim {t_style('border')}"))

    # Contact probability vs distance curve
    lines.append(Text("CONTACT DECAY  P(contact) vs genomic distance", style="dim #aaddaa"))
    matrix = cache["multiscale"]["matrix"]
    n = len(matrix)
    decay = []
    for diag in range(1, n):
        vals = [matrix[i][i + diag] for i in range(n - diag)]
        decay.append(sum(vals) / len(vals) if vals else 0.0)

    # Normalise decay for display
    max_d = max(decay) if decay else 1.0
    decay_norm = [v / (max_d + 1e-9) for v in decay]
    chart_w = max(8, hud_w)
    decay_h = max(2, hud_h - len(lines) - 1)
    lines.extend(_profile_chart(decay_norm, chart_w, decay_h, color="#0EA5E9"))
    lines.append(_axis_labels("↑ near diagonal", "far diagonal ↑", chart_w))

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_6_species_bias(
    tokens: List[int],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[6] Species-Embedding Bias — CpG depletion, repeat density, GC bias."""
    title = f"[{t_style('primary_bold')}]◈ [6] SPECIES-EMBEDDING BIAS ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "species" not in cache:
        n_bins = min(60, max(8, hud_w - 2))
        cache["species"] = {
            "cpg_oe":  _cpg_oe_per_bin(tokens, n_bins),
            "gc":      _gc_per_bin(tokens, n_bins),
            "repeats": _repeat_density_per_bin(tokens, n_bins),
            "n_bins":  n_bins,
        }

    d = cache["species"]
    chart_w = max(8, hud_w)

    cpg_vals = d["cpg_oe"]
    gc_vals = d["gc"]
    rep_vals = d["repeats"]
    mean_cpg = sum(cpg_vals) / len(cpg_vals)
    mean_gc = sum(gc_vals) / len(gc_vals)
    mean_rep = sum(rep_vals) / len(rep_vals)

    # Species inference heuristic
    if mean_cpg < 0.45 and mean_gc > 0.35:
        species_call = "Homo sapiens / Mus musculus (methylated mammalian)"
        species_conf = min(0.95, 0.5 + (0.45 - mean_cpg) * 2)
        species_style = t_style("success_bold")
    elif mean_cpg > 1.0:
        species_call = "Non-mammalian (invertebrate / prokaryote)"
        species_conf = min(0.85, 0.4 + (mean_cpg - 1.0))
        species_style = "bold #0EA5E9"
    elif mean_gc > 0.55:
        species_call = "GC-rich organism (plant / bacteria)"
        species_conf = min(0.80, 0.3 + (mean_gc - 0.55) * 4)
        species_style = "bold #ffd700"
    else:
        species_call = "Unclassified / mixed"
        species_conf = 0.40
        species_style = "dim"

    tbl, tbl_rows = _fs_stat_table([
        ("Mean CpG O/E", f"{mean_cpg:.4f}"), ("Mean GC%", f"{mean_gc * 100:.2f}%"),
        ("Mean repeat density", f"{mean_rep:.4f}"), ("Mammalian norm CpG", "0.60–0.80"),
    ], hud_w, 20)
    # inference (3) + table + rule + 3 titles + note + 2 spacers
    chart_h = max(1, (hud_h - tbl_rows - 10) // 3)

    lines: List[Any] = []

    # Species inference panel
    lines.append(Text("SPECIES CONDITIONING INFERENCE", style="dim #aaddaa"))
    lines.append(Text(f"  ◈ {species_call}", style=species_style))

    conf_w = max(4, hud_w - 22)
    conf_bar_n = int(species_conf * conf_w)
    conf_bar = Text()
    conf_bar.append("  Confidence  ")
    conf_bar.append("█" * conf_bar_n, style=species_style)
    conf_bar.append("░" * (conf_w - conf_bar_n), style="dim")
    conf_bar.append(f"  {species_conf * 100:.1f}%", style=species_style)
    lines.append(conf_bar)
    lines.append(Rule(style=f"dim {t_style('border')}"))

    lines.append(tbl)
    lines.append(Rule(style=f"dim {t_style('border')}"))

    # CpG O/E per bin
    lines.append(Text("CpG OBSERVED/EXPECTED  (depletion = mammalian methylation signature)", style="dim #aaddaa"))
    cpg_norm = [min(1.0, v / 2.0) for v in cpg_vals]
    lines.extend(_profile_chart(cpg_norm, chart_w, chart_h, color="#0EA5E9"))
    lines.append(Text("  Mammalian range: 0.6–0.8 O/E  ·  Plotted max = 2.0", style="dim"))
    lines.append(Text(""))

    # Repeat density per bin
    lines.append(Text("TANDEM REPEAT DENSITY  (runs ≥ 4 identical bases)", style="dim #aaddaa"))
    lines.extend(_profile_chart(rep_vals, chart_w, chart_h, color="#ffd700"))
    lines.append(Text(""))

    # GC profile
    lines.append(Text("GC CONTENT DISTRIBUTION", style="dim #aaddaa"))
    lines.extend(_profile_chart(gc_vals, chart_w, chart_h, color="#00ee88"))

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_7_boundary_scan(
    tokens: List[int],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """[7] Boundary Anchor Scan — CTCF motif density + predicted loop anchors."""
    title = f"[{t_style('primary_bold')}]◈ [7] BOUNDARY ANCHOR SCAN ◈[/{t_style('primary_bold')}]"
    if not tokens:
        return _fs_panel([Text("  No sequence loaded.", style="dim")], title)

    if "boundary" not in cache:
        n_bins = min(60, max(8, hud_w - 2))
        matrix, _ = get_contact_matrix(tokens)
        anchors = find_loop_anchors(matrix, top_n=20)
        ctcf = _ctcf_density_per_bin(tokens, n_bins)
        cache["boundary"] = {
            "ctcf":    ctcf,
            "anchors": anchors,
            "n_bins":  n_bins,
            "matrix":  matrix,
        }

    d = cache["boundary"]
    ctcf_vals = d["ctcf"]
    anchors = d["anchors"]
    chart_w = max(8, hud_w)
    n_bins = d["n_bins"]

    ctcf_peak_bins = sorted(
        range(n_bins), key=lambda i: ctcf_vals[i], reverse=True
    )[:10]
    total_ctcf_hits = sum(ctcf_vals)

    tbl, tbl_rows = _fs_stat_table([
        ("CTCF peak bins (top 10)", str(len(ctcf_peak_bins))),
        ("Loop anchors predicted", str(len(anchors))),
        ("Total CTCF density", f"{total_ctcf_hits:.3f}"),
        ("Min loop dist", "6 bins"),
    ], hud_w, 24)

    # table + rule + chart title + legend + rule + table title + table header
    remaining = hud_h - tbl_rows - 6
    n_rows = min(10, len(anchors), max(1, remaining // 3))
    chart_h = max(2, remaining - n_rows)

    lines: List[Any] = [tbl, Rule(style=f"dim {t_style('border')}")]

    # CTCF density profile
    lines.append(Text("CTCF CORE MOTIF DENSITY  (CCGCGNGGG hits per bin)", style="dim #aaddaa"))
    lines.extend(_profile_chart(
        ctcf_vals, chart_w, chart_h,
        color="#00ffcc",
        markers=ctcf_peak_bins[:5],
        marker_color="#ffd700",
    ))
    lines.append(Text("  ▲ = top-5 CTCF density peaks", style="dim #ffd700"))
    lines.append(Rule(style=f"dim {t_style('border')}"))

    # Loop anchor table
    lines.append(Text("PREDICTED LOOP ANCHOR PAIRS  (top off-diagonal contacts)", style="dim #aaddaa"))
    atbl = Table(
        show_header=True,
        header_style=t_style("primary_bold"),
        border_style="dim",
        box=None,
        padding=(0, 2, 0, 0),
    )
    if hud_w >= 64:
        cols = [("Rank", 5), ("Anchor 1 (bin)", 14), ("Anchor 2 (bin)", 14), ("Distance", 10), ("Contact", 10)]
    else:
        cols = [("#", 3), ("A1", 4), ("A2", 4), ("Dist", 5), ("Contact", 7)]
    for col_name, col_w in cols:
        atbl.add_column(col_name, width=col_w, justify="right", no_wrap=True)
    for rank, (b1, b2, score) in enumerate(anchors[:n_rows], 1):
        atbl.add_row(str(rank), str(b1), str(b2), str(b2 - b1), f"{score:.4f}")
    lines.append(atbl)

    return _fs_panel(lines, title, max_h=hud_h)


def render_hud_8_structural(
    tokens: List[int],
    sim_state: Dict[str, Any],
    cache: Dict[str, Any],
    hud_w: int,
    hud_h: int,
) -> Panel:
    """
    [8] Structural Disruption — 24-bit true-colour ANSI 2D chromatin contact
    matrix, rendered with upper/lower half-block characters for 2× resolution.
    Overlays variant delta map when in Simulation Mode.

    The matrix is kept square and sized to the HUD; the legend and stats sit
    beside it on wide terminals and below it on tall/narrow ones.
    """
    if not tokens:
        return _fs_panel(
            [Text("  No sequence loaded.", style="dim")],
            f"[{t_style('primary_bold')}]◈ [8] STRUCTURAL DISRUPTION MAP ◈[/{t_style('primary_bold')}]",
        )

    if "structural" not in cache:
        matrix, prov = get_contact_matrix(tokens)
        cache["structural"] = {"matrix": matrix, "provenance": prov}

    matrix = cache["structural"]["matrix"]
    prov = cache["structural"].get("provenance", "SIMULATED")

    applied = sim_state.get("applied", False)
    delta = sim_state.get("delta", None) if applied else None
    sdi = sim_state.get("sdi", 0.0) if applied else 0.0

    lines: List[Any] = []

    # Title and provenance
    prov_style = t_style("error_bold") if "SIMULATED" in prov else t_style("success_bold")
    prov_label = "[ SIMULATED — pre-training stub ]" if "SIMULATED" in prov else "[ LIVE MODEL OUTPUT ]"
    lines.append(Text(f"  {prov_label}", style=prov_style))

    if applied:
        sdi_col = _sdi_color(sdi)
        sdi_line = Text()
        sdi_line.append("  OVERLAYING VARIANT DELTA  SDI = ", style="dim")
        sdi_line.append(f"{sdi:.4f}", style=sdi_col)
        sdi_line.append("  (red=gain · blue=loss)", style="dim")
        lines.append(sdi_line)

    lines.append(Rule(style=f"dim {t_style('border')}"))

    # Stats
    n = len(matrix)
    flat = [matrix[r][c] for r in range(n) for c in range(n)]
    mean_v = sum(flat) / len(flat) if flat else 0.0
    max_v = max(flat) if flat else 0.0
    diag_vals = [matrix[i][i] for i in range(n)]
    off_diag = [matrix[r][c] for r in range(n) for c in range(n) if abs(r - c) == 5]
    decay_ratio = (sum(off_diag) / len(off_diag)) / (sum(diag_vals) / len(diag_vals)) if diag_vals else 0.0
    stat_pairs = [
        ("Matrix size", f"{n}×{n}"), ("Mean contact", f"{mean_v:.4f}"),
        ("Max contact", f"{max_v:.4f}"), ("Diag/off-diag ratio", f"{decay_ratio:.3f}"),
    ]

    avail_h = max(1, hud_h - len(lines))
    side_w = 32
    side_dims = _fit_matrix_dims(n, hud_w - side_w - 2, avail_h) if hud_w > side_w + 16 else (0, 0)
    bottom_tbl, bottom_rows = _fs_stat_table(stat_pairs, hud_w, 20)
    bottom_dims = _fit_matrix_dims(n, hud_w, max(1, avail_h - 3 - bottom_rows))
    bare_dims = _fit_matrix_dims(n, hud_w, avail_h)

    if max(side_dims[1], bottom_dims[1]) < 6 and bare_dims[1] > bottom_dims[1]:
        # Too short for the legend and stats — the matrix alone gets the space
        cols, rows = bare_dims
        lines.append(render_matrix_24bit(matrix, cols, rows, delta=delta))
    elif side_dims[0] >= bottom_dims[0]:
        cols, rows = side_dims
        side_tbl, _ = _fs_stat_table(stat_pairs, side_w, 20)
        side = Group(
            Text("Colour legend:", style="dim"),
            render_matrix_color_legend(side_w - 2),
            Text(""),
            side_tbl,
        )
        grid = Table.grid()
        grid.add_column(width=cols)
        grid.add_column(width=2)
        grid.add_column(width=side_w)
        grid.add_row(render_matrix_24bit(matrix, cols, rows, delta=delta), Text(""), side)
        lines.append(grid)
    else:
        cols, rows = bottom_dims
        lines.append(render_matrix_24bit(matrix, cols, rows, delta=delta))
        lines.append(Rule(style=f"dim {t_style('border')}"))
        legend_line = Text("  Colour legend  ", style="dim")
        legend_line.append_text(render_matrix_color_legend(max(10, hud_w - 17)))
        lines.append(legend_line)
        lines.append(bottom_tbl)

    title_s = (
        "[bold #ff4444]◈ [8] STRUCTURAL DISRUPTION — VARIANT ACTIVE ◈[/bold #ff4444]"
        if applied
        else f"[{t_style('primary_bold')}]◈ [8] STRUCTURAL DISRUPTION MAP ◈[/{t_style('primary_bold')}]"
    )

    return _fs_panel(lines, title_s, border_style="#ff4444" if applied else None)


def render_hud_9_goldbeam(
    tokens: List[int],
    cache: Dict[str, Any],
    frame: int,
    hud_w: int,
    hud_h: int,
    gb_countdown: int = 0,
) -> Panel:
    """Tool 9 — GoldBEAM mission control: model status, benchmark, prediction cockpit."""
    lines: List[Any] = []
    gold = "#ffaa00"
    dark_gold = "#cc8800"
    dim_gold = "#886600"
    label_w = 20 if hud_w >= 50 else 16

    def _kv_table() -> Table:
        tbl = Table(show_header=False, box=None, padding=(0, 1))
        tbl.add_column(style=f"dim {dark_gold}", width=label_w, no_wrap=True, overflow="ellipsis")
        tbl.add_column(no_wrap=True, overflow="ellipsis")
        return tbl

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append(Text(""))
    hdr = Text()
    hdr.append("  ⬡  GOLDBEAM PREDICTION ENGINE", style=f"bold {gold}")
    hdr.append("   ·   SWAEV Genomics v0.1.0-α", style="dim")
    lines.append(hdr)
    lines.append(Rule(style=f"dim {dark_gold}"))
    lines.append(Text(""))

    # ── Model status block ────────────────────────────────────────────────────
    status_tbl = _kv_table()
    status_tbl.add_row("MODEL STATUS",     Text("Pre-training  (frozen encoder)", style=gold))
    status_tbl.add_row("ARCHITECTURE",     Text("O(N) Transformer · multi-head contact", style=gold))
    status_tbl.add_row("HEADS",            Text("d1 · d2 · d4 · d8  (Akita-compatible)", style=gold))
    status_tbl.add_row("TRAINING TARGET",  Text("Pearson ρ on ENCODE Hi-C held-out set", style=gold))
    status_tbl.add_row("AKITA BENCHMARK",  Text("0.832 Pearson  (published baseline)", style=gold))
    lines.append(status_tbl)
    lines.append(Text(""))
    lines.append(Rule(style=f"dim {dark_gold}"))

    # ── Sequence status & inference block ────────────────────────────────────
    if not tokens:
        lines.append(Text(""))
        lines.append(Text("  No sequence loaded", style=f"bold {dark_gold}"))
    else:
        seq_len = len(tokens)
        gc_cnt = sum(1 for t in tokens if t in (1, 2))
        gc_pct = gc_cnt / seq_len * 100 if seq_len else 0.0

        lines.append(Text(""))
        seq_tbl = _kv_table()
        seq_tbl.add_row(
            "SEQUENCE LENGTH",
            Text(f"{seq_len/1_000:.1f} kb" if seq_len < 1_000_000 else f"{seq_len/1_000_000:.3f} Mb",
                 style=f"bold {gold}"),
        )
        seq_tbl.add_row("GC CONTENT", Text(f"{gc_pct:.1f}%", style=f"bold {gold}"))
        lines.append(seq_tbl)
        lines.append(Text(""))

        # Inference status
        if gb_countdown > 0:
            # Computing animation
            _dots = "●" * (3 - (gb_countdown // 7) % 4) + "○" * ((gb_countdown // 7) % 4)
            _spinner_frames = ["◐", "◓", "◑", "◒"]
            _sp = _spinner_frames[(frame // 4) % 4]
            computing = Text()
            computing.append(f"  {_sp}  COMPUTING CONTACT MAP  ", style=f"bold {gold}")
            computing.append(_dots, style=f"dim {dark_gold}")
            lines.append(computing)
        else:
            # Result ready
            matrix = cache.get("structural", {}).get("matrix")
            n_bins = len(matrix) if matrix else 0
            prov = cache.get("structural", {}).get("provenance", "SIMULATED")
            cell = cache.get("structural", {}).get("cell_line", "GM12878")

            result_tbl = _kv_table()
            result_tbl.add_row("PREDICTION STATUS", Text("COMPLETE", style=f"bold {gold}"))
            result_tbl.add_row("MATRIX SIZE",       Text(f"{n_bins}×{n_bins} bins", style=gold))
            result_tbl.add_row("CELL CONTEXT",      Text(cell, style=gold))
            result_tbl.add_row("PROVENANCE",        Text(f"[{prov}]", style=f"dim {dark_gold}"))
            lines.append(result_tbl)
            lines.append(Text(""))

            view_hint = Text()
            view_hint.append("  Contact matrix shown in ", style="dim")
            view_hint.append("Structural Disruption Map", style=f"bold {gold}")
            lines.append(view_hint)

    lines.append(Text(""))
    lines.append(Rule(style=f"dim {dark_gold}"))

    # ── Training roadmap ─────────────────────────────────────────────────────
    road = Text()
    road.append("  NEXT MILESTONE  ", style=f"dim {dark_gold}")
    road.append("Train encoder on ENCODE Hi-C  →  replace SIMULATED with live weights",
                style="dim")
    lines.append(road)

    # Pulse character for "live" feel
    _pulse = "▮" if (frame // 12) % 2 == 0 else "▯"
    lines.append(Text(f"  {_pulse}", style=f"dim {dim_gold}"))

    return _fs_panel(
        lines,
        Text("⬡ GOLDBEAM PREDICTION ⬡", style=f"bold {gold}"),
        border_style=dark_gold,
        max_h=hud_h,
    )


def _dispatch_hud(
    tool: int,
    tokens: List[int],
    sim_state: Dict[str, Any],
    cache: Dict[str, Any],
    frame: int,
    hud_w: int,
    hud_h: int,
    gb_countdown: int = 0,
) -> Panel:
    """Route to the correct HUD renderer for the active tool."""
    if tool == 1:
        return render_hud_1_analytics(tokens, cache, hud_w, hud_h)
    elif tool == 2:
        return render_hud_2_deletion_probe(tokens, sim_state, hud_w, hud_h)
    elif tool == 3:
        return render_hud_3_biophysical(tokens, cache, hud_w, hud_h)
    elif tool == 4:
        return render_hud_4_insulation(tokens, cache, hud_w, hud_h)
    elif tool == 5:
        return render_hud_5_multiscale(tokens, cache, frame, hud_w, hud_h)
    elif tool == 6:
        return render_hud_6_species_bias(tokens, cache, hud_w, hud_h)
    elif tool == 7:
        return render_hud_7_boundary_scan(tokens, cache, hud_w, hud_h)
    elif tool == 8:
        return render_hud_8_structural(tokens, sim_state, cache, hud_w, hud_h)
    elif tool == 9:
        return render_hud_9_goldbeam(tokens, cache, frame, hud_w, hud_h, gb_countdown)
    else:
        return Panel(Text("Select a tool [1–9]", style="dim"), border_style="dim")


# ── Inline command parser (Simulation Mode) ───────────────────────────────────

# First letters of the Simulation Mode commands (snp / del / reset). In
# Simulation mode these keys start typing a command instead of acting as hotkeys.
_SIM_COMMAND_STARTS = ("s", "d", "r")


def _parse_fs_command(
    cmd: str,
    tokens: List[int],
    sim_state: Dict[str, Any],
    cache: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Parse and execute an inline Simulation Mode command.
    Returns (handled: bool, toast_message: str).
    """
    lc = cmd.strip().lower()
    if not lc:
        return False, ""

    parts = lc.split()

    if lc == "reset":
        wt = cache.get("structural", {}).get("matrix") or (
            get_contact_matrix(tokens)[0] if tokens else []
        )
        sim_state.update({
            "applied": False,
            "desc": "No variant applied — showing wildtype",
            "wt_matrix": wt,
            "vt_matrix": wt,
            "delta": None,
            "sdi": 0.0,
            "delta_stats": {},
        })
        return True, "Variant reset — wildtype restored"

    if parts[0] == "snp" and len(parts) == 3 and ">" in parts[2]:
        try:
            pos_bp = int(parts[1])
            ref_b, alt_b = parts[2].upper().split(">", 1)
            seq_len = len(tokens)
            n_bins = len(cache.get("structural", {}).get("matrix") or []) or 40
            token_pos = max(0, min(seq_len - 1, pos_bp))
            bin_idx = token_pos * n_bins // max(1, seq_len)
            wt = cache.get("structural", {}).get("matrix")
            if wt is None:
                wt, _ = get_contact_matrix(tokens)
                cache.setdefault("structural", {})["matrix"] = wt
            vt = _perturb_matrix_near_bins(wt, [bin_idx], strength=0.30)
            delta = compute_delta_matrix(wt, vt)
            ds = compute_delta_stats(delta)
            sim_state.update({
                "applied": True,
                "desc": f"SNP  pos {pos_bp:,}  {ref_b}>{alt_b[0]}  (bin {bin_idx})",
                "wt_matrix": wt,
                "vt_matrix": vt,
                "delta": delta,
                "sdi": ds["mean_abs_delta"],
                "delta_stats": ds,
            })
            return True, f"SNP applied at {pos_bp:,}  SDI = {ds['mean_abs_delta']:.4f}"
        except (ValueError, IndexError):
            return True, "Usage: snp <position_bp> <REF>><ALT>  e.g. snp 500000 G>A"

    if parts[0] == "del" and len(parts) == 3:
        try:
            del_start = int(parts[1])
            del_end = int(parts[2])
            if del_start >= del_end:
                return True, "del: start must be less than end"
            seq_len = len(tokens)
            n_bins = len(cache.get("structural", {}).get("matrix") or []) or 40
            center_bin = ((del_start + del_end) // 2) * n_bins // max(1, seq_len)
            wt = cache.get("structural", {}).get("matrix")
            if wt is None:
                wt, _ = get_contact_matrix(tokens)
                cache.setdefault("structural", {})["matrix"] = wt
            vt = _perturb_matrix_near_bins(wt, [center_bin], strength=0.50)
            delta = compute_delta_matrix(wt, vt)
            ds = compute_delta_stats(delta)
            sim_state.update({
                "applied": True,
                "desc": f"DEL  {del_start:,}–{del_end:,}  ({del_end - del_start:,} bp)  bin {center_bin}",
                "wt_matrix": wt,
                "vt_matrix": vt,
                "delta": delta,
                "sdi": ds["mean_abs_delta"],
                "delta_stats": ds,
            })
            return True, f"Deletion {del_start:,}–{del_end:,}  SDI = {ds['mean_abs_delta']:.4f}"
        except (ValueError, IndexError):
            return True, "Usage: del <start_bp> <end_bp>  e.g. del 450000 520000"

    return False, ""


# ── GoldBEAM Genomic Flight Simulator — Main Loop ────────────────────────────

# ── Live UCSC Fetcher / CTCF Scanner / Cell-Line Shifter ─────────────────────

_CTCF_MOTIF_DEFS: List[Tuple[str, str]] = [
    ("CTCF_core",    "CCCTCCTGG"),   # Core CTCF 9-bp motif (JASPAR MA0139.1)
    ("CTCF_core_rc", "CCAGGAGGG"),   # Reverse complement
    ("CTCF_alt",     "GGGTGGCAG"),   # Alternate CTCF binding
    ("CTCF_alt_rc",  "CTGCCACCC"),   # RC of alternate
    ("SP1_GC_box",   "GGGCGG"),      # GC-box / SP1 colocalization
    ("CpG_cluster",  "CCGCGCGG"),    # CpG island seed
]
_NUC_FROM_TOKEN: Dict[int, str] = {0: "A", 1: "C", 2: "G", 3: "T", 4: "N"}

_CELL_LINES: List[Tuple[str, str, str]] = [
    ("GM12878", "Lymphoblastoid", "#aa44ff"),
    ("H1-hESC", "Embryonic Stem", "#00aaff"),
    ("IMR90",   "Fibroblast",     "#ff8800"),
]


def _tokens_to_seq(tokens: List[int]) -> str:
    nmap = _NUC_FROM_TOKEN
    return "".join(nmap.get(t, "N") for t in tokens)


def scan_ctcf_motifs(
    tokens: List[int],
    coord_offset: int = 0,
    max_results: int = 200,
) -> List[Dict[str, Any]]:
    """Exact-string scan of _CTCF_MOTIF_DEFS patterns; returns hit dicts sorted by position."""
    seq = _tokens_to_seq(tokens)
    results: List[Dict[str, Any]] = []
    for motif_name, pattern in _CTCF_MOTIF_DEFS:
        pos = 0
        while len(results) < max_results:
            idx = seq.find(pattern, pos)
            if idx == -1:
                break
            results.append({
                "name":        motif_name,
                "start":       idx + coord_offset,
                "end":         idx + len(pattern) + coord_offset,
                "local_start": idx,
                "local_end":   idx + len(pattern),
                "seq":         pattern,
            })
            pos = idx + 1
    results.sort(key=lambda r: r["start"])
    return results[:max_results]


def _cell_line_shift_matrix(
    matrix: List[List[float]], cell_idx: int
) -> List[List[float]]:
    """Applies a deterministic distance-based bias to simulate cell-line chromatin context."""
    if not matrix or not matrix[0]:
        return matrix
    n = len(matrix)
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            v = matrix[i][j]
            d = abs(i - j)
            if cell_idx == 0:       # GM12878 — sharp TAD compartments
                f = 1.3 if d < n // 8 else (0.75 if d > n // 3 else 1.0)
            elif cell_idx == 1:     # H1-hESC — diffuse, open chromatin
                f = 0.85 if d < n // 8 else (1.2 if d > n // 3 else 1.0)
            else:                   # IMR90 — fibroblast baseline
                f = 1.1 if d < n // 6 else (0.9 if d > n // 4 else 1.05)
            out[i][j] = min(1.0, max(0.0, v * f))
    return out


def _do_ucsc_fetch(coord_str: str, result_dict: Dict[str, Any]) -> None:
    """Thread target: fetches UCSC hg38 sequence, falls back to synthetic on failure."""
    import random as _rnd
    parsed = _parse_genomic_coord(coord_str)
    if parsed is None:
        result_dict.update({"state": "done", "result": None, "error": "Bad coordinate"})
        return
    chrom, start, end = parsed
    real_tokens = fetch_ucsc_sequence(chrom, start, end)
    if real_tokens is not None:
        result_dict.update({"state": "done", "result": real_tokens, "error": None})
    else:
        length = max(1024, min(end - start, 1_000_000))
        result_dict.update({
            "state": "done",
            "result": [_rnd.randint(0, 3) for _ in range(length)],
            "error": "UCSC unavailable — synthetic fallback",
        })


def render_file_browser_overlay(
    files: List[str],
    selected: int,
    fasta_dir: str,
    path_mode: bool,
    path_buffer: str,
    hud_w: int,
    hud_h: int,
) -> Panel:
    """In-panel file browser overlay — replaces HUD while open."""
    lines: List[Any] = []
    lines.append(Text(""))

    dir_disp = fasta_dir
    dir_room = max(8, hud_w - 7)
    if len(dir_disp) > dir_room:
        dir_disp = "…" + dir_disp[-(dir_room - 1):]
    dir_line = Text()
    dir_line.append("  DIR  ", style=f"dim {t_style('border')}")
    dir_line.append(dir_disp, style=t_style("primary_bold"))
    lines.append(dir_line)
    lines.append(Rule(style=f"dim {t_style('border')}"))
    lines.append(Text(""))

    # blank + dir + rule + blank above; blank + more-line (+ rule + path bar) below
    reserved = 4 + 2 + (2 if path_mode else 0)
    max_visible = max(1, hud_h - reserved)

    if not files:
        lines.append(Text("  No FASTA files found in directory.", style="dim"))
    else:
        # Scroll window around selected
        scroll_top = max(0, selected - max_visible // 2)
        scroll_top = min(scroll_top, max(0, len(files) - max_visible))
        visible = files[scroll_top : scroll_top + max_visible]

        for vi, fname in enumerate(visible):
            real_idx = scroll_top + vi
            is_sel = real_idx == selected
            row = Text()
            if is_sel:
                row.append("  ▶ ", style=t_style("primary_bold"))
                row.append(f"{real_idx + 1:>3}. ", style=t_style("primary_bold"))
                row.append(fname, style=t_style("primary_bold"))
            else:
                row.append("    ", style="")
                row.append(f"{real_idx + 1:>3}. ", style="dim")
                row.append(fname, style="dim")
            lines.append(row)

        if len(files) > max_visible:
            lines.append(Text(f"  … {len(files)} files total", style="dim"))

    # Path input bar
    if path_mode:
        lines.append(Text(""))
        lines.append(Rule(style=f"dim {t_style('border')}"))
        cursor = "▮" if int(time.time() * 2) % 2 == 0 else " "
        bar = Text()
        bar.append("  PATH> ", style=t_style("primary_bold"))
        bar.append(path_buffer, style=t_style("primary_bold"))
        bar.append(cursor, style=t_style("primary_bold"))
        lines.append(bar)

    return _fs_panel(lines, Text("◈ SEQUENCE LOADER ◈", style=t_style("primary_bold")), max_h=hud_h)


def render_history_overlay(
    history: List[Dict[str, Any]],
    selected: int,
    current_id: str,
    hud_w: int,
    hud_h: int,
) -> Panel:
    """Session history overlay — replaces the HUD while open."""
    lines: List[Any] = []
    lines.append(Text(""))

    if not history:
        lines.append(Text("  No sessions yet.", style="dim"))
        lines.append(Text("  Sequences you load or fetch from UCSC are listed here.", style="dim"))
        return _fs_panel(lines, Text("◈ SESSION HISTORY ◈", style=t_style("primary_bold")), max_h=hud_h)

    selected = max(0, min(selected, len(history) - 1))
    sel = history[selected]
    variants = sel.get("variants", [])
    exports = sel.get("exports", [])

    # Detail pane for the selected session (dropped on very short terminals)
    detail: List[Any] = []
    if hud_h >= 12:
        detail.append(Rule(style=f"dim {t_style('border')}"))
        src_line = Text()
        if sel["source"] == "file":
            path_disp = sel["locator"]
            path_room = max(8, hud_w - 12 - (11 if not os.path.isfile(path_disp) else 0))
            if len(path_disp) > path_room:
                path_disp = "…" + path_disp[-(path_room - 1):]
            src_line.append("  FILE      ", style="dim")
            src_line.append(path_disp, style=t_style("primary_bold"))
            if not os.path.isfile(sel["locator"]):
                src_line.append("  (missing)", style=t_style("error_bold"))
        else:
            src_line.append("  UCSC hg38 ", style="dim")
            src_line.append(sel["locator"], style=t_style("primary_bold"))
            if sel.get("synthetic"):
                src_line.append("  (synthetic fallback)", style="dim")
        detail.append(src_line)
        ctx_line = Text()
        ctx_line.append("  CELL LINE ", style="dim")
        ctx_line.append(sel.get("cell_line", "—"), style=t_style("primary_bold"))
        ctx_line.append("   OPENED ", style="dim")
        ctx_line.append(sel.get("last_opened", "—"), style=t_style("primary_bold"))
        detail.append(ctx_line)

        room = max(0, (hud_h - 12) // 2)
        show_n = max(1, min(3, room))
        var_line = Text("  VARIANTS  ", style="dim")
        if variants:
            for v in variants[-show_n:]:
                var_line.append(f"{v.get('cmd', '?')}", style=t_style("primary_bold"))
                var_line.append(f" (SDI {v.get('sdi', 0):.4f})  ", style="dim")
            if len(variants) > show_n:
                var_line.append(f"+{len(variants) - show_n} earlier", style="dim")
        else:
            var_line.append("none", style="dim")
        detail.append(var_line)
        exp_line = Text("  EXPORTS   ", style="dim")
        if exports:
            exp_line.append("  ".join(exports[-show_n:]), style=t_style("primary_bold"))
            if len(exports) > show_n:
                exp_line.append(f"  +{len(exports) - show_n} earlier", style="dim")
        else:
            exp_line.append("none", style="dim")
        detail.append(exp_line)

    # blank line above the list, "… N sessions" line below it, then the detail pane
    max_visible = max(1, hud_h - 2 - len(detail))
    scroll_top = max(0, selected - max_visible // 2)
    scroll_top = min(scroll_top, max(0, len(history) - max_visible))

    for idx in range(scroll_top, min(len(history), scroll_top + max_visible)):
        entry = history[idx]
        is_sel = idx == selected
        length = entry.get("length", 0)
        len_str = (
            f"{length / 1_000_000:.2f} Mb" if length >= 1_000_000
            else f"{length / 1_000:.1f} kb" if length >= 1_000
            else f"{length} bp"
        )
        n_var = len(entry.get("variants", []))
        n_exp = len(entry.get("exports", []))
        style = t_style("primary_bold") if is_sel else "dim"

        row = Text()
        row.append("  ▶ " if is_sel else "    ", style=style)
        row.append("● " if entry.get("id") == current_id else "  ", style=t_style("success_bold"))
        row.append(f"{entry.get('last_opened', '')[5:]}  ", style=style)
        row.append("UCSC " if entry["source"] == "ucsc" else "FILE ", style="bold #00ffcc" if is_sel else "dim")
        row.append(entry.get("name", entry["locator"]), style=style)
        row.append(f"  {len_str} · GC {entry.get('gc_pct', 0):.1f}%", style="dim")
        if n_var or n_exp:
            row.append(f" · {n_var} variant{'s' if n_var != 1 else ''} · {n_exp} export{'s' if n_exp != 1 else ''}", style="dim")
        lines.append(row)

    if len(history) > max_visible:
        lines.append(Text(f"  … {len(history)} sessions", style="dim"))
    lines.extend(detail)

    return _fs_panel(lines, Text("◈ SESSION HISTORY ◈", style=t_style("primary_bold")), max_h=hud_h)


def render_ctcf_overlay(
    results: List[Dict[str, Any]],
    selected: int,
    scan_running: bool,
    hud_w: int,
    hud_h: int,
) -> Panel:
    """Full-HUD CTCF motif results overlay with keyboard navigation."""
    lines: List[Any] = []
    if scan_running:
        _sp = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(time.time() * 10) % 10]
        lines.append(Text(f"  {_sp} Scanning sequence for structural anchors…", style=t_style("primary_bold")))
    elif not results:
        lines.append(Text("  No CTCF / GC-box motifs detected in loaded sequence.", style="dim"))
        lines.append(Text("  Try a longer sequence.", style="dim"))
    else:
        n = len(results)
        visible = max(1, hud_h - 1)
        v_start = max(0, min(selected - visible // 2, n - visible))
        v_end = min(n, v_start + visible)
        # "  ▶ " + name(14) + 2 + coord + 2 + seq(≤9)
        _coord_w = max(8, hud_w - 31)
        for idx in range(v_start, v_end):
            r = results[idx]
            is_sel = idx == selected
            sel_bg = f"bold #000000 on {t_style('primary')}"
            _coord = f"{r['start']:,}–{r['end']:,}"
            if len(_coord) > _coord_w:
                _coord = _coord[:_coord_w - 1] + "…"
            row = Text()
            row.append(f"  {'▶' if is_sel else ' '} ", style=sel_bg if is_sel else "dim")
            row.append(f"{r['name']:<14}", style=sel_bg if is_sel else t_style("primary_bold"))
            row.append(f"  {_coord:<{_coord_w}}  ", style=sel_bg if is_sel else "")
            row.append(f"{r['seq']}", style=sel_bg if is_sel else "bold #aaddaa")
            lines.append(row)
        if n > visible:
            pct = int(100 * selected / max(1, n - 1))
            lines.append(Text(f"  … {n} anchors total · {pct}%", style="dim"))
    n_label = (
        f" {len(results)} anchors" if results and not scan_running
        else (" scanning…" if scan_running else "")
    )
    return _fs_panel(
        lines,
        f"[{t_style('primary_bold')}]◈ CTCF MOTIF SCANNER{n_label} ◈[/{t_style('primary_bold')}]",
    )


def run_goldbeam_flight_simulator(
    tokens: List[int],
    filename: str,
    config: Dict[str, Any],
) -> None:
    """
    GoldBEAM Genomic Flight Simulator.

    3-panel immersive retro-terminal analysis platform:
      Left   — HUD Workspace (tool-specific content, instantly responsive to 1–8)
      Centre — Toolkit Registry (keyboard-navigable menu)
      Right  — Sequence Radar (motif-aware rotating DNA double helix)

    Non-blocking keystroke reader via os.read(fd) + select.select runs at 25 fps
    without ever blocking the animation loop.

    Keyboard map
    ────────────
    1–8   switch tool         M   toggle Observation / Simulation mode
    L     load new sequence   I   launch Interpretability Suite
    H     session history     E   export active tool output
    ?     contextual help     Q   quit
    (Simulation mode) type snp/del/reset and press Enter to mutate
    """
    import termios, tty, select as _sel

    # ── Layout (rebuilt whenever the terminal size changes the geometry) ─────
    def _current_geometry(context: str = "main", sim_mode: str = "OBSERVATION") -> Dict[str, Any]:
        term_w, term_h = console.size
        # Reserve the taller of the main and current key bars so opening an
        # overlay doesn't shift the panels by a line
        _, main_lines = _render_key_bar(_fs_key_items("main", sim_mode), term_w)
        _, ctx_lines = _render_key_bar(_fs_key_items(context, sim_mode), term_w)
        return _fs_geometry(term_w, term_h, max(main_lines, ctx_lines))

    geo = _current_geometry()
    layout = _fs_build_layout(geo)

    # ── State ─────────────────────────────────────────────────────────────────
    active_tool: int = 8          # start on the structural map
    mode: str = "OBSERVATION"     # "OBSERVATION" | "SIMULATION"
    frame: int = 0
    pulse_frames: int = 15 if tokens else 0
    cmd_buffer: str = ""          # inline command entry (Simulation mode)
    toast_msg: str = ""
    toast_expire: float = 0.0
    phage_state: str = "idle"
    phage_victory_expire: float = 0.0

    # Per-tool analysis cache (computed lazily on first tool visit)
    analysis_cache: Dict[str, Any] = {}

    # Simulation state (shared across tools 2 and 8)
    wt_matrix = None
    if tokens:
        wt_matrix, _ = get_contact_matrix(tokens)
        analysis_cache["structural"] = {"matrix": wt_matrix, "provenance": "SIMULATED"}

    sim_state: Dict[str, Any] = {
        "applied": False,
        "desc": "No variant applied — showing wildtype",
        "wt_matrix": wt_matrix or [],
        "vt_matrix": wt_matrix or [],
        "delta": None,
        "sdi": 0.0,
        "delta_stats": {},
    }

    # ── New feature state ──────────────────────────────────────────────────────
    cell_line_idx: int = 0           # 0=GM12878 1=H1-hESC 2=IMR90
    goto_mode: bool = False          # GOTO coordinate input active
    goto_buffer: str = ""
    fetch_state: Dict[str, Any] = {"state": "idle", "result": None, "coord": "", "error": None}
    ctcf_overlay: bool = False       # CTCF scanner overlay open
    ctcf_selected: int = 0
    ctcf_scan_state: Dict[str, Any] = {"state": "idle", "results": [], "toast_shown": False}

    # ── File browser overlay state ─────────────────────────────────────────
    file_browser_open: bool = False
    fb_files: List[str] = []
    fb_selected: int = 0
    fb_path_mode: bool = False
    fb_buffer: str = ""

    # ── History overlay state ──────────────────────────────────────────────
    history_open: bool = False
    hist_selected: int = 0
    hist_data: List[Dict[str, Any]] = []
    current_session_id: str = ""     # history entry of the loaded sequence

    # ── GoldBEAM countdown (frames of "computing" animation on tool 9 entry)
    gb_countdown: int = 0

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def _set_toast(msg: str, duration: float = 3.5) -> None:
        nonlocal toast_msg, toast_expire
        toast_msg = msg
        toast_expire = time.time() + duration

    def _activate_sequence(
        new_tokens: List[int],
        name: str,
        source: str,
        locator: str,
        coords: Optional[Tuple[str, int, int]] = None,
        note: str = "",
    ) -> None:
        """Makes new_tokens the working sequence and logs it to session history."""
        nonlocal tokens, filename, wt_matrix, ctcf_overlay, pulse_frames
        nonlocal phage_state, phage_victory_expire, gb_countdown, current_session_id
        tokens = new_tokens
        filename = name
        _LAST_SEQUENCE_INFO["filename"] = name
        _LAST_SEQUENCE_INFO["path"] = locator if source == "file" else ""
        for _key in ("chrom", "start", "end"):
            _LAST_SEQUENCE_INFO.pop(_key, None)
        if coords:
            _LAST_SEQUENCE_INFO.update({"chrom": coords[0], "start": coords[1], "end": coords[2]})
        analysis_cache.clear()
        ctcf_scan_state.update({"state": "idle", "results": [], "toast_shown": False})
        ctcf_overlay = False
        wt_matrix, _ = get_contact_matrix(tokens)
        cl_matrix = _cell_line_shift_matrix(wt_matrix, cell_line_idx)
        analysis_cache["structural"] = {
            "matrix": cl_matrix,
            "provenance": "SIMULATED",
            "cell_line": _CELL_LINES[cell_line_idx][0],
        }
        sim_state.update({
            "applied": False,
            "desc": "No variant applied — showing wildtype",
            "wt_matrix": cl_matrix,
            "vt_matrix": cl_matrix,
            "delta": None, "sdi": 0.0, "delta_stats": {},
        })
        pulse_frames = 20
        phage_state = "victory"
        phage_victory_expire = time.time() + 3.0
        gb_countdown = 24
        current_session_id = record_sequence_session(
            source, locator, name, tokens, _CELL_LINES[cell_line_idx][0], synthetic=bool(note),
        )
        _set_toast(f"Loaded: {name}  ({len(tokens):,} bp)" + (f"  [{note}]" if note else ""))

    def _load_fasta_path(path: str) -> None:
        if not os.path.isfile(path):
            _set_toast(f"File not found: {path}")
            return
        new_tokens = parse_fasta(path)
        if new_tokens:
            _activate_sequence(new_tokens, os.path.basename(path), "file", os.path.abspath(path))
        else:
            _set_toast(f"Could not parse FASTA file: {os.path.basename(path)}")

    def _start_ucsc_fetch(coord: str) -> None:
        if fetch_state["state"] != "idle":
            _set_toast("A UCSC fetch is already running")
            return
        import threading as _threading
        fetch_state.update({"state": "running", "result": None, "coord": coord, "error": None})
        _threading.Thread(target=_do_ucsc_fetch, args=(coord, fetch_state), daemon=True).start()
        _set_toast(f"Fetching UCSC: {coord} …")

    def _run_variant_command(command: str) -> Tuple[bool, str]:
        """Applies an snp/del/reset command and logs applied variants to the session."""
        desc_before = sim_state.get("desc")
        handled, msg = _parse_fs_command(command, tokens, sim_state, analysis_cache)
        if handled:
            analysis_cache.pop("structural", None)
            if wt_matrix:
                analysis_cache["structural"] = {
                    "matrix": sim_state["wt_matrix"],
                    "provenance": "SIMULATED",
                }
            if sim_state.get("applied") and sim_state.get("desc") != desc_before:
                update_session_history(current_session_id, variant={
                    "cmd": " ".join(command.lower().split()),
                    "sdi": round(sim_state.get("sdi", 0.0), 4),
                    "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
        return handled, msg

    def _remove_selected_history() -> None:
        nonlocal hist_data, hist_selected
        if not hist_data:
            return
        entry = hist_data[hist_selected]
        remove_session_history(entry["id"])
        hist_data = load_session_history()
        hist_selected = max(0, min(hist_selected, len(hist_data) - 1))
        _set_toast(f"Removed from history: {entry.get('name', entry['locator'])}")

    live_ref: List[Live] = []

    def _sync_layout(new_geo: Dict[str, Any]) -> Dict[str, Any]:
        """Swap in a new layout tree when the terminal size changes the geometry."""
        nonlocal layout, geo
        if new_geo["key"] != geo["key"]:
            layout = _fs_build_layout(new_geo)
            if live_ref:
                live_ref[0].update(layout)
        geo = new_geo
        if geo["too_small"]:
            layout.update(_fs_too_small_panel(geo["term_w"], geo["term_h"]))
        return geo

    try:
        tty.setcbreak(fd)

        with Live(
            layout,
            console=console,
            screen=True,
            auto_refresh=False,
        ) as live:
            live_ref.append(live)
            # ── Boot animation (same Live context — no flash) ─────────────────
            _boot_msgs = [
                "[✓] Secure gateway       authenticated",
                "[✓] TPU v6e cluster      16× Pod mapped",
                "[✓] GoldBEAM weights     frozen encoder loaded",
                "[✓] Sequence engine      O(N) model active",
                "[✓] 3D genome models     all heads online",
                "[✓] Contact simulator    standby",
            ]
            _boot_phases = [
                ("zoom",          0, 0.10, 1),
                ("zoom",          1, 0.14, 2),
                ("zoom",          2, 0.18, 3),
                ("land_compress", 0, 0.10, 4),
                ("land_stretch",  0, 0.10, 5),
                ("land_compress", 1, 0.10, 5),
                ("idle",          0, 0.16, 6),
                ("idle",          1, 0.14, 6),
                ("idle",          2, 0.22, 6),
            ]
            for _bph_state, _bph_frame, _bdelay, _bn_msgs in _boot_phases:
                geo = _sync_layout(_current_geometry())
                if geo["too_small"]:
                    live.refresh()
                    time.sleep(_bdelay)
                    continue

                _blines: List[Any] = []
                _blines.append(Text(""))
                _blines.append(Text(
                    "  SWAEV GENOMICS — INITIALIZING",
                    style=t_style("primary_bold"),
                ))
                _blines.append(Text(
                    "  SWAEV Genomics v0.1.0-α",
                    style="dim",
                ))
                _blines.append(Rule(style=f"dim {t_style('border')}"))
                _blines.append(Text(""))
                for _bm in _boot_msgs[:_bn_msgs]:
                    _blines.append(Text(f"  {_bm}", style=t_style("success_bold")))
                if _bn_msgs < len(_boot_msgs):
                    _blines.append(Text("  ▮", style=t_style("primary")))
                _blines.append(Text(""))
                if _bn_msgs >= len(_boot_msgs):
                    _blines.append(Rule(style=t_style("border")))
                    _blines.append(Text(
                        "  FLIGHT SIMULATOR READY",
                        style=t_style("primary_bold"),
                    ))

                layout["header"].update(
                    render_flight_header(
                        [], "", config, _bph_frame, active_tool, mode,
                        phage_state=_bph_state,
                        header_mode=geo["header_mode"],
                    )
                )
                layout["hud"].update(_fs_panel(
                    _blines,
                    Text("◈ BOOT SEQUENCE ◈", style=t_style("primary_bold")),
                    max_h=geo["hud_h"],
                ))
                if geo["toolkit_w"]:
                    layout["toolkit"].update(render_toolkit_menu(0, geo["body_h"]))
                else:
                    layout["strip"].update(render_tool_strip(0))
                if geo["helix_w"]:
                    layout["helix"].update(
                        render_sequence_helix([], _bph_frame, geo["helix_w"], geo["body_h"], 0)
                    )
                layout["footer"].update(Text(""))
                live.refresh()
                time.sleep(_bdelay)
            # ── End boot animation ────────────────────────────────────────────

            target_fps = 25
            frame_dt = 1.0 / target_fps

            while True:
                now = time.time()
                frame += 1
                if pulse_frames > 0:
                    pulse_frames -= 1

                # ── Background fetch completion ────────────────────────────────
                if fetch_state["state"] == "done":
                    new_toks = fetch_state["result"]
                    coord_fetched = fetch_state["coord"]
                    err_fetched = fetch_state.get("error")
                    fetch_state.update({"state": "idle", "result": None, "coord": "", "error": None})
                    if new_toks:
                        _activate_sequence(
                            new_toks, f"fetch:{coord_fetched}", "ucsc", coord_fetched,
                            coords=_parse_genomic_coord(coord_fetched), note=err_fetched or "",
                        )
                    else:
                        _set_toast("Fetch failed — check coordinate format")

                # ── CTCF scan completion toast ─────────────────────────────────
                if (ctcf_scan_state["state"] == "done"
                        and not ctcf_scan_state["toast_shown"]):
                    ctcf_scan_state["toast_shown"] = True
                    n_hits = len(ctcf_scan_state["results"])
                    ctcf_selected = 0
                    _set_toast(f"CTCF scan complete: {n_hits} anchors found")

                # Decrement GoldBEAM compute countdown
                if gb_countdown > 0:
                    gb_countdown -= 1

                # Update phage mascot state
                if time.time() < phage_victory_expire:
                    phage_state = "victory"
                elif file_browser_open or history_open:
                    phage_state = "thinking"
                elif active_tool == 9 and gb_countdown > 0:
                    phage_state = "weights"
                elif active_tool == 9 and tokens:
                    phage_state = "weights"
                elif mode == "SIMULATION" and sim_state.get("applied", False):
                    phage_state = "weights"
                elif mode == "SIMULATION":
                    phage_state = "dancing"
                else:
                    phage_state = "idle"

                # ── Terminal geometry (re-measured every frame) ───────────────
                if file_browser_open:
                    key_ctx = "path" if fb_path_mode else "browser"
                elif history_open:
                    key_ctx = "history"
                elif ctcf_overlay:
                    key_ctx = "ctcf"
                elif goto_mode:
                    key_ctx = "goto"
                elif mode == "SIMULATION" and cmd_buffer:
                    key_ctx = "simcmd"
                else:
                    key_ctx = "main"
                geo = _sync_layout(_current_geometry(key_ctx, mode))
                if geo["too_small"]:
                    live.refresh()
                    r_avail, _, _ = _sel.select([fd], [], [], frame_dt)
                    if r_avail and os.read(fd, 1) in (b"q", b"Q", b"\x03", b"\x04"):
                        break
                    continue

                # ── Render all panels ─────────────────────────────────────────
                layout["header"].update(
                    render_flight_header(
                        tokens, filename, config, frame // 8, active_tool, mode,
                        phage_state=phage_state,
                        cell_line_idx=cell_line_idx,
                        goto_mode=goto_mode,
                        goto_buffer=goto_buffer,
                        fetch_running=(fetch_state["state"] == "running"),
                        header_mode=geo["header_mode"],
                    )
                )
                if geo["toolkit_w"]:
                    layout["toolkit"].update(render_toolkit_menu(active_tool, geo["body_h"]))
                else:
                    layout["strip"].update(render_tool_strip(active_tool))
                if geo["helix_w"]:
                    layout["helix"].update(
                        render_sequence_helix(tokens, frame, geo["helix_w"], geo["body_h"], pulse_frames,
                                              helix_tint="gold" if active_tool == 9 else "")
                    )
                key_bar, _ = _render_key_bar(_fs_key_items(key_ctx, mode), geo["term_w"], geo["footer_h"])
                layout["footer"].update(key_bar)

                # A 3-row toast or command bar shares the HUD column with the active panel
                typing_cmd = mode == "SIMULATION" and bool(cmd_buffer) and not (
                    file_browser_open or history_open or ctcf_overlay)
                show_toast = bool(toast_msg) and now < toast_expire and not typing_cmd
                overlay_open = file_browser_open or history_open or ctcf_overlay
                show_cmd_bar = not show_toast and not overlay_open and mode == "SIMULATION"
                bar_rows = 3 if (show_toast or show_cmd_bar) and geo["hud_outer_h"] >= 9 else 0
                hud_w = geo["hud_w"]
                hud_h = max(1, geo["hud_h"] - bar_rows)

                # HUD: file browser → history → CTCF overlay → normal HUD
                if file_browser_open:
                    hud_panel = render_file_browser_overlay(
                        fb_files, fb_selected,
                        config.get("fasta_dir", "."),
                        fb_path_mode, fb_buffer,
                        hud_w, hud_h,
                    )
                elif history_open:
                    hud_panel = render_history_overlay(
                        hist_data, hist_selected, current_session_id, hud_w, hud_h,
                    )
                elif ctcf_overlay:
                    hud_panel = render_ctcf_overlay(
                        ctcf_scan_state["results"],
                        ctcf_selected,
                        ctcf_scan_state["state"] == "running",
                        hud_w, hud_h,
                    )
                else:
                    hud_panel = _dispatch_hud(
                        active_tool, tokens, sim_state, analysis_cache,
                        frame, hud_w, hud_h, gb_countdown,
                    )

                if bar_rows and show_toast:
                    toast_panel = Panel(
                        Text(f"  {toast_msg}", style="bold #111111", no_wrap=True, overflow="ellipsis"),
                        style=f"bold #111111 on {t_style('primary')}",
                        height=3, padding=(0, 1),
                    )
                    hud_panel.height = geo["hud_outer_h"] - 3
                    layout["hud"].update(Group(toast_panel, hud_panel))
                elif bar_rows and show_cmd_bar:
                    cursor = "▮" if int(now * 2) % 2 == 0 else " "
                    cmd_text = Text.assemble(
                        ("  SIMULATE> ", "bold #ff4444"),
                        (cmd_buffer, t_style("primary_bold")),
                        (cursor, t_style("primary_bold")),
                        no_wrap=True, overflow="ellipsis",
                    )
                    if active_tool != 2:  # tool [2] already lists the command syntax
                        cmd_text.append("   snp <pos> <REF>><ALT>  |  del <start> <end>  |  reset", style="dim")
                    cmd_bar = Panel(cmd_text, height=3, border_style="#ff4444", padding=(0, 0))
                    hud_panel.height = geo["hud_outer_h"] - 3
                    layout["hud"].update(Group(hud_panel, cmd_bar))
                else:
                    if show_toast:
                        # Too short for a 3-row bar: carry the message in the panel's bottom border
                        hud_panel.subtitle = Text(f" {toast_msg} ", style=f"bold #111111 on {t_style('primary')}")
                    elif show_cmd_bar:
                        cursor = "▮" if int(now * 2) % 2 == 0 else " "
                        hud_panel.subtitle = Text.assemble(
                            (" SIMULATE> ", "bold #ff4444"),
                            (cmd_buffer, t_style("primary_bold")),
                            (cursor + " ", t_style("primary_bold")),
                        )
                    layout["hud"].update(hud_panel)

                live.refresh()

                # ── Non-blocking input (25 fps budget) ───────────────────────
                elapsed = time.time() - now
                wait = max(0.005, frame_dt - elapsed)
                r_avail, _, _ = _sel.select([fd], [], [], wait)

                if not r_avail:
                    continue

                ch = os.read(fd, 1).decode("utf-8", errors="replace")

                # ESC sequences — drain completely; route arrows to active modal
                if ch == "\x1b":
                    _esc_seq = ""
                    while True:
                        dr, _, _ = _sel.select([fd], [], [], 0.12)
                        if dr:
                            ec = os.read(fd, 1).decode("utf-8", errors="replace")
                            _esc_seq += ec
                            if ec in ("A", "B", "C", "D", "H", "F", "M", "m", "~", "l", "h", "R"):
                                break
                        else:
                            break
                    if file_browser_open:
                        if _esc_seq.endswith("A"):   # Up
                            fb_selected = max(0, fb_selected - 1)
                        elif _esc_seq.endswith("B"): # Down
                            fb_selected = min(max(0, len(fb_files) - 1), fb_selected + 1)
                        elif not _esc_seq:           # bare ESC
                            file_browser_open = False
                            fb_path_mode = False
                            fb_buffer = ""
                    elif history_open:
                        if _esc_seq.endswith("A"):   # Up
                            hist_selected = max(0, hist_selected - 1)
                        elif _esc_seq.endswith("B"): # Down
                            hist_selected = min(max(0, len(hist_data) - 1), hist_selected + 1)
                        elif _esc_seq.endswith("3~"):  # Delete
                            _remove_selected_history()
                        elif not _esc_seq:           # bare ESC
                            history_open = False
                    elif ctcf_overlay:
                        _hits = ctcf_scan_state["results"]
                        if _esc_seq.endswith("A"):   # Up
                            ctcf_selected = max(0, ctcf_selected - 1)
                        elif _esc_seq.endswith("B"): # Down
                            ctcf_selected = min(max(0, len(_hits) - 1), ctcf_selected + 1)
                        elif not _esc_seq:           # bare ESC
                            ctcf_overlay = False
                    elif goto_mode and not _esc_seq:
                        goto_mode = False
                        goto_buffer = ""
                    elif mode == "SIMULATION" and cmd_buffer and not _esc_seq:
                        cmd_buffer = ""
                    continue

                # ── File browser modal ───────────────────────────────────────
                if file_browser_open:
                    fasta_dir_fb = config.get("fasta_dir", ".")
                    if fb_path_mode:
                        # Path input sub-mode
                        if ch in ("\r", "\n"):
                            _load_path = fb_buffer.strip()
                            if not os.path.isabs(_load_path):
                                _load_path = os.path.join(fasta_dir_fb, _load_path)
                            _load_fasta_path(_load_path)
                            file_browser_open = False
                            fb_path_mode = False
                            fb_buffer = ""
                        elif ch in ("\x1b",):
                            fb_path_mode = False
                            fb_buffer = ""
                        elif ch in ("\x7f", "\x08"):
                            fb_buffer = fb_buffer[:-1]
                        elif ord(ch) >= 32:
                            fb_buffer += ch
                    else:
                        # Browse mode
                        if ch in ("l", "L", "\x1b"):
                            file_browser_open = False
                            fb_path_mode = False
                            fb_buffer = ""
                        elif ch in ("\r", "\n") and fb_files:
                            _load_fasta_path(os.path.join(fasta_dir_fb, fb_files[fb_selected]))
                            file_browser_open = False
                        elif ch in ("/", ":"):
                            fb_path_mode = True
                            fb_buffer = ""
                        elif ch in ("g", "G"):
                            # Pivot to GOTO mode
                            file_browser_open = False
                            goto_mode = True
                            ctcf_overlay = False
                    continue

                # ── History overlay modal ─────────────────────────────────────
                if history_open:
                    if ch in ("h", "H", "\x1b"):
                        history_open = False
                    elif ch in ("x", "X"):
                        _remove_selected_history()
                    elif ch in ("\r", "\n") and hist_data:
                        entry = hist_data[hist_selected]
                        history_open = False
                        cl_names = [cl[0] for cl in _CELL_LINES]
                        if entry.get("cell_line") in cl_names:
                            cell_line_idx = cl_names.index(entry["cell_line"])
                        if entry["source"] == "file":
                            _load_fasta_path(entry["locator"])
                        else:
                            _start_ucsc_fetch(entry["locator"])
                    continue

                # ── CTCF overlay modal ────────────────────────────────────────
                if ctcf_overlay:
                    _hits = ctcf_scan_state["results"]
                    if ch in ("c", "C", "\x1b"):
                        ctcf_overlay = False
                    elif ch in ("\r", "\n") and _hits:
                        r = _hits[ctcf_selected]
                        _cmd = f"del {r['local_start']} {r['local_end']}"
                        _ok, _msg = _run_variant_command(_cmd)
                        if _ok:
                            mode = "SIMULATION"
                            active_tool = 2
                        ctcf_overlay = False
                        _set_toast(
                            f"Anchor {r['name']} [{r['local_start']:,}–{r['local_end']:,}] → deletion sandbox"
                            if _ok else f"Sandbox error: {_msg}"
                        )
                    continue

                # ── GOTO coordinate input modal ───────────────────────────────
                if goto_mode:
                    if ch in ("\x1b",):
                        goto_mode = False
                        goto_buffer = ""
                    elif ch in ("\r", "\n"):
                        coord_input = goto_buffer.strip()
                        if coord_input:
                            _start_ucsc_fetch(coord_input)
                        goto_mode = False
                        goto_buffer = ""
                    elif ch in ("\x7f", "\x08"):
                        goto_buffer = goto_buffer[:-1]
                    elif ord(ch) >= 32:
                        goto_buffer += ch
                    continue

                # ── Simulation mode command buffer ────────────────────────────
                if mode == "SIMULATION":
                    if ch in ("\r", "\n"):
                        if cmd_buffer.strip():
                            handled, msg = _run_variant_command(cmd_buffer)
                            if handled:
                                _set_toast(msg)
                                active_tool = 8  # jump to structural view
                            else:
                                _set_toast(f"Unknown command: {cmd_buffer}")
                        cmd_buffer = ""
                        continue
                    elif ch in ("\x7f", "\x08"):
                        cmd_buffer = cmd_buffer[:-1]
                        continue
                    elif ch in ("\x03", "\x04"):
                        raise KeyboardInterrupt()
                    elif ord(ch) >= 32 and (cmd_buffer or ch.lower() in _SIM_COMMAND_STARTS):
                        # Once a command is started every key is text, so letters
                        # that double as hotkeys (e, l, s …) can be typed
                        cmd_buffer += ch
                        continue
                    elif cmd_buffer:
                        continue  # ignore Tab etc. while typing
                    # Empty command line: fall through to global hotkeys

                # ── Global hotkeys ────────────────────────────────────────────
                if ch in ("\x03", "\x04"):
                    raise KeyboardInterrupt()

                if ch in ("q", "Q"):
                    break

                if ch in ("1", "2", "3", "4", "5", "6", "7", "8", "9"):
                    new_tool = int(ch)
                    if new_tool != active_tool:
                        active_tool = new_tool
                        pulse_frames = 6
                        if new_tool == 9 and tokens:
                            gb_countdown = 24
                    # Close overlays when switching tools
                    file_browser_open = False
                    history_open = False
                    ctcf_overlay = False
                    fb_path_mode = False
                    fb_buffer = ""
                    continue

                if ch == "\t":
                    # TAB — cycle cell-line context
                    cell_line_idx = (cell_line_idx + 1) % len(_CELL_LINES)
                    _cl_n, _cl_d, _ = _CELL_LINES[cell_line_idx]
                    if wt_matrix:
                        _cl_mat = _cell_line_shift_matrix(wt_matrix, cell_line_idx)
                        analysis_cache["structural"] = {
                            "matrix": _cl_mat,
                            "provenance": "SIMULATED",
                            "cell_line": _cl_n,
                        }
                        analysis_cache.pop("insulation", None)
                        analysis_cache.pop("boundary", None)
                        sim_state.update({
                            "applied": False,
                            "desc": f"Cell-line shift: {_cl_n}",
                            "wt_matrix": _cl_mat,
                            "vt_matrix": _cl_mat,
                            "delta": None, "sdi": 0.0, "delta_stats": {},
                        })
                    update_session_history(current_session_id, cell_line=_cl_n)
                    _set_toast(f"CELLULAR CONTEXT → {_cl_n}  ({_cl_d})")
                    continue

                if ch in ("g", "G"):
                    # G — toggle GOTO coordinate input
                    if goto_mode:
                        goto_mode = False
                        goto_buffer = ""
                    else:
                        goto_mode = True
                        ctcf_overlay = False
                        file_browser_open = False
                        history_open = False
                    continue

                if ch in ("c", "C"):
                    # C — toggle CTCF motif scanner overlay
                    if ctcf_overlay:
                        ctcf_overlay = False
                    else:
                        if not tokens:
                            _set_toast("Load a sequence first (L)")
                        else:
                            if ctcf_scan_state["state"] == "idle":
                                _offset = _LAST_SEQUENCE_INFO.get("start", 0)
                                _tok_snap = tokens  # snapshot — thread must not see reassignment
                                import threading as _threading
                                ctcf_scan_state.update({
                                    "state": "running", "results": [], "toast_shown": False
                                })
                                _threading.Thread(
                                    target=lambda _t=_tok_snap, _o=_offset: (
                                        ctcf_scan_state.update({
                                            "results": scan_ctcf_motifs(_t, _o),
                                            "state": "done",
                                        })
                                    ),
                                    daemon=True,
                                ).start()
                            goto_mode = False
                            ctcf_overlay = True
                            ctcf_selected = 0
                    continue

                if ch in ("m", "M"):
                    mode = "SIMULATION" if mode == "OBSERVATION" else "OBSERVATION"
                    if mode == "OBSERVATION":
                        cmd_buffer = ""
                    _set_toast(f"Mode: {mode}")
                    continue

                if ch in ("l", "L"):
                    # Toggle in-panel file browser
                    if file_browser_open:
                        file_browser_open = False
                        fb_path_mode = False
                        fb_buffer = ""
                    else:
                        _fasta_dir = config.get("fasta_dir", ".")
                        fb_files = scan_fasta_files(_fasta_dir)
                        fb_selected = 0
                        fb_path_mode = False
                        fb_buffer = ""
                        file_browser_open = True
                        history_open = False
                        goto_mode = False
                        ctcf_overlay = False
                    continue

                if ch in ("i", "I"):
                    if tokens:
                        live.stop()
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        sys.stdout.write("\x1b[?1000l\x1b[?1006l")
                        sys.stdout.flush()
                        clear_screen_completely()
                        run_interpretability_suite(
                            tokens, filename, config,
                            on_export=lambda names: update_session_history(current_session_id, exports=names),
                        )
                        clear_screen_completely()
                        tty.setcbreak(fd)
                        sys.stdout.write("\x1b[?1000h\x1b[?1006h")
                        sys.stdout.flush()
                        live.start()
                    else:
                        _set_toast("No sequence loaded — press L first")
                    continue

                if ch in ("h", "H"):
                    # Toggle in-panel history overlay
                    if history_open:
                        history_open = False
                    else:
                        hist_data = load_session_history()
                        hist_selected = 0
                        history_open = True
                        file_browser_open = False
                        goto_mode = False
                        ctcf_overlay = False
                    continue

                if ch == "?":
                    live.stop()
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    sys.stdout.write("\x1b[?1000l\x1b[?1006l")
                    sys.stdout.flush()
                    run_fs_help(str(active_tool))
                    tty.setcbreak(fd)
                    sys.stdout.write("\x1b[?1000h\x1b[?1006h")
                    sys.stdout.flush()
                    live.start()
                    continue

                if ch in ("s", "S"):
                    live.stop()
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    sys.stdout.write("\x1b[?1000l\x1b[?1006l")
                    sys.stdout.flush()
                    clear_screen_completely()
                    run_settings_menu(config)
                    update_theme_and_lang_globals(config)
                    clear_screen_completely()
                    tty.setcbreak(fd)
                    sys.stdout.write("\x1b[?1000h\x1b[?1006h")
                    sys.stdout.flush()
                    live.start()
                    continue

                if ch in ("e", "E"):
                    if tokens:
                        # Export current tool's output
                        chrom = _LAST_SEQUENCE_INFO.get("chrom", "chrUnknown")
                        start_bp = _LAST_SEQUENCE_INFO.get("start", 0)
                        seq_len = len(tokens)
                        prov = analysis_cache.get("structural", {}).get("provenance", "SIMULATED")
                        n_b = len(analysis_cache.get("structural", {}).get("matrix") or []) or 40
                        bin_bp = max(1, seq_len // n_b)
                        exported = []
                        try:
                            if active_tool in (4, 7):
                                if "insulation" not in analysis_cache:
                                    m, p = get_contact_matrix(tokens)
                                    ins = compute_insulation_score(m)
                                    bds = call_tad_boundaries(ins)
                                    analysis_cache["insulation"] = {
                                        "insulation": ins,
                                        "boundaries": bds,
                                        "matrix": m,
                                    }
                                bds = analysis_cache["insulation"]["boundaries"]
                                p = export_tad_bed(bds, chrom, start_bp, bin_bp, prov)
                                exported.append(p)
                            if active_tool == 7:
                                if "boundary" not in analysis_cache:
                                    m, _ = get_contact_matrix(tokens)
                                    anch = find_loop_anchors(m, top_n=25)
                                    analysis_cache["boundary"] = {
                                        "anchors": anch,
                                        "matrix": m,
                                        "ctcf": _ctcf_density_per_bin(tokens, 40),
                                        "n_bins": 40,
                                    }
                                anch = analysis_cache["boundary"]["anchors"]
                                p = export_loop_tsv(anch, chrom, start_bp, bin_bp, prov)
                                exported.append(p)
                            if active_tool in (1, 3, 6):
                                sal = generate_simulated_saliency(tokens, n_bins=n_b)
                                p = export_saliency_bedgraph(sal, chrom, start_bp, bin_bp, prov)
                                exported.append(p)
                            if exported:
                                names = [os.path.basename(p) for p in exported]
                                update_session_history(current_session_id, exports=names)
                                _set_toast("Exported: " + "  ".join(names))
                            else:
                                _set_toast("Nothing to export for this tool")
                        except Exception as ex_e:
                            _set_toast(f"Export error: {ex_e}")
                    else:
                        _set_toast("No sequence loaded")
                    continue

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[?1000l\x1b[?1006l")
        sys.stdout.flush()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        clear_screen_completely()


if __name__ == "__main__":
    try:
        run_tui()
    except KeyboardInterrupt:
        console.print(t("predict_detached_clean"))
