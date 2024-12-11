# Makefile para automatizar la creación del entorno, despliegue y recarga automática

# Variables
PYTHON := python
VENV_DIR := venv
REQUIREMENTS := requirements.txt
MAIN_SCRIPT := main.py
INPUT_FILE := input_data.txt

# Comando para activar el entorno virtual en diferentes sistemas operativos
ifeq ($(OS),Windows_NT)
    ACTIVATE := .\$(VENV_DIR)\Scripts\activate
else
    ACTIVATE := source $(VENV_DIR)/bin/activate
endif

# Crear el entorno virtual
.PHONY: create-env
create-env:
	@echo "🛠️  Creando entorno virtual..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "✅ Entorno virtual creado."

# Instalar dependencias (asumiendo que el entorno ya existe)
.PHONY: install-deps
install-deps: 
	@echo "📦 Instalando dependencias..."
	$(ACTIVATE) && pip install --upgrade pip && pip install -r $(REQUIREMENTS)
	@echo "✅ Dependencias instaladas."

# Configuración inicial (crear entorno e instalar dependencias)
.PHONY: setup
setup: create-env install-deps

# Ejecutar el script principal usando el archivo de entradas (input_data.txt)
# para evitar la necesidad de entrada interactiva.
.PHONY: run
run:
	@echo "🚀 Ejecutando el script con entradas desde $(INPUT_FILE)..."
	$(ACTIVATE) && python $(MAIN_SCRIPT) < $(INPUT_FILE)

# Recargar automáticamente al guardar cambios (usando entr), solo ejecuta el script sin reinstalar nada
.PHONY: watch
watch:
	@echo "🔄 Iniciando recarga automática..."
	find . -name "*.py" | entr -r make run

# Limpiar el entorno virtual
.PHONY: clean
clean:
	@echo "🧹 Limpiando entorno virtual..."
	rm -rf $(VENV_DIR)
	@echo "✅ Entorno virtual eliminado."

# Ayuda
.PHONY: help
help:
	@echo "📝 Makefile para automatizar tareas del proyecto"
	@echo ""
	@echo "Comandos disponibles:"
	@echo "  make setup          - Crear entorno virtual e instalar dependencias"
	@echo "  make run            - Ejecutar el script principal con entradas desde $(INPUT_FILE)"
	@echo "  make watch          - Recarga automática al guardar cambios (requiere entr)"
	@echo "  make clean          - Eliminar el entorno virtual"
	@echo "  make help           - Mostrar esta ayuda"