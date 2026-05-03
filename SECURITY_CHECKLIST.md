# Lista de Comprobación de Seguridad IA

Antes de cada pase a producción, la IA de Seguridad debe validar:

- [ ] `SECRET_KEY` no expuesta.
- [ ] Base de datos sqlite fuera del tracking git.
- [ ] Controladores protegidos por CSRF.
- [ ] No se loguean PII o contraseñas en `logs/`.
- [ ] Dependencias escaneadas con `bandit` y `pip-audit`.
