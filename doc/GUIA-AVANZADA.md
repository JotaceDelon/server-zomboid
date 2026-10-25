# Configuración avanzada y copias de seguridad

La guía de instalación, conexión por Internet y uso diario está en el [README](../README.md). Este documento amplía la referencia de opciones, las reglas del mundo, las copias de seguridad y el uso manual de Ansible. Los comandos parten de las carpetas indicadas en esa guía.

## Referencia completa de configuración

Estas claves están en [config.example.yml](../config.example.yml). Copia el archivo completo y modifica sus valores en `config.yml`.

### `vm`: máquina virtual

| Clave | Predeterminado | Explicación |
| --- | --- | --- |
| `box` | `bento/ubuntu-24.04` | Imagen de partida; debe ser Ubuntu 24.04+ x86_64 y compatible con VirtualBox |
| `box_version` | `"202510.26.0"` | Versión de la imagen; `null` permite resolver una disponible. Cambiarla no actualiza el Ubuntu ya instalado |
| `name` | `daryl` | Nombre en VirtualBox; utiliza otro si creas otra VM |
| `hostname` | `daryl` | Nombre Linux, sin espacios ni acentos |
| `memory_mb` | `8192` | RAM total en MB |
| `cpus` | `2` | Número de CPU virtuales |
| `network` | `public` | Puente a la LAN; `private` permite acceso directo solo desde el anfitrión |
| `ip` | `null` | DHCP en modo puente; una IP explícita configura una dirección fija. El modo privado requiere una IP |
| `bridge` | `null` | Nombre del adaptador del anfitrión; vacío deja que Vagrant seleccione/pregunte |

### `pz`: instalación y ejecución

| Clave | Predeterminado | Explicación |
| --- | --- | --- |
| `user` | `pzuser` | Cuenta Linux dedicada, distinta de root; no es un jugador |
| `home` | `/home/pzuser` | Directorio personal; contiene configuración, cuentas y partidas |
| `install_dir` | `/opt/pzserver` | Archivos de instalación del juego |
| `steamcmd_dir` | `/opt/steamcmd` | Directorio de SteamCMD |
| `steamcmd_url` | URL HTTPS de Valve incluida en el ejemplo | Descarga del instalador; normalmente no se cambia |
| `branch` | `null` | Rama solicitada; no fija una build exacta |
| `update` | `false` | `true` solicita actualizar en el próximo aprovisionamiento |
| `validate` | `true` | SteamCMD comprueba archivos al instalar/actualizar; no valida el mundo |
| `server_name` | `daryl` | Identificador de archivos y mundo; letras, números, guiones y guiones bajos |
| `public_name` | `Daryl - Project Zomboid` | Nombre visible; controla `PublicName` del INI |
| `admin_password` | `CAMBIAME` | Sustituir por una propia; mínimo 12 caracteres y sin saltos de línea |
| `heap_initial_mb` | `1024` | Heap inicial de Java; positivo y no mayor que el máximo |
| `heap_max_mb` | `5120` | Heap máximo; deja al menos 2048 MB sobre la RAM detectada por Ubuntu |
| `service_name` | `zomboid` | Nombre del servicio systemd; adáptalo en los comandos de administración |
| `enabled` | `true` | Arranque automático al encender Ubuntu. Con `false`, Ansible lo inicia para verificar el despliegue, pero posteriores encendidos requieren inicio manual |
| `startup_timeout` | `600` | Segundos que Ansible espera la señal de disponibilidad; no acelera el juego |
| `shutdown_timeout` | `180` | Segundos para que termine el servicio antes de forzar su salida |
| `settings` | Diccionario de opciones | Ajustes del INI, descritos a continuación |

Las rutas admiten directorios absolutos sencillos sin espacios ni componentes `..`. Para empezar conserva las rutas y la cuenta del ejemplo.

### `pz.settings`: ajustes del INI

| Clave | Predeterminado | Explicación |
| --- | --- | --- |
| `Public` | `false` | Anuncia el servidor en el listado; no configura conectividad ni protege el acceso |
| `Password` | `""` | Contraseña de entrada; vacía significa sin contraseña de servidor |
| `MaxPlayers` | `16` | Máximo permitido; no garantiza recursos para ese número |
| `PVP` | `false` | Permite combate entre jugadores cuando está activado |
| `PauseEmpty` | `true` | Solicita pausar la simulación sin jugadores |
| `DefaultPort` | `16261` | Puerto UDP que introducen los clientes |
| `UDPPort` | `16262` | Segundo puerto UDP; debe ser distinto al anterior |
| `UPnP` | `false` | Permite intentar abrir puertos automáticamente en el router, si la red lo admite |

Puedes añadir claves INI compatibles con tu build dentro de `pz.settings`. Por ejemplo, `PublicDescription: "Servidor de mi comunidad"` al mismo nivel que `MaxPlayers` añade una descripción.

Se admiten valores de una sola línea. Ansible conserva las demás líneas del INI. **Quitar una clave de YAML no la borra del INI**: establece un nuevo valor explícito si quieres cambiarla. Edita los ajustes gestionados en YAML, porque el siguiente aprovisionamiento volverá a aplicarlos.

`PublicName` se controla mediante `pz.public_name`. `Mods` y `WorkshopItems` se controlan mediante la sección opcional `mods`; no los dupliques en `pz.settings`. `Map` combina las carpetas opcionales de mods con `pz.settings.Map`, cuyo valor base predeterminado es `Muldraugh, KY`. Consulta la [guía de mods](MODS.md).

### `mods`: selección opcional de Workshop

Si esta sección no existe en un `config.yml` anterior, se mantiene el modo sin mods. La configuración completa y los ejemplos están en [MODS.md](MODS.md).

| Clave | Predeterminado | Explicación |
| --- | --- | --- |
| `enabled` | `false` | Habilita la selección; requiere Workshop IDs y Mod IDs |
| `workshop_file` | `null` | Archivo de números separados por `;`, relativo a la raíz del proyecto; por ejemplo `Ansible/files/workshopitems.txt` |
| `workshop_items` | `[]` | IDs numéricos adicionales en YAML, preferiblemente entre comillas |
| `mod_ids` | `[]` | Identificadores internos en orden de carga, con mayúsculas y prefijos exactos |
| `map_folders` | `[]` | Carpetas de mapas adicionales que se anteponen al mapa base |

Al desactivar mods se vacían sus líneas de descarga y activación; no se transforma una partida modificada en un mundo vanilla ni se borran las descargas. No se resuelven dependencias automáticamente.

### `firewall`: reglas de Ubuntu

| Clave | Predeterminado | Explicación |
| --- | --- | --- |
| `enabled` | `true` | Activa UFW y aplica reglas. `false` deja el estado y las reglas existentes sin modificar, no lo desactiva |
| `ssh_port` | `22` | Puerto TCP permitido; cambiarlo aquí no cambia el puerto del servicio SSH |
| `extra_udp_ports` | `[]` | Lista de puertos UDP adicionales; normalmente se deja vacía |

Los puertos principales se obtienen de `pz.settings`: no los dupliques aquí. Al cambiar puertos se añaden reglas nuevas, pero no se borran las antiguas. Revísalas con `sudo ufw status` dentro de Ubuntu.

El puente permite que los equipos de la LAN alcancen la VM, incluido SSH según las reglas. El acceso de Vagrant está pensado para administrarla; no redirijas SSH desde Internet como parte de esta guía.

## Reglas del mundo y sandbox

El INI controla jugadores, contraseñas y otras opciones del servidor. Las reglas de **sandbox** —zombis, botín, experiencia…— están en un archivo Lua:

```text
/home/pzuser/Zomboid/Server/daryl_SandboxVars.lua
```

La ruta utiliza `pz.home` y el nombre utiliza `pz.server_name`. Este proyecto genera los valores predeterminados; **todavía no administra SandboxVars mediante YAML**.

Para editarlos:

1. Detén el juego y crea una copia externa de `Zomboid`, como se explica más abajo.
2. Entra con `vagrant ssh` y, dentro de Ubuntu, ejecuta:

   ```sh
   sudo -iu pzuser
   nano ~/Zomboid/Server/daryl_SandboxVars.lua
   ```

3. Cambia opciones conocidas, conservando comas, llaves, tipos y versión del formato Lua. Usa valores compatibles con la build instalada. Algunas reglas solo afectan a zonas nuevas o requieren un mundo nuevo.
4. Guarda, sal del editor y escribe `exit` para volver al usuario `vagrant`. Otro `exit` cierra SSH.
5. Desde el anfitrión, inicia el servicio y consulta el registro:

   ```sh
   vagrant ssh -c "sudo systemctl start zomboid"
   ```

Los cambios manuales no pasan a `config.yml`. Ansible no sustituye SandboxVars, aunque el propio juego puede modificar sus archivos. La selección de mods y mapas se configura según la [guía de mods](MODS.md); las dependencias se eligen manualmente.

## Copias de seguridad y restauración

### Qué hay que guardar

Con las rutas de ejemplo, la partida está en:

```text
/home/pzuser/Zomboid
```

Incluye configuración, cuentas y mundos. **Copiar solo `/opt/pzserver` no guarda la partida.** Conserva también tu `config.yml` en un lugar privado y anota la rama/build utilizada.

Las copias son manuales y deben quedar **fuera de la VM** para sobrevivir a `vagrant destroy` o a un fallo del disco virtual. Guarda otra copia en otro dispositivo si quieres protección frente a la pérdida del anfitrión.

### Crear una copia y descargarla

Los comandos usan nombres predeterminados. Necesitas el cliente **OpenSSH** (`ssh` y `scp`) en el anfitrión. En Windows se puede instalar desde sus características opcionales; en Linux utiliza el paquete cliente de tu distribución.

Desde `Vagrant`, detén el juego para obtener archivos coherentes:

```sh
vagrant ssh -c "sudo systemctl stop zomboid"
```

Comprime el directorio y permite descargarlo con la cuenta de Vagrant:

```sh
vagrant ssh -c "sudo tar -C /home/pzuser -czf /home/vagrant/zomboid-backup.tar.gz Zomboid"
vagrant ssh -c "sudo chown vagrant:vagrant /home/vagrant/zomboid-backup.tar.gz"
vagrant ssh -c "sudo chmod 600 /home/vagrant/zomboid-backup.tar.gz"
```

Crea una carpeta de copias y guarda los datos SSH que Vagrant conoce.

**Windows / PowerShell:**

```powershell
New-Item -ItemType Directory -Force ../backups
vagrant ssh-config | Out-File -Encoding ascii .vagrant/backup-ssh.conf
```

**Linux:**

```sh
mkdir -p ../backups
vagrant ssh-config > .vagrant/backup-ssh.conf
```

Descarga la copia. `default` es el nombre que Vagrant utiliza para identificar esta máquina en la configuración SSH:

```sh
scp -F .vagrant/backup-ssh.conf default:/home/vagrant/zomboid-backup.tar.gz ../backups/zomboid-copia-1.tar.gz
```

**Cambia `zomboid-copia-1.tar.gz` en cada copia** para no sobrescribir la anterior. Comprueba que el archivo existe en el anfitrión y que se puede listar su contenido:

```sh
tar -tzf ../backups/zomboid-copia-1.tar.gz
```

Vuelve a iniciar el juego:

```sh
vagrant ssh -c "sudo systemctl start zomboid"
```

`backups` está ignorada por Git. Sus archivos contienen datos de cuentas: mantenlos privados. La copia temporal dentro de la VM se reemplaza en la siguiente copia; no es tu copia externa definitiva.

### Restaurar

Utiliza una build compatible con la copia. En otra VM, configura antes el mismo `pz.server_name`, usuario y rutas y prepara una instalación compatible del juego.

1. Detén el servicio.
2. Genera de nuevo `.vagrant/backup-ssh.conf` con los pasos anteriores; las claves o los puertos pueden haber cambiado.
3. Sube el archivo:

   ```sh
   scp -F .vagrant/backup-ssh.conf ../backups/zomboid-copia-1.tar.gz default:/home/vagrant/zomboid-restore.tar.gz
   ```

4. Conserva el directorio actual con otro nombre para no mezclar mundos. **Antes de moverlo, comprueba que `Zomboid.antes-restaurar` no existe; si existe, elige otro nombre libre.**

   ```sh
   vagrant ssh -c "sudo test ! -e /home/pzuser/Zomboid.antes-restaurar"
   ```

   Continúa solo si termina correctamente, con código de salida cero. Después:

   ```sh
   vagrant ssh -c "sudo mv -T /home/pzuser/Zomboid /home/pzuser/Zomboid.antes-restaurar"
   vagrant ssh -c "sudo tar -xzf /home/vagrant/zomboid-restore.tar.gz -C /home/pzuser"
   vagrant ssh -c "sudo chown -R pzuser:pzuser /home/pzuser/Zomboid"
   ```

5. Inicia el servicio y comprueba la partida. Conserva el directorio anterior hasta confirmar la recuperación.

El próximo `vagrant provision` aplicará tu `config.yml` sobre el INI restaurado. La contraseña admin configurada también se pasa al juego al arrancar; mantén una configuración coherente con la copia recuperada.

## Ansible sin Vagrant

### Configurar un Ubuntu existente

Es una alternativa para quien ya tenga un servidor Linux; no es necesaria para empezar.

1. Prepara un controlador Linux con Ansible y un destino Ubuntu 24.04+ x86_64 accesible por SSH con permisos sudo.
2. Crea `config.yml` en la raíz. La sección `vm` no se utiliza en este modo.
3. Sustituye la entrada local de `Ansible/inventory` por la IP/hostname remoto. No dejes `localhost ansible_connection=local` si quieres actuar en otra máquina.
4. Desde `Ansible`:

   ```sh
   ansible-galaxy collection install -r requirements.yml
   ansible-playbook site.yml -u TU_USUARIO --become --ask-become-pass
   ```

El playbook no cambia el hostname del servidor remoto.

Las instrucciones para contribuir y ejecutar las pruebas están en [CONTRIBUTING.md](../CONTRIBUTING.md).

### Referencias

- [Instalar Vagrant](https://developer.hashicorp.com/vagrant/install)
- [Primeros pasos y box de ejemplo](https://developer.hashicorp.com/vagrant/tutorials/get-started/setup-project)
- [Ansible local en Vagrant](https://developer.hashicorp.com/vagrant/docs/provisioning/ansible_local)
- [Redes en puente](https://developer.hashicorp.com/vagrant/docs/networking/public_network)
- [Servidor dedicado de Zomboid](https://pzwiki.net/wiki/Dedicated_server)
- [Parámetros de arranque](https://pzwiki.net/wiki/Startup_parameters)

Comprueba las versiones de las páginas: las instrucciones del juego pueden variar entre ramas y builds.
