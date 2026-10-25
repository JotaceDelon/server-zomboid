# Servidores con mods

Puedes añadir o quitar mods al servidor desde `config.yml`, utilizando un archivo de números separados por `;` o una lista YAML. No necesitas crear otro servidor: mantén el mismo `pz.server_name` para continuar con tu mundo.

Los mods están desactivados por defecto. Guarda una [copia de seguridad](GUIA-AVANZADA.md#copias-de-seguridad-y-restauración) antes de cambiar la selección de una partida existente; algunos contenidos o mapas requieren un mundo nuevo.

## 1. Obtener los identificadores

Un mod de Workshop utiliza dos identificadores distintos:

| Dato | Dónde encontrarlo | Para qué sirve |
| --- | --- | --- |
| **Workshop ID** | Número de la URL de Steam, después de `?id=` | Descargar el paquete |
| **Mod ID** | Ficha del autor o campo `id=` de su archivo `mod.info` | Activar el módulo del paquete |

Un paquete puede contener varios módulos. Añade su número de Workshop una vez y los Mod IDs de los módulos que quieras utilizar. Incluye también las dependencias y respeta el orden de carga indicado por el autor.

Las colecciones de Steam agrupan elementos: necesitas los IDs de sus mods, no el ID de la colección. Utiliza contenido compatible con la build del servidor y con multijugador.

## 2. Configurar los mods

Añade o edita la sección `mods` en la raíz de `config.yml`, al mismo nivel que `vm`, `pz` y `firewall`.

### Mediante un archivo de números

[`Ansible/files/workshopitems.txt`](../Ansible/files/workshopitems.txt) incluye un ejemplo con [Better Sorting](https://steamcommunity.com/sharedfiles/filedetails/?id=2313387159):

```text
2313387159
```

Para varios paquetes, escribe sus números separados por punto y coma: `numero1;numero2;numero3`. No pongas URLs ni comentarios dentro del archivo. Puedes utilizar ese archivo o crear `Ansible/files/workshopitems.local.txt`, ignorado por Git, para tu lista personal.

Con el archivo de ejemplo, la configuración es:

```yaml
mods:
  enabled: true
  workshop_file: Ansible/files/workshopitems.txt
  workshop_items: []
  mod_ids:
    - 'BetterSortCC'
  map_folders: []
```

La ruta del archivo es relativa a la raíz del proyecto, aunque ejecutes Vagrant desde su subcarpeta. Al modificar los números, actualiza también `mod_ids` con los módulos correspondientes.

### Mediante una lista YAML

Si prefieres guardar todo en `config.yml`, utiliza `workshop_file: null` y completa `workshop_items`:

```yaml
mods:
  enabled: true
  workshop_file: null
  workshop_items:
    - '2313387159'
  mod_ids:
    - 'BetterSortCC'
  map_folders: []
```

Si usas archivo y lista a la vez, se combinan: primero el archivo y después YAML, sin números duplicados.

Los Mod IDs distinguen mayúsculas de minúsculas y se escriben exactamente como indique el autor o la configuración generada por tu build. El proyecto conserva sus prefijos sin modificarlos. Si un ID necesita una barra inicial, escríbelo entre comillas simples, por ejemplo `'\MiMod'`.

## 3. Mapas adicionales

Además de sus Workshop IDs y Mod IDs, algunos mods de mapas requieren el **Map Folder** indicado por el autor:

```yaml
  map_folders:
    - 'MiMapa'
    - 'OtroMapa'
```

Se añaden en ese orden antes del mapa base: `Map=MiMapa;OtroMapa;Muldraugh, KY`. Puedes cambiar el mapa base mediante `pz.settings.Map` si el mod lo requiere.

Los nombres anteriores son ilustrativos: utiliza los de tus mapas. Los puntos de aparición, regiones y reglas de SandboxVars se editan por separado cuando lo requiera el autor. Consulta la [guía avanzada](GUIA-AVANZADA.md#reglas-del-mundo-y-sandbox).

## 4. Aplicar los cambios

Desde la carpeta `Vagrant`:

```sh
vagrant provision
```

Ansible actualiza las líneas `WorkshopItems`, `Mods` y `Map`, y reinicia el juego si cambia su configuración. Zomboid descarga los paquetes al arrancar; los clientes reciben los mods distribuidos por el servidor al conectar mediante Steam, según sus requisitos.

La descarga puede alargar el arranque. Para seguirlo:

```sh
vagrant ssh -c "sudo journalctl -u zomboid -f"
```

Espera a `SERVER STARTED` antes de entrar. `Ctrl+C` cierra la consulta del registro sin apagar el juego. Activar mods no requiere cambiar los puertos del router.

En el ejemplo de Better Sorting, las categorías del inventario se vuelven más específicas: aparecen etiquetas como «Ropa - Accesorio», «Ropa - Bolsa» o «Limpieza». El mod no añade un botón propio.

## Actualizar o desactivar

- **Cambiar la selección:** edita el archivo/listas y ejecuta `vagrant provision`.
- **Desactivar todos:** establece `mods.enabled: false` y ejecuta `vagrant provision`.
- **Reiniciar sin cambiar configuración:** `vagrant ssh -c "sudo systemctl restart zomboid"`.

Desactivar mods vacía sus listas de descarga y activación; no borra los archivos descargados ni convierte una partida modificada en vanilla. Algunos mundos dependen de sus mods y requieren recuperarlos o restaurar una copia compatible.

El juego gestiona las versiones de Workshop. El proyecto no archiva ni fija versiones de mods; `pz.update` actualiza el servidor del juego, no selecciona versiones de Workshop.

## Problemas frecuentes

| Problema | Qué revisar |
| --- | --- |
| Hay números, pero el contenido no aparece | Faltan Mod IDs, dependencias o el formato correcto para la build |
| Lista rechazada | Números para Workshop, un Mod ID por elemento YAML y separadores `;` en el archivo |
| Archivo no encontrado | Ruta relativa a la raíz, existente y sin componentes `..` |
| Error de carga en Linux | Mayúsculas/minúsculas, requisitos del autor y compatibilidad con la build |
| Versiones de Workshop distintas entre cliente y servidor | Identifica el mod desactualizado, actualízalo y reinicia el lado correspondiente |
| Falla después de retirar contenido | Recupera la selección o una copia compatible; no borres cuentas para resolverlo |

Las dependencias se seleccionan manualmente. La compatibilidad y los permisos de uso dependen de cada autor. El repositorio incluye el ID del ejemplo, no sus archivos.

Referencia: [mods en el servidor dedicado de Project Zomboid](https://pzwiki.net/wiki/Dedicated_server#Installing_mods).
