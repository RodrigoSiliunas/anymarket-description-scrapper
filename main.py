"""
==========================================================================
 ➠ Main Application Entry Point
 ➠ Section By: Rodrigo Siliunas
 ➠ Related system: AnyMarket Description Scrapper
==========================================================================
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Adiciona o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent))

from app.packages.DataRequester import DataRequester
from app.packages.DataWrangler import DataWrangler
from app.packages.GoogleAgent import GoogleAgent


def main():
    """
    Função principal do extrator de documentação AnyMarket.
    """
    print("🚀 Iniciando AnyMarket Description Scrapper")
    print("=" * 60)
    
    # Lista de tabelas/endpoints para extrair
    tables_to_extract = [
        {
            "table": "categories",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/d9d52de92b659-categories-id"
        },
        {
            "table": "devolutions",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/4udvmnv0qno72-orders-id-returns"
        },
        {
            "table": "marketplaces",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/9e68f76778f76-skus-sku-id-marketplaces"
        },
        {
            "table": "orders",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/2c58bb6519cda-orders"
        },
        {
            "table": "products",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/7666cb4a3e779-products"
        },
        {
            "table": "questions",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/ce1ea92cba953-questions-id"
        },
        {
            "table": "stock",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/24df50c4bc9ba-stocks"
        },
        {
            "table": "stock_fulfillment",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/43a14d7909ad4-stocks-fulfillment-marketplace-id-sku"
        },
        {
            "table": "transmissions",
            "url": "https://anymarketdoc.stoplight.io/docs/v3-doc-pt-br/43463080cdf03-transmissions"
        }
    ]

    # Configurações do extrator
    extractor_config = {
        "headless": False,           # Modo headless (sem interface gráfica)
        "window_size": (1920, 1080),
        "page_load_timeout": 30,
        "implicit_wait": 10,
        "max_retries": 3,
        "delay_between_requests": 2.0  # 2 segundos entre requisições
    }
    
    try:
        # Usa context manager para garantir cleanup automático
        with DataRequester(**extractor_config) as requester:
            print(f"📊 Processando {len(tables_to_extract)} endpoint(s)...")
            print()
            
            # Extrai os dados
            results = requester.extract_api_documentation(tables_to_extract)
            
            # Exibe resumo dos resultados
            print("\n" + "=" * 60)
            print("📋 RESUMO DA EXTRAÇÃO")
            print("=" * 60)
            
            total_fields = 0
            for table_name, fields in results.items():
                field_count = len(fields)
                total_fields += field_count
                status = "✅ Sucesso" if field_count > 0 else "❌ Falha"
                print(f"{status} | {table_name}: {field_count} campos extraídos")
            
            print(f"\n🎯 Total de campos extraídos: {total_fields}")
            print(f"📁 Arquivos salvos em: app/assets/")
            
            return results
            
    except KeyboardInterrupt:
        print("\n⚠️ Processo interrompido pelo usuário")
        return {}
    except Exception as e:
        print(f"\n❌ Erro durante a extração: {e}")
        return {}


def test_single_endpoint(table_name: str, url: str, headless: bool = False):
    """
    Função para testar um único endpoint em modo debug.
    
    Args:
        table_name (str): Nome da tabela/endpoint
        url (str): URL da documentação
        headless (bool): Se deve executar em modo headless
    """
    print(f"🧪 MODO TESTE - Testando endpoint: {table_name}")
    print("=" * 60)
    
    test_data = [{"table": table_name, "url": url}]
    
    config = {
        "headless": headless,
        "window_size": (1920, 1080),
        "page_load_timeout": 30,
        "implicit_wait": 10,
        "max_retries": 2,
        "delay_between_requests": 1.0
    }
    
    try:
        with DataRequester(**config) as requester:
            results = requester.extract_api_documentation(test_data)
            
            if results and results.get(table_name):
                fields = results[table_name]
                print(f"\n✅ Teste concluído com sucesso!")
                print(f"📊 {len(fields)} campos extraídos")
                
                # Exibe os primeiros 3 campos como preview
                print("\n📋 Preview dos campos extraídos:")
                for i, field in enumerate(fields[:3]):
                    print(f"  {i+1}. {field['name']} ({field['field_type']})")
                    if field['description']:
                        print(f"     Descrição: {field['description'][:100]}...")
                    print()
                
                if len(fields) > 3:
                    print(f"     ... e mais {len(fields) - 3} campos")
                
            else:
                print(f"\n❌ Nenhum campo foi extraído para {table_name}")
                
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")


def interactive_mode():
    """
    Modo interativo para configurar e executar o extrator.
    """
    print("🎮 MODO INTERATIVO")
    print("=" * 60)
    
    tables = []
    
    print("Adicione os endpoints para extração (digite 'fim' para terminar):")
    
    while True:
        print()
        table_name = input("Nome da tabela/endpoint: ").strip()
        
        if table_name.lower() == 'fim':
            break
            
        if not table_name:
            print("⚠️ Nome não pode ser vazio!")
            continue
            
        url = input("URL da documentação: ").strip()
        
        if not url:
            print("⚠️ URL não pode ser vazia!")
            continue
            
        tables.append({"table": table_name, "url": url})
        print(f"✅ Adicionado: {table_name}")
    
    if not tables:
        print("⚠️ Nenhum endpoint adicionado. Encerrando...")
        return
    
    # Configurações
    print("\n⚙️ CONFIGURAÇÕES")
    headless_input = input("Executar em modo headless? (s/N): ").strip().lower()
    headless = headless_input in ['s', 'sim', 'y', 'yes']
    
    retry_input = input("Número máximo de tentativas por endpoint (padrão: 3): ").strip()
    max_retries = int(retry_input) if retry_input.isdigit() else 3
    
    delay_input = input("Delay entre requisições em segundos (padrão: 2.0): ").strip()
    delay = float(delay_input) if delay_input.replace('.', '').isdigit() else 2.0
    
    config = {
        "headless": headless,
        "window_size": (1920, 1080),
        "page_load_timeout": 30,
        "implicit_wait": 10,
        "max_retries": max_retries,
        "delay_between_requests": delay
    }
    
    print(f"\n🚀 Iniciando extração de {len(tables)} endpoints...")
    
    try:
        with DataRequester(**config) as requester:
            results = requester.extract_api_documentation(tables)
            
            print("\n📋 RESULTADOS:")
            for table_name, fields in results.items():
                print(f"  {table_name}: {len(fields)} campos")
                
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def test_data_wrangler():
    """
    Função para testar o DataWrangler com normalização snake_case.
    """
    print("\n" + "="*60)
    print("🐍 TESTANDO DATA WRANGLER - NORMALIZAÇÃO SNAKE_CASE")
    print("="*60)
    
    try:
        # Inicializa o DataWrangler apontando para a pasta assets
        assets_path = Path(__file__).parent / "app" / "assets"
        wrangler = DataWrangler(assets_path)
        
        # Testa a normalização com exemplos
        print("\n🧪 Testando função de normalização:")
        wrangler.test_normalization()
        
        # Processa todos os arquivos com normalização
        print(f"\n🔄 Processando arquivos JSON...")
        results = wrangler.process_files(normalize=True)
        
        # Mostra resultados
        print(f"\n📊 RESULTADOS:")
        print(f"   ✅ Sucesso: {results['success']}")
        print(f"   📁 Arquivos processados: {results['processed_files']}")
        print(f"   🐍 Arquivos normalizados: {results['normalized_files']}")
        print(f"   ⏱️ Tempo: {results['execution_time']:.2f}s")
        
        if results['errors']:
            print(f"   ❌ Erros: {len(results['errors'])}")
            for error in results['errors']:
                print(f"      • {error}")
        
        print(f"\n📁 Arquivos normalizados salvos em: {wrangler.output_path}")
        
    except Exception as e:
        print(f"❌ Erro no teste do DataWrangler: {e}")


def test_google_agent():
    """
    Função para testar o GoogleAgent com aprimoramento de descrições via Gemini.
    """
    print("\n" + "="*60)
    print("🤖 TESTANDO GOOGLE AGENT - APRIMORAMENTO COM GEMINI")
    print("="*60)
    
    try:
        # Inicializa o GoogleAgent
        agent = GoogleAgent(fast_mode=True)
        
        # Pergunta qual arquivo processar
        print("\n📁 Escolha uma opção:")
        print("1. Processar todos os arquivos")
        print("2. Processar arquivo específico")
        
        choice = input("\nEscolha (1-2): ").strip()
        
        if choice == "1":
            # Processa todos os arquivos
            print("\n🚀 Iniciando processamento de todos os arquivos...")
            agent.process_all_files()
            
        elif choice == "2":
            # Processa arquivo específico
            filename = input("\nDigite o nome do arquivo (ex: categories.json): ").strip()
            print(f"\n🚀 Iniciando processamento de {filename}...")
            agent.process_single_file(filename)
            
        else:
            print("❌ Opção inválida")
            return
        
        print("\n✅ Processamento do GoogleAgent concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste do GoogleAgent: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AnyMarket Description Scrapper")
    parser.add_argument("--test", type=str, help="Testa um endpoint específico (formato: 'nome,url')")
    parser.add_argument("--interactive", action="store_true", help="Modo interativo")
    parser.add_argument("--no-headless", action="store_true", help="Executa com navegador visível")
    parser.add_argument("--wrangler", action="store_true", help="Testa o DataWrangler")
    parser.add_argument("--agent", action="store_true", help="Testa o GoogleAgent com Gemini")
    
    args = parser.parse_args()
    
    if args.wrangler:
        # Teste do DataWrangler
        test_data_wrangler()
    elif args.agent:
        # Teste do GoogleAgent
        test_google_agent()
    elif args.test:
        # Modo teste
        try:
            table_name, url = args.test.split(',', 1)
            test_single_endpoint(table_name.strip(), url.strip(), not args.no_headless)
        except ValueError:
            print("❌ Formato inválido para --test. Use: 'nome,url'")
    elif args.interactive:
        # Modo interativo
        interactive_mode()
    else:
        # Modo padrão
        main()
