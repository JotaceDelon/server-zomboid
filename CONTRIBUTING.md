# Desarrollo

Las instrucciones de instalación y uso están en [README.md](README.md). La configuración compartida se mantiene en `config.example.yml`; no incluyas contraseñas, datos de partidas ni archivos locales en las contribuciones.

## Pruebas

Desde la raíz, con Python 3.10 o posterior:

```sh
python -m unittest discover -s tests -v
```

Para validar la preparación de opciones de mods, con Ansible instalado:

```sh
ansible-playbook -i localhost, -c local tests/mods-playbook.yml
```

Estas pruebas no instalan mods ni modifican el servidor. Los casos de configuración inválida utilizan `rescue`; el resumen debe terminar con `failed=0`.

También puedes ejecutarlas dentro de una VM existente, desde `Vagrant`:

```sh
vagrant ssh -c "cd /vagrant && ansible-playbook -i localhost, -c local tests/mods-playbook.yml"
```

Para validar Vagrant, desde su carpeta:

```sh
vagrant validate
```

## Informar de un problema

Abre una incidencia con el comportamiento esperado, los pasos para reproducirlo, las versiones utilizadas y el error relevante. Elimina contraseñas, direcciones personales y otros datos privados de los registros antes de adjuntarlos.
