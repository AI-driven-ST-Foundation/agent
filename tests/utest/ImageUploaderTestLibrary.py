"""
Librairie Robot Framework pour tester ImageUploader
Simule différents scénarios avec mocks
"""
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from typing import Optional, List

# Ajouter le path du projet
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.AiHelper.utilities.imguploader.imghandler import ImageUploader
from src.AiHelper.config.config import Config


class ImageUploaderTestLibrary:
    """Librairie de test pour ImageUploader"""
    
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    
    def __init__(self):
        self.warnings = []
        
    def _capture_warning(self, message: str, robot_log: bool = False):
        """Capture les messages de warning pour vérification"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def test_upload_with_imgbb(self, base64_data: str) -> str:
        """Teste l'upload avec ImgBB configuré et qui réussit"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_imgbb_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            # Mock de l'uploader ImgBB pour retourner une URL
            with patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
                mock_upload.return_value = 'https://i.ibb.co/test123/image.png'
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_upload_with_freeimagehost(self, base64_data: str) -> str:
        """Teste l'upload avec FreeImageHost configuré et qui réussit"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'):
            
            # Mock de l'uploader FreeImageHost pour retourner une URL
            with patch('src.AiHelper.utilities.imguploader._imghost.FreeImageHostUploader.upload_from_base64') as mock_upload:
                mock_upload.return_value = 'https://freeimage.host/test456/image.png'
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_upload_without_provider(self, base64_data: str) -> str:
        """Teste le fallback quand aucun provider n'est configuré"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(base64_data)
            
            return result
    
    def test_upload_returning_none(self, base64_data: str) -> str:
        """Teste le fallback quand l'upload retourne None"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            # Mock qui retourne None (échec d'upload)
            with patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
                mock_upload.return_value = None
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_upload_with_exception(self, base64_data: str) -> str:
        """Teste le fallback quand une exception est levée"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            # Mock qui lève une exception
            with patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
                mock_upload.side_effect = Exception("Network error: Connection timeout")
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_auto_select_imgbb(self, base64_data: str) -> str:
        """Teste la sélection automatique d'ImgBB"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_imgbb_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'):
            
            # Les deux sont configurés, ImgBB devrait être sélectionné en premier
            with patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
                mock_upload.return_value = 'https://i.ibb.co/auto/image.png'
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_auto_select_freeimagehost(self, base64_data: str) -> str:
        """Teste la sélection automatique de FreeImageHost (quand ImgBB n'est pas disponible)"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'):
            
            with patch('src.AiHelper.utilities.imguploader._imghost.FreeImageHostUploader.upload_from_base64') as mock_upload:
                mock_upload.return_value = 'https://freeimage.host/auto/image.png'
                
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
                
                return result
    
    def test_get_warning_messages(self, base64_data: str) -> List[str]:
        """Récupère les messages de warning générés"""
        self.warnings = []
        
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            # Patch le logger pour capturer les warnings
            with patch('src.AiHelper.utilities._logger.RobotCustomLogger.warning', side_effect=self._capture_warning):
                uploader = ImageUploader(service="auto")
                result = uploader.upload_from_base64(base64_data)
        
        return self.warnings
    
    def get_warnings_count(self) -> int:
        """Retourne le nombre de warnings capturés"""
        return len(self.warnings)
    
    def clear_warnings(self):
        """Efface les warnings capturés"""
        self.warnings = []


# Pour les tests directs Python (optionnel)
if __name__ == "__main__":
    lib = ImageUploaderTestLibrary()
    sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    print("\n🧪 Test 1: Upload avec ImgBB")
    result = lib.test_upload_with_imgbb(sample_base64)
    print(f"   Result: {result}\n")
    
    print("🧪 Test 2: Upload avec FreeImageHost")
    result = lib.test_upload_with_freeimagehost(sample_base64)
    print(f"   Result: {result}\n")
    
    print("🧪 Test 3: Aucun provider configuré")
    result = lib.test_upload_without_provider(sample_base64)
    print(f"   Result: {result[:80]}...\n")
    
    print("🧪 Test 4: Upload retourne None")
    result = lib.test_upload_returning_none(sample_base64)
    print(f"   Result: {result[:80]}...\n")
    
    print("🧪 Test 5: Upload lève une exception")
    result = lib.test_upload_with_exception(sample_base64)
    print(f"   Result: {result[:80]}...\n")
    
    print("🧪 Test 6: Capture des warnings")
    warnings = lib.test_get_warning_messages(sample_base64)
    print(f"   Warnings capturés: {len(warnings)}")
    for w in warnings:
        print(f"   - {w}")
    
    print("\n✅ Tous les tests terminés!")

