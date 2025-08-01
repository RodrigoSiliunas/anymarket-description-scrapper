"""
==========================================================================
 ➠ Data Wrangler Module
 ➠ Section By: Rodrigo Siliunas
 ➠ Related system: Data Processing / Transformation
==========================================================================
"""

import json
import time
import re
from typing import List, Dict, Optional, Any
from pathlib import Path


class DataWrangler:
    """
    Classe responsável pelo processamento e transformação de dados extraídos
    de documentação de APIs.
    """

    def __init__(self, data_path: Path):
        """
        Inicializa o DataWrangler com o caminho dos dados.
        
        Args:
            data_path (Path): Caminho para o diretório contendo os arquivos de dados
        """
        self.data_path = Path(data_path)
        self.output_path = self.data_path / "out"  # Pasta de saída
        self.processed_files = []
        self.errors = []
        
        # Verifica se o caminho existe
        if not self.data_path.exists():
            raise FileNotFoundError(f"Caminho não encontrado: {self.data_path}")
        
        if not self.data_path.is_dir():
            raise NotADirectoryError(f"O caminho deve ser um diretório: {self.data_path}")
        
        # Cria a pasta de saída se não existir
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ DataWrangler inicializado")
        print(f"   📁 Entrada: {self.data_path}")
        print(f"   📁 Saída: {self.output_path}")

    def detect_files(self, file_extension: str = "json") -> List[Path]:
        """
        Detecta automaticamente todos os arquivos com a extensão especificada no diretório.
        
        Args:
            file_extension (str): Extensão dos arquivos a serem detectados (sem o ponto)
            
        Returns:
            List[Path]: Lista de caminhos dos arquivos encontrados
        """
        try:
            # Remove o ponto da extensão se fornecido
            extension = file_extension.lstrip(".")
            
            # Busca por arquivos com a extensão especificada
            pattern = f"*.{extension}"
            found_files = list(self.data_path.glob(pattern))
            
            # Filtra apenas arquivos (não diretórios)
            files = [f for f in found_files if f.is_file()]
            
            print(f"🔍 Detectados {len(files)} arquivo(s) .{extension}")
            
            for file in files:
                print(f"   📄 {file.name}")
            
            return files
            
        except Exception as e:
            error_msg = f"Erro ao detectar arquivos: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return []

    def load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Carrega um arquivo JSON e retorna seu conteúdo.
        
        Args:
            file_path (Path): Caminho para o arquivo JSON
            
        Returns:
            Optional[Dict[str, Any]]: Conteúdo do arquivo JSON ou None se houver erro
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            print(f"✅ Carregado: {file_path.name}")
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"Erro de JSON em {file_path.name}: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Erro ao carregar {file_path.name}: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return None

    def save_json_file(self, data: Dict[str, Any], file_path: Path) -> bool:
        """
        Salva dados em um arquivo JSON.
        
        Args:
            data (Dict[str, Any]): Dados a serem salvos
            file_path (Path): Caminho onde salvar o arquivo
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            
            print(f"💾 Salvo: {file_path.name}")
            return True
            
        except Exception as e:
            error_msg = f"Erro ao salvar {file_path.name}: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return False

    def camel_to_snake_case(self, name: str) -> str:
        """
        Converte camelCase ou PascalCase para snake_case.
        
        Exemplos:
        - stockLocal_priorityPoints -> stock_local_priority_points
        - stockLocal_defaultLocal -> stock_local_default_local
        - categoryId -> category_id
        - firstName -> first_name
        
        Args:
            name (str): Nome em camelCase ou PascalCase
            
        Returns:
            str: Nome convertido para snake_case
        """
        # Primeira conversão: adiciona underscore antes de maiúsculas
        # stockLocalPriorityPoints -> stock_Local_Priority_Points
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        
        # Segunda conversão: adiciona underscore antes de maiúsculas seguidas de minúsculas
        # stock_LocalPriority_Points -> stock_Local_Priority_Points
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        # Converte tudo para minúsculo
        result = s2.lower()
        
        # Remove underscores duplos que podem ter sido criados
        result = re.sub('_{2,}', '_', result)
        
        # Remove underscores no início e fim
        result = result.strip('_')
        
        return result

    def normalize_field_names(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os nomes dos campos em um arquivo de dados para snake_case.
        
        Args:
            data (Dict[str, Any]): Dados do arquivo JSON
            
        Returns:
            Dict[str, Any]: Dados com nomes de campos normalizados
        """
        try:
            # Cria uma cópia dos dados para não modificar o original
            normalized_data = data.copy()
            
            # Atualiza a data de processamento
            normalized_data["processing_date"] = time.strftime("%Y-%m-%d %H:%M:%S")
            normalized_data["normalization_applied"] = True
            
            # Verifica se há campos para processar
            if "fields" not in data or not isinstance(data["fields"], list):
                print(f"⚠️ Estrutura de campos não encontrada ou inválida")
                return normalized_data
            
            original_fields = data["fields"]
            normalized_fields = []
            name_changes = []
            
            for field in original_fields:
                if not isinstance(field, dict) or "name" not in field:
                    print(f"⚠️ Campo inválido ignorado: {field}")
                    continue
                
                # Cria uma cópia do campo
                normalized_field = field.copy()
                
                # Normaliza o nome do campo
                original_name = field["name"]
                normalized_name = self.camel_to_snake_case(original_name)
                
                # Atualiza o campo
                normalized_field["name"] = normalized_name
                normalized_field["original_field_name"] = original_name
                
                # Registra a mudança se houve alteração
                if original_name != normalized_name:
                    name_changes.append({
                        "original": original_name,
                        "normalized": normalized_name
                    })
                
                normalized_fields.append(normalized_field)
            
            # Atualiza os dados
            normalized_data["fields"] = normalized_fields
            normalized_data["normalization_summary"] = {
                "total_fields": len(normalized_fields),
                "fields_renamed": len(name_changes),
                "name_changes": name_changes
            }
            
            print(f"✅ Normalização concluída:")
            print(f"   📊 {len(normalized_fields)} campos processados")
            print(f"   🔄 {len(name_changes)} campos renomeados")
            
            return normalized_data
            
        except Exception as e:
            error_msg = f"Erro durante normalização: {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return data

    def process_files(self, file_extension: str = "json", normalize: bool = True) -> Dict[str, Any]:
        """
        Processa todos os arquivos detectados no diretório com normalização opcional.
        
        Args:
            file_extension (str): Extensão dos arquivos a serem processados
            normalize (bool): Se deve aplicar normalização snake_case
            
        Returns:
            Dict[str, Any]: Resultados do processamento
        """
        print(f"\n🚀 Iniciando processamento de arquivos .{file_extension}")
        if normalize:
            print("🐍 Normalização snake_case: ATIVADA")
        print("=" * 60)
        
        start_time = time.time()
        files = self.detect_files(file_extension)
        
        if not files:
            print("⚠️ Nenhum arquivo encontrado para processar")
            return {
                "success": False,
                "processed_files": 0,
                "errors": self.errors,
                "execution_time": 0
            }
        
        processed_count = 0
        normalized_count = 0
        loaded_data = {}
        
        for file_path in files:
            print(f"\n📋 Processando: {file_path.name}")
            
            if file_extension.lower() == "json":
                # Carrega o arquivo original
                data = self.load_json_file(file_path)
                if data:
                    loaded_data[file_path.stem] = data
                    processed_count += 1
                    self.processed_files.append(str(file_path))
                    
                    # Aplica normalização se solicitado
                    if normalize:
                        print(f"🔄 Aplicando normalização snake_case...")
                        normalized_data = self.normalize_field_names(data)
                        
                        # Salva o arquivo normalizado na pasta out
                        output_file = self.output_path / file_path.name
                        if self.save_json_file(normalized_data, output_file):
                            normalized_count += 1
                            print(f"✅ Arquivo normalizado salvo: {output_file.name}")
                        else:
                            print(f"❌ Erro ao salvar arquivo normalizado: {output_file.name}")
            else:
                # Para outras extensões no futuro
                print(f"⚠️ Tipo de arquivo não suportado ainda: .{file_extension}")
        
        execution_time = time.time() - start_time
        
        print(f"\n✅ Processamento concluído!")
        print(f"   📊 {processed_count}/{len(files)} arquivos processados")
        if normalize:
            print(f"   🐍 {normalized_count}/{processed_count} arquivos normalizados")
        print(f"   ⏱️ Tempo de execução: {execution_time:.2f}s")
        
        if self.errors:
            print(f"   ⚠️ {len(self.errors)} erro(s) encontrado(s)")
        
        return {
            "success": processed_count > 0,
            "processed_files": processed_count,
            "normalized_files": normalized_count if normalize else 0,
            "total_files": len(files),
            "loaded_data": loaded_data,
            "errors": self.errors,
            "execution_time": execution_time,
            "normalization_applied": normalize
        }

    def get_file_summary(self, file_extension: str = "json") -> Dict[str, Any]:
        """
        Retorna um resumo dos arquivos no diretório.
        
        Args:
            file_extension (str): Extensão dos arquivos para análise
            
        Returns:
            Dict[str, Any]: Resumo dos arquivos
        """
        files = self.detect_files(file_extension)
        
        summary = {
            "directory": str(self.data_path),
            "file_extension": file_extension,
            "total_files": len(files),
            "files": []
        }
        
        for file_path in files:
            file_info = {
                "name": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "modified": time.ctime(file_path.stat().st_mtime)
            }
            
            # Para arquivos JSON, adiciona informações específicas
            if file_extension.lower() == "json":
                data = self.load_json_file(file_path)
                if data:
                    file_info.update({
                        "table_name": data.get("table_name", "unknown"),
                        "total_fields": data.get("total_fields", 0),
                        "extraction_date": data.get("extraction_date", "unknown")
                    })
            
            summary["files"].append(file_info)
        
        return summary

    def test_normalization(self, test_names: List[str] = None) -> Dict[str, str]:
        """
        Testa a normalização de nomes com exemplos.
        
        Args:
            test_names (List[str]): Lista de nomes para testar. Se None, usa exemplos padrão.
            
        Returns:
            Dict[str, str]: Mapeamento de nomes originais para normalizados
        """
        if test_names is None:
            test_names = [
                "stockLocal_priorityPoints",
                "stockLocal_defaultLocal", 
                "stockKeepingUnit_partnerId",
                "categoryId",
                "firstName",
                "lastName", 
                "camelCaseExample",
                "PascalCaseExample",
                "already_snake_case",
                "MixedCASE_example",
                "HTMLParser",
                "XMLHttpRequest"
            ]
        
        print("\n🧪 Testando normalização snake_case:")
        print("-" * 50)
        
        results = {}
        
        for name in test_names:
            normalized = self.camel_to_snake_case(name)
            results[name] = normalized
            
            # Emoji para indicar se houve mudança
            status = "🔄" if name != normalized else "✅"
            print(f"{status} {name:25} -> {normalized}")
        
        return results

    def normalize_single_file(self, filename: str) -> bool:
        """
        Normaliza um único arquivo específico.
        
        Args:
            filename (str): Nome do arquivo (com ou sem extensão)
            
        Returns:
            bool: True se processou com sucesso, False caso contrário
        """
        # Garante que tem extensão .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = self.data_path / filename
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {filename}")
            return False
        
        print(f"🔄 Normalizando arquivo: {filename}")
        
        # Carrega o arquivo
        data = self.load_json_file(file_path)
        if not data:
            return False
        
        # Aplica normalização
        normalized_data = self.normalize_field_names(data)
        
        # Salva na pasta out
        output_file = self.output_path / filename
        success = self.save_json_file(normalized_data, output_file)
        
        if success:
            print(f"✅ Arquivo normalizado salvo em: {output_file}")
        
        return success

    def __str__(self) -> str:
        """Representação string da classe."""
        return f"DataWrangler(path='{self.data_path}', processed={len(self.processed_files)})"

    def __repr__(self) -> str:
        """Representação técnica da classe."""
        return f"DataWrangler(data_path=Path('{self.data_path}'))"
