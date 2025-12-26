# bot-telegram-ckan
Bot de telegram que usa los endpoints provistos por la API de CKAN para identificar y notificar de cambios en datasets u organizaciones de un catálogo CKAN. El mismo sigue la siguiente lógica: </br>
<img width="3840" height="596" alt="Untitled diagram _ Mermaid Chart-2025-07-16-000221" src="https://github.com/user-attachments/assets/1aae1786-350f-4152-b293-b3c324402f06" />
Haya o no novedades para notificar, el bot envía un mail a los administradores para avisar de su ejecución. </br> 
## Para replicar el proyecto
Este bot es fácilmente replicable para otros portales CKAN. Previamente se debe haber creado un canal y un bot de Telegram, luego se debe crear un archivo env usando como referencia ejemplo.env. En el mismo se ponen las claves secretas (token para conexión a telegram y para casilla de correo desde donde se envían notificaciones a administradores) así como variables de configuración, como por ejemplo la url del portal CKAN que se quiere consultar y el nombre del archivo .json que servirá de memoria al bot. (Se debe poner un nombre aunque el archivo no exista todavía, el bot lo crea en su primera corrida). 
En el archivo texts.py están los textos que envía el bot, en caso de que se quieran editar.

