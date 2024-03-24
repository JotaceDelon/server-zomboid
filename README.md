# server-zomboid
Monta y configura un servidor de Zomboid haciendo uso de Vagrant y Ansible.

Las instrucciones están pensadas para realizar el proceso en un Linux Ubuntu, en el que se generará una máquina virtual también Linux Ubuntu (sin interfaz) la cual será la que haga la función de servidor de Project Zomboid.

# Prerrequisitos de la máquina
## Instalaciones
Necesitaremos los siguientes programas instalados.
- VirtualBox
```
sudo apt install virtualbox
```
- Openssh
```
sudo apt install openssh-server
```
- Ansible
```
sudo apt install ansible
```
- Vagrant
```
sudo apt install vagrant
```

# Generación de clave SSH
Generar una clave para ejecutar Ansible, sin contraseña, es la que utilizará Ansible para conectarse y hacer las configuraciones de forma remota, si usamos "ansible" como nombre Vagrant se encargará de aprovisionarla en la máquina, ejecutaremos este comando dentro de la carpeta ~/.ssh que es de dónde se encargará de recogerla Vagrant:
```
ssh-keygen -t ed25519 -C "ansible"
```

# Agregar la box de ubuntu a Vagrant
Añadir la box que vamos a utilizar para levantar la máquina con Vagrant:
```
vagrant box add ubuntu/focal64
```

# Levantar la máquina
Ir al directorio server-zomboid/Vagrant y ejecutar:
```
vagrant up
```
Es posible que pregunte que interfaz de red queremos utilizar. La IP asignada por defecto es 192.168.100.216.

# Ansibilizar la máquina
Ir al directorio server-zomboid/Ansible y ejecutar:
```
ansible-playbook --ask-become-pass -u vagrant daryl.yml -v
```
Pedirá una contraseña, en este caso es "vagrant". Esperamos que termine el proceso.

# Iniciar el servidor
Primero iniciaremos sesión como usuario pzuser, la contraseña es "secret".

El servidor vamos a iniciarlo desde tmux, esto hará que el servidor no se apague si accidentalmente cerramos el terminal o perdemos la conexión ssh, Ansible se encargará de aprovisionar este paquete en el servidor.

- Desde la terminal tmux vamos a donde se encuentra el script que inicia el servidor y lo ejecutamos:
```
tmux
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

# Aviso de seguridad
Como vemos las contraseñas usadas deberían cambiarse para más seguridad a posteriori de completar el proceso.

Ansible se asegura que el firewall esté activado y con los puertos correctos abiertos.

No se ha tenido en consideración ninguna configuración adicional de seguridad, por lo que es posible que el servidor no sea del todo seguro, usa este proyecto bajo tu propia responsabilidad. 
