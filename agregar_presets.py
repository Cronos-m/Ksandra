import re
import os
import subprocess

FILE_PATH = "index.html"

def solicitar_datos_preset():
    print("=" * 55)
    print("   CASANDRA - GENERADOR Y GESTOR DE PRESETS (PWA 90s)   ")
    print("=" * 55)
    
    clase = input("\n1. Nombre clave único para el preset (ej. frutas, ciudades, bandas): ").strip().lower()
    clase = re.sub(r'[^a-z0-9_]', '', clase)
    if not clase:
        print("❌ El nombre clave no puede estar vacío.")
        return None

    print("\n--- CONFIGURACIÓN DE ETIQUETAS Y PALABRAS EN CADA IDIOMA ---")
    
    label_es = input("Etiqueta del botón en Español (ej. FRUTAS): ").strip().upper()
    words_es = input("Palabras en Español separadas por comas:\n> ").strip()

    label_en = input("\nEtiqueta del botón en Inglés (ej. FRUITS) [Enter para usar la misma]: ").strip().upper() or label_es
    words_en = input("Palabras en Inglés separadas por comas [Enter para usar las mismas]: ").strip() or words_es

    label_fr = input("\nEtiqueta del botón en Francés (ej. FRUITS) [Enter para usar la misma]: ").strip().upper() or label_es
    words_fr = input("Palabras en Francés separadas por comas [Enter para usar las mismas]: ").strip() or words_fr

    return {
        "clase": clase,
        "EN": {"label": label_en, "words": words_en},
        "FR": {"label": label_fr, "words": words_fr},
        "ES": {"label": label_es, "words": words_es}
    }

def actualizar_index_html(preset_info):
    if not os.path.exists(FILE_PATH):
        print(f"\n❌ Error: No se encontró el archivo '{FILE_PATH}'. Asegúrate de ejecutar este script en la misma carpeta.")
        return False

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        contenido = f.read()

    clase = preset_info["clase"]

    if f'{clase}_words:' in contenido or f'class="preset {clase}' in contenido:
        print(f"\n⚠️ El preset con la clave '{clase}' ya existe en index.html.")
        return False

    # A. Agregar a I18N en JavaScript de forma limpia y segura por bloques de idioma
    for lang in ["EN", "FR", "ES"]:
        label = preset_info[lang]["label"]
        words = preset_info[lang]["words"]
        
        # Buscar el bloque de cierre de superheros_words dentro de cada idioma
        bloque_objetivo = f'superheros_words: "{preset_info[lang]["words"]}"' if lang != "ES" else None
        # Ubicamos con precisión el fin de superheros_words para inyectar la coma y el nuevo preset
        ancla = 'superheros_words: "'
        pos = contenido.find(f'{lang}: {{')
        if pos != -1:
            # Encontrar el superheros_words dentro de ese idioma específico
            fin_superheros = contenido.find('superheros_words:', pos)
            if fin_superheros != -1:
                fin_comilla = contenido.find('"', fin_superheros + 18)
                if fin_comilla != -1:
                    insercion = f',\n                {clase}: "{label}",\n                {clase}_words: "{words}"'
                    contenido = contenido[:fin_comilla + 1] + insercion + contenido[fin_comilla + 1:]

    # B. Agregar botón en el HTML de presets
    label_es = preset_info["ES"]["label"]
    nuevo_boton = f'                            <input type="button" class="preset {clase} grunge-btn py-2 text-xs text-gray-300" value="{label_es}">'
    contenido = contenido.replace(
        '<input type="button" class="preset superheros grunge-btn py-2 text-xs text-gray-300" value="SUPERHÉROES">',
        '<input type="button" class="preset superheros grunge-btn py-2 text-xs text-gray-300" value="SUPERHÉROES">\n' + nuevo_boton
    )

    # C. Agregar lógica de clic en JavaScript
    clic_js = f'if ($(this).hasClass("{clase}")) $("#form").val(dict.{clase}_words);'
    contenido = contenido.replace(
        'if ($(this).hasClass("superheros")) $("#form").val(dict.superheros_words);',
        'if ($(this).hasClass("superheros")) $("#form").val(dict.superheros_words);\n                ' + clic_js
    )

    # D. Actualizar idioma de la etiqueta en JavaScript
    update_lang_js = f'$(".preset.{clase}").val(dict.{clase});'
    contenido = contenido.replace(
        '$(".preset.superheros").val(dict.superheros);',
        '$(".preset.superheros").val(dict.superheros);\n            ' + update_lang_js
    )

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"\n✅ Preset '{preset_info['ES']['label']}' añadido exitosamente a {FILE_PATH} sin errores de sintaxis.")
    return True

def gestionar_git(preset_name):
    print("\n" + "=" * 55)
    print("              ACTUALIZACIÓN DE GITHUB              ")
    print("=" * 55)
    
    confirmacion = input(f"¿Deseas enviar (push) los cambios a GitHub para el preset '{preset_name}'? (s/n): ").strip().lower()
    
    if confirmacion not in ['s', 'si', 'sí', 'y', 'yes']:
        print("ℹ️ Proceso de actualización a GitHub cancelado por el usuario.")
        return

    try:
        print("\n🚀 Agregando cambios a Git (git add)...")
        subprocess.run(["git", "add", FILE_PATH], check=True)
        
        commit_msg = f"Add preset: {preset_name}"
        print(f"📝 Creando commit: '{commit_msg}'...")
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        
        print("⬆️ Subiendo cambios a GitHub (git push)...")
        subprocess.run(["git", "push"], check=True)
        
        print("\n🎉 ¡Repositorio de GitHub actualizado con éxito!")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ocurrió un error durante la ejecución de Git: {e}")
    except FileNotFoundError:
        print("\n❌ Git no está instalado o no está disponible en el PATH del sistema.")

def main():
    # Nota: Si ya tienes tu index.html dañado, te sugiero restaurarlo antes de volver a ejecutar el script.
    datos = solicitar_datos_preset()
    if datos:
        exito = actualizar_index_html(datos)
        if exito:
            gestionar_git(datos["ES"]["label"])

if __name__ == "__main__":
    main()