"""
Gerenciador de lotes para processamento de grandes quantidades de PDFs
"""
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class BatchManager:
    """Gerencia a divisão e processamento de PDFs em lotes"""
    
    def __init__(self, batch_size=50, storage_path="data/batches.json"):
        self.batch_size = batch_size
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.batches = self._load_batches()
    
    def _load_batches(self) -> Dict[str, Any]:
        """Carrega lotes salvos do disco"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_batches(self):
        """Salva lotes no disco"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.batches, f, indent=2, ensure_ascii=False)
    
    def create_batches(self, files: List[Dict[str, Any]], doc_type: str, pattern: str) -> List[str]:
        """
        Divide lista de arquivos em lotes
        
        Args:
            files: Lista de dicionários com informações dos arquivos (sem conteúdo binário no JSON)
            doc_type: Tipo de documento
            pattern: Padrão de nomenclatura
        
        Returns:
            List[str]: Lista de IDs dos lotes criados
        """
        batch_ids = []
        total_files = len(files)
        
        # Dividir arquivos em lotes
        for i in range(0, total_files, self.batch_size):
            batch_files = files[i:i + self.batch_size]
            batch_id = str(uuid.uuid4())[:8]
            
            # Criar metadados dos arquivos (sem conteúdo binário)
            files_metadata = [{"name": f["name"], "index": idx + i} for idx, f in enumerate(batch_files)]
            
            batch_data = {
                "id": batch_id,
                "status": "pending",  # pending, processing, completed, failed
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "total_files": len(batch_files),
                "processed_files": 0,
                "failed_files": 0,
                "doc_type": doc_type,
                "pattern": pattern,
                "files": files_metadata,  # Apenas metadados
                "results": [],
                "errors": []
            }
            
            self.batches[batch_id] = batch_data
            batch_ids.append(batch_id)
        
        self._save_batches()
        return batch_ids
    
    def get_batch(self, batch_id: str) -> Dict[str, Any]:
        """Retorna informações de um lote específico"""
        return self.batches.get(batch_id, {})
    
    def get_all_batches(self) -> Dict[str, Any]:
        """Retorna todos os lotes"""
        return self.batches
    
    def update_batch_status(self, batch_id: str, status: str):
        """Atualiza o status de um lote"""
        if batch_id in self.batches:
            self.batches[batch_id]["status"] = status
            self.batches[batch_id]["updated_at"] = datetime.now().isoformat()
            self._save_batches()
    
    def add_batch_result(self, batch_id: str, result: Dict[str, Any]):
        """Adiciona resultado de processamento ao lote (sem conteúdo binário)"""
        if batch_id in self.batches:
            # Salvar apenas metadados, não o conteúdo binário
            result_metadata = {
                "original": result.get("original"),
                "novo": result.get("novo"),
                "timestamp": datetime.now().isoformat()
            }
            self.batches[batch_id]["results"].append(result_metadata)
            self.batches[batch_id]["processed_files"] = len(self.batches[batch_id]["results"])
            self.batches[batch_id]["updated_at"] = datetime.now().isoformat()
            self._save_batches()
    
    def add_batch_error(self, batch_id: str, error: Dict[str, Any]):
        """Adiciona erro de processamento ao lote"""
        if batch_id in self.batches:
            self.batches[batch_id]["errors"].append(error)
            self.batches[batch_id]["failed_files"] += 1
            self.batches[batch_id]["updated_at"] = datetime.now().isoformat()
            self._save_batches()
    
    def get_progress(self, batch_id: str) -> float:
        """Calcula o progresso de um lote (0.0 a 1.0)"""
        batch = self.get_batch(batch_id)
        if not batch or batch["total_files"] == 0:
            return 0.0
        
        completed = batch["processed_files"] + batch["failed_files"]
        return completed / batch["total_files"]
    
    def clear_completed_batches(self):
        """Remove lotes completados (mais de 7 dias)"""
        current_time = datetime.now()
        to_remove = []
        
        for batch_id, batch_data in self.batches.items():
            if batch_data["status"] == "completed":
                updated_at = datetime.fromisoformat(batch_data["updated_at"])
                days_old = (current_time - updated_at).days
                if days_old > 7:
                    to_remove.append(batch_id)
        
        for batch_id in to_remove:
            del self.batches[batch_id]
        
        if to_remove:
            self._save_batches()
        
        return len(to_remove)
