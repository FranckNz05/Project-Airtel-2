import os
import datetime
import csv
import subprocess
import logging

# Configuration
sms_url_template = "curl -G 'http://172.25.65.42:9002/smshttp/qs/' --data-urlencode 'REQUESTTYPE=SMSSubmitReq' --data-urlencode 'MOBILENO=[{number}]' --data-urlencode 'USERNAME=ittest' --data-urlencode 'ORIGIN_ADDR=Airtel' --data-urlencode 'TYPE=25' --data-urlencode 'MESSAGE={message}' --data-urlencode 'PASSWORD=Airtel@01@'"

fallback_numbers = ["057268371", "050009726"]  # Remplacez par les numéros réels
distribution_list = ["057668371", "055009726", "055027549"]  # Remplacez par les numéros de la liste de distribution

# Configuration du logging
logging.basicConfig(filename='sms_log.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Obtenir la date du jour
today = datetime.datetime.now().strftime('%Y-%m-%d')

# Nom du fichier basé sur la date du jour
filename = f"contacts_{today}.csv"

# Fonction pour envoyer un SMS avec curl
def send_sms(number, message):
    url = sms_url_template.format(number=number, message=message)
    try:
        result = subprocess.run(url, shell=True, capture_output=True, text=True)
        result.check_returncode()  # Lève une exception si la commande curl échoue
        logging.debug(f"SMS envoyé avec succès à {number}")
        return result.returncode, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de l'envoi du SMS à {number} : {e}")
        return None, str(e)

# Exécution principale
def main():
    logging.debug(f"Vérification de l'existence du fichier : {filename}")
    if os.path.isfile(filename):
        try:
            logging.debug(f"Fichier {filename} trouvé. Début de la lecture du fichier.")
            with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    date = row['DATE']
                    daily_ga = row['DAILY_GA']
                    daily_rev = row['DAILY_REV']
                    mtd_ga = row['MTD_GA']
                    lmtd_ga = row['LMTD_GA']
                    mtd_rev = row['MTD_REV']
                    lmtd_rev = row['LMTD_REV']

                    message = (
                        f"Date: {date}\n"
                        f"Daily GA: {daily_ga}\n"
                        f"Daily RV: {daily_rev}\n"
                        f"MTD GA: {mtd_ga}\n"
                        f"LMTD GA: {lmtd_ga}\n"
                        f"MTD RV: {mtd_rev}\n"
                        f"LMTD RV: {lmtd_rev}"
                    )

                    for number in distribution_list:
                        status_code, response_text = send_sms(number, message)
                        if status_code == 0:
                            logging.info(f"Envoyé à {number} : {response_text}")
                        else:
                            logging.error(f"Échec de l'envoi à {number} : {response_text}")
        except Exception as e:
            logging.error(f"Erreur lors de la lecture du fichier CSV : {e}")
            warning_message = f"Erreur lors de la lecture du fichier CSV {filename} : {e}"
            for number in fallback_numbers:
                status_code, response_text = send_sms(number, warning_message)
                if status_code == 0:
                    logging.info(f"Avertissement envoyé à {number} (fallback) : {response_text}")
                else:
                    logging.error(f"Échec de l'envoi de l'avertissement à {number} (fallback) : {response_text}")
            logging.warning(warning_message)
    else:
        warning_message = f"Fichier {filename} non trouvé."
        for number in fallback_numbers:
            status_code, response_text = send_sms(number, warning_message)
            if status_code == 0:
                logging.info(f"Avertissement envoyé à {number} (fallback) : {response_text}")
            else:
                logging.error(f"Échec de l'envoi de l'avertissement à {number} (fallback) : {response_text}")
        logging.warning(warning_message)

if __name__ == "__main__":
    try:
        logging.debug("Début de l'exécution du script principal")
        main()
    except Exception as e:
        logging.critical(f"Exception non gérée : {e}")
        warning_message = f"Une exception non gérée est survenue : {e}"
        for number in fallback_numbers:
            send_sms(number, warning_message)
            logging.error(f"Exception non gérée, avertissement envoyé à {number} (fallback) : {warning_message}")
