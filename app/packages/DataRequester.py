"""
==========================================================================
 ➠ Data Requester Module
 ➠ Section By: Rodrigo Siliunas
 ➠ Related system: Web Scraping / Selenium
==========================================================================
"""

import os
import time
import json
import hashlib
from typing import List, Dict, Optional, Any
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup

from app.configurations.configurations import ROOT_PATH


class DataRequester:
    """
    Classe responsável pela extração de dados de documentação de APIs
    utilizando Selenium WebDriver e BeautifulSoup4.
    """

    def __init__(
        self,
        headless: bool = True,
        window_size: tuple = (1920, 1080),
        page_load_timeout: int = 30,
        implicit_wait: int = 10,
        max_retries: int = 3,
        delay_between_requests: float = 1.0
    ):
        """
        Inicializa o DataRequester com configurações do Selenium.
        """
        self.headless = headless
        self.window_size = window_size
        self.page_load_timeout = page_load_timeout
        self.implicit_wait = implicit_wait
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        
        self.driver: Optional[webdriver.Chrome] = None
        self.output_dir = Path(ROOT_PATH) / "app" / "assets"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _setup_chrome_options(self) -> Options:
        """Configura as opções do Chrome WebDriver."""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        
        return chrome_options

    def initialize_driver(self) -> None:
        """Inicializa o driver do Chrome."""
        try:
            chrome_options = self._setup_chrome_options()
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(self.implicit_wait)
            
            print(f"✅ Driver Chrome inicializado com sucesso!")
            print(f"   Modo headless: {self.headless}")
            
        except WebDriverException as e:
            print(f"❌ Erro ao inicializar o driver Chrome: {e}")
            raise

    def close_driver(self) -> None:
        """Fecha o driver do Chrome."""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Driver Chrome fechado com sucesso!")
            except Exception as e:
                print(f"⚠️ Aviso ao fechar driver: {e}")
            finally:
                self.driver = None

    def is_driver_active(self) -> bool:
        """Verifica se o driver está ativo."""
        if not self.driver:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False

    def __enter__(self):
        """Context manager entry."""
        self.initialize_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_driver()

    def extract_api_documentation(self, tables_data: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Extrai a documentação de campos de API."""
        if not self.is_driver_active():
            print("⚠️ Driver não está ativo. Inicializando...")
            self.initialize_driver()

        extracted_data = {}

        for table_info in tables_data:
            table_name = table_info.get("table")
            url = table_info.get("url")

            if not table_name or not url:
                print(f"❌ Dados inválidos: {table_info}")
                continue

            print(f"🔍 Processando tabela: {table_name}")
            print(f"🌐 URL: {url}")

            fields_data = self._extract_fields_from_url(url, table_name)

            if fields_data:
                extracted_data[table_name] = fields_data
                print(f"✅ {len(fields_data)} campos extraídos para '{table_name}'")
                self._save_to_json(table_name, fields_data)
            else:
                print(f"❌ Nenhum campo extraído para '{table_name}'")
                extracted_data[table_name] = []

            if self.delay_between_requests > 0:
                print(f"⏱️ Aguardando {self.delay_between_requests}s...")
                time.sleep(self.delay_between_requests)

        return extracted_data

    def _extract_fields_from_url(self, url: str, table_name: str) -> List[Dict[str, str]]:
        """Extrai os campos de documentação de uma URL específica."""
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 Tentativa {attempt + 1}/{self.max_retries} para '{table_name}'")

                print("🌐 Acessando URL e aguardando carregamento...")
                self.driver.get(url)

                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                print("✅ Página carregada")
                time.sleep(5)

                two_column_left = self._find_two_column_left_element()
                if not two_column_left:
                    print("❌ Elemento two-column-left não encontrado")
                    continue

                self._expand_collapsed_elements_in_container(two_column_left)
                fields_data = self._extract_fields_from_container(two_column_left)

                if fields_data:
                    return fields_data
                else:
                    print(f"⚠️ Nenhum campo encontrado na tentativa {attempt + 1}")

            except TimeoutException:
                print(f"⏰ Timeout na tentativa {attempt + 1} para '{table_name}'")
            except Exception as e:
                print(f"❌ Erro na tentativa {attempt + 1} para '{table_name}': {e}")

            if attempt < self.max_retries - 1:
                print(f"⏱️ Aguardando 5s antes da próxima tentativa...")
                time.sleep(5)

        print(f"❌ Falha ao extrair dados de '{table_name}' após {self.max_retries} tentativas")
        return []

    def _find_two_column_left_element(self):
        """Localiza o elemento two-column-left específico."""
        try:
            print("🔍 Procurando elemento two-column-left...")
            element = self.driver.find_element(By.CSS_SELECTOR, 'div[data-testid="two-column-left"]')
            
            if element:
                print("✅ Elemento two-column-left encontrado")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'start'});", element)
                time.sleep(2)
                return element
            else:
                print("❌ Elemento two-column-left não encontrado")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao buscar elemento two-column-left: {e}")
            return None

    def _expand_collapsed_elements_in_container(self, container_element):
        """
        NOVA FUNCIONALIDADE: Expande especificamente elementos no contêiner 'content' 
        que vem APÓS o segundo schema-row (conforme solicitado pelo usuário).
        """
        try:
            print("🔍 Iniciando expansão focada no contêiner 'content' (após segundo schema-row)...")
            
            expanded_count = 0
            max_expansions = 50
            clicked_elements = set()
            
            # Busca por elementos schema-row para identificar a estrutura
            schema_rows = container_element.find_elements(By.CSS_SELECTOR, 'div[data-test="schema-row"]')
            print(f"📊 Encontrados {len(schema_rows)} elementos schema-row")
            
            if len(schema_rows) < 2:
                print("⚠️ Menos de 2 schema-rows encontrados, voltando para método original...")
                return self._expand_collapsed_elements_original(container_element)
            
            # Localiza o segundo schema-row
            second_schema_row = schema_rows[1]
            print("🎯 Localizando contêiner 'content' após o segundo schema-row...")
            
            # Busca pelo elemento data-level="1" que vem APÓS o segundo schema-row
            content_container = None
            try:
                # Usa XPath para encontrar o próximo elemento data-level="1" após o segundo schema-row
                content_container = second_schema_row.find_element(By.XPATH, 
                    "./following-sibling::*[contains(@data-level, '1')] | " +
                    "./parent::*/following-sibling::*[contains(@data-level, '1')] | " +
                    "./ancestor::*[1]/following-sibling::*[contains(@data-level, '1')]")
                
                if content_container:
                    print("✅ Contêiner 'content' encontrado após segundo schema-row!")
                else:
                    raise Exception("Contêiner não encontrado")
                    
            except Exception as e:
                print(f"⚠️ Não foi possível localizar contêiner content específico: {e}")
                print("🔄 Buscando todos os contêineres data-level='1' como fallback...")
                
                # Fallback: busca todos os contêineres data-level="1"
                level_1_containers = container_element.find_elements(By.CSS_SELECTOR, 'div[data-level="1"]')
                if len(level_1_containers) >= 2:
                    # Assume que o contêiner content é o segundo
                    content_container = level_1_containers[1] if len(level_1_containers) > 1 else level_1_containers[0]
                    print(f"📦 Usando contêiner data-level='1' (índice 1) como content")
                else:
                    return self._expand_collapsed_elements_original(container_element)
            
            if not content_container:
                print("❌ Contêiner content não encontrado")
                return self._expand_collapsed_elements_original(container_element)
            
            # Foca especificamente no contêiner content encontrado
            print("📋 Processando contêiner 'content' específico...")
            
            # Scroll suave até o contêiner
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", content_container)
            time.sleep(1.5)
            
            # Busca por elementos clicáveis com setas dentro deste contêiner específico
            clickable_elements = content_container.find_elements(By.CSS_SELECTOR, 
                'div[role="button"] i[class*="chevron-right"], ' +
                'div.sl-cursor-pointer i[class*="chevron-right"], ' +
                '[tabindex="0"] i[class*="chevron-right"], ' +
                'i.fa-chevron-right, i.fal.fa-chevron-right, i.far.fa-chevron-right, i.fas.fa-chevron-right')
            
            print(f"🎯 {len(clickable_elements)} elementos com setas encontrados no contêiner content")
            
            # DEBUG: Vamos também tentar buscar no contêiner pai (toda a página)
            all_page_chevrons = container_element.find_elements(By.CSS_SELECTOR, 
                'i[class*="chevron-right"]')
            print(f"🔍 DEBUG: {len(all_page_chevrons)} elementos chevron encontrados na página inteira")
            
            for element_index, arrow_element in enumerate(clickable_elements):
                if expanded_count >= max_expansions:
                    break
                    
                try:
                    if not arrow_element.is_displayed():
                        continue
                        
                    element_id = self._get_element_identifier(arrow_element)
                    if element_id in clicked_elements:
                        print(f"     🛡️ SEGURANÇA: Elemento já clicado, pulando...")
                        continue
                    
                    clickable_parent = arrow_element.find_element(By.XPATH, 
                        "./ancestor::div[@role='button' or contains(@class, 'sl-cursor-pointer') or @tabindex='0'][1]")
                    if not clickable_parent:
                        continue
                        
                    print(f"   🖱️ Clicando em elemento {element_index + 1} do contêiner content")
                    
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", clickable_parent)
                    time.sleep(1.0)
                    
                    fields_before = len(content_container.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                    
                    click_success = False
                    try:
                        clickable_parent.click()
                        click_success = True
                        print(f"     ✅ Clique direto realizado")
                    except Exception as e1:
                        try:
                            self.driver.execute_script("arguments[0].click();", clickable_parent)
                            click_success = True
                            print(f"     ✅ Clique JS realizado")
                        except Exception as e2:
                            print(f"     ❌ Falha no clique: {e2}")
                            continue
                    
                    if click_success:
                        clicked_elements.add(element_id)
                        print(f"     🔒 Elemento marcado: {element_id[:30]}...")
                        time.sleep(2.0)
                        
                        fields_after = len(content_container.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                        if fields_after > fields_before:
                            expanded_count += 1
                            print(f"     🎉 +{fields_after - fields_before} campos expandidos! Total: {expanded_count}")
                        else:
                            print(f"     ℹ️ Nenhuma expansão detectada")
                            
                except Exception as e:
                    print(f"     ❌ Erro ao processar elemento: {e}")
                    continue
            
            print(f"\n✅ Expansão focada no contêiner content finalizada!")
            print(f"   📈 {expanded_count} expansões realizadas")
            print(f"   🎯 {len(clicked_elements)} elementos únicos processados")
            print(f"   🛡️ Sistema de segurança ativo")
            
            # NOVA FUNCIONALIDADE: Expandir objetos (field_type="object") que são expansíveis
            print(f"\n🔍 Fase 2: Procurando elementos 'object' e 'array[object]' expansíveis...")
            object_expanded_count = self._expand_object_fields(container_element, clicked_elements)  # Busca na página inteira
            
            # NOVA FUNCIONALIDADE: Busca específica por array[object] e object
            print(f"\n🔍 Fase 3: Busca específica por elementos array[object] e object...")
            array_object_count = self._expand_array_object_fields(container_element, clicked_elements)  # Busca na página inteira
            
            expanded_count += object_expanded_count + array_object_count
            
            print("🔙 Posicionando no topo para extração...")
            self.driver.execute_script("arguments[0].scrollTop = 0;", container_element)
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Erro durante processo de expansão focada: {e}")
            return self._expand_collapsed_elements_original(container_element)

    def _expand_collapsed_elements_original(self, container_element):
        """Método original de expansão como fallback."""
        try:
            print("🔄 Usando método de expansão original como fallback...")
            
            expanded_count = 0
            max_expansions = 50
            clicked_elements = set()
            
            current_scroll = 0
            scroll_step = 200
            container_height = self.driver.execute_script("return arguments[0].scrollHeight;", container_element)
            max_steps = min(int(container_height / scroll_step) + 2, 15)
            
            for step in range(max_steps):
                print(f"📜 Passo {step + 1}/{max_steps} - Posição: {current_scroll}px")
                
                self.driver.execute_script(f"arguments[0].scrollTo({{top: {current_scroll}, behavior: 'smooth'}});", container_element)
                time.sleep(1.8)
                
                collapsed_elements = container_element.find_elements(By.CSS_SELECTOR, '.sl-truncate.sl-text-muted')
                
                if collapsed_elements:
                    print(f"   🎯 {len(collapsed_elements)} elementos encontrados")
                    
                    processed_count = 0
                    for element in collapsed_elements:
                        if processed_count >= 3 or expanded_count >= max_expansions:
                            break
                            
                        try:
                            if not element.is_displayed():
                                continue
                                
                            element_id = self._get_element_identifier(element)
                            if element_id in clicked_elements:
                                continue
                            
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.8)
                            
                            try:
                                element.click()
                                clicked_elements.add(element_id)
                                expanded_count += 1
                                processed_count += 1
                                print(f"     ✅ Elemento expandido ({expanded_count})")
                                time.sleep(1.5)
                            except:
                                continue
                                
                        except Exception as e:
                            continue
                else:
                    print(f"   ℹ️ Nenhum elemento na posição atual")
                
                current_scroll += scroll_step
                if current_scroll >= container_height:
                    break
            
            print(f"✅ Expansão original finalizada: {expanded_count} elementos expandidos")
            
        except Exception as e:
            print(f"❌ Erro no método original: {e}")

    def _expand_object_fields(self, container_element, clicked_elements):
        """
        NOVA FUNCIONALIDADE: Expande elementos com field_type="object" que são expansíveis.
        Identifica elementos expansíveis pela presença da classe 'sl-ml-2' no contêiner stack.
        """
        try:
            print("🔍 Procurando elementos 'object' expansíveis...")

            object_expanded_count = 0
            max_object_expansions = 30

            # NOVA ESTRATÉGIA: Busca por TODOS os botões de expansão na página
            all_expandable_buttons = container_element.find_elements(By.CSS_SELECTOR, 
                'div[role="button"] i[class*="chevron-right"], ' +
                'div.sl-cursor-pointer i[class*="chevron-right"], ' +
                '[tabindex="0"] i[class*="chevron-right"], ' +
                'button i[class*="chevron-right"], ' +
                'i.fa-chevron-right, i.fal.fa-chevron-right, i.far.fa-chevron-right, i.fas.fa-chevron-right')
            
            print(f"🎯 Encontrados {len(all_expandable_buttons)} botões de expansão na página")
            
            # Filtra apenas elementos que realmente são expansíveis e não foram clicados
            valid_buttons = []
            for button_element in all_expandable_buttons:
                try:
                    if not button_element.is_displayed():
                        continue
                        
                    # Verifica se já foi clicado
                    element_id = self._get_element_identifier(button_element)
                    if element_id in clicked_elements:
                        continue
                    
                    # Encontra o schema-row pai
                    try:
                        schema_row = button_element.find_element(By.XPATH, 
                            "./ancestor::div[@data-test='schema-row'][1]")
                    except:
                        # Se não encontrar schema-row, tenta um contêiner mais genérico
                        try:
                            schema_row = button_element.find_element(By.XPATH, 
                                "./ancestor::div[contains(@class,'sl-') or @data-test][1]")
                        except:
                            continue
                    
                    # Tenta encontrar informações sobre o campo
                    field_name = "unknown"
                    field_type = "unknown"
                    
                    try:
                        name_element = schema_row.find_element(By.CSS_SELECTOR, 
                            '[data-test^="property-name"]')
                        field_name = name_element.text.strip()
                        
                        type_element = schema_row.find_element(By.CSS_SELECTOR, 
                            '[data-test="property-type"]')
                        field_type = type_element.text.strip().lower()
                    except:
                        # Se não conseguir identificar nome/tipo, ainda assim tenta expandir
                        pass
                    
                    valid_buttons.append((button_element, schema_row, field_name, field_type, element_id))
                    
                except Exception as e:
                    continue

            print(f"📦 Filtrados {len(valid_buttons)} botões válidos para expansão")
            
            # Expande todos os botões válidos
            for button_index, (chevron_button, schema_row_container, field_name, field_type, element_id) in enumerate(valid_buttons):
                if object_expanded_count >= max_object_expansions:
                    break
                    
                try:
                    print(f"   🎯 Expandindo elemento '{field_name}' ({field_type}) [{button_index + 1}/{len(valid_buttons)}]")
                    
                    # Scroll até o elemento
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                             chevron_button)
                    time.sleep(0.8)
                    
                    # Conta campos antes da expansão
                    fields_before = len(container_element.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                    
                    # Encontra o elemento clicável pai
                    try:
                        clickable_parent = chevron_button.find_element(By.XPATH, 
                            "./ancestor::div[@role='button' or contains(@class, 'sl-cursor-pointer') or @tabindex='0'][1]")
                    except:
                        # Se não encontrar, usa o próprio botão ou pai direto
                        try:
                            clickable_parent = chevron_button.find_element(By.XPATH, "./parent::*")
                        except:
                            clickable_parent = chevron_button
                    
                    # Realiza o clique
                    click_success = False
                    try:
                        clickable_parent.click()
                        click_success = True
                        print(f"     ✅ Clique direto realizado em '{field_name}'")
                    except Exception as e1:
                        try:
                            self.driver.execute_script("arguments[0].click();", clickable_parent)
                            click_success = True
                            print(f"     ✅ Clique JS realizado em '{field_name}'")
                        except Exception as e2:
                            # Tenta clicar diretamente no ícone da seta
                            try:
                                self.driver.execute_script("arguments[0].click();", chevron_button)
                                click_success = True
                                print(f"     ✅ Clique direto no ícone realizado em '{field_name}'")
                            except Exception as e3:
                                print(f"     ❌ Falha total no clique em '{field_name}': {e3}")
                                continue
                    
                    if click_success:
                        clicked_elements.add(element_id)
                        time.sleep(1.5)  # Tempo para expansão
                        
                        # Conta campos após a expansão
                        fields_after = len(container_element.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                        
                        if fields_after > fields_before:
                            object_expanded_count += 1
                            new_fields = fields_after - fields_before
                            print(f"     🎉 +{new_fields} novos campos encontrados em '{field_name}'!")
                        else:
                            print(f"     ℹ️ Nenhum campo novo encontrado em '{field_name}' (pode já estar expandido)")
                            
                except Exception as e:
                    print(f"     ❌ Erro inesperado ao processar '{field_name}': {type(e).__name__}")
                    continue
            
            print(f"\n✅ Expansão de elementos finalizada!")
            print(f"   📦 {object_expanded_count} elementos expandidos")
            print(f"   🔍 {len(valid_buttons)} elementos analisados")
            
            return object_expanded_count
            
        except Exception as e:
            print(f"❌ Erro durante expansão de elementos: {e}")
            return 0

    def _expand_array_object_fields(self, container_element, clicked_elements):
        """
        Busca específica por elementos com tipo 'array[object]' ou 'object' que possuem setas de expansão.
        """
        try:
            array_object_expanded_count = 0
            max_expansions = 20
            
            # Busca por todos os elementos que têm tipo array[object] ou object
            type_elements = container_element.find_elements(By.CSS_SELECTOR, '[data-test="property-type"]')
            print(f"🔍 Encontrados {len(type_elements)} elementos com tipo definido")
            
            # DEBUG: vamos mostrar quais tipos foram encontrados e buscar especificamente por array[object]
            found_types = []
            array_object_elements = []
            for te in type_elements:
                try:
                    type_text = te.text.strip()
                    found_types.append(type_text)
                    
                    # Se encontrar array[object], guardar o elemento
                    if 'array[object]' in type_text.lower():
                        array_object_elements.append(te)
                        
                except:
                    pass
            print(f"🔍 Tipos encontrados: {found_types}")
            print(f"🎯 Elementos array[object] encontrados: {len(array_object_elements)}")
            
            # Se não encontrou no contêiner atual, vamos buscar na página inteira
            if len(array_object_elements) == 0:
                print("🔍 Buscando array[object] na página inteira...")
                all_type_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-test="property-type"]')
                all_found_types = []
                for te in all_type_elements:
                    try:
                        type_text = te.text.strip()
                        all_found_types.append(type_text)
                        if 'array[object]' in type_text.lower():
                            array_object_elements.append(te)
                    except:
                        pass
                print(f"🌐 Todos os tipos na página: {all_found_types}")
                print(f"🎯 Total array[object] na página: {len(array_object_elements)}")
            
            # Agora vamos processar especificamente os elementos array[object] encontrados
            for type_element in array_object_elements:
                if array_object_expanded_count >= max_expansions:
                    break
                    
                try:
                    field_type = type_element.text.strip().lower()
                    
                    # Procura especificamente por array[object] e object
                    if 'array[object]' in field_type or field_type == 'object':
                        
                        # Encontra o schema-row pai deste elemento
                        try:
                            schema_row = type_element.find_element(By.XPATH, 
                                "./ancestor::div[@data-test='schema-row'][1]")
                        except:
                            # Fallback para contêiner genérico
                            try:
                                schema_row = type_element.find_element(By.XPATH, 
                                    "./ancestor::div[contains(@class,'sl-stack')][1]")
                            except:
                                continue
                        
                        # Busca por campo nome dentro do mesmo schema-row
                        try:
                            name_element = schema_row.find_element(By.CSS_SELECTOR, 
                                '[data-test^="property-name"]')
                            field_name = name_element.text.strip()
                        except:
                            field_name = "unknown"
                        
                        # Busca por ícone de expansão dentro do mesmo schema-row
                        try:
                            chevron_icon = schema_row.find_element(By.CSS_SELECTOR, 
                                'i[class*="chevron-right"]')
                            
                            if not chevron_icon.is_displayed():
                                continue
                                
                            # Verifica se já foi clicado
                            element_id = self._get_element_identifier(chevron_icon)
                            if element_id in clicked_elements:
                                print(f"     🛡️ Campo '{field_name}' ({field_type}) já processado")
                                continue
                            
                            print(f"   🎯 Expandindo campo '{field_name}' ({field_type})")
                            
                            # Encontra o elemento clicável pai
                            try:
                                clickable_parent = chevron_icon.find_element(By.XPATH, 
                                    "./ancestor::div[@role='button' or @tabindex='0' or contains(@class, 'sl-cursor-pointer')][1]")
                            except:
                                clickable_parent = chevron_icon.find_element(By.XPATH, "./parent::*")
                            
                            # Scroll até o elemento
                            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                                     clickable_parent)
                            time.sleep(1.0)
                            
                            # Conta campos antes da expansão
                            fields_before = len(container_element.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                            
                            # Realiza o clique
                            click_success = False
                            try:
                                clickable_parent.click()
                                click_success = True
                                print(f"     ✅ Clique direto realizado em '{field_name}'")
                            except Exception as e1:
                                try:
                                    self.driver.execute_script("arguments[0].click();", clickable_parent)
                                    click_success = True
                                    print(f"     ✅ Clique JS realizado em '{field_name}'")
                                except Exception as e2:
                                    try:
                                        self.driver.execute_script("arguments[0].click();", chevron_icon)
                                        click_success = True
                                        print(f"     ✅ Clique direto no ícone realizado em '{field_name}'")
                                    except Exception as e3:
                                        print(f"     ❌ Falha ao clicar em '{field_name}': {e3}")
                                        continue
                            
                            if click_success:
                                clicked_elements.add(element_id)
                                time.sleep(2.0)  # Tempo para expansão
                                
                                # Conta campos após a expansão
                                fields_after = len(container_element.find_elements(By.CSS_SELECTOR, "[data-test^='property-name']"))
                                
                                if fields_after > fields_before:
                                    array_object_expanded_count += 1
                                    new_fields = fields_after - fields_before
                                    print(f"     🎉 +{new_fields} novos campos encontrados em '{field_name}'!")
                                else:
                                    print(f"     ℹ️ Nenhum campo novo em '{field_name}' (pode já estar expandido)")
                            
                        except Exception as chevron_error:
                            # Não há ícone de expansão para este campo, é normal
                            continue
                        
                except Exception as field_error:
                    continue
            
            print(f"\n✅ Busca específica por array[object] finalizada!")
            print(f"   📦 {array_object_expanded_count} elementos array[object]/object expandidos")
            
            return array_object_expanded_count
            
        except Exception as e:
            print(f"❌ Erro durante busca específica por array[object]: {e}")
            return 0

    def _get_element_identifier(self, element):
        """Cria um identificador único para um elemento."""
        try:
            tag_name = element.tag_name
            text_content = element.text[:100] if element.text else ""
            text_content = text_content.replace("\n", " ").strip()
            css_classes = element.get_attribute("class") or ""
            location = element.location
            location_str = f"{location.get('x', 0)},{location.get('y', 0)}"
            
            identifier_parts = [
                f"tag:{tag_name}",
                f"text:{text_content}",
                f"classes:{css_classes}",
                f"loc:{location_str}"
            ]
            
            identifier = "|".join(identifier_parts)
            hash_id = hashlib.md5(identifier.encode()).hexdigest()[:16]
            final_id = f"{hash_id}:{text_content[:30]}"
            
            return final_id
            
        except Exception as e:
            print(f"⚠️ Erro ao criar identificador: {e}")
            return f"fallback_{id(element)}_{hash(str(element))}"

    def _extract_fields_from_container(self, container_element) -> List[Dict[str, str]]:
        """Extrai os dados dos campos do container especificado com prefixação hierárquica."""
        try:
            print("📋 Extraindo dados dos campos do container...")
            
            container_html = container_element.get_attribute('outerHTML')
            soup = BeautifulSoup(container_html, 'html.parser')
            
            fields_data = []
            
            # NOVA FUNCIONALIDADE: Busca apenas campos dentro da seção "content"
            print("🎯 Localizando seção 'content' para extrair apenas campos relevantes...")
            
            # Encontra o elemento "content" como ponto de referência
            content_element = None
            content_candidates = soup.find_all(attrs={"data-test": lambda x: x and "property-name" in x})
            
            for candidate in content_candidates:
                if candidate.get_text(strip=True).lower() == "content":
                    content_element = candidate
                    break
            
            if not content_element:
                print("⚠️ Elemento 'content' não encontrado, extraindo todos os campos...")
                return self._extract_all_fields_fallback(soup)
            
            print("✅ Seção 'content' encontrada, filtrando campos relevantes...")
            
            # Encontra o contêiner pai do elemento content
            content_schema_row = content_element.find_parent("div", {"data-test": lambda x: x and "schema" in x})
            if not content_schema_row:
                print("⚠️ Schema-row do 'content' não encontrado, usando fallback...")
                return self._extract_all_fields_fallback(soup)
            
            # NOVA FUNCIONALIDADE: Processa campos com hierarquia e prefixação
            print("� Processando campos com hierarquia e prefixação...")
            fields_data = self._extract_fields_with_hierarchy(soup, content_schema_row)
            
            return fields_data
            
        except Exception as e:
            print(f"❌ Erro durante extração de dados: {e}")
            return []

    def _extract_fields_with_hierarchy(self, soup, content_schema_row) -> List[Dict[str, str]]:
        """
        NOVA FUNCIONALIDADE: Extrai campos aplicando prefixação hierárquica.
        
        Lógica de filtragem:
        - Se existir campo 'content': extrai apenas campos dentro do content (ignora paginação)
        - Se não existir campo 'content': extrai todos os campos (como categories)
        """
        try:
            print("🔗 Iniciando extração com hierarquia baseada em data-level...")
            
            fields_data = []
            processed_fields = set()
            
            # Busca todos os schema-rows na página
            all_schema_rows = soup.find_all("div", {"data-test": lambda x: x and "schema" in x})
            print(f"📊 Encontrados {len(all_schema_rows)} schema-rows na página")
            
            # NOVA LÓGICA: Detecta se existe um campo 'content'
            has_content_field = False
            content_field_index = -1
            
            for i, row in enumerate(all_schema_rows):
                name_element = row.find(attrs={"data-test": lambda x: x and "property-name" in x})
                if name_element:
                    field_name = name_element.get_text(strip=True)
                    if field_name.lower() == "content":
                        has_content_field = True
                        content_field_index = i
                        print(f"✅ Campo 'content' detectado no índice {i}")
                        break
            
            if has_content_field:
                print("🎯 Modo: Extraindo apenas campos dentro do 'content' (ignorando paginação)")
                # Filtra apenas campos que vêm APÓS o content
                relevant_rows = all_schema_rows[content_field_index:]
            else:
                print("🎯 Modo: Extraindo todos os campos (sem campo 'content' detectado)")
                # Usa todos os schema-rows
                relevant_rows = all_schema_rows
            
            print(f"📋 Processando {len(relevant_rows)} schema-rows relevantes")
            
            # Analisa a hierarquia usando data-level dos elementos pais
            field_hierarchy = []
            
            for row in relevant_rows:
                try:
                    # Encontra o nome do campo
                    name_element = row.find(attrs={"data-test": lambda x: x and "property-name" in x})
                    if not name_element:
                        continue
                    
                    field_name = name_element.get_text(strip=True)
                    if not field_name:
                        continue
                    
                    # Para campos de paginação (mesmo quando não há content, evita estes)
                    if field_name.lower() in ["page", "size", "totalelements", "totalpages"]:
                        print(f"🛑 Parando extração ao encontrar campo de paginação: '{field_name}'")
                        break
                    
                    # NOVA LÓGICA: Se temos content, ajusta a hierarquia
                    level = self._detect_level_from_parent(row)
                    
                    # Se detectamos content e estamos processando campos após content,
                    # ajusta os níveis para considerar content como nível pai
                    if has_content_field and field_name.lower() != "content":
                        # Se o campo está dentro do content (level > 0), ajusta para considerar content como pai
                        if level > 0:
                            level = level - 1  # Reduz um nível pois content será o pai
                    
                    field_hierarchy.append((level, field_name, row))
                    
                except Exception as e:
                    print(f"⚠️ Erro ao processar schema-row: {e}")
                    continue
            
            print(f"🏗️ Construída hierarquia de {len(field_hierarchy)} campos")
            
            # Debug: mostra a hierarquia detectada
            print("📋 HIERARQUIA DETECTADA:")
            for level, field_name, _ in field_hierarchy:
                indent = "  " * level
                marker = "🏠" if level == 0 else "📦" if level == 1 else "🔗"
                print(f"{indent}{marker} {field_name} - Nível {level}")
            
            # Constrói os nomes com prefixação baseada na hierarquia
            parent_stack = []
            
            # Se temos content, não adicionamos prefixo content_ mas mantemos a hierarquia interna
            if has_content_field:
                print("📦 Modo content ativo: extraindo campos sem prefixo 'content_' (hierarquia interna mantida)")
            
            for level, field_name, schema_row in field_hierarchy:
                try:
                    # NOVA LÓGICA: Se temos content, não incluímos 'content' no stack de prefixos
                    if has_content_field and field_name.lower() != "content":
                        # Ajusta o stack baseado no nível (sem incluir content no prefixo)
                        while len(parent_stack) > level:
                            removed = parent_stack.pop()
                            print(f"   🔙 Removendo '{removed}' do stack (nível {level})")
                    else:
                        # Lógica normal para casos sem content
                        while len(parent_stack) > level:
                            removed = parent_stack.pop()
                            print(f"   🔙 Removendo '{removed}' do stack (nível {level})")
                    
                    # Determina o nome final do campo (sem incluir content no prefixo)
                    if parent_stack and not (has_content_field and field_name.lower() == "content"):
                        prefixed_name = "_".join(parent_stack + [field_name])
                    else:
                        prefixed_name = field_name
                    
                    # Evita duplicatas
                    if prefixed_name in processed_fields:
                        print(f"   ⚠️ Campo duplicado ignorado: {prefixed_name}")
                        continue
                    
                    processed_fields.add(prefixed_name)
                    
                    # Extrai tipo e descrição
                    field_type = "unknown"
                    type_element = schema_row.find(attrs={"data-test": "property-type"})
                    if type_element:
                        field_type = type_element.get_text(strip=True)
                    else:
                        # Busca alternativa por spans com tipos
                        type_candidates = schema_row.find_all("span", class_=lambda x: x and "sl-text-muted" in x)
                        for candidate in type_candidates:
                            candidate_text = candidate.get_text(strip=True)
                            if any(type_word in candidate_text.lower() for type_word in ['string', 'number', 'integer', 'boolean', 'array', 'object']):
                                field_type = candidate_text
                                break
                    
                    description = ""
                    desc_element = schema_row.find(attrs={"data-test": "property-description"})
                    if desc_element:
                        description = desc_element.get_text(strip=True)
                    else:
                        desc_candidates = schema_row.find_all(class_=lambda x: x and ("sl-prose" in x or "sl-markdown-viewer" in x or "description" in x))
                        if desc_candidates:
                            description = desc_candidates[0].get_text(strip=True)
                    
                    # Calcula o nível final para output
                    final_level = level
                    if has_content_field and field_name.lower() != "content":
                        final_level = level  # Mantém o nível original, sem ajustar por content
                    
                    # Adiciona à lista de campos
                    field_data = {
                        "name": prefixed_name,
                        "description": description,
                        "field_type": field_type,
                        "original_name": field_name,
                        "hierarchy_level": final_level
                    }
                    
                    fields_data.append(field_data)
                    
                    # Log com detalhes da hierarquia
                    if parent_stack and not (has_content_field and field_name.lower() == "content"):
                        hierarchy_path = " -> ".join(parent_stack + [field_name])
                        print(f"✅ Campo extraído: {prefixed_name} ({field_type}) | Hierarquia: {hierarchy_path}")
                    else:
                        print(f"✅ Campo extraído: {prefixed_name} ({field_type}) | Nível raiz")
                    
                    # Se este campo é um objeto/array que pode ter filhos, adiciona ao stack de pais
                    if field_type.lower() in ["object", "array[object]"] and level < 10:
                        if not (has_content_field and field_name.lower() == "content"):
                            parent_stack.append(field_name)
                            print(f"   📦 '{field_name}' adicionado ao stack de pais: {parent_stack}")
                    
                except Exception as e:
                    print(f"❌ Erro ao processar campo '{field_name}': {e}")
                    continue
            
            print(f"🎯 Extração hierárquica concluída: {len(fields_data)} campos processados")
            
            # Se temos content, remove o próprio campo content da lista final
            if has_content_field:
                fields_data = [field for field in fields_data if field['name'].lower() != 'content']
                print(f"🗑️ Campo 'content' removido da lista final (mantidos apenas os subcampos)")
                print(f"📋 Total final: {len(fields_data)} campos")
            
            return fields_data
            
        except Exception as e:
            print(f"❌ Erro na extração hierárquica: {e}")
            return self._extract_all_fields_fallback(soup)
    
    def _detect_level_from_parent(self, schema_row):
        """
        Detecta o nível de hierarquia baseado no data-level do elemento pai.
        Baseado no HTML real onde elementos com data-level="0" são raiz e data-level="1" são filhos.
        """
        try:
            # Busca pelo elemento pai com data-level
            current = schema_row.parent
            max_attempts = 5
            attempt = 0
            
            while current and attempt < max_attempts:
                data_level = current.get("data-level")
                if data_level and data_level.isdigit():
                    level = int(data_level)
                    return level
                
                current = current.parent
                attempt += 1
            
            # Fallback: verifica classes CSS específicas
            parent = schema_row.parent
            if parent:
                parent_classes = parent.get("class", [])
                if "sl-ml-7" in parent_classes:
                    return 1
                elif "sl-ml-px" in parent_classes:
                    return 0
            
            # Se não encontrar, assume nível 0
            return 0
            
        except Exception as e:
            print(f"   ⚠️ Erro ao detectar nível do pai: {e}")
            return 0
    
    def _get_field_indentation_level(self, schema_row) -> int:
        """
        Determina o nível de indentação de um campo baseado na estrutura DOM.
        Prioriza data-level para detectar hierarquia corretamente.
        """
        try:
            # Método 1: Busca data-level no elemento pai ou no próprio elemento
            current_element = schema_row
            
            # Primeiro, verifica se o próprio schema-row tem data-level
            data_level = current_element.get("data-level")
            if data_level and data_level.isdigit():
                level = int(data_level)
                return level
            
            # Se não encontrou, busca no elemento pai
            parent_element = current_element.parent
            if parent_element:
                parent_data_level = parent_element.get("data-level")
                if parent_data_level and parent_data_level.isdigit():
                    level = int(parent_data_level)
                    return level
            
            # Método 2: Busca por ancestrais com data-level
            current = schema_row
            for _ in range(5):  # Limita busca
                if current and current.get("data-level"):
                    data_level = current.get("data-level")
                    if data_level.isdigit():
                        return int(data_level)
                current = current.parent if current else None
            
            # Método 3: Análise de classes CSS sl-ml-* mais precisa
            # Procura especificamente por sl-ml-7 (nível 1) e sl-ml-px (nível 0)
            all_elements = schema_row.find_all()
            for element in all_elements:
                classes = element.get("class", [])
                for cls in classes:
                    if cls == "sl-ml-7":  # Indica nível 1 baseado no HTML fornecido
                        return 1
                    elif cls == "sl-ml-px":  # Indica nível 0 baseado no HTML fornecido
                        return 0
            
            # Método 4: Verifica a estrutura de classes CSS do container
            parent_classes = []
            current = schema_row.parent
            if current:
                parent_classes = current.get("class", [])
            
            # Se o pai tem sl-ml-7, este elemento está no nível 1
            if "sl-ml-7" in parent_classes:
                return 1
            elif "sl-ml-px" in parent_classes:
                return 0
            
            # Fallback: Assume nível 0 (raiz)
            return 0
            
        except Exception as e:
            print(f"   ⚠️ Erro ao determinar nível de indentação: {e}")
            return 0  # Fallback para nível raiz

    def _extract_all_fields_fallback(self, soup) -> List[Dict[str, str]]:
        """Método de fallback para extrair todos os campos quando não conseguir filtrar por content."""
        print("🔄 Usando método de extração completa como fallback com hierarquia baseada em data-level...")
        
        try:
            fields_data = []
            processed_fields = set()
            
            # Busca todos os schema-rows
            all_schema_rows = soup.find_all("div", {"data-test": lambda x: x and "schema" in x})
            print(f"📊 Encontrados {len(all_schema_rows)} schema-rows para processar")
            
            # Analisa a hierarquia usando data-level
            field_hierarchy = []
            
            for row in all_schema_rows:
                try:
                    name_element = row.find(attrs={"data-test": lambda x: x and "property-name" in x})
                    if not name_element:
                        continue
                    
                    field_name = name_element.get_text(strip=True)
                    if not field_name:
                        continue
                    
                    # Para campos de paginação
                    if field_name.lower() in ["page", "size", "totalelements", "totalpages"]:
                        continue
                    
                    # Usa a nova detecção baseada em data-level do pai
                    level = self._detect_level_from_parent(row)
                    field_hierarchy.append((level, field_name, row))
                    
                except Exception as e:
                    continue
            
            print(f"🏗️ Construída hierarquia de {len(field_hierarchy)} campos")
            
            # Debug: mostra a hierarquia detectada no fallback
            print("📋 HIERARQUIA DETECTADA (FALLBACK):")
            for level, field_name, _ in field_hierarchy:
                indent = "  " * level
                print(f"{indent}• {field_name} - Nível {level}")
            
            # Constrói os nomes com prefixação baseada na hierarquia
            parent_stack = []
            
            for level, field_name, schema_row in field_hierarchy:
                try:
                    # Ajusta o stack de pais baseado no nível atual
                    while len(parent_stack) > level:
                        parent_stack.pop()
                    
                    # Determina o nome final do campo
                    if parent_stack:
                        prefixed_name = "_".join(parent_stack + [field_name])
                    else:
                        prefixed_name = field_name
                    
                    # Evita duplicatas
                    if prefixed_name in processed_fields:
                        continue
                    processed_fields.add(prefixed_name)
                    
                    # Extrai tipo e descrição
                    field_type = "unknown"
                    type_element = schema_row.find(attrs={"data-test": "property-type"})
                    if type_element:
                        field_type = type_element.get_text(strip=True)
                    else:
                        type_candidates = schema_row.find_all("span", class_=lambda x: x and "sl-text-muted" in x)
                        for candidate in type_candidates:
                            candidate_text = candidate.get_text(strip=True)
                            if any(type_word in candidate_text.lower() for type_word in ['string', 'number', 'integer', 'boolean', 'array', 'object']):
                                field_type = candidate_text
                                break
                    
                    description = ""
                    desc_element = schema_row.find(attrs={"data-test": "property-description"})
                    if desc_element:
                        description = desc_element.get_text(strip=True)
                    else:
                        desc_candidates = schema_row.find_all(class_=lambda x: x and ("sl-prose" in x or "sl-markdown-viewer" in x or "description" in x))
                        if desc_candidates:
                            description = desc_candidates[0].get_text(strip=True)
                    
                    field_data = {
                        "name": prefixed_name,
                        "description": description,
                        "field_type": field_type,
                        "original_name": field_name,
                        "hierarchy_level": level
                    }
                    
                    fields_data.append(field_data)
                    
                    # Log com detalhes da hierarquia
                    if parent_stack:
                        hierarchy_path = " -> ".join(parent_stack + [field_name])
                        print(f"✅ Campo extraído: {prefixed_name} ({field_type}) | Hierarquia: {hierarchy_path}")
                    else:
                        print(f"✅ Campo extraído: {prefixed_name} ({field_type}) | Nível raiz")
                    
                    # Se este campo é um objeto que pode ter filhos, adiciona ao stack
                    if field_type.lower() in ["object", "array[object]"] and level < 10:
                        parent_stack.append(field_name)
                        print(f"   📦 '{field_name}' adicionado ao stack de pais: {parent_stack}")
                        
                except Exception as e:
                    continue
            
            print(f"🔄 Extração fallback concluída: {len(fields_data)} campos processados")
            return fields_data
            
        except Exception as e:
            print(f"❌ Erro no método de fallback: {e}")
            # Se até o fallback falhar, tenta método simples sem hierarquia
            return self._extract_simple_fields_fallback(soup)
    
    def _extract_simple_fields_fallback(self, soup) -> List[Dict[str, str]]:
        """Método mais simples de extração sem hierarquia como último recurso."""
        print("🔄 Usando método simples sem hierarquia como último recurso...")
        
        fields_data = []
        field_name_selectors = [
            "[data-test^='property-name']",
            "[data-testid^='property-name']",
        ]
        
        field_name_elements = []
        for selector in field_name_selectors:
            elements = soup.select(selector)
            field_name_elements.extend(elements)
        
        seen_names = set()
        unique_elements = []
        for element in field_name_elements:
            element_text = element.get_text(strip=True)
            if element_text and element_text not in seen_names:
                seen_names.add(element_text)
                unique_elements.append(element)
        
        for field_element in unique_elements:
            try:
                field_name = field_element.get_text(strip=True)
                
                if not field_name:
                    continue
                
                parent_container = field_element.find_parent("div")
                if not parent_container:
                    continue
                
                for _ in range(3):
                    schema_row = parent_container.find_parent("div", {"data-test": lambda x: x and "schema" in x})
                    if schema_row:
                        parent_container = schema_row
                        break
                    parent_container = parent_container.find_parent("div") or parent_container
                
                field_type = "unknown"
                type_element = parent_container.find(attrs={"data-test": "property-type"})
                if type_element:
                    field_type = type_element.get_text(strip=True)
                else:
                    type_candidates = parent_container.find_all("span", class_=lambda x: x and "sl-text-muted" in x)
                    for candidate in type_candidates:
                        candidate_text = candidate.get_text(strip=True)
                        if any(type_word in candidate_text.lower() for type_word in ['string', 'number', 'integer', 'boolean', 'array', 'object']):
                            field_type = candidate_text
                            break
                
                description = ""
                desc_element = parent_container.find(attrs={"data-test": "property-description"})
                if desc_element:
                    description = desc_element.get_text(strip=True)
                else:
                    desc_candidates = parent_container.find_all(class_=lambda x: x and ("sl-prose" in x or "sl-markdown-viewer" in x or "description" in x))
                    if desc_candidates:
                        description = desc_candidates[0].get_text(strip=True)
                
                field_data = {
                    "name": field_name,
                    "description": description,
                    "field_type": field_type
                }
                
                fields_data.append(field_data)
                
            except Exception as e:
                continue
        
        return fields_data

    def _save_to_json(self, table_name: str, fields_data: List[Dict[str, str]]) -> None:
        """Salva os dados extraídos em um arquivo JSON."""
        try:
            file_path = self.output_dir / f"{table_name}.json"
            
            output_data = {
                "table_name": table_name,
                "extraction_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_fields": len(fields_data),
                "fields": fields_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, indent=4, ensure_ascii=False)
            
            print(f"💾 Dados salvos em: {file_path}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo JSON: {e}")

    def __del__(self):
        """Destrutor para garantir que o driver seja fechado."""
        self.close_driver()
