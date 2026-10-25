# Servidor de Project Zomboid para jugar por Internet

Monta un servidor dedicado de Project Zomboid en tu ordenador para jugar con amigos por Internet. Vagrant crea una máquina virtual Ubuntu y Ansible instala y configura el juego. Solo tienes que ajustar un archivo y redirigir dos puertos en tu router.

Puedes conectarte desde tu red local o desde Internet tras configurar el router. El servidor arranca sin mods por defecto y permite activarlos opcionalmente; puedes cambiar su nombre, recursos, contraseñas y opciones de juego.

## 1. Instalar y descargar

Necesitas un PC Windows o Linux **Intel/AMD x86_64**, virtualización habilitada, Internet y espacio libre para Ubuntu, el juego y las partidas. El ejemplo asigna **8 GB de RAM y 2 CPU a la VM**: deja memoria adicional para tu sistema y el cliente del juego. Reserva al menos 30 GB libres como referencia práctica, y más para copias y mundos grandes.

Instala [VirtualBox](https://www.virtualbox.org/wiki/Downloads) y [Vagrant](https://developer.hashicorp.com/vagrant/install). VirtualBox ejecuta la máquina virtual; Vagrant permite crearla y manejarla con comandos. Ansible se instala dentro de ella: no necesitas instalar Ubuntu, Ansible o SteamCMD manualmente.

Descarga y extrae el ZIP del repositorio, o utiliza Git:

```sh
git clone https://github.com/JotaceDelon/server-zomboid.git
cd server-zomboid
```

Abre PowerShell o una terminal en esa carpeta. Comprueba que `vagrant --version` funciona; si acabas de instalarlo, abre una terminal nueva.

## 2. Configurar

Copia la plantilla a tu archivo personal, desde la raíz del proyecto.

**PowerShell:**

```powershell
Copy-Item config.example.yml config.yml
```

**Linux:**

```sh
cp config.example.yml config.yml
```

Edita `config.yml` con tu editor. Si ya existe, no vuelvas a copiar el ejemplo encima. Conserva las claves e indentación con espacios y guarda como **UTF-8**. Git ignora este archivo porque contiene contraseñas.

Revisa estas opciones:

| Opción | Para qué sirve |
| --- | --- |
| `vm.name` / `vm.hostname` | Nombre en VirtualBox / nombre de Ubuntu. `daryl` es solo el ejemplo |
| `pz.public_name` | Nombre visible del servidor |
| `pz.server_name` | Identificador del mundo y sus archivos; elígelo antes de crear la partida |
| `pz.admin_password` | Sustituye `CAMBIAME` por una contraseña propia de **12 caracteres o más**, entre comillas |
| `pz.settings.Password` | Contraseña para entrar al servidor; `""` significa sin contraseña de entrada |
| `pz.settings.MaxPlayers` / `PVP` | Límite de jugadores y combate entre ellos |
| `pz.settings.Public` | `true` lo anuncia en el listado público; `false` permite conectar por IP igualmente |
| `pz.branch` | `null`: rama predeterminada de Steam; `legacy41`: Build 41, si está disponible. Cliente y servidor deben ser compatibles |
| `vm.memory_mb` / `vm.cpus` | Recursos de la máquina virtual |
| `pz.heap_max_mb` | Memoria máxima de Java: debe dejar al menos 2048 MB para Ubuntu. El ejemplo usa 5120 MB sobre una VM de 8192 MB |

Mantén `pz.update: false` para el uso normal. La primera instalación descargará el juego igualmente.

Para este despliegue, conserva estas opciones dentro de `vm`:

```yaml
  network: public
  ip: null
  bridge: null
```

`public` significa **puente hacia tu red doméstica**, no publicación automática en Internet. El router asignará una IP a la VM. Si Vagrant pregunta por el adaptador, selecciona el Wi-Fi o Ethernet con el que el anfitrión se conecta al router. Puedes fijar su nombre exacto en `bridge` para evitar la pregunta.

Las demás opciones pueden quedarse como están. Tienes la [referencia completa y los ajustes del mundo](doc/GUIA-AVANZADA.md) como consulta opcional.

## 3. Instalar e iniciar el servidor

Desde la raíz del proyecto:

```sh
cd Vagrant
vagrant validate
vagrant up --provider=virtualbox
```

Vagrant crea Ubuntu; Ansible instala el servidor, configura el firewall y arranca el juego. No crees otra VM a mano en VirtualBox.

Espera a que termine sin errores (`failed=0`). La descarga inicial ocupa varios GB y **el juego puede tardar varios minutos en cargar en cada arranque**.

> La pantalla de login de Ubuntu es normal: no necesitas iniciar sesión. Que la VM esté encendida no significa que el juego ya acepte conexiones.

**Todos los comandos `vagrant` siguientes se ejecutan desde la carpeta `Vagrant` del proyecto, en tu ordenador anfitrión.**

Para seguir el arranque:

```sh
vagrant ssh -c "sudo journalctl -u zomboid -f"
```

Espera a `*** SERVER STARTED ****`. Pulsa `Ctrl+C` para salir del registro; no apaga el juego. Los comandos usan el nombre de servicio predeterminado `zomboid`: sustitúyelo si cambias `pz.service_name`.

## 4. Consultar la IP y conectarse

```sh
vagrant ssh -c "ip -4 -brief address"
```

Busca la dirección de tu red doméstica, por ejemplo **`192.168.1.50`**. No utilices `127.0.0.1`, la interfaz NAT `10.0.2.15` ni el sufijo `/24`.

En Project Zomboid, abre **Unirse → Favoritos → Añadir servidor**:

| Casilla | Qué poner |
| --- | --- |
| IP / IP local | La IP de la VM para conectar desde tu red local |
| Puerto | `16261`, salvo que cambies `pz.settings.DefaultPort` |
| Contraseña del servidor | `pz.settings.Password`; **déjala vacía si vale `""`** |
| Usuario | Tu nombre de jugador; para administrar, `admin` |
| Contraseña del usuario | La de tu cuenta de jugador; para `admin`, la de `pz.admin_password` |

En un servidor nuevo con registro abierto, elige un nombre de jugador nuevo y una contraseña para crear tu cuenta; reutilízalos al volver. No compartas la contraseña admin para que otros entren como jugadores normales.

Dentro de tu red utiliza la IP local de la VM. Para conexiones desde fuera, configura el router como se explica a continuación y utiliza la IP pública.

## 5. Abrir el acceso desde Internet

El recorrido de una conexión será:

```text
Jugador → IP pública de tu conexión → Router → IP local de la VM → Zomboid
```

### Redirigir los puertos en el router

1. **Reserva la IP de la VM en el router**, en el apartado DHCP/reservas, para que no cambie. Como alternativa, configura una IP fija válida y libre en `vm.ip`.
2. Abre la administración del router en el navegador. Su dirección suele ser la puerta de enlace de tu red: consúltala con `ipconfig` en Windows o `ip route` en Linux. Utiliza las credenciales de administración de tu router.
3. Busca **Redirección de puertos**, **Port Forwarding**, **NAT** o **Virtual Servers**. Los menús dependen del modelo.
4. Crea y activa estas dos reglas, sustituyendo la IP de ejemplo por la tuya:

   | Regla | Protocolo | Puerto externo | IP interna de destino | Puerto interno |
   | --- | --- | --- | --- | --- |
   | Zomboid | UDP | 16261 | `192.168.1.50` | 16261 |
   | Zomboid directo | UDP | 16262 | `192.168.1.50` | 16262 |

   **El destino es la IP de la VM, no la del Windows/Linux anfitrión.** En modo puente son equipos distintos en tu red. Si tu router acepta rangos, también puedes usar `16261–16262` UDP con los mismos puertos de destino.
5. Guarda las reglas. El firewall de Ubuntu ya permite esos puertos mediante Ansible. Si los cambias en `pz.settings`, aplica la configuración y cambia también las reglas del router.
6. Consulta la **IP pública/WAN** de tu conexión en el router y compártela con los jugadores. Desde fuera utilizarán esa IP, puerto **16261** y las contraseñas del apartado anterior.

Mantén encendidos el anfitrión y la VM, con el juego listo. `Public: true` permite anunciarlo, pero **no sustituye la redirección de puertos**. Para jugar no necesitas redirigir SSH ni RCON.

### Si no funciona desde fuera

- **CGNAT:** el proveedor puede no darte una IP pública propia. Si la WAN del router es privada o del rango `100.64.0.0/10`, o tienes dudas, consulta al proveedor si permite conexiones entrantes y cómo salir de CGNAT. En ese caso, abrir puertos solo en tu router no basta.
- **Dos routers / doble NAT:** ambos pueden estar traduciendo la conexión. Hay que resolver ese doble salto o redirigir en ambos hacia el siguiente equipo; con modo puente de la VM no se elimina el NAT del proveedor o de otro router.
- **Conexión desde fuera:** pide a alguien de otra conexión que entre al juego. Probar tu IP pública desde tu propia LAN puede fallar porque el router no soporta NAT loopback. Los comprobadores que solo prueban TCP no validan estos puertos UDP.
- **IP pública cambiante:** si tu proveedor la cambia, tendrás que comunicar la nueva; puedes configurar DNS dinámico en tu router si lo admite.

La instalación sirve para Internet, pero la accesibilidad exterior depende también del router, el proveedor y la red.

## Uso diario: lo que necesitas recordar

| Quiero… | Qué ejecutar desde `Vagrant` |
| --- | --- |
| Encender la VM y el servidor | `vagrant up` |
| Apagar toda la VM, conservando la partida | `vagrant halt` |
| Detener solo el juego | `vagrant ssh -c "sudo systemctl stop zomboid"` |
| Iniciar solo el juego | `vagrant ssh -c "sudo systemctl start zomboid"` |
| Reiniciar solo el juego | `vagrant ssh -c "sudo systemctl restart zomboid"` |
| Ver si Ubuntu está encendido | `vagrant status` |
| Ver el estado del servicio | `vagrant ssh -c "sudo systemctl status zomboid --no-pager"` |

Con `pz.enabled: true`, el servicio arranca al encender Ubuntu. Después de iniciarlo o reiniciarlo, espera a `SERVER STARTED`; `active (running)` puede aparecer mientras aún carga.

El apagado del servicio solicita `quit` para guardar. Evita el botón **Reiniciar** de VirtualBox como uso habitual: reinicia bruscamente toda la VM. **`vagrant destroy` elimina la máquina y sus datos**, no es un apagado.

### He cambiado `config.yml`: ¿cómo lo aplico?

Guarda el archivo y ejecuta:

```sh
vagrant provision
```

Ansible actualiza la configuración interna y reinicia el juego si hace falta. Sirve para nombres visibles, contraseñas, ajustes del INI y memoria Java. **Reiniciar la VM o el servicio por sí solo no aplica los cambios del YAML.**

Si cambias RAM/CPU, IP o modo de red de la VM, utiliza:

```sh
vagrant halt
vagrant up --provision
```

No necesitas reinstalar ni crear otra VM. Cambiar `pz.server_name` sí selecciona otro mundo; cambiar usuario Linux, rutas o servicio requiere migrar sus datos manualmente.

### ¿Cómo cambio las contraseñas?

Modifica `pz.settings.Password` para la entrada al servidor o `pz.admin_password` para la cuenta admin y ejecuta `vagrant provision`. Los jugadores deben actualizar la casilla correspondiente. El lanzador aplica admin mediante `-adminpassword`; no confundas esa cuenta con la contraseña de entrada.

### ¿Cómo actualizo el juego?

Detén el servicio y guarda antes una copia completa de `/home/pzuser/Zomboid` **fuera de la VM**. Pon `pz.update: true`, ejecuta `vagrant provision` y devuelve la opción a `false`. Si cambias de rama, comprueba compatibilidad de mundo y clientes. Tienes [instrucciones de copia y restauración](doc/GUIA-AVANZADA.md#copias-de-seguridad-y-restauración).

## Problemas habituales

| Problema | Qué revisar |
| --- | --- |
| No responde | Espera a `SERVER STARTED`; comprueba IP, puerto, versión del cliente y que el anfitrión no se haya suspendido |
| Funciona en casa pero no por Internet | Redirección UDP hacia la VM, IP pública correcta, CGNAT o doble NAT |
| Contraseña de servidor inválida | Casilla del servidor = `pz.settings.Password`; vacía si es `""`. Borra cualquier valor guardado incorrecto |
| Contraseña de usuario incorrecta | Usa la contraseña de esa cuenta; para admin, aplica `pz.admin_password` con `vagrant provision` |
| Ubuntu muestra un login | Es normal, el juego funciona en segundo plano |
| Falla la validación | Lee el motivo: contraseña admin de 12 caracteres, nombres/rutas válidos y al menos 2048 MB de margen de RAM real |

Para ver el error concreto del juego:

```sh
vagrant ssh -c "sudo journalctl -u zomboid -n 100 --no-pager"
```

No borres la partida o las cuentas para solucionar una contraseña. Si el juego sigue cargando con progreso, dale tiempo antes de reiniciarlo.

## Servidores con mods

Puedes reutilizar `Ansible/files/workshopitems.txt`, con números separados por `;`, o guardar los Workshop IDs en `config.yml`. La sección opcional `mods` permite activar los módulos y añadir mapas. Necesitas tanto los números de descarga como los IDs internos del mod. Sigue la [guía de mods](doc/MODS.md) antes de aplicarlos a una partida existente.

## Más información

- [Referencia completa, reglas del mundo, copias y Ansible manual](doc/GUIA-AVANZADA.md).
- `config.example.yml` es público y conserva `CAMBIAME`; `config.yml`, `.vagrant`, copias y registros se excluyen de Git. Exclúyelos también si haces un ZIP a mano.
- [Crear un servidor con mods](doc/MODS.md): archivo de números Workshop o lista YAML, IDs de activación, dependencias y mapas. Se mantienen desactivados por defecto. Las reglas Lua de sandbox se configuran según la guía avanzada.

Referencias: [puertos del juego, The Indie Stone](https://projectzomboid.com/blog/news/2022/09/upstairs-downstairs/), [ejemplo de redirección y problemas de NAT, TP-Link](https://www.tp-link.com/us/support/faq/1379/).

## Descargo de responsabilidad y soporte

He creado y compartido este proyecto con la intención de facilitar la instalación de un servidor de Project Zomboid. Es un proyecto personal, proporcionado tal cual, sin garantía de funcionamiento, disponibilidad, seguridad o compatibilidad con todos los equipos, redes y versiones del juego o de sus dependencias.

Su uso es voluntario y bajo tu responsabilidad. Te corresponde revisar la configuración, proteger las credenciales, mantener el sistema actualizado y realizar copias de seguridad antes de modificar o actualizar el servidor. En la medida permitida por la legislación aplicable, no asumo responsabilidad por pérdidas de datos, interrupciones del servicio, problemas de seguridad u otros daños derivados de su uso.

Si tienes dudas o encuentras un error, puedes comunicarlo mediante una incidencia en este repositorio. Agradezco los informes que incluyan pasos para reproducir el problema y registros sin contraseñas ni datos personales. No obstante, no ofrezco soporte garantizado ni me comprometo a leer o responder todos los mensajes, resolver incidencias en un plazo determinado o mantener el proyecto de forma continuada.

Este proyecto es independiente y no está afiliado ni cuenta con el respaldo oficial de The Indie Stone ni de los desarrolladores de las herramientas utilizadas.
