# AWS URL Shortener (S3 + EC2 + DynamoDB)

Aplicación web integral para acortar enlaces construida con servicios cloud de AWS (**Amazon S3**, **Amazon EC2** y **Amazon DynamoDB**) junto a un backend moderno en **FastAPI** y frontend vanilla (HTML5, CSS3, JavaScript).

---

## 🏗️ Arquitectura de la Solución

```
                    ┌───────────────────────────────┐
                    │       Cliente (Navegador)     │
                    └──────────────┬────────────────┘
                                   │
              1. Descarga Interfaz │ 2. POST /shorten
                 (HTML/CSS/JS)     │    GET /{uuid} (Redirección 307)
                                   │
               ▼                   ▼
     ┌───────────────────┐    ┌───────────────────────────────┐
     │   Amazon S3       │    │          Amazon EC2           │
     │ (Static Website)  │    │  FastAPI + Uvicorn + Systemd  │
     └───────────────────┘    └──────────────┬────────────────┘
                                             │
                                             │ 3. IAM Role (Instance Profile)
                                             │    PutItem / GetItem
                                             ▼
                                ┌───────────────────────────┐
                                │      Amazon DynamoDB      │
                                │   (Table: short_code PK)  │
                                └───────────────────────────┘
```

1. **Frontend (Amazon S3)**: Interfaz de usuario servida como sitio estático en S3. Realiza llamadas asíncronas vía `fetch()` a la API en EC2.
2. **Backend (Amazon EC2)**: Instancia Linux (Ubuntu) ejecutando FastAPI con Uvicorn bajo gestión de procesos con **systemd**.
3. **Base de Datos (Amazon DynamoDB)**: Almacena pares `short_code` (UUID v4), `original_url` y fecha de creación `created_at`.
4. **Seguridad (AWS IAM)**: La instancia EC2 utiliza un **IAM Instance Profile** con políticas de mínimos privilegios para interactuar con DynamoDB sin almacenar claves ni credenciales en disco o código.

---

## 📁 Estructura del Proyecto

```text
aws-url-shortener/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuración y variables de entorno
│   │   ├── database.py           # Conexión y operaciones en DynamoDB (Boto3)
│   │   ├── models.py             # Schemas Pydantic con validación de URL
│   │   ├── routes.py             # Endpoints /shorten, /{short_code}, /urls/{short_code}
│   │   └── main.py               # Aplicación FastAPI y CORS
│   ├── requirements.txt          # Dependencias de Python
│   └── urlshortener.service      # Servicio Systemd para autoarranque en EC2
├── frontend/
│   ├── index.html                # Interfaz de usuario
│   ├── style.css                 # Estilos limpios y responsivos
│   └── app.js                    # Consumo de API y lógica de copiado
├── scripts/
│   ├── ec2_setup.sh              # Aprovisionamiento automatizado en EC2
│   └── dynamodb_policy.json      # Política IAM con permisos mínimos
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Guía de Despliegue Paso a Paso

### Paso 1: Crear la tabla en Amazon DynamoDB
1. Ve a la consola de **DynamoDB** en la región de tu preferencia (ej. `us-east-1`).
2. Haz clic en **Create table**.
3. Configuración:
   - **Table name**: `url-shortener-links`
   - **Partition key**: `short_code` (Tipo: `String`)
   - **Table class**: DynamoDB Standard
   - **Capacity mode**: On-demand (Bajo demanda)

### Paso 2: Crear el Rol IAM para EC2
1. Ve a la consola de **IAM** > **Roles** > **Create role**.
2. Selecciona **AWS service** y caso de uso **EC2**.
3. En permisos, crea una política inline o personalizada usando el archivo [`scripts/dynamodb_policy.json`](file:///C:/Users/estudiante.LABS/.gemini/antigravity/scratch/aws-url-shortener/scripts/dynamodb_policy.json).
4. Asigna un nombre al rol (ej. `EC2-DynamoDB-URLShortener-Role`) y créalo.

### Paso 3: Desplegar la instancia EC2
1. Lanza una instancia EC2:
   - **AMI**: Ubuntu Server 22.04 LTS o 24.04 LTS (x86_64).
   - **Tipo**: `t2.micro` o `t3.micro` (Capa gratuita).
   - **IAM Instance Profile**: Asocia el rol `EC2-DynamoDB-URLShortener-Role`.
   - **Security Group**:
     - SSH (Puerto 22) desde tu IP personal.
     - Custom TCP (Puerto 8000) desde cualquier origen (`0.0.0.0/0`) para exponer la API.
2. Conéctate a la instancia por SSH:
   ```bash
   ssh -i tu-clave.pem ubuntu@<IP-PUBLICA-EC2>
   ```
3. Clona el repositorio en `/home/ubuntu/aws-url-shortener`:
   ```bash
   git clone <URL_DE_TU_REPOSITORIO> /home/ubuntu/aws-url-shortener
   ```
4. Configura el archivo `.env`:
   ```bash
   cd /home/ubuntu/aws-url-shortener/backend
   cp ../.env.example .env
   nano .env
   ```
   *Actualiza `BASE_URL` con la IP pública de tu EC2 (`http://<IP-PUBLICA-EC2>:8000`).*
5. Ejecuta el script de aprovisionamiento:
   ```bash
   chmod +x /home/ubuntu/aws-url-shortener/scripts/ec2_setup.sh
   /home/ubuntu/aws-url-shortener/scripts/ec2_setup.sh
   ```

### Paso 4: Desplegar el Frontend en Amazon S3
1. En tu máquina local, abre [`frontend/app.js`](file:///C:/Users/estudiante.LABS/.gemini/antigravity/scratch/aws-url-shortener/frontend/app.js) y edita la constante:
   ```javascript
   const API_BASE_URL = "http://<TU_IP_PUBLICA_EC2>:8000";
   ```
2. Ve a la consola de **Amazon S3** y crea un bucket (ej. `mi-acortador-enlaces-aws-2026`).
3. Desactiva **Block all public access** (bloquear todo el acceso público) y confirma.
4. Habilita **Static website hosting** en la pestaña **Properties**:
   - Index document: `index.html`
5. Sube los archivos `index.html`, `style.css` y `app.js`.
6. En la pestaña **Permissions**, añade la siguiente política de lectura pública al bucket:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::TU-NOMBRE-DE-BUCKET/*"
       }
     ]
   }
   ```
7. Obtén el endpoint web estático generado por S3 y ábrelo en el navegador.

---

## 🧪 Pruebas de Funcionamiento

1. **Creación de URL acortada**:
   ```bash
   curl -X POST http://<IP-PUBLICA-EC2>:8000/shorten \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://aws.amazon.com/es/dynamodb/"}'
   ```
2. **Consulta de metadata**:
   ```bash
   curl http://<IP-PUBLICA-EC2>:8000/urls/<UUID>
   ```
3. **Redirección HTTP 307**:
   Abre `http://<IP-PUBLICA-EC2>:8000/<UUID>` en un navegador. Debe redirigirte de inmediato a la URL original.
4. **Verificación de 404**:
   Consulta un UUID aleatorio que no exista. Deberá devolver status 404 con `"Short URL not found"`.
