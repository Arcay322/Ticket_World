# tickets/storage_backends.py
from storages.backends.gcloud import GoogleCloudStorage
import traceback

class CustomGoogleCloudStorage(GoogleCloudStorage):
    def _save(self, name, content):
        print(f"--- CUSTOM STORAGE: Intentando guardar el archivo: {name} ---")
        try:
            # Llamamos al método de guardado original de la librería
            result = super()._save(name, content)
            print(f"--- CUSTOM STORAGE: El guardado parece haber tenido éxito. Resultado: {result} ---")
            
            # Verifiquemos inmediatamente si el archivo existe en el bucket
            if self.exists(name):
                print(f"--- CUSTOM STORAGE: ¡ÉXITO! El archivo '{name}' ahora existe en el bucket. ---")
            else:
                print(f"--- CUSTOM STORAGE: ¡FALLO SILENCIOSO! El archivo '{name}' NO existe en el bucket después de guardar. ---")
            
            return result
        except Exception as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"!!!!!!!!!! ERROR DENTRO DEL MÉTODO _save: {e} !!!!!!!!!!!")
            traceback.print_exc()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # Volvemos a lanzar la excepción para que Django sepa que algo falló
            raise
