# Introducción
Este proyecto pretende automatizar la creación de un servidor de "Proyect Zomboid" para ello se usará Vagrant y Ansible, en este documento veremos las acciones necesarias para crear el servidor de forma manual, proceso que luego pasará a automatizarse.

# Utilidades
 - Configurar teclado español (por si hubiera que intervenir directamente en el servidor):
```
sudo loadkeys es
```

 - Actualizar la release de Ubuntu, este paso es opcional:
```
do-release-upgrade -f DistUpgradeViewNonInteractive
```

- Instalar ifconfig para depuración IP:
```
sudo apt install net-tools -y
```

# Configuraciones necesarias
En esta parte del documento se definirán las tareas necesarias a realizar para configurar e instalar el servidor.

 - Añadir repositorio multiverso, añadir arquitectura, actualizar repositorios (pide confirmación cuidado):
```
sudo add-apt-repository multiverse; sudo dpkg --add-architecture i386; sudo apt update
```

- Instalar steamcmd:
```
sudo apt install steamcmd
```

- Habilitar repositorio non-free:
```
sudo apt-get install software-properties-common -y
sudo apt-add-repository non-free
```

- Instalar steamcmd:
```
sudo dpkg --add-architecture i386
sudo apt-get update -y
sudo apt-get install steamcmd -y
```

- Creamos un usuario y establecemos la contraseña:
```
sudo adduser pzuser
```

- Instalar servidor zomboid:
```
sudo mkdir /opt/pzserver
sudo chown pzuser:pzuser /opt/pzserver
```

- Login cómo pzuser:
```
sudo -u pzuser -i
```
- Crear script de instalación/actualización del servidor que ejecutará steamcmd:
```
cat >$HOME/update_zomboid.txt <<'EOL'
// update_zomboid.txt
//
@ShutdownOnFailedCommand 1 //set to 0 if updating multiple servers at once
@NoPromptForPassword 1
force_install_dir /opt/pzserver/
//for servers which don't need a login
login anonymous
app_update 380870 validate
quit
EOL
```

- Ahora instalamos el server haciendo uso del script anterior:
```
export PATH=$PATH:/usr/games
steamcmd +runscript $HOME/update_zomboid.txt
```

# Configuración firewall
Habrá que poner reglas especiales para el firewall por lo que vamos al super usuario y si hacemos sudo ufw status podemos ver que el firewall está deshabilitado lo cual no está bien, para añadir las excepciones al firewall:
```
sudo ufw allow 22
```
Necesitamos añadir unos puertos para el servidor de Project Zomboid
```
sudo ufw allow 16261/udp
sudo ufw allow 16262/udp
```
Puede que necesitemos estos otros puertos:
```
sudo ufw allow 8766/udp
sudo ufw allow 8767/udp
```
Para activar el firewall:
```
sudo ufw enable
```
Para reiniciar el firewall:
```
sudo ufw reload
```

# Iniciar el servidor
- Vamos a hacerlo desde tmux, esto hará que el servidor no se apague si accidentalmente cerramos el terminal o perdemos la conexión ssh:
```
sudo apt-get install tmux
tmux
```
- Vamos a donde se encuentra el script que inicia el servidor y lo ejecutamos:
```
cd /opt/pzserver/
bash start-server.sh
```
- Para cerrar el servidor después, en la pantalla dónde se está ejecutando:
```
quit
```
- Y para salir de tmux:
```
exit
```

# Configuraciones opcionales
- Se habrá creado una carpeta Zomboid, si nos dirigimos a ella y a Server vemos configuraciones básicas que podemos tocar del servidor en el fichero servertest.ini, como por ejemplo el nombre del servidor:
```
cd ~/Zomboid/Server
nano servertest.ini
```

# Instalación de mods
Para instalar mods en el servidor necesitamos los ID de los mods que queremos instalar en el servidor, una forma sencilla de obtener estos ID sin copiarlos uno por uno de la lista de mods (el ID del mod forma parte de la ruta en la que se encuentra el mod en la Workshop), podemos hacer lo siguiente:
1. Vamos a la Workshop de Steam y nos suscribimos a los mods que queramos que estén en el servidor.
2. Creamos una colección en Explorar-Artículos suscritos-Guardar en la colección.
3. Una vez puesto un nombre y creada la colección la hacemos pública, luego podemos cambiar esto, pero necesitamos que sea pública para el siguiente paso.
4. Vamos a la web https://getcollectionids.moonguy.me/ y pegamos en enlace de nuestra colección
5. Copiamos la lista de IDS separados por punto y coma, y la guardamos.
6. Ya podemos poner el repositorio en privado, o si va a ser un servidor para jugar con amigos, puede ser útil dejar la visibilidad en sólo amigos, permitiendo así que puedan tener los mismos mods que el servidor de forma sencilla.

Ahora que ya tenemos la lista de mods tendríamos que ir al fichero indicado de configuraciones opcionales y en la línea "WorkshopItems=" añadimos los ID copiados anteriormente.

