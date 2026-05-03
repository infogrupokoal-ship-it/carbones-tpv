
# Simula el debate entre dos o más agentes
def debate():
    print("Iniciando debate de IAs (Arquitecto vs Seguridad)...")
    print("Arquitecto: 'Propongo migrar la DB a PostgreSQL por rendimiento.'")
    print("Seguridad: 'Rechazado, la migración puede exponer datos si no aseguramos la conexión.'")
    print("Conclusión: Mantener SQLite por ahora y auditar endpoints.")
    print("El resultado se guardaría en .ai_agents/memory/decisions_log.md")

if __name__ == '__main__':
    debate()
