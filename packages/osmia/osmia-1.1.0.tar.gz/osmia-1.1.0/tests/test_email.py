import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

list_files = [
    os.path.join(BASE_DIR, "random.hpp"),
    os.path.join(BASE_DIR, "libcurl-x64.dll")
]

from Osmia.email_message import EmailMessage
from Osmia.email_config import EmailConfig

# Configuration de l'email
config = EmailConfig(
    smtp_server="smtp.gmail.com", # server smtp
    smtp_port=587, # port smtp
    login="email_envoyeur@gmail.com", # email de l'envoyeur 
    password="mot de passe d'application" # password d'application
)

# Création du mail
email = EmailMessage(
    config.smtp_server,
    config.smtp_port,
    config.login,
    config.password
)

html_message = """
<html>
    <body>
        <h1 style="color:blue;">Ceci est un test HTML !</h1>
        <p>Envoi d'un email en <b>HTML</b> avec une pièce jointe.</p>
    </body>
</html>
"""

text_message = "Ceci est un test."

format_mail = ["plain", "html"]

# envoie le même email à tout les email de la list to_email
responses = email.send_email(
    to_email=["destinatere@gmail.com", "destinatere2@gmail.com", "destinatere3@gmail.com"], # email du destinataire ou faire une list d'email de destinataire
    subject="Test Email",
    message=html_message, 
    type_email=str(format_mail[1]), # html => pour envoyer sous format html, plain => sous format text
    list_files=list_files # 1 ou plusieur fichier cela fonctionne
)

# peut garder cette syntax 
response = email.send_email(
    to_email="destinatere@gmail.com", # email du destinataire ou faire une list d'email de destinataire
    subject="Test Email",
    message=html_message, 
    type_email=str(format_mail[1]), # html => pour envoyer sous format html, plain => sous format text
    list_files=list_files # 1 ou plusieur fichier cela fonctionne
)
